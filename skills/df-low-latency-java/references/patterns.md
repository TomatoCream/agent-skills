# Low-Latency Java Patterns Reference

## 1. Single-Writer Principle

**Rule:** For any item of data, only one thread writes. Multiple readers are fine.

**Why:** 393x speedup -- single thread completes 500M counter increments in 300ms vs 118,000ms with two contending threads. Reads are free via cache coherency (MESI shared state); writes cause exclusive ownership transitions that invalidate caches on other cores.

**Implementation patterns:**

| Pattern | Description |
|---------|-------------|
| Single-threaded BLP | All state mutation in one thread (LMAX model). Input via Disruptor/Aeron subscription, output via publication. |
| Thread-per-core + message passing | Each core owns its data. Communicate via lock-free queues (Agrona ring buffers), never shared mutable state. |
| Aeron Agent model | `Agent` / `AgentRunner` / `CompositeAgent` -- single-threaded event loops, `doWork()` called by runner. No context switches. |

---

## 2. False Sharing

Cache lines are **64 bytes**. Two threads writing logically unrelated fields on the same cache line = false sharing.

**Fixes:**

```java
// @Contended adds 128B padding (2x cache line, accounts for prefetcher)
// Requires -XX:-RestrictContended for non-JDK classes
@jdk.internal.vm.annotation.Contended
private volatile long sequence;

// Manual padding: 7 longs = 56 bytes fills rest of 64-byte cache line
class PaddedSequence {
    long p1, p2, p3, p4, p5, p6, p7;
    volatile long value;
    long p8, p9, p10, p11, p12, p13, p14;
}
```

**Note:** HotSpot reorders fields by size (longs first, then ints, then shorts, then bytes). Group fields accessed by the same thread together. Agrona ring buffers use explicit offset constants (`HEAD_POSITION_OFFSET`, `TAIL_POSITION_OFFSET`) with 64-byte spatial separation.

---

## 3. VarHandle Memory Ordering

### Mode Table

| Mode | Guarantees | Cost on x86 | Use Case |
|------|-----------|-------------|----------|
| **Plain** | None. Allows elimination/reordering. | Free | Thread-confined or lock-protected |
| **Opaque** | Atomicity (no torn long/double), eventual visibility, progress | Free | Status flags, spin-loop termination |
| **Release/Acquire** | Causality: writes before `setRelease` visible after `getAcquire` on same var | **Free on x86/TSO** | Producer-consumer, most j.u.c internals |
| **Volatile** | Total order across all threads | MFENCE | Mutual exclusion, global sequence agreement |

`lazySet` = `setRelease`. Performance: Plain > Opaque > Release/Acquire > Volatile.

### SPSC Pattern (Release/Acquire)

```java
// Setup
private static final VarHandle SEQ;
static {
    try {
        SEQ = MethodHandles.lookup()
            .findVarHandle(RingBuffer.class, "sequence", long.class);
    } catch (Exception e) { throw new ExceptionInInitializerError(e); }
}
private long sequence;

// Producer: write data THEN publish sequence
buffer[idx] = data;                    // plain store
SEQ.setRelease(this, sequence + 1);    // release fence -- all prior writes visible

// Consumer: read sequence THEN read data
long seq = (long) SEQ.getAcquire(this); // acquire fence -- all subsequent reads see prior writes
if (seq > lastSeen) {
    Object data = buffer[idx];          // guaranteed to see producer's write
}
```

### CAS for Lock-Free State Machines

```java
// Strong CAS: full volatile semantics, never fails spuriously
boolean success = STATE.compareAndSet(this, IDLE, RUNNING);

// Weak CAS: may fail spuriously, cheaper -- use in retry loops
while (!STATE.weakCompareAndSet(this, expected, desired)) {
    expected = (int) STATE.getAcquire(this);
}
```

---

## 4. GC Avoidance

**Rules:** No `new` on hot path. No autoboxing. No String concatenation (`+`).

| Strategy | Technique |
|----------|-----------|
| Object pooling | Pre-allocate at startup, acquire/release cycle |
| Flyweight pattern | SBE codecs: typed view over raw buffer, zero allocation |
| Off-heap | `DirectByteBuffer`, `Unsafe`, Foreign Memory API (JDK 21+) |
| ThreadLocal reuse | Per-thread scratch buffers, encoders, decoders |
| Primitive collections | Agrona `Long2ObjectHashMap`, Eclipse Collections `LongObjectHashMap` |

### ThreadLocal Buffer Reuse

```java
private static final ThreadLocal<ByteBuffer> BUFFER =
    ThreadLocal.withInitial(() -> ByteBuffer.allocateDirect(4096));

public void onMessage(DirectBuffer src, int offset, int length) {
    ByteBuffer buf = BUFFER.get();
    buf.clear();
    // reuse buf -- zero allocation per call
}
```

### Object Pool Acquire/Release

```java
public final class ObjectPool<T> {
    private final T[] pool;
    private int index;

    @SuppressWarnings("unchecked")
    public ObjectPool(int size, Supplier<T> factory) {
        pool = (T[]) new Object[size];
        for (int i = 0; i < size; i++) pool[i] = factory.get();
        index = size - 1;
    }

    public T acquire() {
        if (index < 0) throw new IllegalStateException("pool exhausted");
        return pool[index--];
    }

    public void release(T obj) {
        pool[++index] = obj;  // single-writer: only one thread calls release
    }
}
```

**GC choices:** EpsilonGC (`-XX:+UseEpsilonGC`) for zero-GC (app must not fill heap). ZGC/Shenandoah for sub-1ms pauses when some allocation is unavoidable.

---

## 5. Mechanical Sympathy

### Cache Hierarchy Latencies (Intel Skylake)

| Level | Latency | Notes |
|-------|---------|-------|
| L1 | ~1 ns (4 cycles) | 32-64 KB per core |
| L2 | ~3 ns (12 cycles) | 256 KB per core |
| L3 | ~10 ns (42 cycles) | Shared across cores |
| Main memory | ~60-100 ns | 42 cycles + 51 ns |
| Branch misprediction | 16-20 cycles | |
| TLB miss (L1 DTLB) | 9 cycles | |

**Sequential vs random access (2GB array):** Linear walk 0.88 ns/element. Random heap walk 9.2-28.9 ns/element. TLB misses rise from 0.02% to 33.4%. **Sequential is 5-33x faster.**

**Design rules:**
- **Sequential access:** Arrays over linked structures. Iterate in memory order.
- **Cache-line alignment:** Keep hot fields in same 64-byte line. Separate writer fields.
- **Branch prediction:** Common case as fall-through path. Sorted data helps.
- **NUMA:** Cross-socket memory access ~3x slower. Pin threads + memory to same node with `numactl`. Disable kernel NUMA balancing.
- **Thread affinity:** Pin to isolated cores (`taskset`, `isolcpus`). Eliminates scheduler migration and cache pollution.

---

## 6. Escape Analysis Limitations

JVM escape analysis enables **scalar replacement** (fields remapped to registers/stack slots) -- NOT true stack allocation.

**EA fails on:**
- **Control flow merges:** Same object type created in if/else branches -> 16 bytes/op allocation vs zero
- **Non-inlined methods:** If callee not inlined, JVM cannot prove non-escape
- **Identity-dependent operations:** `synchronized`, `identityHashCode()`

**Mitigation:** Graal's **Partial Escape Analysis** is more resilient than HotSpot C2 for complex data flows. For hot paths, avoid branched object creation entirely.

---

## 7. Concurrency Without Locks

**Why `ConcurrentHashMap`/`BlockingQueue` are too slow:** Multiple CAS contentions on shared head/tail/size variables. Each CAS = cache-line invalidation across cores.

### Benchmark: Disruptor vs ArrayBlockingQueue

| Metric | Disruptor (Unicast) | ArrayBlockingQueue |
|--------|--------------------|--------------------|
| Throughput | **160M ops/sec** | 21M ops/sec |
| Mean latency | **52 ns** | 32,757 ns |
| p99.99 latency | **8,192 ns** | 4,200,000 ns |

Disruptor restricts CAS to producer sequence claiming only. Consumers track position independently.

**Agrona `OneToOneRingBuffer`:** Completely CAS-free. Uses negative length values as in-progress markers with VarHandle release/acquire. One producer, one consumer, zero CAS.

**Agrona `ManyToOneRingBuffer`:** CAS only for tail position claiming. Producer/consumer fields spatially separated with 64-byte padding to prevent false sharing.

### Busy-Spin with Thread.onSpinWait()

```java
while ((long) SEQ.getAcquire(this) < targetSequence) {
    Thread.onSpinWait();  // x86 PAUSE instruction: reduces power, avoids pipeline flush
}
```

`Thread.onSpinWait()` is a JVM intrinsic mapping to x86 `PAUSE`. It signals the CPU that this is a spin loop, improving performance of the spinning core and freeing execution resources for the sibling hyperthread.

---

## Quick Reference: JVM Flags

```
-XX:-RestrictContended          # Enable @Contended outside JDK
-XX:+UseEpsilonGC               # Zero GC (must not fill heap)
-XX:+AlwaysPreTouch             # Pre-fault heap pages at startup
-XX:+UseLargePages              # 2MB/1GB pages, reduce TLB misses
-XX:+UseCountedLoopSafepoints   # Prevent safepoint delay in counted loops
-XX:+TieredCompilation          # Ensure hot code is JIT-compiled early
```

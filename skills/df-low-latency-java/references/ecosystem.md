# Low-Latency Java Ecosystem Beyond Aeron/Agrona/SBE

Quick reference for LMAX Disruptor, Chronicle Queue/Map, thread affinity, object pooling, and primitive collections.

---

## LMAX Disruptor

Lock-free ring buffer for intra-process (same JVM) inter-thread communication. Uses **sequence counters** (not head/tail pointers) -- each producer/consumer tracks its own position independently, implementing single-writer at the data structure level. LMAX achieved 6M TPS single-threaded on their trading platform. Benchmarks show ~160M ops/sec vs ArrayBlockingQueue ~21M ops/sec.

**Core concepts:**
- **Pre-allocated events** -- RingBuffer slots populated by EventFactory at construction, then reused forever. Zero GC on hot path.
- **ProducerType.SINGLE** -- avoids CAS entirely, ~3x faster than MULTI.
- **BusySpinWaitStrategy** -- lowest latency, burns a full core. Only use with more physical cores than handler threads. Other strategies: YieldingWaitStrategy, SleepingWaitStrategy, BlockingWaitStrategy.
- **Buffer size must be power of 2** -- enables bitwise AND for index wrapping.

**Pipeline wiring (DAG):**
```java
// A and B run in PARALLEL, C waits for both, D waits for C
disruptor.handleEventsWith(handlerA, handlerB)
         .then(handlerC)
         .then(handlerD);
```

**Setup and publish pattern:**
```java
Disruptor<OrderEvent> disruptor = new Disruptor<>(
    OrderEvent::new,              // EventFactory
    1024,                         // buffer size (power of 2)
    DaemonThreadFactory.INSTANCE,
    ProducerType.SINGLE,
    new BusySpinWaitStrategy()
);
disruptor.handleEventsWith(new MyHandler()).then(new ClearingHandler());
disruptor.start();

RingBuffer<OrderEvent> ringBuffer = disruptor.getRingBuffer();

// Recommended: EventTranslator (guarantees publish)
ringBuffer.publishEvent((event, sequence) -> event.set(id, price, qty));

// Legacy: two-phase (MUST use try/finally)
long seq = ringBuffer.next();
try {
    ringBuffer.get(seq).set(id, price, qty);
} finally {
    ringBuffer.publish(seq);
}
```

**EventHandler** receives `(event, sequence, endOfBatch)`. Use `endOfBatch` for I/O batching (flush network buffer only on last event of batch). Place a ClearingHandler at end of chain to null references and prevent memory leaks across ring wraps.

---

## Disruptor vs Aeron

| Aspect | Disruptor | Aeron |
|---|---|---|
| Scope | Intra-process (same JVM) | Inter-process + network |
| Transport | Shared memory ring buffer | Shared memory IPC, UDP, TCP |
| Persistence | None | Aeron Archive for replay |
| Use case | Event pipeline within a process | Cross-process/machine messaging |

**Use both together:** Disruptor for the internal event pipeline (journal, replicate, process, cleanup stages), Aeron for communication between processes and machines. Agrona's ring buffers serve a similar role to Disruptor but are off-heap and optimized for Aeron's IPC protocol.

---

## Chronicle Queue

Memory-mapped file persistence with microsecond IPC. ~1us latency same-machine, <40us p99.99 cross-service. "Insignificant on-heap overhead, even for 100TB." No broker needed -- embedded library.

**Write and read:**
```java
try (ChronicleQueue queue = ChronicleQueue.singleBuilder(queueDir)
        .rollCycle(RollCycles.FAST_HOURLY)
        .build()) {

    // Write
    try (ExcerptAppender appender = queue.createAppender()) {
        try (DocumentContext dc = appender.writingDocument()) {
            dc.wire().write("symbol").text("AAPL");
            dc.wire().write("bid").int64(15000);
        } // published on close, no explicit flush needed
    }

    // Read
    try (ExcerptTailer tailer = queue.createTailer()) {
        try (DocumentContext dc = tailer.readingDocument()) {
            if (dc.isPresent()) {
                String sym = dc.wire().read("symbol").text();
                long bid = dc.wire().read("bid").int64();
            }
        }
    }
}
```

**Named tailers** persist read position across JVM restarts -- `queue.createTailer("my-consumer")` resumes from last position. Unnamed tailers start from beginning each time. Use `tailer.toEnd()` for tail-f style consumers.

**Roll cycles** control file rotation (DAILY default, FAST_HOURLY for testing). Data persists as `.cq4` files. Also supports `writeDocument(marshallableObject)` and `writeBytes()` for raw binary.

---

## Chronicle Map

Off-heap shared-memory key-value store using memory-mapped files. Shared between JVMs on the same machine. Millions of ops/sec with zero GC overhead. Use for shared state (position caches, reference data) where Aeron's pub/sub model is overkill.

---

## Thread Affinity (OpenHFT Java-Thread-Affinity)

Pins threads to CPU cores to eliminate OS scheduler jitter (1-10us per context switch) and keep caches warm.

```java
// Auto-select next available CPU
try (AffinityLock lock = AffinityLock.acquireLock()) {
    // pinned -- do latency-sensitive work
}

// Pin to specific CPU
try (AffinityLock lock = AffinityLock.acquireLock(cpuId)) { ... }

// Reserve entire physical core (both HT siblings)
try (AffinityLock lock = AffinityLock.acquireCore()) { ... }

// Hierarchical: worker on same socket as parent (L3 sharing)
try (AffinityLock mainLock = AffinityLock.acquireLock()) {
    Thread worker = new Thread(() -> {
        try (AffinityLock wLock = mainLock.acquireLock(
                AffinityStrategies.SAME_SOCKET,
                AffinityStrategies.ANY)) {
            // runs on same socket as main thread
        }
    });
}
```

**Prerequisites:** `isolcpus` kernel parameter to reserve cores from OS scheduler. Disable HT for BusySpinWaitStrategy consumers. String-based selection supported: `acquireLock("last")`, `acquireLock("last-1")`.

---

## Object Pooling

Pre-allocate objects to achieve zero GC on hot path. The benefit is zero GC pauses at p99.99, not faster allocation.

**Single-threaded pool (zero overhead):**
```java
public class SingleThreadObjectPool<T> {
    private final T[] pool;
    private final int mask;       // size - 1, for bitwise wrap
    private int acquireIndex;
    private int releaseIndex;

    public T acquire() {
        T obj = pool[acquireIndex & mask];
        acquireIndex++;
        return obj;
    }
    public void release(T obj) {
        pool[releaseIndex & mask] = obj;
        releaseIndex++;
    }
}
```

**Concurrent pool:** Replace int indices with `AtomicInteger` + CAS loop.

**Flyweight domain objects** use `populate()` to set fields on acquire and `reset()` to clear before release. No final fields, no constructor dependencies. Always use try-finally for release:

```java
OrderMessage msg = pool.acquire();
try {
    msg.populate(orderId, price, qty, side);
    processOrder(msg);
} finally {
    msg.reset();
    pool.release(msg);
}
```

Pool size must be power of 2 for bitwise masking.

---

## Eclipse Collections / HPPC

Primitive-specialized collections (alternatives to Agrona with broader API):
- `LongObjectHashMap`, `IntIntHashMap`, `LongArrayList` -- no autoboxing.
- Functional iteration: `select`, `reject`, `collect` operate without boxing.
- HPPC (High Performance Primitive Collections) provides similar primitive maps/sets.

Use when you need a richer API than Agrona's collections but still need zero-boxing guarantees.

---

## When to Use What

| Need | Tool | Latency | Persistence |
|---|---|---|---|
| Inter-thread pipeline (same JVM) | **Disruptor** | ~tens of ns | No |
| Inter-process / cross-machine messaging | **Aeron** | <5us IPC, ~10-50us network | Via Archive |
| Persistent IPC / journaling / event sourcing | **Chronicle Queue** | ~1us same-machine | Yes (mmap files) |
| High-throughput cross-datacenter streaming | **Kafka** | ms-level | Yes (replicated log) |
| Shared state between JVMs (same machine) | **Chronicle Map** | sub-us | Yes (mmap files) |

**Decision guide:**
- Same JVM, need max throughput? **Disruptor**
- Cross-process on same machine? **Aeron IPC** (no persistence) or **Chronicle Queue** (with persistence)
- Cross-machine? **Aeron** (low latency) or **Kafka** (high throughput, ms-level OK)
- Need durable journal for replay/audit? **Chronicle Queue** or **Aeron Archive**

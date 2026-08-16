# Agrona Library Reference

Agrona is the foundational primitive library behind Aeron. It eliminates three latency sources in standard Java: GC (via off-heap allocation), autoboxing (via primitive-specialized collections), and lock contention (via lock-free algorithms).

---

## Buffer Hierarchy

```
DirectBuffer (read-only: getInt, getLong, getBytes, getStringAscii)
  +-- MutableDirectBuffer (write: putInt, putLong, putBytes, putStringAscii)
        +-- AtomicBuffer (atomic ops: getAndAddLong, compareAndSetLong,
                          putLongRelease, getLongAcquire, putIntRelease)
```

**UnsafeBuffer** implements `AtomicBuffer`. It wraps any backing store:

```java
new UnsafeBuffer(new byte[256]);                         // heap byte[]
new UnsafeBuffer(ByteBuffer.allocateDirect(256));        // off-heap ByteBuffer
new UnsafeBuffer(address, length);                       // raw memory address
```

`wrap()` methods re-point an existing UnsafeBuffer without allocation.

**ExpandableDirectByteBuffer** -- grows automatically on writes that exceed capacity. Use for variable-length encoding only, never on the hot path (growth allocates).

---

## Ring Buffers

Off-heap IPC ring buffers. Used by Aeron's media driver protocol.

| Type | Concurrency | CAS usage |
|------|-------------|-----------|
| `OneToOneRingBuffer` | Single producer, single consumer | CAS-free -- uses negative length as in-progress marker with release/acquire |
| `ManyToOneRingBuffer` | Many producers, single consumer | CAS on tail only (`compareAndSetLong` in a do-while loop) |

**Capacity**: must be power-of-2. Total buffer = capacity + `RingBufferDescriptor.TRAILER_LENGTH`. Producer and consumer position fields are padded to separate 64-byte cache lines.

**Write with offer**:
```java
int capacity = 1024;
UnsafeBuffer underlying = new UnsafeBuffer(
    ByteBuffer.allocateDirect(capacity + RingBufferDescriptor.TRAILER_LENGTH));
OneToOneRingBuffer ringBuffer = new OneToOneRingBuffer(underlying);

UnsafeBuffer msg = new UnsafeBuffer(new byte[64]);
msg.putStringAscii(0, "hello");
boolean success = ringBuffer.write(MSG_TYPE_ID, msg, 0, msg.capacity());
```

**Zero-copy write with tryClaim**:
```java
int msgLength = 32;
int claimIndex = ringBuffer.tryClaim(MSG_TYPE_ID, msgLength);
if (claimIndex > 0) {
    // Write directly into the ring buffer -- no intermediate copy.
    AtomicBuffer buffer = ringBuffer.buffer();
    buffer.putInt(claimIndex, 42);
    buffer.putLong(claimIndex + 4, System.nanoTime());
    ringBuffer.commit(claimIndex);   // or abort(claimIndex) to discard
}
```

**Read**:
```java
int messagesRead = ringBuffer.read((msgTypeId, buffer, index, length) -> {
    // buffer, index, length point directly into the ring buffer memory.
    int value = buffer.getInt(index);
    // process...
}, MESSAGE_COUNT_LIMIT);
```

---

## Concurrent Queues

Lock-free array queues for inter-thread communication within a JVM.

| Type | Concurrency |
|------|-------------|
| `OneToOneConcurrentArrayQueue` | Single producer, single consumer |
| `ManyToOneConcurrentArrayQueue` | Many producers, single consumer |
| `ManyToManyConcurrentArrayQueue` | Many producers, many consumers |

Cache-line padded with three levels of 64-byte padding between producer and consumer fields to prevent false sharing. Capacity must be power of 2.

```java
ManyToOneConcurrentArrayQueue<Event> queue = new ManyToOneConcurrentArrayQueue<>(1024);
queue.offer(event);                      // returns false if full
int drained = queue.drain(this::onEvent, LIMIT);
```

---

## Primitive Collections

Open addressing + linear probing. No boxing. Cache-friendly sequential memory access.

| Class | Key -> Value |
|-------|-------------|
| `Int2ObjectHashMap<V>` | int -> V |
| `Long2ObjectHashMap<V>` | long -> V |
| `Object2IntHashMap<K>` | K -> int |
| `Object2LongHashMap<K>` | K -> long |
| `Int2IntHashMap` | int -> int |
| `Long2LongHashMap` | long -> long |
| `IntHashSet` | int set |
| `LongHashSet` | long set |
| `IntArrayList` | int array list |
| `LongArrayList` | long array list |

```java
// missingValue is returned for absent keys (replaces null -- no boxing)
Long2ObjectHashMap<Session> sessions = new Long2ObjectHashMap<>();
sessions.put(correlationId, session);
Session s = sessions.get(correlationId);  // no Long boxing

Int2IntHashMap counters = new Int2IntHashMap(Integer.MIN_VALUE); // missingValue
counters.put(streamId, 0);
counters.put(streamId, counters.get(streamId) + 1);

// shouldAvoidAllocation=true prevents iterator allocation on forEach
Long2ObjectHashMap<String> map = new Long2ObjectHashMap<>();
map.forEach((key, value) -> { /* no allocation */ });
```

---

## Clock Abstractions

`System.currentTimeMillis()` costs ~25-30ns per call (vDSO on Linux). In a tight duty cycle calling time() dozens of times, this compounds.

| Clock | Source | Cost |
|-------|--------|------|
| `SystemEpochClock.INSTANCE` | `System.currentTimeMillis()` | ~25-30ns |
| `CachedEpochClock` | Volatile read of cached value | ~1ns (L1 cache hit) |
| `SystemEpochMicroClock` | Microsecond epoch clock | System call |
| `SystemNanoClock` | `System.nanoTime()` | ~25ns |
| `CachedNanoClock` | Volatile read of cached nanoTime | ~1ns |

**CachedEpochClock** stores the time in a volatile field with full cache-line padding (128 bytes of padding on each side). Call `update()` once at the top of each duty cycle, then `time()` is a volatile read.

```java
CachedEpochClock clock = new CachedEpochClock();

// In Agent.doWork():
public int doWork() {
    clock.update(SystemEpochClock.INSTANCE.time());  // ONE system call
    long nowMs = clock.time();                        // volatile read (~free)

    if (nowMs >= nextHeartbeatMs) {
        sendHeartbeat();
        nextHeartbeatMs = nowMs + HEARTBEAT_INTERVAL_MS;
    }
    if (nowMs - lastReceivedMs > TIMEOUT_MS) {
        closeStaleConnection();
    }
    return workCount;
}
```

---

## Agent / AgentRunner / CompositeAgent

The agent model implements single-threaded event loops.

**Agent interface**:
```java
public interface Agent {
    int doWork() throws Exception;  // returns work count (0 = idle)
    String roleName();              // thread name
    default void onStart() {}       // called once before first doWork()
    default void onClose() {}       // called on shutdown
}
```

**AgentRunner** loops: `doWork()` -> idle strategy based on work count. NOT simply a renamed thread -- it integrates error handling, idle strategy, and lifecycle.

```java
AgentRunner runner = new AgentRunner(
    new BackoffIdleStrategy(),       // idle strategy
    Throwable::printStackTrace,      // error handler
    null,                            // AtomicCounter for error count (optional)
    myAgent);                        // the Agent
Thread agentThread = AgentRunner.startOnThread(runner);
// ... later:
runner.close();  // triggers agent.onClose()
```

**CompositeAgent** groups multiple agents on one thread. Each agent's `doWork()` is called in sequence per duty cycle.

```java
CompositeAgent composite = new CompositeAgent(agentA, agentB, agentC);
AgentRunner runner = new AgentRunner(idleStrategy, errorHandler, null, composite);
AgentRunner.startOnThread(runner);
```

---

## Idle Strategies

One instance per agent. NOT thread-safe -- do not share across threads.

| Strategy | CPU | Latency | When to use |
|----------|-----|---------|-------------|
| `NoOpIdleStrategy` | 0% idle | None | Testing only |
| `BusySpinIdleStrategy` | 100% | Lowest (~ns) | Dedicated core, sub-us required |
| `YieldingIdleStrategy` | ~100% | Low (~us) | Shared core, low latency |
| `BackoffIdleStrategy` | Adaptive | Medium | Default for most workloads -- spins, then yields, then parks |
| `SleepingIdleStrategy` | Low | Higher (~100us+) | Uses `LockSupport.parkNanos(1)` |
| `SleepingMillisIdleStrategy` | Very low | High (~ms) | Background agents, monitoring |

---

## DeadlineTimerWheel

O(1) schedule/cancel. Single-threaded only. Zero GC (primitive arrays internally).

```java
DeadlineTimerWheel wheel = new DeadlineTimerWheel(
    TimeUnit.MILLISECONDS,
    System.currentTimeMillis(),   // startTime
    100,                          // tickResolution (100ms)
    64);                          // ticksPerWheel (power of 2)

long timerId = wheel.scheduleTimer(deadlineMs);

// In duty cycle:
int expired = wheel.poll(nowMs, (timeUnit, now, id) -> {
    handleExpiry(id);
    // Reschedule for recurring timer:
    wheel.scheduleTimer(now + intervalMs);
    return true;  // true = consume, false = stop processing
}, MAX_EXPIRIES);

wheel.cancelTimer(timerId);  // O(1)
```

**Recurring timers**: reschedule inside the handler. **Expiry limit**: the third arg to `poll()` caps how many timers fire per call, preventing a thundering herd from starving other work in the duty cycle.

---

## Broadcast Buffer

One writer (`BroadcastTransmitter`), N readers (`CopyBroadcastReceiver`). No back-pressure -- slow readers get lapped. Used by Aeron's CnC file for driver-to-client events.

Buffer: power-of-2 capacity + `BroadcastBufferDescriptor.TRAILER_LENGTH`.

```java
int capacity = 1024;
AtomicBuffer buf = new UnsafeBuffer(
    ByteBuffer.allocateDirect(capacity + BroadcastBufferDescriptor.TRAILER_LENGTH));

// Writer (single-threaded, NOT thread-safe):
BroadcastTransmitter tx = new BroadcastTransmitter(buf);
tx.transmit(msgTypeId, srcBuffer, offset, length);

// Reader (one instance per consumer, each single-threaded):
CopyBroadcastReceiver rx = new CopyBroadcastReceiver(new BroadcastReceiver(buf));
int received = rx.receive((msgTypeId, buffer, index, length) -> {
    // Message has been copied into scratch buffer -- safe from overwrite.
});
// received = 1 if a message was consumed, 0 if none available.
// Check rx.broadcastReceiver().lappedCount() to detect missed messages.
```

---

## DistinctErrorLog

GC-free error recording. De-duplicates repeated errors (same exception type + message + stack trace). On repeat, only the atomic observation counter and last-seen timestamp are updated -- zero buffer writes, zero allocations.

```java
UnsafeBuffer errorBuffer = new UnsafeBuffer(ByteBuffer.allocateDirect(64 * 1024));
DistinctErrorLog log = new DistinctErrorLog(errorBuffer, SystemEpochClock.INSTANCE);

log.record(exception);  // First call: writes full stack trace.
log.record(exception);  // Repeat: atomic counter increment only.

// Read from monitoring thread/process (lock-free):
ErrorLogReader.read(errorBuffer, (count, firstTimestamp, lastTimestamp, encoded) -> {
    System.out.printf("Observations: %d, First: %d, Last: %d, Error: %s%n",
        count, firstTimestamp, lastTimestamp, encoded.lines().findFirst().orElse(""));
});
```

---

## BitUtil / BufferUtil

```java
BitUtil.CACHE_LINE_LENGTH         // 64 (bytes)
BitUtil.align(value, alignment)   // round up to alignment boundary
BitUtil.isPowerOfTwo(n)           // true if n is power of 2
BitUtil.findNextPositivePowerOfTwo(n)

BufferUtil.allocateDirectAligned(capacity, BitUtil.CACHE_LINE_LENGTH)
// Allocates a DirectByteBuffer aligned to cache-line boundary.
```

---

## Key Code Patterns

**Full Agent skeleton with CachedEpochClock and timer wheel**:
```java
public class MyServiceAgent implements Agent {
    private final CachedEpochClock clock = new CachedEpochClock();
    private final DeadlineTimerWheel timerWheel;
    private final Long2ObjectHashMap<Session> sessions = new Long2ObjectHashMap<>();

    @Override public void onStart() {
        clock.update(SystemEpochClock.INSTANCE.time());
        // schedule initial timers...
    }

    @Override public int doWork() {
        clock.update(SystemEpochClock.INSTANCE.time());
        long nowMs = clock.time();
        int workCount = 0;

        workCount += timerWheel.poll(nowMs, this::onTimerExpiry, 16);
        workCount += pollSubscription();
        return workCount;
    }

    @Override public String roleName() { return "my-service"; }
}
```

**Launching with AgentRunner**:
```java
AgentRunner runner = new AgentRunner(
    new BackoffIdleStrategy(), Throwable::printStackTrace, null, new MyServiceAgent());
AgentRunner.startOnThread(runner);
new ShutdownSignalBarrier().await();
runner.close();
```

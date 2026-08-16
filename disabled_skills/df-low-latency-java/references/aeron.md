# Aeron Messaging Reference

## Architecture

The **Media Driver** handles all network I/O, buffering, and retransmission. Application threads never make system calls on the hot path -- they interact only with memory-mapped log buffers via a lock-free client API.

Three internal agents inside the Media Driver:

| Agent | Role |
|-------|------|
| **Conductor** | Accepts commands, orchestrates actions, name resolution |
| **Sender** | Manages data transmission via Java NIO |
| **Receiver** | Manages data reception, handles NAK/Status messages |

Four threading models:

| Model | Threads | Use case |
|-------|---------|----------|
| `DEDICATED` | 3 (one per agent) | Production -- maximum throughput |
| `SHARED_NETWORK` | 2 (Sender+Receiver combined, Conductor separate) | Moderate load |
| `SHARED` | 1 (all agents) | Minimal resource usage |
| `INVOKER` | 0 (caller drives via `AgentInvoker`) | Resource-constrained / embedded |

Client API: `Aeron.connect(ctx)` returns an `Aeron` instance. Create `Publication` / `Subscription` objects from it. Available in Java, C, .NET.

---

## Transport Modes

| Mode | Channel URI | Notes |
|------|-------------|-------|
| **IPC** | `aeron:ipc` | Shared memory, sub-5us latency, same host only |
| **UDP Unicast** | `aeron:udp?endpoint=host:port` | One-to-one, sends to specific address |
| **UDP Multicast** | `aeron:udp?endpoint=224.x.x.x:port\|interface=localhost` | One-to-many, network-level fan-out via IGMP |
| **MDC** (Multi-Destination Cast) | `aeron:udp?control=host:port\|control-mode=dynamic` | Unicast to multiple endpoints, no multicast infra needed |

- IPC uses `/dev/shm` (or `aeronDirectoryName`). Docker default shm is 64MB -- use `--shm-size=2g`.
- Messages sent before subscriber connects are lost (no store-and-forward).
- Multicast requires OS/network IGMP support. On Linux: `sudo ip route add 224.0.0.0/4 dev lo`.

---

## Publications

Two types:

| Type | API | Thread-safe | Overhead |
|------|-----|-------------|----------|
| `ConcurrentPublication` | `aeron.addPublication()` | Yes (CAS internally) | Higher |
| `ExclusivePublication` | `aeron.addExclusivePublication()` | No (single thread only) | 10-30% faster |

Use `ExclusivePublication` when a single thread owns the publication (the common case). Required for Archive replay with initial position.

### offer() return codes

| Value | Constant | Meaning | Action |
|-------|----------|---------|--------|
| > 0 | -- | New stream position | Success |
| -1 | `NOT_CONNECTED` | No subscriber connected | Wait / log |
| -2 | `BACK_PRESSURED` | Subscriber can't keep up | Idle + retry |
| -3 | `ADMIN_ACTION` | Log rotation in progress | Retry immediately |
| -4 | `CLOSED` | Publication closed | Stop sending |
| -5 | `MAX_POSITION_EXCEEDED` | Term buffer exhausted | Create new publication |

### tryClaim() zero-copy pattern

`tryClaim()` claims a range directly in the publication log buffer. No copy occurs. Combined with SBE for maximum performance:

```java
final BufferClaim bufferClaim = new BufferClaim();
if (publication.tryClaim(messageLength, bufferClaim) > 0) {
    encoder.wrap(bufferClaim.buffer(), bufferClaim.offset())
           .serialNumber(1234)
           .modelYear(2023);
    bufferClaim.commit();  // MUST call commit() or abort()
}
```

If `commit()`/`abort()` is not called within the unblock timeout (default 15s), the publication log buffer blocks.

---

## Subscriptions

- **Push model** -- data offered to a publication is pushed to subscriptions, not pulled.
- `Subscription.poll(handler, fragmentLimit)` is non-blocking, returns fragment count.
- `fragmentLimit` caps fragments per poll to prevent starvation of other work.
- Subscriptions are **NOT thread-safe** -- poll from a single thread only.

### FragmentAssembler

Messages exceeding MTU (~1408 bytes UDP) are auto-fragmented by the publisher. On the subscriber side:

| Handler | Sees | Use when |
|---------|------|----------|
| Raw `FragmentHandler` | Individual fragments (BEGIN/MIDDLE/END flags) | Zero-copy per-fragment, or messages always < MTU |
| `FragmentAssembler` | Complete reassembled messages | Default choice for most applications |

```java
// Basic IPC pub/sub with FragmentAssembler
try (MediaDriver driver = MediaDriver.launchEmbedded();
     Aeron aeron = Aeron.connect(new Aeron.Context()
         .aeronDirectoryName(driver.aeronDirectoryName()));
     Publication pub = aeron.addPublication("aeron:ipc", 1001);
     Subscription sub = aeron.addSubscription("aeron:ipc", 1001))
{
    final UnsafeBuffer buf = new UnsafeBuffer(
        BufferUtil.allocateDirectAligned(256, 64));
    final IdleStrategy idle = YieldingIdleStrategy.INSTANCE;

    // Wait for connection
    while (!pub.isConnected()) { idle.idle(); }

    // Publish
    buf.putStringWithoutLengthAscii(0, "Hello IPC");
    while (pub.offer(buf, 0, 9) < 0) { idle.idle(); }

    // Subscribe with FragmentAssembler
    final FragmentAssembler assembler = new FragmentAssembler(
        (buffer, offset, length, header) -> {
            String msg = buffer.getStringWithoutLengthAscii(offset, length);
            // process msg
        });
    while (sub.poll(assembler, 10) == 0) { idle.idle(); }
}
```

---

## Back-Pressure and Flow Control

Three control points:

| Point | Constraint | Default |
|-------|-----------|---------|
| Client to driver sender | Publication Term Window Length | 1/2 term buffer |
| Sender to receiver | Receiver window from Status Messages | Configurable |
| Receiver to subscription | Receiver Window | 128KB |

Multicast flow control strategies:

| Strategy | Behavior |
|----------|----------|
| **Max** (default) | Fastest receiver sets pace; slower receivers may lose data |
| **Min** | Slowest receiver controls flow; prevents loss but risks back-pressure |
| **Tagged** | Minimum of tagged receivers only; selective QoS |

**Tethered subscriptions** (default): back-pressure the publisher when a subscriber falls behind.
**Untethered subscriptions**: allow the subscriber to fall behind and rejoin at the current position; publisher is not slowed.

---

## Idle Strategies

Applied in poll/offer loops to trade CPU for latency:

| Strategy | CPU | Latency | Mechanism | Use case |
|----------|-----|---------|-----------|----------|
| `NoOpIdleStrategy` | 100% | Lowest | No-op | Benchmarking only |
| `BusySpinIdleStrategy` | 100% | Sub-us | `Thread.onSpinWait()` | Dedicated cores, sub-microsecond |
| `YieldingIdleStrategy` | High | Low | `Thread.yield()` | Shared cores, low latency |
| `BackoffIdleStrategy` | Adaptive | Medium | Spin -> yield -> park | Variable message rates (good default) |
| `SleepingIdleStrategy` | Low | Higher | `LockSupport.parkNanos()` | Throughput-oriented |
| `SleepingMillisIdleStrategy` | Minimal | Highest | `Thread.sleep(ms)` | Background / non-critical |

Rule: use `BusySpinIdleStrategy` only when you have dedicated CPU cores pinned to the thread. Otherwise `BackoffIdleStrategy` is the safe default.

---

## Performance Tuning

| Parameter | Setting | Effect |
|-----------|---------|--------|
| Term buffer length | Power-of-2, e.g. `1 << 25` (32MB) | Larger = more buffering before back-pressure |
| MTU length | Up to 8KB (UDP) | Larger = fewer fragments, better throughput |
| `SO_RCVBUF` | Match or exceed receiver window | Prevents kernel drops |
| Receiver window | Match expected burst size | Controls sender pacing |
| Aeron directory | `/dev/shm` | Required for IPC performance |
| Docker | `--shm-size=2g` | Default 64MB is insufficient |
| Pre-touch buffers | `MediaDriver.Context.preTouchMappedMemory(true)` | Avoids page faults on first access |
| CPU isolation | `isolcpus`, `taskset`, `lstopo` | Eliminates scheduling jitter |
| `vm.swappiness` | `0` | Prevents swapping shared memory |
| `ulimit -n` | At least 65536 | Enough file descriptors |

JVM flags for Aeron (Java 17+):
```
--add-opens java.base/sun.nio.ch=ALL-UNNAMED
```
Missing `--add-opens` causes `InaccessibleObjectException` at runtime.

---

## Anti-Patterns

1. **Ignoring offer() return codes** -- must handle all negative values with idle strategy + retry.
2. **Too many streams** -- Aeron is designed for 10s-100s of streams, not 1000s. Each stream allocates fixed buffer resources. Multiplex messages onto fewer streams.
3. **Insufficient /dev/shm** -- causes `InternalError: Unsafe Memory Access`. On systemd, `/dev/shm` files may be deleted when user sessions terminate; fix with `RemoveIPC=no` in `/etc/systemd/logind.conf`.
4. **Not calling commit/abort on tryClaim** -- blocks the entire publication after unblock timeout (15s).
5. **Non-deterministic Cluster services** -- `System.currentTimeMillis()`, `Math.random()`, `HashMap` iteration order, config file reads all break state machine consistency across replicas. Use `clusterTime()`.
6. **No encryption** -- Aeron has no built-in encryption (GitHub issue #203). Use application-level encryption for untrusted networks.

---

## Monitoring Tools

| Tool | Purpose |
|------|---------|
| **AeronStat** | Counter inspection -- bytes sent/received, NAKs, errors, retransmits. Outputs once per second. |
| **ErrorStat** | Reads error logs from the media driver |
| **LossStat** | Analyzes `loss-report.dat`, generates CSV |
| **BacklogStat** | Shows bytes buffered between processing stages |
| **LogInspector** | Examines publication log buffer contents |

Programmatic access: `aeron.countersReader()` or map the CnC file (`{aeronDir}/cnc.dat`) directly for out-of-process monitoring.

Key counters to watch: Bytes sent/received, NAKs sent, Errors, Retransmits sent, Short sends (OS socket buffer too small), heartbeat age (stale > 1000ms = driver problem).

---

## Key Code Patterns

### UDP Unicast Publisher

```java
final String CHANNEL = "aeron:udp?endpoint=localhost:20121";
final int STREAM_ID = 1001;

try (MediaDriver driver = MediaDriver.launchEmbedded();
     Aeron aeron = Aeron.connect(new Aeron.Context()
         .aeronDirectoryName(driver.aeronDirectoryName()));
     Publication pub = aeron.addPublication(CHANNEL, STREAM_ID))
{
    final UnsafeBuffer buf = new UnsafeBuffer(
        BufferUtil.allocateDirectAligned(256, 64));

    final int len = buf.putStringWithoutLengthAscii(0, "Hello UDP");
    final long result = pub.offer(buf, 0, len);

    if (result == Publication.BACK_PRESSURED) { /* idle + retry */ }
    else if (result == Publication.NOT_CONNECTED) { /* wait */ }
    else if (result == Publication.ADMIN_ACTION) { /* retry */ }
    else if (result == Publication.CLOSED) { /* stop */ }
    else if (result == Publication.MAX_POSITION_EXCEEDED) { /* new pub */ }
}
```

### tryClaim + SBE Zero-Copy

```java
final BufferClaim claim = new BufferClaim();
final MyEncoder encoder = new MyEncoder();

// Zero allocation, zero copy: encode directly into log buffer
if (publication.tryClaim(MyEncoder.BLOCK_LENGTH, claim) > 0) {
    encoder.wrap(claim.buffer(), claim.offset())
           .field1(value1)
           .field2(value2);
    claim.commit();
} else {
    // Handle back-pressure (same return codes as offer())
}
```

### FragmentAssembler for Large Messages

```java
// Subscriber reassembles messages > MTU automatically
final FragmentAssembler assembler = new FragmentAssembler(
    (buffer, offset, length, header) -> {
        // Always receives complete message, regardless of fragmentation
        processMessage(buffer, offset, length);
    });

final IdleStrategy idle = new BackoffIdleStrategy(100, 10,
    TimeUnit.MICROSECONDS.toNanos(1), TimeUnit.MICROSECONDS.toNanos(100));

while (running.get()) {
    idle.idle(subscription.poll(assembler, 10));
}
```

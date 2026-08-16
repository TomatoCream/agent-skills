# Aeron Cluster Reference

## Architecture (4 Components)

Every Aeron Cluster node runs four cooperating components:

| Component | Role |
|---|---|
| **ConsensusModule** | Raft leader election, log replication, membership, timers. Sequences client ingress into the replicated log. |
| **ClusteredServiceContainer** | Hosts the user's `ClusteredService` implementation. Replays log entries through `onSessionMessage()`. Single-threaded -- all state mutation happens here. |
| **Archive** | Durable storage for the replicated log and snapshots. Writes to disk; used during recovery and catch-up. |
| **MediaDriver** | Aeron's I/O layer (shared memory IPC + UDP). All inter-node and client-to-cluster communication flows through it. |

Typical deployment: 3 or 5 nodes. Leader handles ingress; followers replicate. Committed = majority acknowledged.

## Raft Enhancements

Aeron Cluster departs from textbook Raft for performance:

- **Byte indexing** -- indexes by byte offset, not message count. Enables millions of events/sec.
- **Async/pipelining** -- write-to-disk, ack, data passing, and response execute in parallel (not sequential).
- **Batching** -- multiple messages processed as a single unit, reducing per-message overhead.
- **Canvassing** -- nodes gather opinions before starting an election, reducing failed elections.
- **Veto** -- nodes can reject unsuitable leader candidates.
- **Standby nodes** -- replacements are pre-provisioned. No dynamic membership changes (simpler, safer).

## Determinism Rules (CRITICAL)

The `ClusteredService` MUST be fully deterministic. All replicas process the same log and must arrive at identical state. Violations cause silent state divergence discovered only after leader failover.

| Forbidden | Replacement |
|---|---|
| `System.currentTimeMillis()` / `System.nanoTime()` | `cluster.time()` (leader's ingestion timestamp) |
| `Math.random()` / `ThreadLocalRandom` | Seeded RNG initialized from cluster state |
| `HashMap` / `HashSet` iteration order | `TreeMap` / `LinkedHashMap` / Agrona ordered collections |
| File I/O, config file reads | Pass configuration as cluster messages |
| Database access, network calls | External data enters only through the ingress log |
| `UUID.randomUUID()` | Deterministic ID generation (counter, seeded) |
| `new Date()` / `Instant.now()` | Derive from `cluster.time()` |

Rule of thumb: if the output depends on anything other than the log contents, it breaks determinism.

## ClusteredService Interface

```java
public class MyService implements ClusteredService {
    private Cluster cluster;
    private IdleStrategy idleStrategy;

    @Override
    public void onStart(Cluster cluster, Image snapshotImage) {
        this.cluster = cluster;
        this.idleStrategy = cluster.idleStrategy();
        if (snapshotImage != null) {
            restoreSnapshot(snapshotImage); // decode SBE from image
        }
    }

    @Override
    public void onSessionMessage(
        ClientSession session, long timestamp,
        DirectBuffer buffer, int offset, int length, Header header) {
        // Decode SBE, mutate state deterministically.
        // Use timestamp (not System.currentTimeMillis()).
        // session is null during log replay -- guard egress sends.
        if (session != null) {
            session.offer(responseBuffer, 0, responseLen);
        }
    }

    @Override
    public void onTakeSnapshot(ExclusivePublication snapshotPublication) {
        // Encode ALL mutable state with SBE into snapshotPublication.
    }

    @Override
    public void onTimerEvent(long correlationId, long timestamp) {
        // Fired when a scheduled timer expires.
        // correlationId ties back to the business object.
    }

    @Override
    public void onRoleChange(Cluster.Role newRole) {
        // LEADER, FOLLOWER, CANDIDATE.
        // Only LEADER should perform external side effects.
    }

    @Override public void onSessionOpen(ClientSession session, long ts) {}
    @Override public void onSessionClose(ClientSession session, long ts, CloseReason reason) {}
    @Override public void onTerminate(Cluster cluster) {}
}
```

## Snapshots

Any node can take a snapshot (not just the leader), avoiding latency pauses on the leader.

**Protocol:** Header message + N record messages, SBE-encoded.

```java
// --- SAVE (onTakeSnapshot) ---
@Override
public void onTakeSnapshot(ExclusivePublication pub) {
    // 1. Write header: order count, nextOrderId, timestamp
    encodeSbeHeader(buf, 0, SNAP_HDR_BODY_LEN, SNAP_HDR_TEMPLATE_ID);
    buf.putInt(HEADER_SIZE + OFFSET_COUNT, liveOrders.size(), LITTLE_ENDIAN);
    buf.putLong(HEADER_SIZE + OFFSET_NEXT_ID, nextOrderId, LITTLE_ENDIAN);
    offerWithRetry(pub, buf, HEADER_SIZE + SNAP_HDR_BODY_LEN);

    // 2. Write each record
    for (var it = liveOrders.entrySet().iterator(); it.hasNext(); ) {
        it.next();
        LiveOrder order = it.getValue();
        encodeSbeHeader(buf, 0, SNAP_ORD_BODY_LEN, SNAP_ORD_TEMPLATE_ID);
        // ... encode order fields ...
        offerWithRetry(pub, buf, HEADER_SIZE + SNAP_ORD_BODY_LEN);
    }
}

// --- RESTORE (called from onStart) ---
private void restoreSnapshot(Image snapshotImage) {
    FragmentHandler handler = (buffer, offset, length, header) -> {
        int templateId = buffer.getShort(offset + 2, LITTLE_ENDIAN) & 0xFFFF;
        if (templateId == SNAP_HDR_TEMPLATE_ID) {
            // decode header, set expectedCount, nextOrderId
        } else if (templateId == SNAP_ORD_TEMPLATE_ID) {
            // decode order, put into liveOrders map
        }
    };
    while (!snapshotImage.isEndOfStream()) {
        int fragments = snapshotImage.poll(handler, 20);
        idleStrategy.idle(fragments);
    }
}
```

**Recovery sequence:** Load latest snapshot -> replay log entries after snapshot position -> state is current.

Key rule: snapshot must encode ALL mutable state. Anything missing is lost on restart.

## Timer Scheduling

```java
// Schedule a timer (e.g., order expiry)
long correlationId = orderId; // tie timer to business object
cluster.scheduleTimer(correlationId, cluster.time() + expiryDurationMs);

// Cancel if no longer needed
cluster.cancelTimer(correlationId);
```

- **"No sooner than" guarantee** -- timer fires at or after the scheduled time, never before.
- Correlation IDs link timers to business objects. Must be included in snapshots for restoration.
- Timers are deterministic: they fire based on cluster logical time, not wall-clock time.

## Client Gateway Pattern

```java
// --- CONNECTION ---
AeronCluster cluster = AeronCluster.connect(
    new AeronCluster.Context()
        .egressListener(myEgressListener)           // receives responses
        .egressChannel("aeron:udp?endpoint=localhost:0") // OS picks port
        .ingressChannel("aeron:udp")
        .ingressEndpoints("0=host0:9010,1=host1:9110,2=host2:9210")
        .aeronDirectoryName(mediaDriver.aeronDirectoryName())
        .messageTimeoutNs(10_000_000_000L));         // 10s timeout

// --- SEND (ingress) ---
idleStrategy.reset();
while (true) {
    long result = cluster.offer(buffer, 0, length);
    if (result > 0) break;
    // IMPORTANT: poll egress even while retrying -- processes leader changes
    idleStrategy.idle(cluster.pollEgress());
}

// --- RECEIVE (egress) ---
// EgressListener.onMessage() is called by pollEgress()
cluster.pollEgress(); // call regularly in event loop

// --- LEADER CHANGES ---
// EgressListener.onNewLeader() fires automatically.
// In-flight requests may need retry after leader transition.
// Committed messages are safe; uncommitted offers may be lost.

// --- KEEP-ALIVE ---
cluster.sendKeepAlive(); // prevent session timeout
```

## Anti-Patterns

| Anti-Pattern | Consequence |
|---|---|
| Non-deterministic service (wall clock, random, HashMap) | Silent state divergence across replicas; discovered only after failover |
| Missing snapshot strategy | Full log replay on restart; recovery time grows unbounded |
| Not polling archive clients | Back-pressure stalls; blocked publications |
| Ignoring `offer()` return codes | Lost messages; `BACK_PRESSURED`, `NOT_CONNECTED`, `ADMIN_ACTION` all need handling |
| Sending egress during log replay (`session` is null) | NullPointerException; always guard with `if (session != null)` |
| Incomplete snapshot (missing state fields) | Data loss on restart; partial state reconstruction |
| Not retrying after leader change | In-flight requests silently dropped |
| Using dynamic membership instead of standby nodes | Aeron Cluster does not support dynamic membership; use standby nodes |

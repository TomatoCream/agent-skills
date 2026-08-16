---
name: para-java-aeron-cluster
description: Use when designing or implementing fault-tolerant replicated services with Aeron Cluster in Java — ClusteredService implementation, Raft consensus tuning, determinism enforcement, snapshot strategy, election configuration, client gateway patterns, matching engine integration, operational monitoring
---

# Aeron Cluster Reference

## Overview

Aeron Cluster is a Raft-based replicated state machine framework built on Aeron Transport and Aeron Archive. It sequences multiple client connections into a single replicated log, achieving 76-95us p50 consensus latency (3-node, 100K msgs/sec) on AWS. Used in production at Coinbase, EDX Markets (73us median RTT), SIX (35M payments/day), Man Group, and 6+ other financial institutions.

## When to Use

- Building fault-tolerant stateful services (matching engines, CLOB, risk checks, sequencers)
- Need automatic leader election and failover with zero data loss on committed entries
- Require deterministic replay for debugging and recovery
- **Not for**: cross-DC consensus, stateless services, or when millisecond latency is acceptable (use Kafka)

## Architecture Quick Reference

```
Client --> [Ingress] --> ConsensusModule (Raft) --> [Log] --> ClusteredService
                                  |                              |
                              [Consensus]                    [Egress] --> Client
                              (peer-to-peer)
```

**3 threads per node:** Media Driver (Conductor+Sender+Receiver), ConsensusModuleAgent, ClusteredServiceAgent

**5 ports per member:** Ingress, Log, Consensus, Catchup, Archive

**Key classes:** `ConsensusModule`, `ConsensusModuleAgent`, `ClusteredServiceAgent`, `BoundedLogAdapter`, `Election` (18 states), `LogPublisher`, `IngressAdapter`

## ClusteredService Implementation Pattern

```java
public class MatchingEngineService implements ClusteredService {
    private Cluster cluster;
    private IdleStrategy idleStrategy;

    @Override
    public void onStart(Cluster cluster, Image snapshotImage) {
        this.cluster = cluster;
        this.idleStrategy = cluster.idleStrategy();
        if (snapshotImage != null) loadSnapshot(snapshotImage);
    }

    @Override
    public void onSessionMessage(ClientSession session, long timestamp,
            DirectBuffer buffer, int offset, int length, Header header) {
        // Decode with SBE, apply to state machine, send egress
        // MUST check session != null (null during replay)
        if (session != null) {
            idleStrategy.reset();
            while (session.offer(responseBuffer, 0, responseLength) < 0) {
                idleStrategy.idle();
            }
        }
    }

    @Override
    public void onTakeSnapshot(ExclusivePublication pub) {
        // Serialize complete state with SBE: orders, balances, sequences
        idleStrategy.reset();
        while (pub.offer(snapshotBuffer, 0, snapshotLength) < 0) {
            idleStrategy.idle();
        }
    }

    @Override public void onTimerEvent(long correlationId, long timestamp) { }
    @Override public void onRoleChange(Cluster.Role newRole) { }
    @Override public void onSessionOpen(ClientSession s, long ts) { }
    @Override public void onSessionClose(ClientSession s, long ts, CloseReason r) { }
    @Override public void onTerminate(Cluster cluster) { }
}
```

**Callback constraints:** Cannot send messages or schedule timers from `onStart`, `onTakeSnapshot`, `onRoleChange`, `onTerminate`. Schedule timers from `onSessionOpen` (first client) or `onSessionMessage`.

## Determinism Rules (Non-Negotiable)

| Rule | Use Instead |
|------|-------------|
| No `System.currentTimeMillis()` | `timestamp` param or `cluster.time()` |
| No `Math.random()`, `UUID.randomUUID()` | Deterministic seed from cluster state |
| No external I/O (files, DB, network) | Submit all inputs through ingress |
| No `HashMap`/`HashSet` iteration | `TreeMap`, `LinkedHashMap`, Agrona sorted |
| No threading (`CompletableFuture`, parallel streams) | Single-threaded by design |
| No `System.nanoTime()` for logic | Cluster-provided timestamps only |

**Enforce with:** CheckStyle/PMD rules flagging violations in ClusteredService package. Non-determinism is the #1 production failure cause.

## Configuration Parameters

| Parameter | Default | System Property | Tuning Notes |
|-----------|---------|-----------------|--------------|
| Election timeout | 1s | `aeron.cluster.election.timeout` | Base timeout; randomized |
| Leader heartbeat timeout | 10s | `aeron.cluster.leader.heartbeat.timeout` | Reduce to 1-3s for faster failover; must exceed GC pause |
| Leader heartbeat interval | 200ms | `aeron.cluster.leader.heartbeat.interval` | Fine for same-rack |
| Startup canvass timeout | 60s | `aeron.cluster.startup.canvass.timeout` | Time for initial member discovery |
| Session timeout | 10s | `aeron.cluster.session.timeout` | Client inactivity limit |
| Max concurrent sessions | 10 | `aeron.cluster.max.sessions` | Set slightly above expected clients |
| File sync level | 0 | Archive config | 0=async, 1=fdatasync, 2=fsync |

## Performance (AWS 2025, 3-node, c6in.16xlarge)

| Rate | Variant | P50 | P99 | P99.9 |
|------|---------|-----|-----|-------|
| 100K/s | OSS Java | 95us | 136us | 197us |
| 100K/s | Premium | 76us | 98us | 106us |
| 1M/s | OSS Java | 3,301us | 8,479us | 9,306us |
| 1M/s | Premium | 106us | 143us | 158us |

**Critical:** OSS degrades 35x at 1M msgs/sec; Premium stays flat (kernel bypass/DPDK). Budget Premium for >500K msgs/sec peak.

**Throughput limit:** Little's Law -- `throughput = 1 / processing_time`. At 50us/command = 20K cmds/sec max.

## Monitoring Counters

| Counter | Watch For |
|---------|-----------|
| `Cluster commit-pos` (61) | Stalling = replication failure |
| `Consensus Module state` | 5=Terminating, 6=Closed, 2=Suspended |
| `Cluster node role` | Exactly one Leader (2); prolonged Candidate (1) = stuck election |
| `Cluster election state` (57) | Frequent transitions = instability |
| `Cluster Errors` | Non-zero = investigate via ClusterTool |

**Streams:** 100=Log, 101=Ingress, 102=Egress, 108=Consensus

## ClusterTool Commands

```bash
java --add-opens java.base/jdk.internal.misc=ALL-UNNAMED \
     --add-opens java.base/java.util.zip=ALL-UNNAMED \
     -cp aeron-all-*.jar io.aeron.cluster.ClusterTool <cluster-dir> <cmd>
```

| Command | Purpose |
|---------|---------|
| `describe` | Inspect mark files and component state |
| `list-members` | Show members, endpoints, replication status |
| `recording-log` | Inspect terms, positions, validity |
| `snapshot` | Trigger snapshot |
| `errors` | Retrieve error logs |
| `shutdown` | Clean cluster termination |

## Client Connection Pattern

```java
AeronCluster.connect(new AeronCluster.Context()
    .egressListener(egressListener)
    .egressChannel("aeron:udp?endpoint=localhost:0")
    .ingressChannel("aeron:udp")
    .ingressEndpoints(ingressEndpoints));
```

- Client auto-switches to new leader via `onNewLeader` callback
- Full disconnect requires manual reconnection (new `AeronCluster.connect()`)
- Poll egress in offer loops: `idleStrategy.idle(aeronCluster.pollEgress())`

## Gateway Patterns

- **Active/Passive**: One hot gateway, one standby. Failover via `ProcessManager` state transitions.
- **Active/Active**: Both process messages. Requires monotonic sequence numbers for deduplication. Cluster rejects out-of-sequence messages.
- **Strong consistency**: Gateway sequences request through cluster, responds only after cluster acknowledgment.

## Snapshot Strategy (Matching Engine)

Snapshot must capture: (1) all open orders per instrument with price/qty/side/orderId/time-priority, (2) account balances/positions, (3) sequence counters (orderID, execID, tradeID, MD sequence), (4) trading session/auction state. Use SBE encoding. Structure as stream of typed messages with start/end markers. Snapshot every 15-30 min to bound recovery time.

## Common Pitfalls

| Pitfall | Consequence | Fix |
|---------|-------------|-----|
| Using system clock in ClusteredService | Silent state divergence on failover | Use `cluster.time()` / callback `timestamp` |
| HashMap for order book levels | Different iteration order on nodes | TreeMap or sorted Agrona collections |
| External DB call in onSessionMessage | Non-deterministic state | Submit reference data via ingress messages |
| Unchecked archive growth | Disk full = cluster crash | Purge old recordings after snapshot |
| Embedded Media Driver | GC pauses affect consensus | Run Media Driver as separate process |
| Snapshot too infrequently | Hours of log replay on recovery | Snapshot every 15-30 min |

## Tail Latency Causes

1. **GC pauses** -- use ZGC/Shenandoah, minimize allocations
2. **Snapshot coordination** -- pauses all nodes; use Premium Standby Snapshots
3. **Disk I/O** -- NVMe SSDs required; never `/dev/shm` for persistent logs
4. **OS jitter** -- `isolcpus`, disable THP, `tuned` latency-performance profile

See [reference.md](reference.md) for full architecture deep dive, election state machine details, production case studies, failure mode analysis, and comparison with alternatives.

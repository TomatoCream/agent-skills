# Para Java Aeron Cluster Skill

Fault-tolerant replicated services with Aeron Cluster in Java — ClusteredService implementation, Raft consensus tuning, determinism enforcement, snapshot strategy, election configuration, client gateway patterns, matching engine integration, operational monitoring.

## Installation

No additional dependencies required. Aeron Cluster and related libraries are loaded from Maven Central.

## Usage

```
design a fault-tolerant matching engine with Aeron Cluster
implement Raft consensus for my stateful service
how do I handle leader election and failover?
troubleshoot Aeron Cluster election timeouts
```

## Overview

Aeron Cluster is a Raft-based replicated state machine framework built on Aeron Transport and Aeron Archive. It sequences multiple client connections into a single replicated log, achieving 76-95us p50 consensus latency (3-node, 100K msgs/sec) on AWS.

Used in production at:
- Coinbase
- EDX Markets (73us median RTT)
- SIX (35M payments/day)
- Man Group
- And 6+ other financial institutions

## When to Use

- Building fault-tolerant stateful services (matching engines, CLOB, risk checks, sequencers)
- Need automatic leader election and failover with zero data loss on committed entries
- Require deterministic replay for debugging and recovery
- **Not for**: cross-DC consensus, stateless services, or when millisecond latency is acceptable (use Kafka)

## Key Topics Covered

| Topic | Description |
|-------|-------------|
| ClusteredService Implementation | Service lifecycle, session handling, snapshot callbacks |
| Determinism Rules | No system clock, no HashMap, no external I/O in cluster path |
| Configuration | Election timeouts, heartbeat settings, session limits |
| Monitoring | Commit position counters, election state, ClusterTool |
| Client Patterns | Connection, reconnection, egress polling |
| Snapshot Strategy | State capture for matching engines |
| Performance | Latency benchmarks, throughput limits |

## Architecture

```
Client --> [Ingress] --> ConsensusModule (Raft) --> [Log] --> ClusteredService
                                  |                              |
                              [Consensus]                    [Egress] --> Client
                              (peer-to-peer)
```

**3 threads per node:** Media Driver (Conductor+Sender+Receiver), ConsensusModuleAgent, ClusteredServiceAgent

**5 ports per member:** Ingress, Log, Consensus, Catchup, Archive

## Performance (AWS 2025, 3-node, c6in.16xlarge)

| Rate | Variant | P50 | P99 | P99.9 |
|------|---------|-----|-----|-------|
| 100K/s | OSS Java | 95us | 136us | 197us |
| 100K/s | Premium | 76us | 98us | 106us |
| 1M/s | OSS Java | 3,301us | 8,479us | 9,306us |
| 1M/s | Premium | 106us | 143us | 158us |

**Critical:** OSS degrades 35x at 1M msgs/sec; Premium stays flat (kernel bypass/DPDK).

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-04-27 | Initial release with ClusteredService patterns, determinism rules, configuration guide, monitoring counters, and ClusterTool commands |

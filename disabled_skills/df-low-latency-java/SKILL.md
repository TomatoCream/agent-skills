---
name: low-latency-java
description: Use when writing Java code that uses Aeron, Agrona, SBE, LMAX Disruptor, Chronicle Queue, or any low-latency pattern. Also use when tuning JVM flags for latency, configuring Linux for real-time, avoiding GC on hot paths, using VarHandle memory ordering, lock-free data structures, thread affinity, off-heap memory, or mechanical sympathy. Triggers on imports of io.aeron, org.agrona, uk.co.real_logic.sbe, com.lmax.disruptor, net.openhft.chronicle, or keywords like "latency", "throughput", "zero-copy", "lock-free", "false sharing", "single-writer".
---

# Low-Latency Java: Aeron, Agrona, SBE & High-Performance Patterns

## Overview

Comprehensive reference for building high-performance, low-latency Java systems using the Real Logic stack (Aeron, Agrona, SBE) and associated patterns (mechanical sympathy, lock-free concurrency, GC avoidance, OS tuning).

## When to Use

- Writing or reviewing code that imports `io.aeron.*`, `org.agrona.*`, or SBE codecs
- Designing message-passing architectures with microsecond latency targets
- Tuning JVM or Linux for low-latency workloads
- Implementing lock-free data structures or single-writer patterns
- Choosing between Aeron, Disruptor, Chronicle Queue, or Kafka
- Debugging latency spikes, GC pauses, or false sharing
- Writing JMH benchmarks or measuring tail latency with HdrHistogram

## When NOT to Use

- General Java development without latency requirements
- CRUD/web apps where millisecond latency is acceptable
- Kafka/RabbitMQ usage for throughput-oriented workloads

## Reference Loading Strategy

Load ONLY the reference files relevant to the current task:

```
User working with Aeron pub/sub?     → Load reference/aeron.md
User working with Aeron Cluster?     → Load reference/aeron-cluster.md
User writing SBE schemas or codecs?  → Load reference/sbe.md
User using Agrona data structures?   → Load reference/agrona.md
User asking about GC/cache/locks?    → Load reference/patterns.md
User using Disruptor/Chronicle?      → Load reference/ecosystem.md
User tuning JVM flags?               → Load reference/jvm-tuning.md
User tuning Linux kernel?            → Load reference/linux-tuning.md
Multiple domains?                    → Load multiple files
```

## Quick Decision Matrix

| Need | Solution | Reference |
|------|----------|-----------|
| Inter-process messaging (same machine) | Aeron IPC | aeron.md |
| Network messaging (cross-machine) | Aeron UDP | aeron.md |
| Fault-tolerant replicated state | Aeron Cluster | aeron-cluster.md |
| Fast serialization (< 100ns) | SBE | sbe.md |
| Off-heap buffers, primitive collections | Agrona | agrona.md |
| Intra-JVM event pipeline | LMAX Disruptor | ecosystem.md |
| Persistent IPC with replay | Chronicle Queue | ecosystem.md |
| GC elimination on hot path | Object pool + flyweight + off-heap | patterns.md |
| Thread-to-core pinning | Java Thread Affinity | ecosystem.md |
| Eliminate lock contention | Single-writer + VarHandle | patterns.md |
| JVM latency flags | ZGC/Epsilon + AlwaysPreTouch + huge pages | jvm-tuning.md |
| OS-level jitter elimination | isolcpus + nohz_full + IRQ affinity | linux-tuning.md |

## Cardinal Rules (Always Apply)

1. **No `new` on the hot path.** Pre-allocate, pool, or use flyweights.
2. **Single writer per data structure.** Multiple writers = cache line contention = 100x+ slowdown.
3. **Use Release/Acquire, not volatile.** On x86, Release/Acquire is free (zero instructions). Volatile costs an MFENCE.
4. **Measure percentiles, not averages.** Report p50/p99/p99.9/max at a defined throughput. Correct for coordinated omission.
5. **Tune the full stack.** Java patterns without OS tuning (or vice versa) leaves latency on the table.

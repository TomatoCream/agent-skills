# JVM Tuning for Low-Latency Java

Skill reference for configuring the JVM, measuring latency, and launching Aeron/Agrona applications in production.

---

## 1. GC Selection

| Collector | Flag | Pause | Heap Reclamation | When to Use |
|-----------|------|-------|------------------|-------------|
| **EpsilonGC** | `-XX:+UnlockExperimentalVMOptions -XX:+UseEpsilonGC` | Zero | None | Hot path allocates nothing; heap never fills. Shortest tail latency. |
| **ZGC** | `-XX:+UseZGC -XX:+ZGenerational` | <1 ms | Yes (concurrent) | Default choice for latency-sensitive services. Works at any heap size. JDK 21+ for generational mode. |
| **Shenandoah** | `-XX:+UseShenandoahGC` | <1 ms | Yes (concurrent compaction) | Alternative to ZGC. Available in Red Hat builds; not in Oracle JDK. |
| **G1** | `-XX:+UseG1GC` | Multi-ms | Yes | JDK default. Acceptable when p99 target is >5 ms. |

Rule: if your hot path does `new`, use ZGC or Shenandoah. If it never allocates, use EpsilonGC.

## 2. Memory Flags

```
-Xms8g -Xmx8g                     # Fixed heap -- ALWAYS set equal. Prevents resize pauses.
-XX:+AlwaysPreTouch                # Fault all pages at startup, not during operation.
-XX:+UseLargePages                 # Use 2 MB huge pages to reduce TLB misses.
-XX:LargePageSizeInBytes=2m        # Explicit page size.
-XX:+UseCompressedOops             # 32-bit object refs when heap < 32 GB. Saves ~15% memory.
```

On Linux, disable Transparent Huge Pages (`echo never > /sys/kernel/mm/transparent_hugepage/enabled`) and reserve explicit huge pages via `vm.nr_hugepages`. THP background compaction causes latency spikes.

## 3. JIT Compilation

```
-XX:+TieredCompilation             # C1 (fast startup) then C2 (peak throughput).
-XX:CompileThreshold=1000          # Compile sooner than default (10000) for faster warmup.
-XX:MaxInlineSize=100              # Inline methods up to 100 bytes (default 35).
-XX:FreqInlineSize=400             # Inline hot methods up to 400 bytes (default 325).
```

**Megamorphic call sites:** When a virtual call has 3+ receiver types, HotSpot falls back to a vtable lookup -- roughly 3x slower than a monomorphic (single-type) call. Keep hot-path call sites monomorphic. If you must use polymorphism, keep it to 2 receiver types (bimorphic inline cache).

## 4. Safepoints

The JVM stops all threads at safepoints for GC, deoptimization, and class redefinition. Latency-sensitive tuning:

```
-XX:+UseCountedLoopSafepoints      # Insert safepoint polls in counted loops.
                                    # Without this, a long counted loop blocks ALL safepoints.
-XX:GuaranteedSafepointInterval=0  # JDK 17+: disable timed safepoints entirely.
```

- Safepoint poll cost: ~0.4-0.6 ns per poll (negligible).
- **Thread-local handshakes** (JEP 312, JDK 11+): the JVM can stop individual threads instead of all threads. Reduces stop-the-world scope.

## 5. Aeron / Agrona Specific

```
--add-opens=java.base/sun.nio.ch=ALL-UNNAMED        # Aeron media driver needs NIO internals.
--add-opens=java.base/jdk.internal.misc=ALL-UNNAMED  # Agrona Unsafe access.
-Dagrona.disable.bounds.checks=true                  # Skip bounds checks in production.
-Daeron.dir=/dev/shm/aeron-myapp                     # Place media driver buffers on tmpfs.
```

Always run the Aeron media driver directory on `/dev/shm` (shared memory tmpfs) for IPC. Ensure `/dev/shm` is large enough: `mount -o remount,size=4G /dev/shm`.

## 6. Benchmarking with JMH

```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.NANOSECONDS)
@Warmup(iterations = 5, time = 1)
@Measurement(iterations = 10, time = 1)
@Fork(2)
@State(Scope.Thread)
public class MyBenchmark {

    @Benchmark
    public void measure(Blackhole bh) {
        bh.consume(doWork());
    }
}
```

- `@State(Scope.Thread)` -- per-thread state, no contention.
- `@State(Scope.Benchmark)` + `@Threads(N)` -- shared state for concurrent benchmarks.
- `Blackhole.consume()` -- prevents dead code elimination.
- Build uber-jar: `maven-shade-plugin` with `org.openjdk.jmh.Main` as main class.
- JMH limitation: iterations are independent -- cannot detect coordinated omission.

## 7. Latency Measurement

Use **HdrHistogram** with coordinated omission correction:

```java
SingleWriterRecorder recorder = new SingleWriterRecorder(1, 3_600_000_000_000L, 3);

// Record WITH correction -- synthetic values fill the gap for missed requests.
recorder.recordValueWithExpectedInterval(latencyNs, expectedIntervalNs);

// Snapshot for reporting (lock-free, concurrent with recording).
Histogram snapshot = recorder.getIntervalHistogram();
long p50   = snapshot.getValueAtPercentile(50.0);
long p99   = snapshot.getValueAtPercentile(99.0);
long p999  = snapshot.getValueAtPercentile(99.9);
long p9999 = snapshot.getValueAtPercentile(99.99);
long max   = snapshot.getMaxValue();
```

- `SingleWriterRecorder` -- one recorder per thread, no contention.
- Report: **p50 / p99 / p99.9 / p99.99 / max**. NEVER use averages.
- **JLBH** (Java Latency Benchmarking Harness, OpenHFT): accepts target throughput, accounts for coordinated omission. Use for system-level latency benchmarks.

## 8. Coordinated Omission

When a load generator waits for a slow response before sending the next request, requests that *would have arrived* during the slow period are never measured. Effect: your measured p99.999 may actually be your real p90.

- JMH cannot detect this (iterations are independent by design).
- Fix: use `HdrHistogram.recordValueWithExpectedInterval()` or JLBH.
- Always specify the offered throughput rate when reporting latency numbers. Latency without throughput context is meaningless.

## 9. Production Launch Script

```bash
#!/bin/bash
# Low-latency JVM launch script

JAVA_OPTS=(
    # Memory
    "-Xms8g" "-Xmx8g"
    "-XX:+AlwaysPreTouch"
    "-XX:+UseLargePages"
    "-XX:LargePageSizeInBytes=2m"

    # GC (choose one)
    "-XX:+UseZGC" "-XX:+ZGenerational"        # ZGC generational (JDK 21+)
    # "-XX:+UnlockExperimentalVMOptions" "-XX:+UseEpsilonGC"  # Zero-GC

    # JIT
    "-XX:+TieredCompilation"
    "-XX:CompileThreshold=1000"
    "-XX:MaxInlineSize=100"
    "-XX:FreqInlineSize=400"

    # Safepoints
    "-XX:+UseCountedLoopSafepoints"
    "-XX:GuaranteedSafepointInterval=0"

    # Object layout
    "-XX:+UseCompressedOops"

    # Aeron / Agrona
    "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED"
    "--add-opens=java.base/jdk.internal.misc=ALL-UNNAMED"
    "-Dagrona.disable.bounds.checks=true"
    "-Daeron.dir=/dev/shm/aeron-myapp"

    # Diagnostics (enable selectively)
    # "-XX:+UnlockDiagnosticVMOptions"
    # "-XX:+PrintCompilation"
    # "-Xlog:gc*:file=gc.log:time"
)

# Pin to isolated cores (kernel boot: isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7)
taskset -c 2-7 java "${JAVA_OPTS[@]}" -jar myapp.jar
```

## 10. GraalVM Native Image

```bash
native-image --no-fallback -jar myapp.jar
```

- Peak performance from the first request -- no JIT warmup.
- Sub-millisecond startup time.
- **Tradeoff:** no profile-guided JIT optimization. For long-running services, HotSpot C2 will eventually outperform native-image on hot paths.
- Best for: short-lived processes, serverless functions, CLI tools, or when deterministic first-request latency matters more than sustained throughput.

# Linux OS Tuning for Low-Latency Java

Quick reference for kernel and OS settings that eliminate jitter on the hot path.
No amount of Java optimization compensates for an untuned kernel.

---

## 1. CPU Isolation

Remove cores from the general scheduler so only your pinned threads run on them.

**Kernel boot parameters** (in `/etc/default/grub`, then `update-grub && reboot`):

```
GRUB_CMDLINE_LINUX="isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7"
```

- `isolcpus=2-7` -- cores 2-7 are invisible to the CFS scheduler.
- Pin application threads to isolated cores with `taskset -c 2 java ...` or OpenHFT Java Thread Affinity in code.
- Move leftover kernel threads to housekeeping core 0:
  ```bash
  pgrep -P 2 | xargs -i taskset -p -c 0 {}
  ```
- **Verify** with `perf stat -e 'sched:sched_switch' -a -A` -- isolated cores should show near-zero context switches.

## 2. Timer Tick Suppression

```
nohz_full=2-7 rcu_nocbs=2-7
```

- Reduces timer interrupts on isolated cores from 1000/sec to ~1 every 2 seconds.
- `rcu_nocbs` offloads RCU callbacks to housekeeping cores.
- Reduce VM stats polling: `sysctl -w vm.stat_interval=120`

## 3. IRQ Affinity

Move all hardware interrupts to housekeeping cores (0-1):

```bash
irqbalance --foreground --oneshot
```

Verify and manually fix stragglers:

```bash
cat /proc/interrupts                    # check per-core counts
cat /proc/irq/*/smp_affinity_list       # which cores handle each IRQ
echo 0-1 > /proc/irq/<N>/smp_affinity_list   # force to cores 0-1
```

## 4. Huge Pages

Disable THP (background compaction causes multi-millisecond jitter):

```bash
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

Reserve explicit 2MB pages (4096 pages = 8 GB):

```bash
echo 4096 > /proc/sys/vm/nr_hugepages
```

JVM flags:

```
-XX:+UseLargePages -XX:LargePageSizeInBytes=2m
```

Why: a 1 GB heap with 4 KB pages needs 262,144 TLB entries; TLB holds ~1,500. Each TLB miss costs ~100 ns. With 2 MB pages the same heap needs only 512 entries.

## 5. Memory

```bash
swapoff -a                                          # prevent major page faults
sysctl -w vm.swappiness=0                           # never swap
echo 0 > /proc/sys/kernel/numa_balancing            # stop page migration
echo 0 > /sys/kernel/mm/ksm/run                     # disable Kernel Same-page Merging
```

In code, call `mlockall(MCL_CURRENT | MCL_FUTURE)` (via JNI or Agrona) to wire all pages into RAM and prevent future page faults.

## 6. CPU Frequency

Lock cores to maximum frequency:

```bash
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > "$cpu"
done
```

Enable turbo boost (Intel):

```bash
echo 0 > /sys/devices/system/cpu/intel_pstate/no_turbo
```

Frequency transitions (C-state exits, P-state shifts) cost 10-100 us. The performance governor eliminates them.

## 7. Hyper-Threading (SMT)

Disable SMT -- sharing a physical core causes contention on execution units, caches, and branch predictors.

Options (pick one):
- BIOS: disable Hyper-Threading.
- Kernel boot: `nosmt`
- Runtime: `echo off > /sys/devices/system/cpu/smt/control`

## 8. Network

Aeron socket buffers:

```bash
sysctl -w net.core.rmem_max=8388608     # 8 MB
sysctl -w net.core.wmem_max=8388608     # 8 MB
sysctl -w net.core.rmem_default=2097152 # 2 MB
sysctl -w net.core.wmem_default=2097152 # 2 MB
```

Aeron `SO_RCVBUF` sweet spot: 2-4 MB.

Kernel bypass for lowest latency: DPDK, Solarflare OpenOnload, Mellanox VMA. Aeron Premium integrates kernel bypass.

Always disable Nagle's algorithm: set `TCP_NODELAY`.

Size `/dev/shm` for Aeron media driver:

```bash
mount -o remount,size=4G /dev/shm
```

## 9. Security Tradeoff

```
mitigations=off
```

Removes Spectre/Meltdown/MDS overhead. **Only for dedicated, single-tenant machines running trusted code.** Do not use on shared or multi-tenant hosts.

## 10. Verification

- **System jitter**: run the `hiccups` tool (from Azul) on isolated cores. Target < 1 us max hiccup.
- **Interrupts on isolated cores**: `watch -n 1 'cat /proc/interrupts'` -- isolated core columns should increment rarely.
- **Context switches**: `perf stat -e 'sched:sched_switch' -a -A` on isolated cores.
- **Timer interrupts**: `watch -n 1 'grep LOC /proc/interrupts'` -- isolated cores should show ~0.5 increments/sec.

## 11. Complete Tuning Script

```bash
#!/bin/bash
# Low-latency Linux tuning for Java / Aeron applications.
# Run as root BEFORE starting the application.
# Kernel boot params (require reboot):
#   isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7 nosmt mitigations=off

set -euo pipefail

# --- CPU Frequency ---
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > "$cpu"
done
echo 0 > /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null || true

# --- Memory ---
swapoff -a
sysctl -w vm.swappiness=0
sysctl -w vm.stat_interval=120
echo 0 > /proc/sys/kernel/numa_balancing
echo 0 > /sys/kernel/mm/ksm/run 2>/dev/null || true

# --- Huge Pages ---
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
echo 4096 > /proc/sys/vm/nr_hugepages   # 4096 x 2MB = 8GB

# --- Network ---
sysctl -w net.core.rmem_max=8388608
sysctl -w net.core.wmem_max=8388608
sysctl -w net.core.rmem_default=2097152
sysctl -w net.core.wmem_default=2097152

# --- IRQ Affinity ---
irqbalance --foreground --oneshot || true

# --- Shared Memory (Aeron media driver) ---
mount -o remount,size=4G /dev/shm

# --- File Descriptors ---
ulimit -n 65536

echo "Tuning complete. Verify with:"
echo "  perf stat -e 'sched:sched_switch' -a -A  (context switches)"
echo "  watch -n1 'cat /proc/interrupts'          (interrupt counts)"
echo "  hiccups -c 2 -d 60                        (system jitter)"
```

---

*Source: Research report 2026-04-24 -- Finding 9 and Appendix C.11.*

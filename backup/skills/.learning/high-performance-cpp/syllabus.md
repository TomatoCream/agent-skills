# High Performance C++ - Syllabus

## Overview

This syllabus builds a foundation in high-performance C++ from the ground up, focusing on understanding *why* C++ is fast, how hardware and software interact, and the mental models that distinguish performance-aware engineers. Emphasis on theory, real-world production patterns, and interview-ready knowledge.

## Prerequisites

- Basic programming experience in any language (variables, loops, functions, conditionals)
- Familiarity with compiling and running a C or C++ program (or willingness to set up a toolchain)
- No prior performance optimization experience required

## Learning Objectives

By the end of this syllabus, you will be able to:
1. Explain the C++ memory model and how stack vs. heap allocation affects performance
2. Reason about cache behavior and data layout for real-world programs
3. Understand move semantics, RAII, and zero-cost abstractions
4. Profile code and identify bottlenecks using standard tools
5. Answer common C++ performance interview questions with confidence
6. Apply key optimization patterns used in production systems

---

## Phase 1: Foundations — How C++ Maps to Hardware

*Goal: Build the mental model of what happens between your code and the CPU.*

- [ ] **1.1 The Compilation Model** — Translation units, the preprocessor, compiler, linker. Why C++ compiles to native code and what that means for performance vs. interpreted/JIT languages.
- [ ] **1.2 Memory Layout Fundamentals** — Stack vs. heap. How local variables, function calls, and dynamic allocation map to physical memory. The cost of `new`/`delete`.
- [ ] **1.3 CPU Caches and Data Locality** — L1/L2/L3 cache hierarchy. Cache lines. Why accessing memory sequentially is fast and random access is slow. The concept of "cache-friendly" code.
- [ ] **1.4 Value Semantics vs. Reference Semantics** — Pass by value, reference, pointer. When copies happen implicitly. Why C++ defaults to value semantics and how this helps performance.
- [ ] **1.5 Sizeof, Alignment, and Padding** — How structs are laid out in memory. Alignment requirements. Why field order matters for memory footprint.

**Interview milestone:** Explain why iterating a `vector<int>` is faster than iterating a `list<int>`. Explain struct padding.

---

## Phase 2: Ownership, Lifetime, and the Cost of Abstraction

*Goal: Understand RAII, move semantics, and how C++ achieves zero-cost abstractions.*

- [ ] **2.1 RAII — Resource Acquisition Is Initialization** — Constructors, destructors, and deterministic cleanup. Why RAII eliminates resource leaks without a garbage collector.
- [ ] **2.2 Copy vs. Move Semantics** — Lvalue vs. rvalue. Copy constructors vs. move constructors. `std::move`. Why moves are cheap and copies can be expensive.
- [ ] **2.3 Smart Pointers** — `unique_ptr`, `shared_ptr`, `weak_ptr`. Ownership models. The performance cost of `shared_ptr` (reference counting, atomic operations) vs. `unique_ptr` (zero overhead).
- [ ] **2.4 Templates and Zero-Cost Abstractions** — How templates generate specialized code at compile time. Why `std::sort` outperforms C's `qsort`. Monomorphization.
- [ ] **2.5 Inline Functions and Compiler Optimizations** — What `inline` really means. Link-time optimization (LTO). How the compiler eliminates abstraction overhead.

**Interview milestone:** Explain move semantics. Compare `unique_ptr` vs. `shared_ptr` performance. What is a zero-cost abstraction?

---

## Phase 3: Containers, Algorithms, and Data-Oriented Design

*Goal: Choose the right data structures and understand their performance characteristics.*

- [ ] **3.1 STL Containers — Performance Tradeoffs** — `vector`, `array`, `deque`, `list`, `map`, `unordered_map`, `set`. Big-O is not the full story — cache behavior matters more in practice.
- [ ] **3.2 std::vector Deep Dive** — Contiguous memory. Growth strategy (amortized O(1) push_back). `reserve()` and `shrink_to_fit()`. Why vector is almost always the right default.
- [ ] **3.3 Hash Maps in Practice** — `unordered_map` internals (buckets, load factor, rehashing). Open addressing vs. chaining. Real-world alternatives (flat hash maps, Swiss tables).
- [ ] **3.4 STL Algorithms and Iterators** — `std::sort`, `std::find`, `std::transform`, `std::accumulate`. Why algorithms on contiguous data are fast. Iterator categories.
- [ ] **3.5 Data-Oriented Design (DOD) Intro** — Struct-of-Arrays vs. Array-of-Structs. Designing data layouts for the CPU, not the programmer. Hot/cold splitting.

**Interview milestone:** When would you use `unordered_map` vs. `map`? Why is `vector` usually faster than `list` even for insertions? What is SoA vs. AoS?

---

## Phase 4: Profiling, Measurement, and Real-World Optimization

*Goal: Learn to measure before optimizing. Apply knowledge to real-world scenarios.*

- [ ] **4.1 Benchmarking Fundamentals** — Microbenchmarks vs. real workloads. `std::chrono` for timing. Google Benchmark basics. Avoiding common pitfalls (dead code elimination, warm-up).
- [ ] **4.2 Profiling Tools** — `perf`, `Instruments` (macOS), `Valgrind/Callgrind`, `VTune`. Reading flame graphs. Finding hotspots in real code.
- [ ] **4.3 Compiler Explorer (Godbolt)** — Reading compiler output. Checking if the compiler optimized what you expected. Comparing optimization levels (`-O0` vs. `-O2` vs. `-O3`).
- [ ] **4.4 Common Optimization Patterns** — Avoiding unnecessary copies. Reserving container capacity. String optimizations (SSO, string_view). Branch prediction hints. Loop unrolling awareness.
- [ ] **4.5 Real-World Case Studies** — Performance patterns from game engines, trading systems, database internals. What production C++ performance work actually looks like.

**Interview milestone:** Walk through how you'd profile and optimize a slow function. Explain SSO (Small String Optimization). What's the difference between `-O2` and `-O3`?

---

## Teaching Milestones

After each phase, you should be able to:
1. **Phase 1:** Draw a diagram of stack vs. heap and explain cache lines to a non-C++ developer
2. **Phase 2:** Explain why `std::vector<std::unique_ptr<T>>` is idiomatic and efficient
3. **Phase 3:** Choose the right container for a given problem and justify it with cache/memory reasoning
4. **Phase 4:** Profile a program, identify the bottleneck, and propose a targeted fix

## Resources

- *"A Tour of C++" by Bjarne Stroustrup* — concise modern C++ overview
- *"Effective Modern C++" by Scott Meyers* — items on move semantics, smart pointers, templates
- *"Data-Oriented Design" by Richard Fabian* — DOD principles
- Compiler Explorer: godbolt.org
- CppCon talks on YouTube (especially Chandler Carruth on performance, Mike Acton on DOD)
- Quick C++ Benchmark: quick-bench.com

## Success Criteria

- Can explain the performance implications of any C++ code at the memory/cache level
- Can profile a program and identify real bottlenecks (not guess)
- Can answer 80%+ of common C++ performance interview questions
- Can make informed data structure and design choices based on hardware realities

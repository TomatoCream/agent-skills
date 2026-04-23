## Summary

This class has several critical issues that will cause production failures: a resource leak in database connections, thread-safety violations on shared mutable state, and hardcoded credentials in source code. These must be fixed before deployment.

## Critical / Major Issues

### Critical

1. **Resource leak in `saveOrder` -- Connection and PreparedStatement are never closed (line 68-75)**

   If `saveOrder` is called repeatedly (which it will be, once per order), every invocation opens a new JDBC connection and PreparedStatement that are never closed. Under load this will exhaust the database connection pool or OS file descriptors and crash the application.

   **Fix:** Use try-with-resources for both the Connection and PreparedStatement:
   ```java
   private void saveOrder(Order order) throws Exception {
       try (var conn = dataSource.getConnection();
            var ps = conn.prepareStatement(
                "UPDATE orders SET total = ?, status = ? WHERE id = ?")) {
           ps.setDouble(1, order.getTotal());
           ps.setString(2, order.getStatus());
           ps.setLong(3, order.getId());
           ps.executeUpdate();
       }
   }
   ```

2. **Hardcoded database credentials in source code (line 68-69)**

   `"root"` and `"password123"` are checked into the codebase. This is a security vulnerability -- anyone with repository access has full database credentials. Additionally, `DriverManager.getConnection()` is called per-order instead of using a connection pool.

   **Fix:** Inject a `DataSource` (e.g., HikariCP) via the constructor and read credentials from environment variables or a secrets manager. Never commit credentials to source control.

3. **Thread-safety violation on `pendingOrders` (lines 9, 14, 19, 28, 80, 91, 100)**

   `pendingOrders` is a plain `ArrayList` accessed from multiple threads without synchronization. `addOrder()` can be called concurrently with `processAllOrders()`, `groupOrdersByStatus()`, `findExpensiveOrders()`, or `calculateAverageOrderValue()`. This causes `ConcurrentModificationException` or silent data corruption.

   **Fix:** Either:
   - Use a `CopyOnWriteArrayList` or `ConcurrentLinkedQueue`, or
   - Synchronize all access to `pendingOrders`, or
   - Redesign so that submission and processing happen on clearly separated phases with proper handoff (e.g., swap the list under a lock).

4. **Race condition in `processAllOrders` -- clearing list while tasks may still reference it (lines 19-29)**

   The method iterates `pendingOrders`, submits async tasks, then immediately calls `clear()`. The submitted tasks capture `order` references from the iteration, so the objects themselves survive, but a concurrent call to `addOrder()` between the iteration and `clear()` would lose that order. More critically, setting `processing = false` on line 29 happens immediately, not when all tasks complete -- callers have no way to know when processing is actually done.

   **Fix:** Snapshot the list, clear it atomically, and use a `CountDownLatch` or `Future` list so callers can await completion:
   ```java
   public List<Future<?>> processAllOrders() {
       List<Order> snapshot;
       synchronized (this) {
           snapshot = new ArrayList<>(pendingOrders);
           pendingOrders.clear();
       }
       List<Future<?>> futures = new ArrayList<>();
       for (Order order : snapshot) {
           futures.add(executor.submit(() -> {
               try { processOrder(order); }
               catch (Exception e) { /* log properly */ }
           }));
       }
       return futures;
   }
   ```

5. **Swallowed exceptions in async tasks (lines 20-25)**

   Wrapping the exception in `RuntimeException` and rethrowing inside a `Runnable` submitted to an executor means the exception is silently swallowed (nobody calls `Future.get()`). Failed orders disappear with no trace.

   **Fix:** Log the exception with order context using SLF4J/Log4J, and track failures (e.g., set order status to `"FAILED"`, collect Futures and check them).

6. **`ExecutorService` is never shut down (line 10)**

   The `newCachedThreadPool()` is created as a field but never shut down. This leaks threads and prevents JVM shutdown. Also, `newCachedThreadPool()` has an unbounded thread pool -- a burst of orders could create thousands of threads.

   **Fix:** Use a bounded pool (`newFixedThreadPool` or a `ThreadPoolExecutor` with explicit bounds), inject it or manage its lifecycle, and shut it down in a `close()` / `@PreDestroy` method. Name the threads for debuggability:
   ```java
   private final ExecutorService executor = new ThreadPoolExecutor(
       4, 16, 60L, TimeUnit.SECONDS,
       new LinkedBlockingQueue<>(1000),
       new ThreadFactoryBuilder().setNameFormat("order-processor-%d").build());
   ```

### Major

7. **Floating-point arithmetic for monetary values (lines 38-58)**

   Using `double` for currency calculations introduces rounding errors. For example, `0.1 + 0.2 != 0.3` in IEEE 754. The rounding on line 58 (`Math.round(total * 100) / 100`) also returns a `long` divided by an `int`, which truncates to integer -- this is a bug. `Math.round(total * 100)` returns `long`, and `100` is `int`, so the division is integer division, discarding cents.

   **Fix:** Use `BigDecimal` for all monetary calculations:
   ```java
   BigDecimal total = BigDecimal.ZERO;
   // ...
   total = total.setScale(2, RoundingMode.HALF_UP);
   ```

8. **Division by zero in `calculateAverageOrderValue` (line 104)**

   If `pendingOrders` is empty, `count` is 0 and `sum / count` produces `Infinity` (since both are doubles) or would be an `ArithmeticException` with integers. Either way, this is wrong.

   **Fix:** Guard against empty list:
   ```java
   public double calculateAverageOrderValue() {
       if (pendingOrders.isEmpty()) return 0.0;
       // ...
   }
   ```
   Better yet, return `OptionalDouble` to make absence explicit.

9. **Order status is a raw String (line 61)**

   Using `"PROCESSED"` as a string is fragile -- typos compile fine but break at runtime, and there is no way to enumerate valid states.

   **Fix:** Use an enum:
   ```java
   public enum OrderStatus { PENDING, PROCESSED, FAILED, CANCELLED }
   ```

10. **`volatile boolean processing` provides no meaningful synchronization (lines 11, 18, 29)**

    Setting `processing = true` at the start and `false` at the end of `processAllOrders()` provides no actual coordination. It does not wait for tasks to finish, and concurrent reads of this flag give a misleading picture of whether processing is underway.

    **Fix:** Remove this flag and use `Future`-based tracking or a `CountDownLatch` as described in issue 4.

## Minor Issues / Nits

1. **`groupOrdersByStatus` can be simplified (lines 78-88)** -- This is a textbook use case for `Collectors.groupingBy`:
   ```java
   return pendingOrders.stream().collect(Collectors.groupingBy(Order::getStatus));
   ```

2. **Unnecessary parallel stream in `findExpensiveOrders` (line 92)** -- The filtering operation (`o.getTotal() > threshold`) is trivially cheap. A parallel stream adds thread-scheduling overhead for no benefit. Use a sequential stream.

3. **`order.getItems().size() == 0` on line 36** -- Prefer `order.getItems().isEmpty()` for readability and intent clarity.

4. **Null check on `order` inside `processOrder` (line 34)** -- Silent returns on null/empty hide programming errors. It is better to reject null at the public boundary (`addOrder`) with `Objects.requireNonNull(order, "order must not be null")` and fail fast.

5. **Tax rate is hardcoded (line 54)** -- `0.08` should be a named constant or configurable value. Different jurisdictions have different tax rates.

6. **Discount thresholds are magic numbers (lines 44, 46)** -- Extract `10`, `5`, `0.9`, and `0.95` into named constants for clarity and maintainability.

7. **No input validation on `OrderItem` values** -- Negative prices or quantities would silently produce wrong totals. Validate at the boundary.

8. **`pendingOrders` field is not final (line 9)** -- The list reference itself should be `final` to prevent accidental reassignment. Mutability of the contents is a separate concern (addressed in issue 3).

## What's Good

- The use of `PreparedStatement` with parameter binding (lines 72-74) correctly prevents SQL injection. This is the right approach.
- The discount logic (lines 44-48) is structured clearly with readable conditions and is easy to follow.
- The method decomposition (`processOrder`, `saveOrder`, `groupOrdersByStatus`) shows reasonable separation of concerns as a starting point.

---
name: Using Jedis
description: >
  Jedis Java Redis client library. Use when writing Java code that connects to Redis,
  uses RedisClient, RedisClusterClient, RedisSentinelClient, JedisPooled, JedisCluster,
  JedisSentineled, Jedis, UnifiedJedis, JedisPool, connection pooling, pipelining,
  transactions, pub/sub, client-side caching, Redis Streams, or Redis modules (JSON,
  Search, TimeSeries, Bloom). Also use when user mentions jedis, redis java client,
  or redis.clients.jedis. Not for Lettuce, Redisson, Spring Data Redis internals,
  or non-Java Redis clients.
---

# Jedis

## Quick Start

```xml
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>7.1.0</version>
</dependency>
```

```java
// v7+ recommended: use RedisClient (thread-safe, connection-pooled)
RedisClient client = RedisClient.create("localhost", 6379);
client.set("key", "value");
String val = client.get("key");
client.close();
```

For authenticated connections:
```java
RedisClient client = RedisClient.builder()
    .hostAndPort("localhost", 6379)
    .clientConfig(DefaultJedisClientConfig.builder()
        .user("myuser")
        .password("secret")
        .database(0)
        .build())
    .build();
```

URI form: `RedisClient.create("redis://user:pass@localhost:6379/0")`
SSL form: `RedisClient.create("rediss://localhost:6380")`

## Common Patterns

### Connection Pooling (Standalone)

```java
// v7+ builder pattern (recommended)
ConnectionPoolConfig poolConfig = new ConnectionPoolConfig();
poolConfig.setMaxTotal(128);
poolConfig.setMaxIdle(128);
poolConfig.setMinIdle(16);
poolConfig.setBlockWhenExhausted(true);
poolConfig.setMaxWait(Duration.ofSeconds(1));

RedisClient client = RedisClient.builder()
    .hostAndPort("localhost", 6379)
    .clientConfig(DefaultJedisClientConfig.builder()
        .password("secret")
        .build())
    .poolConfig(poolConfig)
    .build();

// Use directly - pool management is automatic
client.set("key", "value");
client.close(); // closes pool
```

### Redis Cluster

```java
Set<HostAndPort> nodes = new HashSet<>();
nodes.add(new HostAndPort("127.0.0.1", 7000));
nodes.add(new HostAndPort("127.0.0.1", 7001));

RedisClusterClient cluster = RedisClusterClient.builder()
    .nodes(nodes)
    .clientConfig(DefaultJedisClientConfig.builder()
        .password("secret")
        .build())
    .maxAttempts(5)
    .maxTotalRetriesDuration(Duration.ofSeconds(10))
    .build();

cluster.set("key", "value");
cluster.close();
```

### Redis Sentinel

```java
RedisSentinelClient client = RedisSentinelClient.builder()
    .masterName("mymaster")
    .sentinel("localhost", 26379)
    .sentinel("localhost", 26380)
    .clientConfig(DefaultJedisClientConfig.builder()
        .password("secret")
        .build())
    .build();
```

### Pipelining

```java
Pipeline p = client.pipelined();
p.set("key1", "val1");
p.set("key2", "val2");
Response<String> r1 = p.get("key1");
Response<String> r2 = p.get("key2");
p.sync();  // MUST call sync() before reading responses

String v1 = r1.get();  // "val1"
String v2 = r2.get();  // "val2"
```

### Transactions

```java
// Simple transaction
try (AbstractTransaction tx = client.multi()) {
    tx.set("key1", "val1");
    Response<String> r = tx.get("key1");
    List<Object> results = tx.exec();
    System.out.println(r.get()); // "val1"
}

// Optimistic locking with WATCH
try (AbstractTransaction tx = client.transaction(false)) {
    tx.watch("counter");
    String current = client.get("counter");
    int newVal = Integer.parseInt(current) + 1;

    tx.multi();
    tx.set("counter", String.valueOf(newVal));
    List<Object> results = tx.exec(); // null if key was modified
    if (results == null) {
        // Retry - another client modified "counter"
    }
}
```

### Pub/Sub

```java
JedisPubSub listener = new JedisPubSub() {
    @Override
    public void onMessage(String channel, String message) {
        System.out.println(channel + ": " + message);
    }
};

// subscribe() BLOCKS the calling thread
new Thread(() -> client.subscribe(listener, "my-channel")).start();

// Publish from another client
client.publish("my-channel", "hello");

// Unsubscribe to stop the blocking thread
listener.unsubscribe();
```

## Gotchas

### Client Class Selection

- **`Jedis` is NOT for production.** It is single-connection, not thread-safe, not pooled.
  Use `RedisClient` (v7+) or `JedisPooled` (v5-v6) for production.
  ```java
  // WRONG - single connection, not thread-safe
  Jedis jedis = new Jedis("localhost");

  // RIGHT - pooled, thread-safe
  RedisClient client = RedisClient.create("localhost", 6379);
  ```

### Pool Exhaustion (Default 8 Connections)

- **Pool defaults to 8 max connections.** Under load, `getResource()` blocks indefinitely.
  ```java
  // WRONG - uses default maxTotal=8
  RedisClient client = RedisClient.create("localhost", 6379);

  // RIGHT - configure pool for your workload
  ConnectionPoolConfig poolConfig = new ConnectionPoolConfig();
  poolConfig.setMaxTotal(128);
  poolConfig.setMaxIdle(128);
  poolConfig.setMinIdle(16);
  poolConfig.setMaxWait(Duration.ofSeconds(1)); // fail fast instead of blocking forever

  RedisClient client = RedisClient.builder()
      .hostAndPort("localhost", 6379)
      .poolConfig(poolConfig)
      .build();
  ```

### Timeout Defaults

- **Default socket timeout is 2000ms.** Slow commands (KEYS, large SORT, DEBUG SLEEP)
  will throw `SocketTimeoutException: Read timed out`.
  ```java
  JedisClientConfig config = DefaultJedisClientConfig.builder()
      .socketTimeoutMillis(5000)         // read timeout
      .connectionTimeoutMillis(5000)     // connect timeout
      .blockingSocketTimeoutMillis(0)    // for BLPOP etc. (0 = infinite)
      .build();
  ```

### Transaction Response Timing

- **`Response.get()` before `exec()` throws `IllegalStateException`.**
  ```java
  // WRONG
  AbstractTransaction tx = client.multi();
  Response<String> r = tx.get("key");
  String val = r.get(); // throws IllegalStateException!

  // RIGHT
  AbstractTransaction tx = client.multi();
  Response<String> r = tx.get("key");
  tx.exec();
  String val = r.get(); // works now
  ```

- **Cannot use intermediate results within a transaction.**
  Redis MULTI/EXEC does not support intra-transaction dependencies.

### Subscribe Blocks the Thread

- `subscribe()` and `psubscribe()` are **blocking** calls.
  They block the calling thread until unsubscribed. Always run in a separate thread.

### Pipeline Must Be Synced

- Forgetting `p.sync()` means responses are never read and `Response.get()` will fail.

### Binary vs String

- Redis stores raw bytes. Java `String` operations incur encode/decode overhead.
  For binary data (images, protobuf), use `byte[]` method variants directly.

## Configuration

### Pool Defaults (ConnectionPoolConfig)

| Setting | Default | Note |
|---------|---------|------|
| maxTotal | 8 | **Increase for production** |
| maxIdle | 8 | Match maxTotal |
| minIdle | 0 | Set >0 to pre-warm |
| testWhileIdle | true | Jedis default (differs from commons-pool) |
| minEvictableIdleTime | 60s | |
| timeBetweenEvictionRuns | 30s | |
| blockWhenExhausted | true | Set maxWait to avoid infinite blocks |

### Socket Buffer Size (System Properties)

Available since Jedis 4.2.0:
- `jedis.bufferSize.input` - input stream buffer
- `jedis.bufferSize.output` - output stream buffer
- `jedis.bufferSize` - both (if individual not set)

### Cluster Init Error Suppression

Set `jedis.cluster.initNoError` system property to suppress
`JedisClusterOperationException: Could not initialize cluster slots cache.`
Useful for Spring beans with unavailable clusters at startup. Available since 4.4.2.

### Client-Side Caching

```java
RedisClient client = RedisClient.builder()
    .hostAndPort("localhost", 6379)
    .cacheConfig(CacheConfig.builder()
        .maxSize(10000)
        .build())
    .build();

// GET results are cached locally and invalidated by Redis server
String val = client.get("key"); // fetched from Redis
String val2 = client.get("key"); // served from local cache
```

Requires Redis 6.0+ with RESP3 protocol or Redis 7.4+ tracking support.

## Version Notes

### v7 (current) - Major API Modernization

- **New client classes:** `RedisClient`, `RedisClusterClient`, `RedisSentinelClient`
  replace `JedisPooled`, `JedisCluster`, `JedisSentineled` (which still work but are older).
- **Builder pattern** for all client creation.
- **Removed:** `JedisSharding`, `ShardedPipeline`, `ShardedConnectionProvider`.
- **Renamed:** `PipelineBase` -> `AbstractPipeline`, `TransactionBase` -> `AbstractTransaction`.
- **Failover:** `MultiClusterClientConfig` -> `MultiDbConfig` with `MultiDbClient`.

### v6 - Redis 8.0 Support

- **Removed:** RedisGraph, Triggers & Functions (RedisGears v2).
- **Search dialect defaults to DIALECT 2.** To revert: `client.setDefaultSearchDialect(1)`.
- `FT.PROFILE` returns `ProfilingInfo` instead of `Map<String, Object>`.
- New `SslOptions` builder for SSL/TLS.
- Token-based authentication support.
- New hash commands: `HGETDEL`, `HGETEX`, `HSETEX`.

### v5 - Return Type Changes

- `zdiff`/`zinter`/`zunion` return `List` not `Set`.
- `configGet` returns `Map` not `List`.
- `blpop`/`brpop` return `KeyValue` not `KeyedListElement`.
- `bzpopmax`/`bzpopmin` return `KeyValue` not `KeyedZSetElement`.
- `SetParams.get()` removed; use `setGet(key, value)` instead.

## References

- [Modules & Data Types](references/modules.md) - JSON, Search, TimeSeries, Bloom, VectorSets
- [Failover & Resilience](references/failover.md) - Multi-database failover, circuit breaker, retry
- [Advanced Configuration](references/advanced-config.md) - SSL, NAT/Docker mapping, Unix sockets, RESP3

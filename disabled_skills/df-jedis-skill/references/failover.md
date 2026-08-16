# Failover & Resilience

## Multi-Database Failover (v7+)

Jedis supports automatic failover between Redis deployments using the circuit breaker pattern.

### Required Dependencies

```xml
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-all</artifactId>
    <version>1.7.1</version>
</dependency>
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-circuitbreaker</artifactId>
    <version>1.7.1</version>
</dependency>
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-retry</artifactId>
    <version>1.7.1</version>
</dependency>
```

### Configuration

```java
HostAndPort east = new HostAndPort("redis-east.example.com", 14000);
HostAndPort west = new HostAndPort("redis-west.example.com", 14000);

JedisClientConfig config = DefaultJedisClientConfig.builder()
    .user("cache").password("secret")
    .socketTimeoutMillis(5000).connectionTimeoutMillis(5000)
    .build();

ConnectionPoolConfig poolConfig = new ConnectionPoolConfig();
poolConfig.setMaxTotal(8);
poolConfig.setMaxIdle(8);

MultiDbConfig multiConfig = MultiDbConfig.builder()
    // Databases with weights (highest weight = preferred)
    .database(DatabaseConfig.builder(east, config)
        .connectionPoolConfig(poolConfig).weight(1.0f).build())
    .database(DatabaseConfig.builder(west, config)
        .connectionPoolConfig(poolConfig).weight(0.5f).build())
    // Circuit breaker (failure detection)
    .failureDetector(MultiDbConfig.CircuitBreakerConfig.builder()
        .slidingWindowSize(1000)
        .failureRateThreshold(50.0f)   // % failures to trip
        .minNumOfFailures(500)
        .build())
    // Failback settings
    .failbackSupported(true)
    .failbackCheckInterval(1000)       // ms between health checks
    .gracePeriod(10000)                // ms before re-enabling
    // Retry settings
    .commandRetry(MultiDbConfig.RetryConfig.builder()
        .maxAttempts(3)
        .waitDuration(500)
        .exponentialBackoffMultiplier(2)
        .build())
    .fastFailover(true)
    .retryOnFailover(false)
    .build();

MultiDbClient client = MultiDbClient.builder()
    .multiDbConfig(multiConfig)
    .build();
```

### Dynamic Weight Management (v7.4.0+)

```java
// Change weights at runtime without recreating client
client.updateWeight("redis-east.example.com:14000", 0.3f);
client.updateWeight("redis-west.example.com:14000", 1.0f);
```

### Migrating from v6 to v7

| v6 Class | v7 Replacement |
|----------|---------------|
| `MultiClusterClientConfig` | `MultiDbConfig` |
| `MultiClusterPooledConnectionProvider` | Built into `MultiDbClient` |
| `ClusterConfig` | `DatabaseConfig` |
| `UnifiedJedis(provider)` | `MultiDbClient.builder()...build()` |

## Cluster Retry Behavior

`RedisClusterClient` has built-in retry with defaults:
- `DEFAULT_MAX_ATTEMPTS = 5`
- `DEFAULT_TIMEOUT = 2000ms`

Override via builder:
```java
RedisClusterClient.builder()
    .nodes(nodes)
    .maxAttempts(10)
    .maxTotalRetriesDuration(Duration.ofSeconds(30))
    .build();
```

The client automatically handles `MOVED` and `ASK` redirections.

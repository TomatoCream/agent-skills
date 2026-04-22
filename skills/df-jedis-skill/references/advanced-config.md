# Advanced Configuration

## SSL/TLS

### Simple SSL

```java
RedisClient client = RedisClient.create("rediss://localhost:6380");
```

### Advanced SSL with SslOptions (v6+)

```java
SslOptions sslOptions = SslOptions.builder()
    .keystore(new File("/path/to/keystore.jks"))
    .keystorePassword("password".toCharArray())
    .truststore(new File("/path/to/truststore.jks"))
    .truststorePassword("password".toCharArray())
    .sslVerifyMode(SslVerifyMode.FULL)
    .build();

JedisClientConfig config = DefaultJedisClientConfig.builder()
    .ssl(true)
    .sslOptions(sslOptions)
    .build();

RedisClient client = RedisClient.builder()
    .hostAndPort("localhost", 6380)
    .clientConfig(config)
    .build();
```

## NAT / Docker / Kubernetes Port Mapping

When Redis cluster nodes report internal addresses (e.g. `172.18.0.2:6379`) but are
externally reachable at different addresses (e.g. `my-redis.example.com:7001`):

```java
Map<HostAndPort, HostAndPort> mapping = new HashMap<>();
mapping.put(new HostAndPort("172.18.0.2", 6379), new HostAndPort("my-redis.example.com", 7001));
mapping.put(new HostAndPort("172.18.0.3", 6379), new HostAndPort("my-redis.example.com", 7002));

HostAndPortMapper mapper = internal -> mapping.getOrDefault(internal, internal);

JedisClientConfig config = DefaultJedisClientConfig.builder()
    .hostAndPortMapper(mapper)
    .build();

RedisClusterClient cluster = RedisClusterClient.builder()
    .nodes(Set.of(new HostAndPort("my-redis.example.com", 7001)))
    .clientConfig(config)
    .build();
```

## Unix Domain Sockets

Lower latency when client and server are on the same machine. Requires junixsocket:

```xml
<dependency>
    <groupId>com.kohlschutter.junixsocket</groupId>
    <artifactId>junixsocket-core</artifactId>
    <version>2.10.1</version>
</dependency>
```

```java
// Implement JedisSocketFactory
public class UdsSocketFactory implements JedisSocketFactory {
    private final File socketFile;
    public UdsSocketFactory(String path) { this.socketFile = new File(path); }

    @Override
    public Socket createSocket() throws JedisConnectionException {
        try {
            Socket socket = AFUNIXSocket.newStrictInstance();
            socket.connect(new AFUNIXSocketAddress(socketFile), Protocol.DEFAULT_TIMEOUT);
            return socket;
        } catch (IOException e) {
            throw new JedisConnectionException("Failed to connect via UDS", e);
        }
    }
}

// Wire into RedisClient
JedisSocketFactory sf = new UdsSocketFactory("/tmp/redis.sock");
JedisClientConfig config = DefaultJedisClientConfig.builder().build();
ConnectionFactory cf = new ConnectionFactory(sf, config);
PooledConnectionProvider provider = new PooledConnectionProvider(cf);

RedisClient client = RedisClient.builder()
    .connectionProvider(provider)
    .clientConfig(config)
    .build();
```

## RESP3 Protocol

```java
JedisClientConfig config = DefaultJedisClientConfig.builder()
    .resp3()  // or .protocol(RedisProtocol.RESP3)
    .build();
```

RESP3 enables:
- Client-side caching with server-assisted invalidation
- Richer type information in responses
- Push notifications

**Gotcha:** Some response types differ under RESP3 (e.g. `jsonNumIncrBy` returns
`List<Double>` instead of `JSONArray`).

## Token-Based Authentication (v5.3+)

For cloud-managed Redis (Azure AMR/ACR, custom identity providers):

```java
// Custom identity provider
TokenAuthConfig tokenAuthConfig = TokenAuthConfig.builder()
    .identityProviderConfig(new YourCustomIdentityProviderConfig())
    .build();

JedisClientConfig config = DefaultJedisClientConfig.builder()
    .authXManager(new AuthXManager(tokenAuthConfig))
    .build();

RedisClient client = RedisClient.builder()
    .hostAndPort("managed-redis.example.com", 6380)
    .clientConfig(config)
    .build();
```

For Microsoft Entra ID, add dependency `redis.clients.authentication:redis-authx-entraid`
and use `EntraIDTokenAuthConfigBuilder`.

**Gotcha:** Blocking pub/sub is NOT supported with token-based auth on RESP2.
Use RESP3 protocol for pub/sub with TBA.

## Read-Only Cluster Replicas

Route read commands to replica nodes for reduced latency:

```java
JedisClientConfig config = DefaultJedisClientConfig.builder()
    .readOnlyForRedisClusterReplicas(true)
    .build();

RedisClusterClient cluster = RedisClusterClient.builder()
    .nodes(nodes)
    .clientConfig(config)
    .build();
```

## Client Name and CLIENT SETINFO

Jedis automatically sends `CLIENT SETINFO` with library name/version.
To customize or disable:

```java
// Custom client name
JedisClientConfig config = DefaultJedisClientConfig.builder()
    .clientName("my-service")
    .build();

// Disable CLIENT SETINFO
JedisClientConfig config = DefaultJedisClientConfig.builder()
    .clientSetInfoConfig(ClientSetInfoConfig.DISABLED)
    .build();
```

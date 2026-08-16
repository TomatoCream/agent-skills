# Modules & Data Types

## JSON (RedisJSON / built-in since Redis 8.0)

```java
// Set JSON
client.jsonSet("user:1", Path2.of("$"), "{\"name\":\"John\",\"age\":30}");

// Get JSON
String json = client.jsonGet("user:1");

// Get nested path
Object name = client.jsonGet("user:1", Path2.of("$.name"));

// Set nested path
client.jsonSet("user:1", Path2.of("$.age"), 31);

// Numeric increment
client.jsonNumIncrBy("user:1", Path2.of("$.age"), 1);

// Array append
client.jsonArrAppend("user:1", Path2.of("$.tags"), "\"new-tag\"");

// Delete path
client.jsonDel("user:1", Path2.of("$.temporary"));
```

**Gotcha:** In v5+ under RESP3, `jsonNumIncrBy` returns `List<Double>` not `JSONArray`.
Cast accordingly.

## Search (RediSearch / built-in since Redis 8.0)

### Index Creation

```java
import redis.clients.jedis.search.*;
import redis.clients.jedis.search.schemafields.*;

client.ftCreate("idx:users",
    FTCreateParams.createParams()
        .on(IndexDataType.JSON)
        .addPrefix("user:"),
    TextField.of("$.name").as("name"),
    NumericField.of("$.age").as("age"),
    TagField.of("$.role").as("role"));
```

### Search

```java
// Simple text search
SearchResult result = client.ftSearch("idx:users", "@name:John");

// With query builder
Query query = new Query("@name:John @age:[25 35]")
    .returnFields("name", "age")
    .limit(0, 10);
SearchResult result = client.ftSearch("idx:users", query);

for (Document doc : result.getDocuments()) {
    String name = doc.getString("name");
}
```

### Aggregation

```java
AggregationBuilder agg = new AggregationBuilder("@role:{admin}")
    .groupBy("@role", Reducers.count().as("count"))
    .sortBy(SortedField.desc("@count"))
    .limit(0, 10);

AggregationResult result = client.ftAggregate("idx:users", agg);
```

**Gotcha:** Default search dialect changed to DIALECT 2 in Jedis 6.0.
If queries break after upgrade, check dialect compatibility or revert:
`client.setDefaultSearchDialect(1);`

## TimeSeries

```java
// Create time series
client.tsCreate("sensor:temp",
    TSCreateParams.createParams()
        .retention(86400000)  // 24h in ms
        .label("type", "temperature")
        .label("location", "office"));

// Add data point
client.tsAdd("sensor:temp", System.currentTimeMillis(), 22.5);

// Auto-timestamp: use * (0L triggers server-side timestamp)
client.tsAdd("sensor:temp", 0L, 23.1);

// Range query
List<TSElement> data = client.tsRange("sensor:temp",
    TSRangeParams.rangeParams(startTs, endTs)
        .aggregation(AggregationType.AVG, 3600000)); // 1h buckets
```

## Bloom Filter

```java
// Reserve a bloom filter (error rate, capacity)
client.bfReserve("emails", 0.01, 100000);

// Add items
client.bfAdd("emails", "user@example.com");

// Check existence
boolean exists = client.bfExists("emails", "user@example.com"); // true (or false positive)
boolean notExist = client.bfExists("emails", "no@example.com"); // definitely false

// Bulk operations
client.bfMAdd("emails", "a@b.com", "c@d.com");
List<Boolean> results = client.bfMExists("emails", "a@b.com", "x@y.com");
```

## VectorSets (Redis 8.4+)

```java
// Add vectors
client.vadd("my-vectors", "vec1", new float[]{0.1f, 0.2f, 0.3f});

// Similarity search
List<RawVector> results = client.vsim("my-vectors",
    VSimParams.vsimParams()
        .count(5),
    new float[]{0.1f, 0.2f, 0.3f});
```

## Streams

```java
// Add to stream
StreamEntryID id = client.xadd("mystream",
    StreamEntryID.NEW_ENTRY,
    Map.of("sensor", "temp", "value", "22.5"));

// Read from stream
List<Map.Entry<String, List<StreamEntry>>> entries =
    client.xread(XReadParams.xReadParams().count(10),
        Map.of("mystream", StreamEntryID.UNRECEIVED_ENTRY));

// Consumer groups
client.xgroupCreate("mystream", "mygroup", StreamEntryID.LAST_ENTRY, true);

List<Map.Entry<String, List<StreamEntry>>> groupEntries =
    client.xreadGroup("mygroup", "consumer1",
        XReadGroupParams.xReadGroupParams().count(10),
        Map.of("mystream", StreamEntryID.UNRECEIVED_ENTRY));

// Acknowledge processing
client.xack("mystream", "mygroup", id);
```

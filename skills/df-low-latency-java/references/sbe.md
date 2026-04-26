# Simple Binary Encoding (SBE) Reference

## Core Concept

SBE generates **flyweight codec classes** that read/write directly on a `DirectBuffer` containing the wire-format bytes. There is no intermediate object, no serialization step, no copy. The byte sequence in memory IS the wire format.

- **Zero allocation** -- codecs are reusable wrappers, not new objects per message
- **Zero copy** -- fields are written at computed offsets into the target buffer
- **Sequential access** -- fields accessed in schema order; predictable and prefetch-friendly
- **Generated codecs** -- XML schema compiles to Java, C++, C# encoder/decoder classes

## Schema Definition (XML)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sbe:messageSchema xmlns:sbe="http://fixprotocol.io/2016/sbe"
                   package="com.example.sbe"
                   id="1" version="1" byteOrder="littleEndian">
  <types>
    <!-- REQUIRED: message header composite -->
    <composite name="messageHeader">
      <type name="blockLength" primitiveType="uint16"/>
      <type name="templateId"  primitiveType="uint16"/>
      <type name="schemaId"    primitiveType="uint16"/>
      <type name="version"     primitiveType="uint16"/>
    </composite>

    <enum name="Side" encodingType="uint8">
      <validValue name="BUY">0</validValue>
      <validValue name="SELL">1</validValue>
    </enum>

    <composite name="decimalEncoding">
      <type name="mantissa" primitiveType="int64"/>
      <type name="exponent" primitiveType="int8" presence="constant">-8</type>
    </composite>
  </types>

  <!-- Fixed fields only -->
  <sbe:message name="Order" id="1">
    <field name="orderId"   id="1" type="int64"/>
    <field name="price"     id="2" type="decimalEncoding"/>
    <field name="quantity"  id="3" type="int32"/>
    <field name="side"      id="4" type="Side"/>
    <field name="timestamp" id="5" type="int64"/>
  </sbe:message>

  <!-- Repeating group + variable-length data -->
  <sbe:message name="Trade" id="2">
    <field name="tradeId"  id="1" type="int64"/>
    <field name="price"    id="2" type="int64"/>
    <field name="quantity" id="3" type="int32"/>

    <group name="parties" id="10" dimensionType="groupSizeEncoding">
      <field name="partyId"   id="11" type="int64"/>
      <field name="partyRole" id="12" type="uint8"/>
    </group>

    <!-- Variable-length data MUST come last -->
    <data name="symbol" id="20" type="varStringEncoding"/>
  </sbe:message>

  <!-- Schema evolution: sinceVersion + presence="optional" -->
  <sbe:message name="OrderV2" id="3">
    <field name="orderId"  id="1" type="int64"/>
    <field name="price"    id="2" type="int64"/>
    <field name="quantity" id="3" type="int32"/>
    <field name="venue"    id="4" type="uint16"
           presence="optional" sinceVersion="1"/>
  </sbe:message>
</sbe:messageSchema>
```

### Type System

| Category    | Examples                                  | Notes                                        |
|-------------|-------------------------------------------|----------------------------------------------|
| Primitives  | `int8`, `int16`, `int32`, `int64`, `uint8`, `uint16`, `uint32`, `uint64`, `float`, `double`, `char` | Fixed-width, little/big endian per schema |
| Enums       | `<enum encodingType="uint8">`             | Maps symbolic names to integer wire values   |
| Sets        | `<set encodingType="uint8">`              | Bitfield; multiple choices encoded in one int |
| Composites  | `messageHeader`, `decimalEncoding`        | Grouping of primitives into reusable structs |

### Required Built-in Composites

- **messageHeader** -- `blockLength`(u16) + `templateId`(u16) + `schemaId`(u16) + `version`(u16) = **8 bytes**
- **groupSizeEncoding** -- `blockLength`(u16) + `numInGroup`(u16) = 4 bytes (default)
- **varStringEncoding** / **varDataEncoding** -- `length`(u32) + raw bytes

## Wire Layout

```
[messageHeader 8B] [fixed fields at static offsets] [repeating groups...] [var-length data...]
```

| Section          | Size           | Access Pattern               |
|------------------|----------------|------------------------------|
| Header           | 8 bytes fixed  | Static offsets               |
| Block (fields)   | blockLength    | Static offsets within block  |
| Repeating groups | Variable       | Sequential: count then entries |
| Variable data    | Variable       | Sequential: must be last     |

**Strict ordering**: fixed fields, then groups, then var-data. Within each section, fields appear in schema order.

## Encoding Rules

```java
// 1. Wrap header encoder on buffer
headerEncoder.wrap(buffer, offset)
    .blockLength(OrderEncoder.BLOCK_LENGTH)
    .templateId(OrderEncoder.TEMPLATE_ID)
    .schemaId(OrderEncoder.SCHEMA_ID)
    .version(OrderEncoder.SCHEMA_VERSION);

// 2. Wrap message encoder after header
orderEncoder.wrap(buffer, offset + MessageHeaderEncoder.ENCODED_LENGTH)
    .orderId(12345L)
    .price(50000L)
    .quantity(100)
    .side(Side.BUY);
```

**Repeating groups** -- call `xxxCount(n)` first, then `next()` for each entry:

```java
TradeEncoder.PartiesEncoder parties = tradeEncoder.partiesCount(2);
parties.next().partyId(1001L).partyRole((short) 1);
parties.next().partyId(1002L).partyRole((short) 2);
```

**Variable-length data** -- encode LAST, in schema order. Cannot skip fields:

```java
tradeEncoder.symbol("AAPL");  // must come after all groups
```

## Decoding Rules

```java
// 1. Wrap header decoder -- read templateId for dispatch
headerDecoder.wrap(buffer, offset);
int templateId = headerDecoder.templateId();
int actingBlockLength = headerDecoder.blockLength();
int actingVersion = headerDecoder.version();

// 2. Dispatch on templateId
switch (templateId) {
    case OrderDecoder.TEMPLATE_ID:
        orderDecoder.wrap(buffer,
            offset + MessageHeaderDecoder.ENCODED_LENGTH,
            actingBlockLength,
            actingVersion);
        long orderId = orderDecoder.orderId();
        long price = orderDecoder.price();
        // ... fields in schema order
        break;

    case TradeDecoder.TEMPLATE_ID:
        tradeDecoder.wrap(buffer,
            offset + MessageHeaderDecoder.ENCODED_LENGTH,
            actingBlockLength,
            actingVersion);
        // Fixed fields first
        long tradeId = tradeDecoder.tradeId();

        // MUST consume groups before var-data
        for (TradeDecoder.PartiesDecoder party : tradeDecoder.parties()) {
            long partyId = party.partyId();
            short role = party.partyRole();
        }

        // Var-data last, in schema order
        String symbol = tradeDecoder.symbol();
        break;
}
```

**Critical**: you MUST consume repeating groups before reading variable-length data. The decoder advances an internal cursor -- skipping groups corrupts var-data offsets.

## Versioning

New fields are **appended** at the end of the block with `sinceVersion` and `presence="optional"`.

```xml
<field name="venue" id="4" type="uint16"
       presence="optional" sinceVersion="1"/>
```

**Decoder behavior**: the generated decoder checks `actingVersion >= sinceVersion`. If the field is not present (old producer), it returns the type's `nullValue`.

```java
// Version-safe access pattern
if (orderDecoder.venueNullValue() != orderDecoder.venue()) {
    // Field is present -- use it
    int venue = orderDecoder.venue();
} else {
    // Old schema version -- field absent
}
```

**Rules**: append-only at end of block. Never reorder. Never remove. Never change field types. Variable-length fields can only be added at the end of the var-data section.

## Benchmarks

### C++ Benchmarks (128-byte domain model)

| Format      | Serialize | Deserialize | Wire Size |
|-------------|-----------|-------------|-----------|
| **SBE**     | **35 ns** | **52 ns**   | 138 bytes |
| Cap'n Proto | 247 ns    | 184 ns      | 208 bytes |
| FlatBuffers | 272 ns    | 81 ns       | 280 bytes |
| Protobuf    | 322 ns    | 351 ns      | **120 bytes** |

### Java Benchmarks (market data, Martin Thompson)

| Metric        | SBE           | Protobuf     | Ratio  |
|---------------|---------------|--------------|--------|
| Encode        | 10,436 ops/ms | 462 ops/ms   | **23x** |
| Decode        | 34,078 ops/ms | 1,148 ops/ms | **30x** |

SBE wins on speed. Protobuf wins on wire size for sparse messages (no padding).

## Integration with Aeron (Zero-Copy Pipeline)

Use `tryClaim()` to encode SBE directly into the Aeron log buffer -- no intermediate buffer:

```java
// PUBLISH: encode in-place into Aeron log buffer
long result = publication.tryClaim(encodedLength, bufferClaim);
if (result > 0) {
    headerEncoder.wrap(bufferClaim.buffer(), bufferClaim.offset())
        .blockLength(OrderEncoder.BLOCK_LENGTH)
        .templateId(OrderEncoder.TEMPLATE_ID)
        .schemaId(OrderEncoder.SCHEMA_ID)
        .version(OrderEncoder.SCHEMA_VERSION);

    orderEncoder.wrap(bufferClaim.buffer(),
                      bufferClaim.offset() + MessageHeaderEncoder.ENCODED_LENGTH)
        .orderId(orderId)
        .price(price)
        .quantity(quantity)
        .side(side);

    bufferClaim.commit();  // atomic publish
}

// SUBSCRIBE: decode from Aeron log buffer (zero-copy)
FragmentHandler handler = (buffer, offset, length, header) -> {
    headerDecoder.wrap(buffer, offset);
    int templateId = headerDecoder.templateId();
    // dispatch and wrap decoder on buffer -- no copy
    orderDecoder.wrap(buffer,
        offset + MessageHeaderDecoder.ENCODED_LENGTH,
        headerDecoder.blockLength(),
        headerDecoder.version());
    // read fields directly from Aeron's log buffer
};
subscription.poll(handler, 10);
```

The full pipeline: publisher encodes into shared-memory log buffer via SBE -> Aeron transmits (IPC or UDP) -> subscriber's FragmentHandler decodes in-place via SBE. Zero intermediate objects at every stage.

## Tradeoffs

| Advantage                        | Limitation                                       |
|----------------------------------|--------------------------------------------------|
| 10-30x faster than Protobuf     | No random field access -- must read in order      |
| Zero allocation on hot path     | Stricter schema evolution (append-only)           |
| Predictable latency (no GC)     | Larger wire size than Protobuf for sparse messages |
| Hardware prefetch friendly       | Variable data must come last; cannot skip fields  |
| Direct Aeron integration        | Not suited for general-purpose RPC                |
| Multi-language codegen           | Requires discipline in encode/decode ordering     |

## Quick Reference: Common Mistakes

1. **Reading var-data before consuming groups** -- corrupts internal cursor position
2. **Skipping a var-data field** -- all subsequent var-data reads return garbage
3. **Encoding fields out of schema order** -- undefined behavior
4. **Forgetting `actingBlockLength`/`actingVersion` in wrap** -- breaks versioning
5. **Not calling `next()` on group encoder** -- writes overwrite group header
6. **Reusing encoder without re-wrapping** -- stale offset from previous message

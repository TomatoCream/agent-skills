# Grafana Mastery for Distributed Systems Monitoring

## Stack: Java Micrometer → Prometheus → Grafana

---

## Executive Summary

This guide covers everything needed to transform bad Grafana dashboards (plain lines, no colors, bad labels, manual editing) into production-grade observability for distributed systems. It covers the full spectrum: from choosing the right panel type for each scenario, to color-coded thresholds, to dashboard hierarchy design, to dashboard-as-code via JSON/Grafonnet. Each section includes concrete PromQL queries, JSON snippets, and scenarios mapped to specific distributed system architectures (sharded + replicated, replicated, microservices, co-located).

---

## 1. Monitoring Methodologies: Know Which One to Apply

### RED Method — For Services (User-Facing)

**What it answers:** "Are my users happy?"

| Signal | What to measure | Micrometer metric | PromQL |
|--------|----------------|-------------------|--------|
| **Rate** | Requests/sec | `http_server_requests_seconds_count` | `sum(rate(http_server_requests_seconds_count[5m]))` |
| **Errors** | Failed requests/sec | `http_server_requests_seconds_count{status=~"5.."}` | `sum(rate(http_server_requests_seconds_count{status=~"5.."}[5m]))` |
| **Duration** | Latency distribution | `http_server_requests_seconds_bucket` | `histogram_quantile(0.99, sum(rate(http_server_requests_seconds_bucket[5m])) by (le))` |

**When to use:** Every service-level dashboard. This is your default.

**Dashboard layout:** Rate + Errors on left column, Duration on right column. One row per service.

### USE Method — For Infrastructure (Resources)

**What it answers:** "Are my machines healthy?"

| Signal | What to measure | Example metric | PromQL |
|--------|----------------|---------------|--------|
| **Utilization** | % time busy | `system_cpu_usage` | `system_cpu_usage{instance="$instance"}` |
| **Saturation** | Queue depth / backlog | `jvm_threads_states_threads{state="blocked"}` | `sum(jvm_threads_states_threads{state="blocked"})` |
| **Errors** | Error events | `logback_events_total{level="error"}` | `rate(logback_events_total{level="error"}[5m])` |

**When to use:** JVM dashboards, host-level dashboards, database connection pool dashboards.

### Four Golden Signals — For SRE

Latency, Traffic, Errors, Saturation. This is the superset — use it when building the top-level "are we on fire?" dashboard.

### Which Method for Which Architecture

| Architecture | Primary Method | Secondary |
|-------------|---------------|-----------|
| Sharded + Replicated (your 8x2) | RED per partition + USE per instance | Golden Signals for overview |
| Replicated (stateless) | RED aggregate + per-instance comparison | USE for capacity planning |
| Microservices | RED per service, trace-driven | USE for bottleneck services |
| Co-located (IPC) | USE per host + RED per service | Noisy neighbor detection |

---

## 2. Dashboard Hierarchy: The Three-Level Pattern

Never put everything on one dashboard. Use drill-down.

### Level 1: Fleet Overview (The "War Room" Dashboard)

**Purpose:** Is anything on fire? Glanceable in 2 seconds.

**Panel types to use:**
- **Stat panels** with colored backgrounds for each partition/service
- **Status history** panels showing health over time
- **Table** with color-coded cells for multi-dimensional overview

**Example: 8-Partition Overview**

```
┌─────────────────────────────────────────────────┐
│  [Stat] Total QPS   [Stat] Error Rate  [Stat] P99│
│  (green/red bg)     (green/red bg)     (green/red)│
├─────────────────────────────────────────────────┤
│  Partition Health (8 stat panels, repeated)       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│  │ P-0  │ │ P-1  │ │ P-2  │ │ P-3  │            │
│  │ 245  │ │ 312  │ │ 289  │ │ 301  │  QPS       │
│  │(green)│ │(green)│ │(yellow)│ │(green)│          │
│  ├──────┤ ├──────┤ ├──────┤ ├──────┤            │
│  │ P-4  │ │ P-5  │ │ P-6  │ │ P-7  │            │
│  │ 278  │ │ 295  │ │ 0    │ │ 310  │            │
│  │(green)│ │(green)│ │(RED) │ │(green)│           │
│  └──────┘ └──────┘ └──────┘ └──────┘            │
├─────────────────────────────────────────────────┤
│  [Status History] Partition availability timeline │
│  P-0: ████████████████████████████████████ green  │
│  P-1: ████████████████████████████████████ green  │
│  P-6: ████████████████████░░░░████████████ red    │
└─────────────────────────────────────────────────┘
```

**Key techniques:**
- Stat panels with `colorMode: "background"` — the whole panel turns green/yellow/red
- Repeat panels by `$partition` variable — create ONE panel, Grafana replicates it 8 times
- Status history panel to show health over time (green blocks = up, red = down)
- Link each stat panel to the Level 2 dashboard for that partition

### Level 2: Partition/Service Detail

**Purpose:** What's happening in this specific partition/service?

**Panel types to use:**
- **Time series** for rate, latency, errors over time
- **Heatmap** for latency distribution
- **Gauge** for resource utilization (CPU, memory, connections)
- **Bar gauge** for comparing replicas side-by-side

**Example: Partition Detail Dashboard**

```
┌──────────────────────┬──────────────────────┐
│  [Time Series]       │  [Heatmap]           │
│  Request Rate        │  Latency Distribution│
│  (2 lines: replica   │  (shows where        │
│   A vs replica B)    │   requests cluster)  │
├──────────────────────┼──────────────────────┤
│  [Time Series]       │  [Time Series]       │
│  Error Rate          │  P50 / P95 / P99     │
│  (red fill for       │  (3 lines, different │
│   errors)            │   colors)            │
├──────────────────────┴──────────────────────┤
│  Replica Comparison                          │
│  ┌──────────────────┬──────────────────┐    │
│  │  [Gauge] CPU     │  [Gauge] CPU     │    │
│  │  Replica A: 45%  │  Replica B: 72%  │    │
│  │  (green)         │  (yellow)        │    │
│  ├──────────────────┼──────────────────┤    │
│  │  [Gauge] Memory  │  [Gauge] Memory  │    │
│  │  Replica A: 60%  │  Replica B: 61%  │    │
│  │  (yellow)        │  (yellow)        │    │
│  └──────────────────┴──────────────────┘    │
└──────────────────────────────────────────────┘
```

**Key techniques:**
- Template variable `$partition` filters all panels
- Use **overrides** to color replica A and replica B differently
- Heatmap for latency reveals bimodal distributions that P99 alone hides
- Gauges with thresholds for resource utilization (green < 60%, yellow < 80%, red >= 80%)

### Level 3: Instance Detail (JVM Deep Dive)

**Purpose:** Debug a specific instance.

**Panel types:** Time series for GC, heap, thread pools, connection pools. Use the standard JVM Micrometer dashboard (Grafana ID: 4701) as a starting point and customize.

---

## 3. Panel Type Selection Guide

### When to Use Each Panel Type

| Panel Type | Use When | Never Use When | Scenario |
|-----------|----------|---------------|----------|
| **Stat** | Single KPI, health check, count | Showing trends over time | Overview dashboard: total QPS, error count |
| **Gauge** | Value within known bounds (0-100%) | Value has no meaningful max | CPU %, memory %, disk %, connection pool usage |
| **Time Series** | Showing change over time | Comparing categories | Request rate trend, latency over time |
| **Heatmap** | Distribution over time | Small number of discrete values | Latency distribution, request size distribution |
| **Bar Gauge** | Comparing discrete items | More than 15 items | Comparing partitions, top-N endpoints |
| **Table** | Multi-dimensional data, raw values | When a chart would be clearer | Instance list with status, endpoint breakdown |
| **Status History** | Discrete state changes over time | Continuous numeric data | Service up/down over time, deployment status |
| **State Timeline** | Showing state duration | Numeric metrics | Instance lifecycle (starting, running, draining) |
| **Pie Chart** | Proportions (error breakdown) | More than 7 segments | Error types: 500 vs 502 vs 503 vs timeout |
| **Bar Chart** | Category comparison | Time series data | QPS by endpoint, errors by partition |
| **Node Graph** | Service dependencies | Simple metrics | Microservice call graph |

### Common Mistakes to Avoid

| Bad Practice | Why It's Bad | Better Alternative |
|-------------|-------------|-------------------|
| Time series for everything | Lines hide the story | Stat for KPIs, Heatmap for distributions |
| No thresholds on gauges | No visual meaning, just a number | Add green/yellow/red thresholds |
| Stacking area charts | Hides individual series, misleading | Separate lines or use a table |
| Too many series on one chart | Spaghetti, unreadable | Use template variables to filter, or top-N |
| Plain white/default colors | Cannot tell good from bad at a glance | Threshold-based coloring |

---

## 4. Color, Thresholds, and Visual Meaning

### Threshold Configuration

Thresholds are the single most impactful improvement you can make. They turn "a number" into "is this good or bad?"

**Standard threshold pattern (JSON):**

```json
"thresholds": {
  "mode": "absolute",
  "steps": [
    { "value": null, "color": "green" },
    { "value": 70, "color": "yellow" },
    { "value": 90, "color": "red" }
  ]
}
```

**Common threshold recipes:**

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| CPU usage | < 60% | 60-80% | > 80% |
| Memory usage | < 70% | 70-85% | > 85% |
| Error rate | < 1% | 1-5% | > 5% |
| P99 latency (ms) | < 200 | 200-500 | > 500 |
| Connection pool usage | < 70% | 70-90% | > 90% |
| Disk usage | < 70% | 70-85% | > 85% |
| Queue depth | < 100 | 100-500 | > 500 |
| Request rate (low = bad) | > 100 | 50-100 | < 50 |

**For "lower is worse" metrics (e.g., throughput dropping):** Reverse the threshold order.

### Color Modes

| Color Mode | Where to Use | JSON |
|-----------|-------------|------|
| `"background"` | Stat panels — whole panel turns color | `"options": { "colorMode": "background" }` |
| `"value"` | Stat panels — only the number changes color | `"options": { "colorMode": "value" }` |
| `"thresholds"` | Time series — line color changes at threshold | `"color": { "mode": "thresholds" }` |
| `"fixed"` | Override a specific series to always be one color | `"color": { "mode": "fixed", "fixedColor": "blue" }` |
| `"palette-classic"` | Multiple series, auto-assigned colors | `"color": { "mode": "palette-classic" }` |

### Value Mappings

Transform raw numbers into meaningful text with color.

**Example: Service health status**

```json
"mappings": [
  {
    "type": "value",
    "options": {
      "0": { "text": "DOWN", "color": "red" },
      "1": { "text": "UP", "color": "green" }
    }
  }
]
```

**Example: Range-based status**

```json
"mappings": [
  {
    "type": "range",
    "options": {
      "from": 0, "to": 0.01,
      "result": { "text": "HEALTHY", "color": "green" }
    }
  },
  {
    "type": "range",
    "options": {
      "from": 0.01, "to": 0.05,
      "result": { "text": "DEGRADED", "color": "yellow" }
    }
  },
  {
    "type": "range",
    "options": {
      "from": 0.05, "to": 1,
      "result": { "text": "CRITICAL", "color": "red" }
    }
  }
]
```

**Example: Null/empty handling**

```json
"mappings": [
  {
    "type": "special",
    "options": {
      "match": "null",
      "result": { "text": "NO DATA", "color": "gray" }
    }
  }
]
```

### Field Overrides — Per-Series Styling

Override specific series to have distinct visual treatment.

**Color errors red, success green (by query):**

```json
"overrides": [
  {
    "matcher": { "id": "byFrameRefID", "options": "A" },
    "properties": [
      { "id": "color", "value": { "fixedColor": "green", "mode": "fixed" } },
      { "id": "custom.fillOpacity", "value": 10 }
    ]
  },
  {
    "matcher": { "id": "byFrameRefID", "options": "B" },
    "properties": [
      { "id": "color", "value": { "fixedColor": "red", "mode": "fixed" } },
      { "id": "custom.fillOpacity", "value": 20 }
    ]
  }
]
```

**Match by series name regex (e.g., all error series):**

```json
"overrides": [
  {
    "matcher": { "id": "byRegexp", "options": ".*error.*" },
    "properties": [
      { "id": "color", "value": { "fixedColor": "red", "mode": "fixed" } },
      { "id": "custom.lineWidth", "value": 2 }
    ]
  }
]
```

### Threshold Display on Time Series

Show thresholds as visual lines or filled regions on graphs:

```json
"fieldConfig": {
  "defaults": {
    "custom": {
      "thresholdsStyle": {
        "mode": "line+area"
      }
    },
    "thresholds": {
      "mode": "absolute",
      "steps": [
        { "value": null, "color": "transparent" },
        { "value": 500, "color": "red" }
      ]
    }
  }
}
```

This draws a red line at 500ms and fills the area above it — instant visual indicator of SLA breach.

---

## 5. Template Variables: Build Once, Filter Everywhere

### Variable Hierarchy for Sharded + Replicated Architecture

```json
"templating": {
  "list": [
    {
      "name": "service",
      "type": "query",
      "query": "label_values(http_server_requests_seconds_count, service)",
      "refresh": 2,
      "multi": false
    },
    {
      "name": "partition",
      "type": "query",
      "query": "label_values(http_server_requests_seconds_count{service=\"$service\"}, partition)",
      "refresh": 2,
      "multi": true,
      "includeAll": true
    },
    {
      "name": "instance",
      "type": "query",
      "query": "label_values(http_server_requests_seconds_count{service=\"$service\", partition=\"$partition\"}, instance)",
      "refresh": 2,
      "multi": true,
      "includeAll": true
    }
  ]
}
```

**Key settings:**
- `refresh: 2` = refresh on time range change
- `multi: true` = allow selecting multiple values
- `includeAll: true` = "All" option to see everything
- Variables chain: service → partition → instance (dependent filtering)

### Repeat Panels by Variable

Create ONE panel, Grafana duplicates it for each variable value:

```json
{
  "type": "stat",
  "title": "QPS - Partition $partition",
  "repeat": "partition",
  "repeatDirection": "h",
  "maxPerRow": 4,
  "targets": [{
    "expr": "sum(rate(http_server_requests_seconds_count{partition=\"$partition\"}[5m]))"
  }]
}
```

This creates 8 stat panels (one per partition), 4 per row.

**Repeat rows** for grouped panels:

```json
{
  "type": "row",
  "title": "Partition $partition",
  "repeat": "partition",
  "collapsed": true,
  "panels": [
    { "title": "Request Rate", "..." : "..." },
    { "title": "Latency", "..." : "..." },
    { "title": "Errors", "..." : "..." }
  ]
}
```

This creates a collapsible row per partition, each containing Rate/Latency/Error panels.

### Performance Warning

Repeating panels multiplies queries. 8 partitions × 4 panels × 2 queries = 64 queries. Use `$__rate_interval` and avoid expensive regex. Consider using recording rules in Prometheus for heavy queries.

---

## 6. PromQL Patterns for Each Architecture

### Sharded + Replicated (Your 8 Partitions × 2 Replicas)

```promql
# Total QPS across all partitions
sum(rate(http_server_requests_seconds_count{service="my-service"}[$__rate_interval]))

# QPS per partition (for bar chart or repeated stat)
sum by (partition)(rate(http_server_requests_seconds_count{service="my-service"}[$__rate_interval]))

# Compare replicas within one partition (for time series overlay)
sum by (instance)(rate(http_server_requests_seconds_count{service="my-service", partition="$partition"}[$__rate_interval]))

# Error rate per partition (percentage)
sum by (partition)(rate(http_server_requests_seconds_count{service="my-service", status=~"5.."}[$__rate_interval]))
/
sum by (partition)(rate(http_server_requests_seconds_count{service="my-service"}[$__rate_interval]))
* 100

# Detect hot partition (partition handling >20% more than average)
sum by (partition)(rate(http_server_requests_seconds_count{service="my-service"}[$__rate_interval]))
> 1.2 * avg(sum by (partition)(rate(http_server_requests_seconds_count{service="my-service"}[$__rate_interval])))

# Detect replica drift (one replica doing significantly less work)
sum by (instance)(rate(http_server_requests_seconds_count{partition="$partition"}[$__rate_interval]))
< 0.5 * avg(sum by (instance)(rate(http_server_requests_seconds_count{partition="$partition"}[$__rate_interval])))

# Latency heatmap (for heatmap panel, format: heatmap)
sum(rate(http_server_requests_seconds_bucket{partition="$partition"}[$__rate_interval])) by (le)

# P99 latency per partition
histogram_quantile(0.99, sum by (partition, le)(rate(http_server_requests_seconds_bucket{service="my-service"}[$__rate_interval])))
```

### Replicated (Stateless, Load-Balanced)

```promql
# Total QPS
sum(rate(http_server_requests_seconds_count{service="my-service"}[$__rate_interval]))

# Per-instance QPS (detect uneven load balancing)
sum by (instance)(rate(http_server_requests_seconds_count{service="my-service"}[$__rate_interval]))

# Instance count (for stat panel)
count(up{service="my-service"} == 1)

# SLO: % of requests under 500ms
sum(rate(http_server_requests_seconds_bucket{le="0.5", service="my-service"}[$__rate_interval]))
/
sum(rate(http_server_requests_seconds_count{service="my-service"}[$__rate_interval]))
* 100
```

### Microservices (Inter-Service)

```promql
# Per-service error rate (for table with color)
sum by (service)(rate(http_server_requests_seconds_count{status=~"5.."}[$__rate_interval]))
/
sum by (service)(rate(http_server_requests_seconds_count[$__rate_interval]))
* 100

# Upstream dependency latency
histogram_quantile(0.99, sum by (le, target_service)(rate(http_client_requests_seconds_bucket[$__rate_interval])))

# Circuit breaker state (if using Resilience4j)
resilience4j_circuitbreaker_state{service="$service"}
```

### JVM / Micrometer Common Metrics

```promql
# Heap usage percentage
jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} * 100

# GC pause time
rate(jvm_gc_pause_seconds_sum[$__rate_interval])

# Thread pool utilization
hikaricp_connections_active / hikaricp_connections_max * 100

# Active threads
jvm_threads_live_threads
```

---

## 7. Annotations: Correlate Events with Metrics

### Deployment Markers

Add annotations to show when deployments happened — critical for correlating metric changes.

**Annotation query (Prometheus-based):**

```json
"annotations": {
  "list": [{
    "name": "Deployments",
    "datasource": { "type": "prometheus", "uid": "prometheus" },
    "enable": true,
    "iconColor": "purple",
    "expr": "changes(deployment_timestamp_seconds{service=\"$service\"}[1m]) > 0",
    "tagKeys": "service,version",
    "textFormat": "Deployed {{version}}"
  }]
}
```

**CI/CD integration (curl to Grafana API):**

```bash
curl -X POST http://grafana:3000/api/annotations \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboardUID": "my-dashboard",
    "time": '$(date +%s000)',
    "tags": ["deploy", "my-service", "v2.3.1"],
    "text": "Deployed my-service v2.3.1"
  }'
```

### Other Useful Annotations

- **Alerts fired** — built-in, enable in annotation settings
- **Scaling events** — when instances scale up/down
- **Config changes** — when config maps or feature flags change
- **Incidents** — manual markers for postmortem correlation

---

## 8. Naming Conventions

### Dashboard Naming

```
[Level] - [Architecture] - [Service/Component]
```

Examples:
- `L1 - Fleet Overview - All Services`
- `L2 - Partition Detail - Order Service`
- `L3 - Instance JVM - Order Service`

### Panel Titles

**Bad:** `Graph`, `Panel 1`, `Untitled`, `http requests`

**Good:** Format: `[What] — [Unit/Context]`
- `Request Rate — req/s by partition`
- `P99 Latency — ms`
- `Error Rate — % of total requests`
- `Heap Usage — % of max`
- `Connection Pool — active / max`

### Panel Descriptions

Every panel should have a description (hover info icon). Include:
- What the metric means
- What "good" looks like
- What to do if it's red

Example description for an error rate panel:
```
Percentage of HTTP 5xx responses out of total requests.
- Green (< 1%): Normal operation
- Yellow (1-5%): Investigate — check logs for the affected partition
- Red (> 5%): Escalate — possible service degradation
```

### Legend Format

Use `legendFormat` to make series labels meaningful:

| Bad | Good |
|-----|------|
| `{instance="10.0.1.23:8080"}` | `{{partition}}-{{instance}}` → `P3-replica-a` |
| `{__name__="http_server..."}` | `{{method}} {{uri}}` → `GET /api/orders` |
| `{job="my-service"}` | `{{status}}` → `200`, `500` |

---

## 9. Dashboard-as-Code: Stop Manual Editing

### Why

- Version control (git)
- Code review for dashboard changes
- Reproducible across environments
- Reusable patterns (DRY)
- No more "who broke the dashboard?"

### Approach 1: JSON Files + Provisioning

Store dashboard JSON in git. Grafana auto-loads from a provisioning directory.

**Provisioning config (`/etc/grafana/provisioning/dashboards/default.yaml`):**

```yaml
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: 'Production'
    type: file
    disableDeletion: true
    editable: false
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

**`editable: false`** prevents UI edits to provisioned dashboards — forces all changes through code.

### Approach 2: Grafonnet (Jsonnet Library)

Write dashboards in Jsonnet, compile to JSON.

```jsonnet
local grafana = import 'grafonnet/grafana.libsonnet';
local dashboard = grafana.dashboard;
local prometheus = grafana.prometheus;
local timeseries = grafana.timeseries;

dashboard.new('L2 - Partition Detail')
+ dashboard.withVariables([
    grafana.variable.query.new('partition', 'label_values(http_server_requests_seconds_count, partition)')
  ])
+ dashboard.withPanels([
    timeseries.new('Request Rate')
    + timeseries.withTargets([
        prometheus.new('sum by (instance)(rate(http_server_requests_seconds_count{partition="$partition"}[$__rate_interval]))')
      ])
    + timeseries.fieldConfig.defaults.thresholds.withSteps([
        { value: null, color: 'green' },
        { value: 1000, color: 'red' },
      ])
  ])
```

**Advantages over raw JSON:**
- ~90 lines of Jsonnet = ~350 lines of JSON
- Functions for reusable panel patterns
- Compile-time validation

### Approach 3: grafanalib (Python)

If your team knows Python better than Jsonnet:

```python
from grafanalib.core import Dashboard, TimeSeries, Target

dashboard = Dashboard(
    title="L2 - Partition Detail",
    panels=[
        TimeSeries(
            title="Request Rate",
            targets=[
                Target(expr='sum by (instance)(rate(http_server_requests_seconds_count{partition="$partition"}[$__rate_interval]))'),
            ],
        ),
    ],
)
```

---

## 10. Complete Scenario Recipes

### Scenario A: Sharded + Replicated (8 Partitions × 2 Replicas)

**L1 Overview Dashboard:**

| Row | Panels | Type | Purpose |
|-----|--------|------|---------|
| Header | Total QPS, Total Error Rate, Overall P99 | 3× Stat (background color) | Instant health |
| Partition Grid | QPS per partition | 8× Stat (repeat by `$partition`) | Spot dead/hot partition |
| Error Grid | Error rate per partition | 8× Stat (repeat by `$partition`) | Spot failing partition |
| Timeline | Partition health over time | Status History | Availability history |
| Distribution | QPS distribution across partitions | Bar Chart | Spot imbalance |

**L2 Partition Detail:**

| Row | Panels | Type | Purpose |
|-----|--------|------|---------|
| RED Summary | Rate, Errors, Duration | 3× Stat | Partition KPIs |
| Rate | Request rate by replica | Time Series (2 lines) | Replica comparison |
| Latency | Latency heatmap | Heatmap | Distribution visibility |
| Latency Lines | P50, P95, P99 | Time Series (3 lines) | Percentile trends |
| Errors | Error rate + types | Time Series + Pie | Error detail |
| Resources | CPU, Memory, Connections | 2× Gauge per replica | Resource health |
| Replica Drift | Ratio of replica A / replica B work | Time Series | Detect imbalance |

### Scenario B: Replicated Stateless Services

**L1 Overview:**

| Row | Panels | Type | Purpose |
|-----|--------|------|---------|
| KPIs | QPS, Errors, P99, Instance Count | 4× Stat | Health at a glance |
| Per-Instance | QPS per instance | Bar Gauge (horizontal) | Load distribution |
| Timeline | Service health | Status History | Uptime visualization |

**L2 Service Detail:**

| Row | Panels | Type | Purpose |
|-----|--------|------|---------|
| Rate | Total + per-instance QPS | Time Series | Traffic patterns |
| Latency | Heatmap + percentile lines | Heatmap + Time Series | Full latency picture |
| SLO | % requests within SLO | Gauge (threshold at 99.9%) | SLO tracking |
| Scaling | Instance count over time | Time Series | Capacity correlation |

### Scenario C: Microservices

**L1 Service Map Overview:**

| Row | Panels | Type | Purpose |
|-----|--------|------|---------|
| Service Grid | Error rate per service | Table (color cells) | Red rows = problems |
| Dependencies | Service call graph | Node Graph | Topology view |
| Latency Ranking | P99 by service | Bar Gauge (sorted) | Slowest services |

**L2 Service Detail:**

| Row | Panels | Type | Purpose |
|-----|--------|------|---------|
| RED | Rate, Errors, Duration | Time Series trio | Standard RED layout |
| Upstream | Dependency latency | Time Series per dependency | Blame the right service |
| Circuit Breaker | CB state over time | State Timeline | Open/closed/half-open |

### Scenario D: Co-located Services (IPC)

**L1 Host Overview:**

| Row | Panels | Type | Purpose |
|-----|--------|------|---------|
| Host Health | CPU, Memory per host | Stat grid (repeat by host) | Spot overloaded hosts |
| Noisy Neighbor | CPU stacked by service per host | Time Series (stacked) | Identify resource hog |

**L2 Host Detail:**

| Row | Panels | Type | Purpose |
|-----|--------|------|---------|
| Resource Split | CPU by service | Pie Chart | Proportion view |
| Service RED | Rate/Error/Duration per service on this host | Time Series | Per-service health |
| IPC | IPC latency between services | Heatmap | Communication health |

---

## 11. JSON Snippets Library

### Complete Stat Panel with Background Color + Thresholds

```json
{
  "id": 1,
  "type": "stat",
  "title": "Error Rate — %",
  "description": "HTTP 5xx as percentage of total. Green < 1%, Yellow < 5%, Red >= 5%.",
  "gridPos": { "x": 0, "y": 0, "w": 6, "h": 4 },
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [{
    "refId": "A",
    "expr": "sum(rate(http_server_requests_seconds_count{service=\"$service\", status=~\"5..\"}[$__rate_interval])) / sum(rate(http_server_requests_seconds_count{service=\"$service\"}[$__rate_interval])) * 100",
    "legendFormat": "Error %"
  }],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "decimals": 2,
      "color": { "mode": "thresholds" },
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "value": null, "color": "green" },
          { "value": 1, "color": "yellow" },
          { "value": 5, "color": "red" }
        ]
      },
      "mappings": [{
        "type": "special",
        "options": {
          "match": "null",
          "result": { "text": "NO DATA", "color": "gray" }
        }
      }]
    },
    "overrides": []
  },
  "options": {
    "colorMode": "background",
    "graphMode": "area",
    "reduceOptions": { "calcs": ["lastNotNull"] },
    "textMode": "auto"
  }
}
```

### Complete Time Series with Threshold Lines + Override Colors

```json
{
  "id": 2,
  "type": "timeseries",
  "title": "Request Rate — req/s by replica",
  "description": "Request throughput per replica in partition. Lines should be roughly equal — divergence indicates replica drift.",
  "gridPos": { "x": 0, "y": 4, "w": 12, "h": 8 },
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [
    {
      "refId": "A",
      "expr": "sum by (instance)(rate(http_server_requests_seconds_count{partition=\"$partition\"}[$__rate_interval]))",
      "legendFormat": "{{instance}}"
    }
  ],
  "fieldConfig": {
    "defaults": {
      "unit": "reqps",
      "color": { "mode": "palette-classic" },
      "custom": {
        "drawStyle": "line",
        "lineWidth": 2,
        "fillOpacity": 10,
        "pointSize": 5,
        "spanNulls": false,
        "showPoints": "auto",
        "thresholdsStyle": { "mode": "line" }
      },
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "value": null, "color": "transparent" },
          { "value": 0, "color": "red" }
        ]
      }
    },
    "overrides": []
  },
  "options": {
    "legend": {
      "displayMode": "table",
      "placement": "bottom",
      "showLegend": true,
      "calcs": ["mean", "max", "last"]
    },
    "tooltip": { "mode": "multi", "sort": "desc" }
  }
}
```

### Complete Heatmap for Latency Distribution

```json
{
  "id": 3,
  "type": "heatmap",
  "title": "Latency Distribution — ms",
  "description": "Request latency distribution over time. Darker colors = more requests at that latency. Reveals bimodal distributions that percentiles hide.",
  "gridPos": { "x": 12, "y": 4, "w": 12, "h": 8 },
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [{
    "refId": "A",
    "expr": "sum(rate(http_server_requests_seconds_bucket{partition=\"$partition\"}[$__rate_interval])) by (le)",
    "legendFormat": "{{le}}",
    "format": "heatmap"
  }],
  "options": {
    "calculate": false,
    "color": {
      "mode": "scheme",
      "scheme": "Oranges",
      "steps": 64
    },
    "yAxis": {
      "unit": "s",
      "decimals": 0
    },
    "cellGap": 1,
    "tooltip": { "show": true }
  }
}
```

### Complete Gauge with Thresholds

```json
{
  "id": 4,
  "type": "gauge",
  "title": "Heap Usage — %",
  "description": "JVM heap memory usage as percentage of max. If consistently > 85%, consider increasing heap or investigating memory leaks.",
  "gridPos": { "x": 0, "y": 12, "w": 6, "h": 6 },
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [{
    "refId": "A",
    "expr": "jvm_memory_used_bytes{area=\"heap\", instance=\"$instance\"} / jvm_memory_max_bytes{area=\"heap\", instance=\"$instance\"} * 100",
    "legendFormat": "Heap %"
  }],
  "fieldConfig": {
    "defaults": {
      "unit": "percent",
      "min": 0,
      "max": 100,
      "decimals": 1,
      "color": { "mode": "thresholds" },
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "value": null, "color": "green" },
          { "value": 70, "color": "yellow" },
          { "value": 85, "color": "red" }
        ]
      }
    },
    "overrides": []
  },
  "options": {
    "reduceOptions": { "calcs": ["lastNotNull"] },
    "showThresholdLabels": false,
    "showThresholdMarkers": true
  }
}
```

### Status History for Partition Availability

```json
{
  "id": 5,
  "type": "status-history",
  "title": "Partition Availability Timeline",
  "description": "Shows each partition's health over time. Green = healthy, Red = down/errors. Look for patterns across partitions.",
  "gridPos": { "x": 0, "y": 20, "w": 24, "h": 6 },
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [{
    "refId": "A",
    "expr": "up{service=\"my-service\"} * on(partition) group_left() (1 - (sum by (partition)(rate(http_server_requests_seconds_count{status=~\"5..\"}[$__rate_interval])) / sum by (partition)(rate(http_server_requests_seconds_count[$__rate_interval])) > 0.05))",
    "legendFormat": "Partition {{partition}}"
  }],
  "fieldConfig": {
    "defaults": {
      "color": { "mode": "thresholds" },
      "thresholds": {
        "mode": "absolute",
        "steps": [
          { "value": null, "color": "red" },
          { "value": 1, "color": "green" }
        ]
      },
      "mappings": [
        { "type": "value", "options": { "0": { "text": "DOWN", "color": "red" } } },
        { "type": "value", "options": { "1": { "text": "UP", "color": "green" } } }
      ]
    }
  }
}
```

### Table with Color-Coded Cells

```json
{
  "id": 6,
  "type": "table",
  "title": "Service Health Matrix",
  "description": "All services at a glance. Cells colored by health. Click service name to drill down.",
  "gridPos": { "x": 0, "y": 26, "w": 24, "h": 8 },
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "targets": [
    {
      "refId": "A",
      "expr": "sum by (service)(rate(http_server_requests_seconds_count[$__rate_interval]))",
      "legendFormat": "QPS",
      "format": "table",
      "instant": true
    },
    {
      "refId": "B",
      "expr": "sum by (service)(rate(http_server_requests_seconds_count{status=~\"5..\"}[$__rate_interval])) / sum by (service)(rate(http_server_requests_seconds_count[$__rate_interval])) * 100",
      "legendFormat": "Error %",
      "format": "table",
      "instant": true
    }
  ],
  "fieldConfig": {
    "defaults": {},
    "overrides": [
      {
        "matcher": { "id": "byName", "options": "Error %" },
        "properties": [
          { "id": "unit", "value": "percent" },
          { "id": "decimals", "value": 2 },
          {
            "id": "thresholds",
            "value": {
              "mode": "absolute",
              "steps": [
                { "value": null, "color": "green" },
                { "value": 1, "color": "yellow" },
                { "value": 5, "color": "red" }
              ]
            }
          },
          { "id": "custom.cellOptions", "value": { "type": "color-background" } }
        ]
      }
    ]
  }
}
```

---

## 12. Alerting Visualization Best Practices

### Alert on Symptoms (RED), Not Causes (USE)

- **Good alert:** Error rate > 5% for 5 minutes (symptom — users affected)
- **Bad alert:** CPU > 80% (cause — might not affect users)

### Alert Annotations on Dashboards

Enable the built-in alert annotation to show when alerts fired as vertical markers on time series panels. This is critical for postmortem correlation.

### Contact Points Hierarchy

| Severity | Channel | Condition |
|----------|---------|-----------|
| Critical (P1) | PagerDuty / Phone | Error rate > 10% for 2m |
| Warning (P2) | Slack channel | Error rate > 5% for 5m |
| Info (P3) | Slack / Email | Approaching capacity (> 80%) |

---

## 13. Micrometer-Specific Tips

### Common Tags (Set Once, Applied Everywhere)

```java
@Configuration
public class MicrometerConfig {
    @Bean
    MeterRegistryCustomizer<MeterRegistry> commonTags(
            @Value("${app.partition}") String partition,
            @Value("${app.instance-id}") String instanceId) {
        return registry -> registry.config().commonTags(
            "service", "order-service",
            "partition", partition,
            "instance", instanceId
        );
    }
}
```

### Avoid High Cardinality

**Bad tags** (creates metric explosion):
- `userId`, `sessionId`, `requestId`, `traceId`
- `uri` with path parameters: `/users/12345` (use `/users/{id}` instead)

**Good tags:**
- `service`, `partition`, `instance`, `method`, `status`, `uri` (templated)

### Custom Business Metrics

```java
// Counter — things that only go up
registry.counter("orders.placed", "partition", partition).increment();

// Timer — duration of operations
Timer.builder("order.processing.time")
    .tag("partition", partition)
    .tag("type", orderType)
    .register(registry)
    .record(duration);

// Gauge — current value
Gauge.builder("queue.depth", queue, Queue::size)
    .tag("partition", partition)
    .register(registry);
```

### Histogram Buckets for Latency

Configure meaningful buckets in `application.yml`:

```yaml
management:
  metrics:
    distribution:
      percentiles-histogram:
        http.server.requests: true
      sla:
        http.server.requests: 50ms, 100ms, 200ms, 500ms, 1s, 5s
      percentiles:
        http.server.requests: 0.5, 0.95, 0.99
```

---

## 14. Dashboard Maturity Model

### Level 0: Chaos (Where You Are Now)

- All plain time series lines
- No thresholds or colors
- Bad/default panel names
- No descriptions
- Manual editing in UI or raw JSON
- No template variables
- No dashboard hierarchy

### Level 1: Functional

- [ ] Thresholds on all stat and gauge panels
- [ ] Meaningful panel titles and descriptions
- [ ] Template variables for filtering (service, partition, instance)
- [ ] Dashboard links for drill-down
- [ ] legendFormat customized per panel
- [ ] Correct panel types (not all time series)

### Level 2: Professional

- [ ] Three-level dashboard hierarchy (overview → detail → instance)
- [ ] Repeat panels by partition/instance
- [ ] Heatmaps for latency
- [ ] Status history for availability
- [ ] Deployment annotations
- [ ] Overrides for per-series coloring
- [ ] Value mappings for status indicators
- [ ] Panel descriptions explaining what to do when red

### Level 3: Excellent

- [ ] Dashboard-as-code (Grafonnet or JSON in git)
- [ ] Automated deployment annotations from CI/CD
- [ ] Recording rules for expensive queries
- [ ] Alert-driven navigation (alerts link to right dashboard)
- [ ] SLO tracking panels
- [ ] No browser-based editing of production dashboards
- [ ] Regular dashboard review cadence

---

## 15. Quick Reference: Feature → JSON Key

| Feature | JSON Path |
|---------|-----------|
| Panel type | `type` |
| Panel position | `gridPos: { x, y, w, h }` |
| Query | `targets[].expr` |
| Legend label | `targets[].legendFormat` |
| Thresholds | `fieldConfig.defaults.thresholds.steps[]` |
| Color mode | `fieldConfig.defaults.color.mode` |
| Background color | `options.colorMode: "background"` |
| Value mappings | `fieldConfig.defaults.mappings[]` |
| Field overrides | `fieldConfig.overrides[]` |
| Override matcher | `fieldConfig.overrides[].matcher.id` (byName, byRegexp, byFrameRefID) |
| Line style | `fieldConfig.defaults.custom.drawStyle` |
| Fill opacity | `fieldConfig.defaults.custom.fillOpacity` |
| Threshold on graph | `fieldConfig.defaults.custom.thresholdsStyle.mode` |
| Repeat by variable | `repeat: "variableName"` |
| Repeat direction | `repeatDirection: "h"` or `"v"` |
| Max per row | `maxPerRow: 4` |
| Template variable | `templating.list[]` |
| Annotation | `annotations.list[]` |
| Tooltip mode | `options.tooltip.mode` ("single", "multi", "none") |
| Legend placement | `options.legend.placement` ("bottom", "right") |
| Legend calcs | `options.legend.calcs` (["mean", "max", "last"]) |
| Unit | `fieldConfig.defaults.unit` |
| Decimals | `fieldConfig.defaults.decimals` |
| Dashboard refresh | `refresh: "30s"` |
| Time range | `time: { from: "now-1h", to: "now" }` |

---

## Sources

- Grafana Official Documentation: Dashboard Best Practices
- Grafana Blog: The RED Method by Tom Wilkie
- Grafana Documentation: Thresholds, Value Mappings, Field Overrides, Panel Types
- Google SRE Book, Chapter 6: Monitoring Distributed Systems
- Brendan Gregg: The USE Method
- Grafana Community: Template Variables, Repeating Panels
- Grafana Blog: How to Visualize Prometheus Histograms
- Grafana Labs: JVM Micrometer Dashboard Templates

---
name: improving-grafana-dashboards
description: Use when reviewing, improving, or creating Grafana dashboards for distributed systems. Triggers on bad dashboards (plain lines, no colors, wrong panel types, bad labels), dashboard JSON review, PromQL optimization, Micrometer instrumentation, or building new monitoring for sharded, replicated, or microservice architectures. Also use when user says "grafana", "dashboard", "monitoring", "observability", "metrics visualization", or asks about panel types, thresholds, heatmaps, or template variables.
---

# Improving Grafana Dashboards for Distributed Systems

## Overview

Diagnose and fix bad Grafana dashboards. Transform plain-line, colorless, badly-labeled dashboards into production-grade observability. Covers the full stack: Micrometer tags, PromQL queries, panel selection, thresholds, colors, naming, hierarchy, and dashboard-as-code.

## When to Use

- Reviewing existing Grafana dashboard JSON for improvements
- Creating new dashboards for distributed systems
- Fixing dashboards that "don't indicate problems well"
- Choosing panel types, colors, thresholds for a monitoring scenario
- Writing PromQL queries for Micrometer/Prometheus metrics
- Designing dashboard hierarchy for sharded/replicated/microservice architectures
- Moving from manual UI editing to dashboard-as-code

When NOT to use: Grafana installation/infrastructure setup, alerting rule logic (use Prometheus alertmanager docs), log-based dashboards (Loki-specific).

## Diagnosis Flowchart

```
Dashboard Review
├── All plain time series lines?
│   └── Fix: Choose correct panel types (see Panel Selection)
├── No colors / all default white?
│   └── Fix: Add thresholds + colorMode (see Thresholds)
├── Bad/generic panel names?
│   └── Fix: "[What] — [Unit/Context]" pattern (see Naming)
├── No descriptions on panels?
│   └── Fix: Add what-good-looks-like + what-to-do-when-red
├── No template variables / separate dashboard per instance?
│   └── Fix: Add $service → $partition → $instance chain
├── Everything on one dashboard?
│   └── Fix: Three-level hierarchy (see Dashboard Hierarchy)
├── Can't tell good from bad at a glance?
│   └── Fix: Stat panels with background color + value mappings
├── Latency shown only as P99 line?
│   └── Fix: Add heatmap (reveals distributions P99 hides)
├── Manual UI editing / no version control?
│   └── Fix: Dashboard-as-code (JSON provisioning or Grafonnet)
└── Spaghetti chart (too many series)?
    └── Fix: Template variables to filter, or top-N query
```

## Priority Order (Highest Impact First)

1. **Thresholds + colors** — instant "is this good or bad?" signal
2. **Panel type selection** — right visualization for the data
3. **Naming + descriptions** — self-documenting dashboards
4. **Template variables** — eliminate dashboard sprawl
5. **Dashboard hierarchy** — overview → detail → instance drill-down
6. **Heatmaps for latency** — reveal what percentiles hide
7. **Annotations** — correlate deployments with metric changes
8. **Dashboard-as-code** — version control, reproducibility

## Quick Reference: Panel Type Selection

| Data Type | Panel | Key Config |
|-----------|-------|------------|
| Single KPI (QPS, error rate) | **Stat** | `colorMode: "background"`, thresholds |
| Bounded value (CPU %, memory %) | **Gauge** | `min: 0, max: 100`, thresholds |
| Metric over time | **Time Series** | `thresholdsStyle.mode: "line"` |
| Latency distribution | **Heatmap** | `format: "heatmap"`, color scheme |
| Comparing items (partitions) | **Bar Gauge** | Horizontal, sorted |
| Multi-dimensional overview | **Table** | `cellOptions: "color-background"` |
| Up/down over time | **Status History** | Value mappings: 0=DOWN/red, 1=UP/green |
| State duration | **State Timeline** | For lifecycle states |
| Proportions (< 7 items) | **Pie Chart** | Error type breakdown |

## Quick Reference: Threshold Recipes

| Metric | Green | Yellow | Red |
|--------|-------|--------|-----|
| CPU | < 60% | 60-80% | > 80% |
| Memory | < 70% | 70-85% | > 85% |
| Error rate | < 1% | 1-5% | > 5% |
| P99 latency | < 200ms | 200-500ms | > 500ms |
| Connection pool | < 70% | 70-90% | > 90% |
| Disk | < 70% | 70-85% | > 85% |

## Quick Reference: Monitoring Method by Architecture

| Architecture | Method | Key Concern |
|-------------|--------|-------------|
| Sharded + replicated | RED per partition + USE per instance | Hot partitions, replica drift |
| Replicated stateless | RED aggregate + per-instance comparison | Load balance evenness |
| Microservices | RED per service | Inter-service latency, cascading failure |
| Co-located (IPC) | USE per host + RED per service | Noisy neighbor |

## Quick Reference: Naming

**Dashboard:** `[Level] - [Architecture] - [Service]` (e.g., `L1 - Fleet Overview - All Services`)

**Panel title:** `[What] — [Unit/Context]` (e.g., `Error Rate — % of total requests`)

**Panel description:** What it means + what good looks like + what to do when red.

**Legend:** `{{partition}}-{{instance}}` not `{instance="10.0.1.23:8080"}`

## Detailed Reference

For JSON snippets, complete PromQL patterns, dashboard layout recipes, Micrometer configuration, and full scenario walkthroughs: see [reference.md](reference.md).

Key sections in reference:
- **Section 4:** Color modes, value mappings, field overrides with JSON
- **Section 5:** Template variable hierarchy with JSON
- **Section 6:** PromQL for each architecture type
- **Section 10:** Complete dashboard recipes per scenario
- **Section 11:** Copy-paste JSON snippets for every panel type
- **Section 13:** Micrometer common tags, cardinality, histogram config
- **Section 14:** Dashboard maturity model checklist (Level 0→3)
- **Section 15:** Feature → JSON key quick lookup

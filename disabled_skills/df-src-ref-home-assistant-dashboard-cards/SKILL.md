---
name: df-src-ref-home-assistant-dashboard-cards
description: |
  Complete YAML reference for Home Assistant dashboard cards. Use this skill whenever working with Home Assistant dashboards, Lovelace UI, or any Home Assistant card configuration. Trigger on mentions of "Home Assistant dashboard", "Lovelace card", "HA card YAML", home automation dashboard configuration, or when a user asks how to configure any Home Assistant dashboard card type (entities, sensor display, climate control, media player, picture cards, conditional cards, history graphs, etc.). This skill is the authoritative reference for all 36+ Home Assistant card types with working YAML examples.
---

# Home Assistant Dashboard Cards Skill

Use this skill as the authoritative reference for Home Assistant Lovelace dashboard configuration. The complete card reference is in `references/cards.md`.

## Quick Lookup

| Card Category | Types |
|--------------|-------|
| **Display** | entity, sensor, gauge, glance, history-graph, statistics-graph, statistic, plant-status, map, calendar, clock, weather-forecast, logbook |
| **Control** | light, humidifier, thermostat, alarm-panel, media-control, tile, button, cover, climate |
| **Layout** | vertical-stack, horizontal-stack, grid, sections, picture-elements |
| **Media** | picture, picture-entity, picture-glance, iframe, markdown |
| **State-based** | conditional, entity-filter, area |
| **Energy** | energy-*, power-sankey, power-total, gas-total, water-total |
| **Lists** | entities, todo-list, heading |

## Common Patterns

### Most Used Cards

**Entities card** (most common):
```yaml
type: entities
entities:
  - light.living_room
  - switch.ac_unit
```

**Sensor with graph**:
```yaml
type: sensor
entity: sensor.temperature
graph: line
hours_to_show: 24
```

**Conditional visibility**:
```yaml
type: conditional
conditions:
  - condition: state
    entity: light.bed_light
    state: "on"
card:
  type: entities
  entities:
    - light.bed_light
```

### Actions

All cards support `tap_action`, `hold_action`, `double_tap_action`:

| Action | YAML |
|--------|------|
| Navigate | `action: navigate`, `navigation_path: /lovelace/home` |
| URL | `action: url`, `url_path: https://...` |
| Service | `action: perform-action`, `perform_action: light.toggle` |
| More info | `action: more-info` |
| Toggle | `action: toggle` |

### View Types

| Type | Use case |
|------|----------|
| `sections` (default) | Grouped, collapsible sections |
| `masonry` | Free-form, variable heights |
| `panel` | Single full-width card |
| `sidebar` | Navigation sidebar |

## When to Read the Full Reference

Read `references/cards.md` when:
- User asks about a specific card type not covered above
- You need complete YAML options for a card
- You're debugging card configuration issues
- User wants to see all 36 card types with examples

## Tips

- Use `type: vertical-stack` or `horizontal-stack` to group cards
- `type: conditional` shows/hides cards based on entity states
- `type: picture-elements` is powerful for floor plan layouts
- Energy cards (type: energy-*) work with the Home Assistant energy dashboard
- The `entities` card supports special rows: `divider`, `section`, `weblink`, `attribute`, `button`, `buttons`, `conditional`

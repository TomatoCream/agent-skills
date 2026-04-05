# Home Assistant Dashboard Cards - Complete YAML Reference

## Overview

Home Assistant dashboards allow you to display information about your smart home. Dashboards are customizable and provide a powerful way to manage your home from your mobile or desktop.

**Key features:**
- Multiple card types to visualize data and control devices
- Themes (even per-card)
- Override entity names and icons
- Custom community cards

---

## View Types

| Type | Description |
|------|-------------|
| **Masonry** | Free-form layout, cards flow top-to-bottom, left-to-right |
| **Panel** | Single card takes full width |
| **Sections** (default) | Cards grouped into collapsible sections |
| **Sidebar** | Navigation sidebar on left |

---

## Layout Cards (Containers)

| Card | What it does |
|------|-------------|
| **horizontal-stack** | Cards side-by-side in same column |
| **vertical-stack** | Cards stacked in same column |
| **grid** | Multiple cards in a grid layout |

---

## Card Types (36 Cards)

### 1. Activity (Logbook)

**What it does:** Displays historical state changes from the logbook for specific entities.

```yaml
type: logbook
target:
  entity_id:
    - fan.ceiling_fan
    - light.ceiling_lights
hours_to_show: 24
state_filter:
  - "on"
```

---

### 2. Alarm Panel

**What it does:** Keypad-style interface to arm/disarm alarm systems.

```yaml
type: alarm-panel
entity: alarm_control_panel.alarm
name: "House Alarm"
states:
  - arm_home
  - arm_away
  - arm_night
```

---

### 3. Area

**What it does:** Control center for all entities in a room. Shows camera feed, buttons for lights/fans/switches, sensor readings.

```yaml
type: area
area: bedroom
display_type: picture          # compact, icon, picture, camera
camera_view: auto
features:
  - type: area-controls
sensor_classes:
  - temperature
  - humidity
```

---

### 4. Button

**What it does:** Interactive button to trigger scripts, services, or entity actions.

```yaml
type: button
entity: light.living_room
name: "Turn Off Lights"
icon: mdi:lightbulb
tap_action:
  action: perform-action
  perform_action: script.turn_off_lights
hold_action:
  action: more-info
```

---

### 5. Calendar

**What it does:** Displays calendar events in month, day, or list view.

```yaml
type: calendar
title: "My Calendar"
initial_view: dayGridMonth
entities:
  - calendar.calendar_1
  - calendar.calendar_2
```

---

### 6. Clock

**What it does:** Displays time in digital or analog format with timezone support.

```yaml
type: clock
title: "London"
clock_style: digital           # or: analog
clock_size: small              # small, medium, large
time_format: "24"
time_zone: "Europe/London"
show_seconds: false
```

---

### 7. Conditional

**What it does:** Show/hide cards based on entity states, user, time, location, or screen size.

```yaml
type: conditional
conditions:
  - condition: state
    entity: light.bed_light
    state: "on"
  - condition: numeric_state
    entity: sensor.temperature
    above: 25
card:
  type: entities
  entities:
    - device_tracker.demo_paulus
```

**Available condition types:**

| Condition | Description |
|-----------|-------------|
| `state` | Entity has a specified state |
| `numeric_state` | Entity state matches threshold (above/below) |
| `screen` | Screen size matches media query |
| `user` | Specific users can see the card |
| `location` | User's location matches zones |
| `time` | Time of day/weekday matches |
| `and` | All conditions must match |
| `or` | At least one condition must match |
| `not` | Condition must not match |

---

### 8. Energy Cards

**What it does:** Collection of cards for energy monitoring (solar, consumption, grid, etc.)

```yaml
# Energy Date Picker
type: energy-date-selection

# Usage Graph
type: energy-usage-graph

# Solar Production
type: energy-solar-graph

# Distribution
type: energy-distribution
link_dashboard: true

# Grid Neutrality Gauge
type: energy-grid-neutrality-gauge

# Power Flow Sankey
type: power-sankey
layout: horizontal

# Badges
type: power-total
type: gas-total
type: water-total
```

---

### 9. Entities

**What it does:** Most common card - displays a list of entities with state info.

```yaml
type: entities
title: Home Control
show_header_toggle: true
entities:
  - entity: alarm_control_panel.alarm
    name: Alarm Panel
  - device_tracker.demo_paulus
  - type: divider
  - type: button
    icon: mdi:power
    name: Bed light transition
    tap_action:
      action: perform-action
      perform_action: light.toggle
```

**Special row types:**

| Type | Description |
|------|-------------|
| `attribute` | Display entity attribute |
| `button` | Button row |
| `buttons` | Multiple button rows |
| `divider` | Horizontal divider line |
| `section` | Section header |
| `weblink` | External link |
| `conditional` | Conditional row |

---

### 10. Entity

**What it does:** Compact single-entity overview with optional attribute display.

```yaml
type: entity
entity: cover.kitchen_window
name: Front Door

type: entity
entity: light.bedroom
attribute: brightness
unit: "%"
```

---

### 11. Entity Filter

**What it does:** Shows entities only when they match specified conditions.

```yaml
type: entity-filter
entities:
  - light.bed_light
  - light.kitchen_lights
conditions:
  - condition: state
    state: "on"
card:
  type: glance
  title: Active Lights
```

---

### 12. Gauge

**What it does:** Numeric sensor displayed as a gauge with severity colors or custom segments.

```yaml
type: gauge
entity: sensor.cpu_usage
name: CPU Usage
unit: '%'
min: 0
max: 100
severity:
  green: 0
  yellow: 45
  red: 85

# With custom segments (needle mode)
type: gauge
entity: sensor.kitchen_humidity
needle: true
segments:
  - from: 0
    color: '#db4437'
  - from: 35
    color: '#ffa600'
  - from: 40
    color: '#43a047'
```

---

### 13. Glance

**What it does:** Compact grid of small icons with names and states for multiple sensors.

```yaml
type: glance
title: Home Status
columns: 4
entities:
  - binary_sensor.movement_backyard
  - light.bed_light
  - sensor.outside_temperature
  - lock.kitchen_door
```

---

### 14. Grid

**What it does:** Display multiple cards in a grid layout.

```yaml
type: grid
title: Backyard
columns: 2
square: false
cards:
  - type: picture-entity
    entity: group.all_lights
    image: /local/house.png
  - type: horizontal-stack
    cards:
      - type: picture-entity
        entity: light.ceiling_lights
```

---

### 15. Heading

**What it does:** Section header with title, icon, navigation, and optional badges.

```yaml
type: heading
heading: Kitchen
icon: mdi:fridge
badges:
  - type: entity
    entity: sensor.kitchen_temperature
  - type: button
    icon: mdi:lightbulb-off
    text: Turn off lights
    color: yellow
```

---

### 16. History Graph

**What it does:** Graph showing historical state changes over time for up to 8 entities.

```yaml
type: history-graph
title: Temperatures
hours_to_show: 48
entities:
  - sensor.outside_temperature
  - entity: sensor.lounge_temperature
    name: "Lounge"
fit_y_data: true
```

---

### 17. Horizontal Stack

**What it does:** Group cards side-by-side in the same column.

```yaml
type: horizontal-stack
cards:
  - type: picture-entity
    entity: light.ceiling_lights
    image: /local/bed_1.png
  - type: picture-entity
    entity: light.bed_light
    image: /local/bed_2.png
```

---

### 18. Humidifier

**What it does:** Control humidifier/dehumidifier entities with target humidity and mode.

```yaml
type: humidifier
entity: humidifier.bedroom
name: Bedroom Humidifier
show_current_as_primary: false
```

---

### 19. Light

**What it does:** Change brightness of a light entity.

```yaml
type: light
entity: light.bedroom
name: Kids Bedroom
hold_action:
  action: more-info
```

---

### 20. Map

**What it does:** Display device trackers, zones, and geolocation on a map.

```yaml
type: map
aspect_ratio: "16:9"
default_zoom: 8
auto_fit: true
entities:
  - device_tracker.demo_paulus
  - zone.home
hours_to_show: 48
cluster: true
```

---

### 21. Markdown

**What it does:** Render Markdown content with template support, icons, alerts, QR codes.

```yaml
type: markdown
content: |
  ## Dashboard Header
  Welcome to my smart home

  {% for l in config.entities %}
    - {{ l.entity }}
  {%- endfor %}

  <ha-alert alert-type="warning">System alert!</ha-alert>

  <ha-qr-code data='hello' width="180"></ha-qr-code>
```

---

### 22. Media Control

**What it does:** Media player controls with play/pause, volume, etc.

```yaml
type: media-control
entity: media_player.lounge_room
name: Living Room
```

---

### 23. Picture

**What it does:** Static image that performs actions on tap.

```yaml
type: picture
image: /local/home.jpg
tap_action:
  action: navigate
  navigation_path: /lovelace/home
```

---

### 24. Picture Elements

**What it does:** Position icons, labels, buttons on an image (perfect for floor plans).

```yaml
type: picture-elements
image: /local/floorplan.png
elements:
  - type: state-icon
    entity: light.ceiling_lights
    tap_action:
      action: toggle
    style:
      top: 47%
      left: 42%
  - type: state-label
    entity: sensor.outside_temperature
    suffix: "°C"
    style:
      top: 82%
      left: 79%
  - type: action-button
    title: All Lights Off
    action: homeassistant.turn_off
    target:
      entity_id: group.all_lights
    style:
      top: 95%
      left: 60%
```

**Element types:**

| Type | Description |
|------|-------------|
| `state-badge` | Colored badge showing entity state |
| `state-icon` | Icon that reflects entity state |
| `state-label` | Text showing entity state |
| `action-button` | Button triggering an action |
| `icon` | Static icon |
| `image` | Static or state-based image |
| `conditional` | Conditional element visibility |

---

### 25. Picture Entity

**What it does:** Image that changes based on entity state.

```yaml
type: picture-entity
entity: light.bed_light
state_image:
  "on": /local/bed_light_on.png
  "off": /local/bed_light_off.png
show_state: true

# Live camera
type: picture-entity
entity: camera.backdoor
camera_view: live
```

---

### 26. Picture Glance

**What it does:** Image with overlay icons for controlling multiple entities.

```yaml
type: picture-glance
title: Living room
image: /local/living_room.png
entities:
  - switch.decorative_lights
  - light.ceiling_lights
  - entity: lock.front_door
    icon: mdi:door
    show_state: true
    tap_action:
      action: toggle
```

---

### 27. Plant Status

**What it does:** Display detailed status for plants (battery, moisture, illumination).

```yaml
type: plant-status
entity: plant.bonsai
name: My Bonsai
```

---

### 28. Sensor

**What it does:** Single sensor with optional line graph showing history.

```yaml
type: sensor
entity: sensor.illumination
name: Illumination
graph: line
hours_to_show: 24
detail: 1
```

---

### 29. Statistic

**What it does:** Display aggregated statistics (min, max, mean, change) over a period.

```yaml
type: statistic
entity: sensor.energy_consumption
stat_type: change
period:
  calendar:
    period: month
    offset: -1

# Rolling window
type: statistic
entity: sensor.energy_consumption
period:
  rolling_window:
    duration:
      hours: 1
      minutes: 10
stat_type: change
```

**Period options:**

| Period Type | Description |
|-------------|-------------|
| `calendar` | Fixed period (day, week, month, year) with optional offset |
| `fixed_period` | Specific start/end dates |
| `rolling_window` | Sliding time window with duration and offset |
| `energy_date_selection` | Links to energy-date-selection card |

**Stat types:** `min`, `max`, `mean`, `change`, `sum`, `state`

---

### 30. Statistics Graph

**What it does:** Graph multiple entities' statistical trends over time.

```yaml
type: statistics-graph
title: Temperature Overview
entities:
  - sensor.outside_temperature
  - entity: sensor.inside_temperature
    name: Inside
days_to_show: 7
chart_type: line
stat_types:
  - min
  - max
  - mean
```

---

### 31. Thermostat

**What it does:** Control climate/water heater entities (temperature and mode).

```yaml
type: thermostat
entity: climate.nest
name: Nest
show_current_as_primary: false
features:
  - type: climate-hvac-modes
```

---

### 32. Tile

**What it does:** Quick entity overview with icon, optional picture, and toggle.

```yaml
type: tile
entity: cover.kitchen_window

type: tile
entity: light.bedroom
icon: mdi:lamp
color: yellow

type: tile
entity: person.anne_therese
show_entity_picture: true
vertical: true

type: tile
entity: vacuum.ground_floor
features:
  - type: vacuum-commands
    commands:
      - start_pause
      - return_home
```

**Available colors:** `primary`, `accent`, `disabled`, `red`, `pink`, `purple`, `deep-purple`, `indigo`, `blue`, `light-blue`, `cyan`, `teal`, `green`, `light-green`, `lime`, `yellow`, `amber`, `orange`, `deep-orange`, `brown`, `grey`, `blue-grey`, `black`, `white`, or hex codes (e.g., `#93c47d`)

---

### 33. To-do List

**What it does:** Add, edit, check-off, and clear items from a to-do list.

```yaml
type: todo-list
entity: todo.todo_list
title: Todo List
hide_completed: false
display_order: alpha_asc
due_date_period:
  calendar:
    period: week
    offset: 1
```

**Display order options:** `none`, `alpha_asc`, `alpha_desc`, `duudate_asc`, `duedate_desc`

---

### 34. Vertical Stack

**What it does:** Group multiple cards in the same column.

```yaml
type: vertical-stack
title: Backyard
cards:
  - type: picture-entity
    entity: camera.demo_camera
  - type: entities
    entities:
      - binary_sensor.movement_backyard
```

---

### 35. Weather Forecast

**What it does:** Display current weather and forecast.

```yaml
type: weather-forecast
entity: weather.openweathermap
forecast_type: daily            # daily, hourly, twice_daily
show_current: true
show_forecast: true
round_temperature: true
```

---

### 36. Webpage (Iframe)

**What it does:** Embed any webpage in your dashboard.

```yaml
type: iframe
url: https://www.home-assistant.io
aspect_ratio: 75%
allow_open_top_navigation: false
hide_background: false
```

---

## Common Actions

All cards support these actions via `tap_action`, `hold_action`, `double_tap_action`:

| Action | Description |
|--------|-------------|
| `navigate` | Navigate to another dashboard/path |
| `url` | Open URL in browser |
| `perform-action` | Call a Home Assistant service |
| `more-info` | Show entity more-info dialog |
| `toggle` | Toggle entity state |
| `call-service` | Call a service |

---

## Quick Reference Table

| Card | Type String | Required Field | Best For |
|------|-------------|----------------|----------|
| Activity | `logbook` | `target` | History/state changes |
| Alarm Panel | `alarm-panel` | `entity` | Security systems |
| Area | `area` | `area` | Room control |
| Button | `button` | None | Quick actions |
| Calendar | `calendar` | `entities` | Events/schedules |
| Clock | `clock` | None | Time displays |
| Conditional | `conditional` | `conditions`, `card` | Dynamic visibility |
| Energy | `energy-*` | varies | Energy monitoring |
| Entities | `entities` | `entities` | Entity lists |
| Entity | `entity` | `entity` | Single entity |
| Entity Filter | `entity-filter` | `entities`, `conditions` | State-filtered lists |
| Gauge | `gauge` | `entity` | Numeric visualization |
| Glance | `glance` | `entities` | Compact overview |
| Grid | `grid` | `cards` | Card grids |
| Heading | `heading` | None | Section headers |
| History Graph | `history-graph` | `entities` | Historical data |
| Horizontal Stack | `horizontal-stack` | `cards` | Side-by-side |
| Humidifier | `humidifier` | `entity` | Humidity control |
| Light | `light` | `entity` | Light brightness |
| Map | `map` | None | Location tracking |
| Markdown | `markdown` | `content` | Rich text/content |
| Media Control | `media-control` | `entity` | Media players |
| Picture | `picture` | `image` | Image navigation |
| Picture Elements | `picture-elements` | `image`, `elements` | Floor plans |
| Picture Entity | `picture-entity` | `entity` | State-based images |
| Picture Glance | `picture-glance` | `image`, `entities` | Visual controls |
| Plant Status | `plant-status` | `entity` | Plant monitoring |
| Sensor | `sensor` | `entity` | Sensor display |
| Statistic | `statistic` | `entity`, `stat_type`, `period` | Aggregated stats |
| Statistics Graph | `statistics-graph` | `entities` | Stats over time |
| Thermostat | `thermostat` | `entity` | Climate control |
| Tile | `tile` | `entity` | Quick toggle |
| To-do List | `todo-list` | `entity` | Task management |
| Vertical Stack | `vertical-stack` | `cards` | Card stacking |
| Weather Forecast | `weather-forecast` | `entity` | Weather display |
| Webpage | `iframe` | `url` | Embedded web content |

---

## Resources

- **Official Docs:** https://www.home-assistant.io/dashboards/
- **Interactive Demo:** https://demo.home-assistant.io
- **Custom Cards:** https://github.com/custom-cards
- **Card Gallery:** https://home-assistant-cards.bessarabov.com/

---

## Documentation Links

### Views
- [Masonry](https://www.home-assistant.io/dashboards/masonry/)
- [Panel](https://www.home-assistant.io/dashboards/panel/)
- [Sections](https://www.home-assistant.io/dashboards/sections/)
- [Sidebar](https://www.home-assistant.io/dashboards/sidebar/)

### Cards
- [Activity (Logbook)](https://www.home-assistant.io/dashboards/logbook/)
- [Alarm Panel](https://www.home-assistant.io/dashboards/alarm-panel/)
- [Area](https://www.home-assistant.io/dashboards/area/)
- [Button](https://www.home-assistant.io/dashboards/button/)
- [Calendar](https://www.home-assistant.io/dashboards/calendar/)
- [Clock](https://www.home-assistant.io/dashboards/clock/)
- [Conditional](https://www.home-assistant.io/dashboards/conditional/)
- [Energy Cards](https://www.home-assistant.io/dashboards/energy/)
- [Entities](https://www.home-assistant.io/dashboards/entities/)
- [Entity](https://www.home-assistant.io/dashboards/entity/)
- [Entity Filter](https://www.home-assistant.io/dashboards/entity-filter/)
- [Gauge](https://www.home-assistant.io/dashboards/gauge/)
- [Glance](https://www.home-assistant.io/dashboards/glance/)
- [Grid](https://www.home-assistant.io/dashboards/grid/)
- [Heading](https://www.home-assistant.io/dashboards/heading/)
- [History Graph](https://www.home-assistant.io/dashboards/history-graph/)
- [Horizontal Stack](https://www.home-assistant.io/dashboards/horizontal-stack/)
- [Humidifier](https://www.home-assistant.io/dashboards/humidifier/)
- [Light](https://www.home-assistant.io/dashboards/light/)
- [Map](https://www.home-assistant.io/dashboards/map/)
- [Markdown](https://www.home-assistant.io/dashboards/markdown/)
- [Media Control](https://www.home-assistant.io/dashboards/media-control/)
- [Picture](https://www.home-assistant.io/dashboards/picture/)
- [Picture Elements](https://www.home-assistant.io/dashboards/picture-elements/)
- [Picture Entity](https://www.home-assistant.io/dashboards/picture-entity/)
- [Picture Glance](https://www.home-assistant.io/dashboards/picture-glance/)
- [Plant Status](https://www.home-assistant.io/dashboards/plant-status/)
- [Sensor](https://www.home-assistant.io/dashboards/sensor/)
- [Statistic](https://www.home-assistant.io/dashboards/statistic/)
- [Statistics Graph](https://www.home-assistant.io/dashboards/statistics-graph/)
- [Thermostat](https://www.home-assistant.io/dashboards/thermostat/)
- [Tile](https://www.home-assistant.io/dashboards/tile/)
- [To-do List](https://www.home-assistant.io/dashboards/todo-list/)
- [Vertical Stack](https://www.home-assistant.io/dashboards/vertical-stack/)
- [Weather Forecast](https://www.home-assistant.io/dashboards/weather-forecast/)
- [Webpage (Iframe)](https://www.home-assistant.io/dashboards/iframe/)

### Advanced
- [Features](https://www.home-assistant.io/dashboards/features/)
- [Headers & Footers](https://www.home-assistant.io/dashboards/header-footer/)
- [Actions](https://www.home-assistant.io/dashboards/actions/)
- [Custom Cards Dev](https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/)

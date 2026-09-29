# obstacles and charging_stations

## `obstacles`
**One row = one obstacle (a rectangle of blocked cells) with a lifetime.** Primary key `(episode_id, obstacle_id)`.
Static layout obstacles (shelves, walls) and, from Phase 7, obstacles that appear and disappear during an episode all
live here; `is_static` tells them apart.

| Column | Unit | Meaning |
|---|---|---|
| `episode_id`, `obstacle_id` | — | Identity (`O1`…) |
| `obstacle_kind` | — | What it is: `wall`, `shelf` now. Later `fallen_package`, `maintenance_equipment`, `cleaning_vehicle`, … |
| `cause` | — | *Why* it exists. Static ones: `fixed_infrastructure`. Dynamic ones will carry the cause (e.g. `high_traffic`) — this is what lets you study correlated blockages |
| `is_static` | bool | `true` = part of the layout from t = 0, never removed |
| `x_min`, `y_min`, `x_max`, `y_max` | cells | Rectangle, **both ends inclusive** (O1: x 7..7, y 3..19 = a 1×17 wall) |
| `appear_time_s` | s | When it becomes blocking (0.0 for static) |
| `remove_time_s` | s | When it stops blocking; NULL = never |
| `source_type`, `schema_version`, `created_at` | | Provenance / audit |

Stage 0 rows: `O1` wall (7,3)–(7,19); `O2` shelf (10,5)–(11,12); `O3` shelf (13,6)–(14,16).
Their union is exactly the `#` cells of `environments.map_grid` (55 cells → density 0.1375).

Static obstacles are **not** in `obstacle_events`: nothing about them *changes*. From Phase 7 a dynamic obstacle gets
one `obstacles` row (its lifetime) **plus** `OBSTACLE_APPEARED` / `OBSTACLE_REMOVED` events.

## `charging_stations`
**One row = one charging station in one episode.** Primary key `(episode_id, station_id)`.

| Column | Unit | Meaning |
|---|---|---|
| `episode_id`, `station_id` | — | Identity (`C1`) |
| `x`, `y` | cells | Location (1, 1) |
| `power_w` | W | Charging power (200). Not yet used — no robot ever needs charging in Stage 0 |
| `n_slots` | count | Robots that can charge at once (1). Charging *competition* (Stage 3) depends on this |
| `source_type`, `schema_version`, `created_at` | | Provenance / audit |

The location also appears in `environments.charging_station_locations` (JSON) by design.
`loading_stations` / `delivery_stations` have no table of their own: they are only the JSON lists in `environments`.

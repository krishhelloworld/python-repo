# robot_types and robots

```
robot_types   = the CATALOGUE  (nominal specs of a kind of robot)    1 row per kind, global
robots        = the FLEET      (the actual robots of one episode)     1 row per robot per episode
```
Why two tables: in Stage 9 each robot's real numbers will be drawn from a distribution around the type's nominal
values, so `robots` stores the *effective* values of that individual robot, not just a pointer to the type.

---
## `robot_types` (1 row today: `small_fast_robot`)
**One row = one kind of robot and its nominal specification.** Seeded by the migration; the Python catalogue must match it
(a test checks). The other 8 planned kinds (`large_payload_robot`, `slow_heavy_robot`, `high_clearance_robot`,
`low_battery_robot`, `specialized_picker`, `delivery_robot`, `charging_robot`, `human_operator`) are added in Phase 8.

| Column | Unit | Meaning | Stage 0 value |
|---|---|---|---|
| `robot_type` | — | Name (primary key) | `small_fast_robot` |
| `description` | — | Human description | Small, quick, low-payload grid robot |
| `introduced_in_stage` | — | Stage that first uses it | 0 |
| `max_speed_mps` | m/s | Top speed | 1.0 |
| `battery_capacity_wh` | Wh | Full battery energy | 100 |
| `payload_capacity_kg` | kg | Maximum carried mass | 20 |
| `length_m`, `width_m` | m | Body footprint | 0.6, 0.5 |
| `turning_radius_m` | m | Smallest turn; 0 = spins on the spot (grid robot) | 0 |
| `operating_cost_per_hour` | currency/h | Synthetic running cost (no real currency implied) | 4.0 |
| `communication_range_m` | m | Radio range (used from Stage 4) | 50 |
| `sensor_reliability` | 0–1 | Probability a sensor reading is valid; 1 = perfect | 1.0 |
| `failure_probability_per_hour` | 1/h, 0–1 | Nominal breakdown probability (used from Stage 4) | 0.0 |
| `energy_per_meter_wh` | Wh/m | Energy per metre driven | 0.05 |
| `idle_power_w` | W | Baseline draw, *always on* (also while moving) | 5.0 |

---
## `robots` (1 row today: `R1`)
**One row = one robot in one episode: its static configuration and its starting state.** Primary key `(episode_id, robot_id)`.
Anything that changes over time (position, battery, status) is in `trajectories`, not here.

| Column | Meaning |
|---|---|
| `episode_id`, `robot_id` | Which episode; robot name inside it (`R1`) |
| `robot_type` | FK → `robot_types` |
| `initial_x`, `initial_y` (m) | Start position (2.0, 3.0). Equals trajectory row at t = 0 |
| `initial_velocity` (m/s), `initial_acceleration` (m/s²) | 0, 0 |
| `max_speed_mps`, `battery_capacity_wh`, `payload_capacity_kg`, `length_m`, `width_m`, `turning_radius_m`, `operating_cost_per_hour`, `communication_range_m`, `sensor_reliability`, `failure_probability_per_hour`, `energy_per_meter_wh`, `idle_power_w` | **Effective** values for this robot; same meanings/units as the catalogue. Identical to the type in Stage 0; will differ per robot from Stage 9 |
| `initial_battery_wh` (Wh) | Battery at t = 0 (100 = full). Will vary in later stages |
| `initial_maintenance_state` | `nominal`. Later: degraded, due_for_service… |
| `initial_status` | `idle`: status *before* events at t = 0 are applied (trajectory row at t = 0 already says `moving`) |
| `initial_task_id` | Task carried at t = 0; NULL |
| `source_type`, `schema_version`, `created_at` | Provenance / audit |

**How Stage 0 battery is computed** (useful for checking your own feature engineering):
`battery_wh(t) = initial_battery_wh − energy_per_meter_wh × metres_travelled − idle_power_w × t / 3600`.

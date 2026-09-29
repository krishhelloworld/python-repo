# scenarios → environments → episodes

Think of three nested things:

```
scenario     = the RECIPE   (config + seed + versions)         "how to build a world"
environment  = the WORLD    (map, stations, conditions)        "the world that recipe produced"
episode      = one RUN      (robots + tasks acting in it)      "what happened when we ran it"
```
One scenario can have many episodes (different `random_seed` for the dynamics). In Stage 0: 1 / 1 / 1.

---
## `scenarios`
**One row = one reproducible world recipe.** Written once, shared by every episode run in it.

| Column | Type | Meaning / how to read it |
|---|---|---|
| `scenario_id` | uuid | Deterministic: `uuid5(namespace, "scenario|generator_version|scenario_version|scenario_seed|config_hash")`. Same inputs → same id, on any machine. |
| `stage` | int | Progression stage that introduced this family (0 = controlled world). |
| `difficulty_level` | int 1–12 | Curriculum level (section 24 of the brief). Stage 0 = 1. |
| `scenario_category` | text | `nominal` now; later `rare_event`, `adversarial`, `distribution_shift`… Use it to keep rare scenarios out of normal training sets. |
| `scenario_seed` | bigint | Seed for **layout** generation. Stage 0 uses none but records `0`. NULL is forbidden for synthetic rows (CHECK). |
| `scenario_version` | text | Version of the scenario *definition*. Stage 0: `stage0-fixed-v1`. |
| `generator_version` | text | Version of the generator *code*. Stage 0: `stage0-gen-0.1.0`. |
| `config` | jsonb | The **complete** recipe (sizes, obstacles, stations, robots, tasks, planner). If you have this, you can rebuild the world without the code. |
| `config_hash` | text | sha256 of `config` as canonical JSON (sorted keys, no whitespace). Two scenarios with identical `config` share it. |
| `source_type` | text | `synthetic` / `external` / `derived`. |
| `schema_version` | text | Schema the row was written under (`0.1.0`). |
| `created_at` | timestamptz | Wall-clock insert time. Audit only. |

Constraint: `UNIQUE (generator_version, scenario_version, scenario_seed, config_hash)`.

**Real row (Stage 0):** `scenario_id 3a9f3085-…`, stage 0, difficulty 1, category `nominal`, seed 0,
version `stage0-fixed-v1`, generator `stage0-gen-0.1.0`, config_hash `07f021c1…`.

---
## `environments`
**One row = the physical world built from a scenario.**

| Column | Type | Meaning / how to read it |
|---|---|---|
| `environment_id` | uuid | Deterministic uuid5 of the scenario id + environment version. |
| `scenario_id` | uuid | FK → `scenarios`. |
| `environment_type` | text | `warehouse` now; the CHECK allows all 10 future types (factory, port, …). |
| `width`, `height` | int (cells) | Grid size. Stage 0: 20 × 20. |
| `cell_size_m` | double (m) | Edge of one cell. Stage 0: 1.0. Multiply cell indices by this to get metres. |
| `map_representation` | text | How the map is stored. `occupancy_grid` = a grid of free/blocked cells. |
| `map_grid` | jsonb | List of `height` strings of `width` characters, indexed `[cy][cx]`; `.` free, `#` blocked. NULL if `map_uri` is used. |
| `map_uri` | text | Path to a map file for maps too large to keep in the row. NULL in Stage 0. (One of `map_grid` / `map_uri` must be set.) |
| `terrain_type` | text | Floor class (`smooth_concrete`). Later: affects speed / energy. |
| `obstacle_density` | double 0–1 | Blocked cells ÷ total cells at t = 0. Stage 0: 55 / 400 = 0.1375. |
| `aisle_configuration` | jsonb | Description of the aisles. Stage 0: `layout: hand_authored_stage0` and 3 aisles (`A1`, `A2`, `A3`) each with orientation and x/y ranges (cells, inclusive). |
| `charging_station_locations` | jsonb | `[{station_id, x, y}]` in cells. |
| `loading_station_locations` | jsonb | Same shape. Pickup points. |
| `delivery_station_locations` | jsonb | Same shape. Drop-off points. |
| `environmental_conditions` | jsonb | Ambient conditions. Stage 0: `{"indoor": true, "temperature_c": 20.0}`. Weather arrives in Stage 6. |
| `environment_version` | text | Version of the environment definition (`warehouse-fixed-v1`). |
| `scenario_version`, `scenario_seed`, `generator_version` | text/bigint/text | Copies from the scenario, kept here so an environment row is self-describing. |
| `source_type`, `schema_version`, `created_at` | | As above. |

Note: charging station *locations* here duplicate the `charging_stations` table on purpose (the brief lists both);
the table adds per-station attributes (power, slots).

---
## `episodes`
**One row = one run of robots and tasks in an environment. This is the provenance hub** — every other episode-level
row points here through `episode_id`.

| Column | Type | Meaning / how to read it |
|---|---|---|
| `episode_id` | uuid | Deterministic uuid5 of scenario id + `random_seed` + simulator version + robot-config version. |
| `scenario_id`, `environment_id` | uuid | FKs to the recipe and world. |
| `random_seed` | bigint | Seed for the **dynamics** (obstacles appearing, failures, demand…). Not used in Stage 0, recorded anyway. Not the same thing as `scenario_seed`. |
| `generator_version`, `scenario_version`, `environment_version` | text | Versions of the things that built the world. |
| `simulator_version` | text | Version of the code that ran the episode. |
| `robot_configuration_version` | text | Version of the fleet definition (`robots-v1`). |
| `schema_version` | text | Schema version. |
| `source_type` | text | `synthetic` here. CHECKs: `external` ⇒ `external_source_id` required; `derived` ⇒ `parent_dataset` and `transformation_description` required. |
| `external_source_id`, `parent_dataset`, `transformation_description` | text | NULL for synthetic episodes. |
| `sim_epoch` | timestamptz | The calendar time that `sim_time_s = 0` corresponds to (simulated, not real). |
| `tick_seconds` | double (s) | Length of one simulation tick (1.0). |
| `n_ticks` | int | **Index of the last tick**, not the count: Stage 0 has `n_ticks = 31`, ticks are `0..31`, so 32 rows per robot. Rows per robot = `n_ticks + 1`. |
| `n_robots`, `n_tasks`, `n_trajectory_rows` | int | Counts (1, 1, 32). `n_trajectory_rows = n_robots × (n_ticks + 1)`. |
| `termination_reason` | text | Why it ended: `all_tasks_completed`. Later: timeout, all robots failed, … (an outcome label — episode-level). |
| `content_sha256` | text | Fingerprint of all rows of the episode (see below). |
| `raw_uri` | text | Relative path of the episode's Parquet folder under `raw/`. |
| `created_at` | timestamptz | Wall-clock insert time. |

### What `content_sha256` covers
Canonical JSON of every row in: scenarios, environments, episodes, robots, tasks, charging_stations, obstacles,
task_events, robot_events, obstacle_events, trajectories — rows sorted by primary key, timestamps in UTC,
**excluding** `created_at`, `raw_uri` and the hash itself. If you regenerate an episode and the hash differs, something
in the generator changed (or is non-deterministic). The database and the raw `manifest.json` both store it.

**Real row:** `episode_id bd1d2e38-…`, seed 0, `simulator_version orbit-sim-0.1.0`, `n_ticks 31`, 32 trajectory rows,
`all_tasks_completed`, `content_sha256 fa396c03…`.

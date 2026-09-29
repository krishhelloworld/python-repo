# ORBIT docs — how to read the data

Everything in the database and in `raw/` is **RAW, synthetic** data from the Stage 0 world
(1 warehouse, 1 robot `R1`, 1 task `T1`). Nothing has been cleaned, scaled, imputed or split.

| Read this | To learn |
|---|---|
| [table_status.md](table_status.md) | Which tables/folders are filled today, which are empty, and *which phase fills each one* |
| [tables/01_scenarios_environments_episodes.md](tables/01_scenarios_environments_episodes.md) | The three "identity" tables: recipe → world → run |
| [tables/02_robots.md](tables/02_robots.md) | `robot_types`, `robots` |
| [tables/03_tasks.md](tables/03_tasks.md) | `tasks` (final-state row + which columns are labels) |
| [tables/04_events.md](tables/04_events.md) | `event_types`, `task_events`, `robot_events`, `obstacle_events` |
| [tables/05_obstacles_and_charging.md](tables/05_obstacles_and_charging.md) | `obstacles`, `charging_stations` |
| [tables/06_trajectories.md](tables/06_trajectories.md) | `trajectories` (the big one) |
| [tables/07_registry_tables.md](tables/07_registry_tables.md) | Empty-for-now tables: external data, dataset versions, experiments, corruption registry |
| [tables/08_raw_files.md](tables/08_raw_files.md) | The Parquet files + `manifest.json` under `raw/` |
| [phase6_procedural_environments_spec.md](phase6_procedural_environments_spec.md) | **Next step (Phase 6 / Stage 1).** A spec for you to implement — no code provided |
| [../metadata/data_dictionary.md](../metadata/data_dictionary.md) | Auto-generated one-line-per-column dictionary (terse; the docs above are the readable version) |

## Conventions used in every table

**Grid and coordinates.** A cell is `(cx, cy)`, both integers, `0 <= cx < width`, `0 <= cy < height`.
`environments.map_grid` is a list of strings indexed `map_grid[cy][cx]`; the **first string is row `cy = 0`**.
If you print it top-to-bottom, y grows *downward* on screen — flip it if you want a "y up" picture.
`'.'` = free cell, `'#'` = blocked cell.

**Two coordinate units (a classic trap).**
- `tasks.pickup_x / destination_x / …`, `obstacles.x_min…`, `charging_stations.x/y` are **cells** (integers).
- `trajectories.x / y`, `robots.initial_x / initial_y` are **metres** = `cell * cell_size_m`.
They only look identical because Stage 0 uses `cell_size_m = 1.0`. Convert before comparing once that changes.

**Time.** Three different time-like things exist:
| Column | Meaning | Use for modelling? |
|---|---|---|
| `sim_time_s` | seconds since episode start on the *simulated* clock | Yes |
| `timestamp` | `episodes.sim_epoch + sim_time_s` (simulated calendar time; Stage 0 epoch = Monday 2026-01-05 08:00 UTC) | Yes (hour-of-day etc. once demand patterns exist) |
| `created_at` | *wall-clock* time the row was inserted into PostgreSQL; identical for every row of an episode (one transaction) | **No.** Audit only |

**"State at time t".** A trajectory row at time `t` is the state **after** all events with `sim_time_s <= t` were applied.
`velocity` is a backward difference: distance moved in `(t - dt, t]` divided by `dt`.

**NULL means "not applicable" or "not yet knowable"**, never "missing sensor reading" (that kind of missingness is
introduced deliberately and documented in Stage 4+ via `corruption_mechanisms`).

**Provenance columns.** `source_type` (`synthetic` | `external` | `derived`) and `schema_version` are on every row.
Seeds and generator/simulator versions live once per episode in `episodes`; join to get them
(`trajectories_with_provenance` view does it for trajectories).

**`known_at`** (in the auto dictionary, repeated in the table docs): *when* a value becomes knowable inside the episode.
`static` < `creation` < `assignment` < `completion`; `row_time` = observed at that row's timestamp;
`episode_end` = whole-episode summary. A feature is only legal for a prediction made at time *T* if it was knowable at *T*.

## Lineage in one query
"Where did this trajectory row come from?"
```sql
SELECT t.sim_time_s, t.x, t.y,
       e.episode_id, e.random_seed, e.simulator_version,
       s.scenario_id, s.scenario_seed, s.generator_version, s.scenario_version, s.config_hash
FROM trajectories t
JOIN episodes  e USING (episode_id)
JOIN scenarios s USING (scenario_id)
WHERE t.episode_id = '<episode uuid>' AND t.sim_time_s = 12;
```

## Whole-episode event timeline (all event tables, in true order)
```sql
SELECT event_seq, sim_time_s, event_type, task_id, robot_id, NULL AS obstacle_id, payload FROM task_events     WHERE episode_id = '<uuid>'
UNION ALL
SELECT event_seq, sim_time_s, event_type, task_id, robot_id, NULL,               payload FROM robot_events    WHERE episode_id = '<uuid>'
UNION ALL
SELECT event_seq, sim_time_s, event_type, NULL,    NULL,     obstacle_id,        payload FROM obstacle_events WHERE episode_id = '<uuid>'
ORDER BY event_seq;
```

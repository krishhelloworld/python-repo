# What is filled, what is empty — and why

"Empty" is expected. Each table is created up front (Phase 1) so the schema is stable, but a table only gets rows
when the phase that *needs* it is built. Counts below are from the PostgreSQL database after the Stage 0 run.

## Database tables

| Table | Rows now | Filled by | Why it looks the way it does today |
|---|---:|---|---|
| `scenarios` | 1 | Phase 2 (fixed world) → Phase 6 (many) | One hand-authored scenario |
| `environments` | 1 | same | One 20×20 warehouse |
| `episodes` | 1 | every run | One run |
| `robot_types` | 1 | seeded by migration; grows in Phase 8 | Only `small_fast_robot`; the other 8 types need parameters (Phase 8) |
| `robots` | 1 | every run | `R1` |
| `tasks` | 1 | every run | `T1` |
| `charging_stations` | 1 | every run | `C1` (not used yet — battery never gets low) |
| `obstacles` | 3 | Phase 2 (static) → Phase 7 (dynamic) | 3 fixed obstacles, all `is_static = true` |
| `task_events` | 3 | every run | `TASK_CREATED`, `TASK_ASSIGNED`, `TASK_COMPLETED` |
| `robot_events` | 2 | every run | `ROBOT_STARTED`, `ROBOT_STOPPED` |
| `obstacle_events` | **0** | **Phase 7** (dynamic obstacles) | Static obstacles are part of the layout, not events. Nothing *changes* in Stage 0 |
| `trajectories` | 32 | every run | 1 robot × 32 ticks |
| `event_types` | 22 | seeded by migration | Vocabulary for all stages; `introduced_in_stage` tells you when each is first emitted. Only 5 are emitted today |
| `schema_migrations` | 1 | each migration | `001` |
| `external_sources` | **0** | **Phase 13** (external ingestion) | No external data exists yet |
| `datasets` | **0** | **Phase 15** (dataset builders) | You have not built a dataset yet |
| `dataset_versions` | **0** | **Phase 15** | same |
| `dataset_version_episodes` | **0** | **Phase 15** | Link table: which episodes belong to which dataset version |
| `experiment_metadata` | **0** | **Phase 14+** | You have not run experiments yet |
| `corruption_mechanisms` | **0** | **Phase 9** (failures + uncertainty) | No deliberate data-quality traps exist yet; Stage 0 is clean by design |

## Columns that are constant (zero variance) in Stage 0
These exist for later stages; today they cannot teach a model anything. Whether to drop them is *your* decision later.
`trajectories.nearby_robot_count` (always 0), `trajectories.local_congestion` (always 0),
`robots.sensor_reliability` (1.0), `robots.failure_probability_per_hour` (0.0), `tasks.delay_s` (0.0),
`tasks.cancelled` / `failed` (false), `tasks.depends_on` (`[]`), `episodes.n_robots` / `n_tasks` (1).

## Folders in `orbit-data/`

| Folder | Content now | Filled by |
|---|---|---|
| `schemas/sql/` | `001_core_schema.sql` | every schema change adds a new numbered file (old ones are never edited) |
| `raw/synthetic/stage0/<episode_id>/` | 3 Parquet files + `manifest.json` | every synthetic run |
| `raw/external/` | empty (`.gitkeep`) | Phase 13: downloaded files, archived untouched |
| `raw/derived/` | empty | data derived from other datasets (transformations you define) |
| `scenarios/` | empty | Phase 6+: exported scenario definitions (config files) if you want them on disk as well as in the DB |
| `maps/` | empty | Phase 7 / large maps: files referenced by `environments.map_uri` |
| `trajectories/` | empty | scale-up: big trajectory Parquet exports that no longer belong in PostgreSQL |
| `experiments/` | empty | Phase 14+: experiment configs and results |
| `exports/` | empty | Phase 15+: CSV / Parquet / JSON / NumPy dataset exports |
| `metadata/` | `data_dictionary.csv`, `.md` | regenerated whenever the row models change |
| `docs/` | these documents | — |

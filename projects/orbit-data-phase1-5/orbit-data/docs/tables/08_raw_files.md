# Raw files under `raw/`

Each synthetic episode is also written as files, **once**:
```
raw/synthetic/stage0/<episode_id>/
    manifest.json          provenance + content hash + per-file sha256 and row counts
    task_events.parquet
    robot_events.parquet
    trajectories.parquet
    (obstacle_events.parquet is only written when an episode has obstacle events)
```
The files are the same rows as the database (row counts and the episode `content_sha256` match). The database is for
querying and joins; Parquet is for pulling large tables into pandas/Polars. Only the three high-volume tables are written
as files; scenario/environment/robot/task definitions live in the DB (and `scenarios.config`).

## `manifest.json`
| Key | Meaning |
|---|---|
| `episode_id` | Which episode the folder belongs to |
| `content_sha256` | Same fingerprint as `episodes.content_sha256`. Re-running a generator compares against this and **refuses to overwrite** |
| `provenance` | `orbit.schema_version`, `orbit.generator_version`, `orbit.simulator_version`, `orbit.scenario_version`, `orbit.random_seed`, `orbit.episode_id`, `orbit.source_type` |
| `sim_epoch` | Simulated time of `sim_time_s = 0` |
| `files` | For each Parquet: `sha256` of the file and `rows` |
| `note` | Reminder that this is unmodified RAW synthetic data |

## Parquet details
- Same column names as the tables (including `episode_id` as text).
- `payload` in event files is a **JSON string** (its keys differ per event type; a string keeps one stable schema). Parse it yourself.
- `timestamp` columns are timezone-aware UTC.
- The same provenance keys as the manifest are embedded in each file's schema metadata (`orbit.*`).
- Files are set read-only (advisory — an administrator can still change them; the hash in the manifest is what proves integrity).
- `current_task_id` is NULL in the last rows (pandas shows it as `NaN`).

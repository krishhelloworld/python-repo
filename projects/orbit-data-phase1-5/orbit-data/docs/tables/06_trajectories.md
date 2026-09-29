# trajectories

**One row = one robot's state at one tick.** Primary key `(episode_id, robot_id, sim_time_s)`.
Stage 0: 1 robot × 32 ticks (`t = 0 … 31`) = 32 rows. This is the table that will grow to millions of rows; large runs will be
exported to Parquet (`trajectories/` folder / episode Parquet) rather than kept in PostgreSQL.

| Column | Unit | `known_at` | Meaning / how to read it |
|---|---|---|---|
| `episode_id`, `robot_id` | — | — | Which run, which robot |
| `sim_time_s` | s | row_time | Tick time on the simulated clock (0.0, 1.0, …) |
| `timestamp` | tz | row_time | `sim_epoch + sim_time_s` |
| `x`, `y` | m | row_time | Position = cell × `cell_size_m`. Anchor of the cell, not its centre |
| `velocity` | m/s | row_time | Speed averaged over `(t−dt, t]` (backward difference). Row 0 is 0 by definition |
| `acceleration` | m/s² | row_time | `(velocity_t − velocity_{t−dt}) / dt` |
| `battery_wh` | Wh | row_time | Remaining energy. In Stage 0 this is the **true** simulator value (no noise); Stage 4 adds separate *observed* values |
| `current_task_id` | — | row_time | Task being executed after events at `t` are applied; NULL when none |
| `status` | — | row_time | `idle`, `moving`, `loading`, `unloading`, `charging`, `waiting`, `failed`, `offline`. Stage 0 uses `moving` and `idle` |
| `nearby_robot_count` | count | row_time | Other robots in the neighbourhood. **Always 0 in Stage 0** (one robot) |
| `local_congestion` | index ≥ 0 | row_time | Congestion around the robot. **Always 0.0 in Stage 0** |
| `source_type`, `schema_version`, `created_at` | | audit | Provenance / audit |

## The Stage 0 episode, row by row (selected)
| t | (x, y) | velocity | accel | battery_wh | task | status | what is going on |
|---:|---|---:|---:|---:|---|---|---|
| 0 | (2, 3) | 0 | 0 | 100.000000 | T1 | moving | events at t=0 already applied (task assigned, robot started) so status is `moving` although it has not moved yet |
| 1 | (3, 3) | 1 | 1 | 99.948611 | T1 | moving | first step; speed jumps 0→1, so acceleration = 1 for one tick |
| 14–16 | (8, 9)–(8, 11) | 1 | 0 | ≈99.28–99.18 | T1 | moving | cruising up aisle A1 (x = 8) |
| 30 | (15, 18) | **1** | 0 | 98.458333 | *NULL* | idle | arrived; velocity is still 1 because it is the average over the last tick, but status is already `idle` (`ROBOT_STOPPED` and `TASK_COMPLETED` at t=30) |
| 31 | (15, 18) | 0 | −1 | 98.456944 | NULL | idle | settle tick: robot at rest, deceleration recorded |

## Things worth noticing (your EDA, your decisions)
- `velocity > 0` with `status = idle` at t = 30 is not a bug: `velocity` is an interval average, `status` is post-event state.
- `nearby_robot_count` and `local_congestion` have zero variance today; they become meaningful in Stage 3.
- Consecutive rows are strongly autocorrelated (position, battery). A random row-level train/test split will leak across
  time — group by `episode_id` (and consider `scenario_id`) when you split.
- `battery_wh` decreases linearly here; real degradation and noise arrive in Stage 4/9.
- View `trajectories_with_provenance` = this table joined to the episode's seed and versions.

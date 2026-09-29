# tasks

**One row = one task in one episode, written as its FINAL state after the episode finished.**
Primary key `(episode_id, task_id)`. Because RAW tables are append-only, the row is inserted once at the end — the
*history* of the task (created → assigned → completed) is in `task_events`. Never use a `tasks` row as if it were a
snapshot in time; columns are grouped below by when they become knowable.

| Column | Unit | `known_at` | Meaning |
|---|---|---|---|
| `episode_id`, `task_id` | — | creation | Identity (`T1`) |
| `task_type` | — | creation | `single` now. Allowed: single, multi_step, dependent, urgent, cancelled, rescheduled, batch, fragile, high_priority, time_window |
| `priority` | 1–5 | creation | 5 = highest. Stage 0: 3 |
| `creation_time_s` | s | creation | When the task appeared (0.0) |
| `pickup_x`, `pickup_y` | cells | creation | Where the load is (2, 3) |
| `destination_x`, `destination_y` | cells | creation | Where it must go (15, 18) |
| `payload_kg` | kg | creation | Load mass (5.0) |
| `deadline_s` | s | creation | **Absolute** simulated time by which it should be done (60.0), not a duration |
| `depends_on` | JSON list | creation | Task ids that must finish first. `[]` |
| `assigned_robot_id` | — | assignment | Robot chosen (`R1`); FK → `robots` |
| `assignment_time_s` | s | assignment | When it was assigned (0.0) |
| `expected_service_time_s` | s | assignment | The **planner's estimate**: planned path cells × cell size ÷ max speed (30.0). An *intended* value, not a measurement |
| `actual_service_time_s` | s | **completion** | `completion_time_s − assignment_time_s` (30.0). **Label** |
| `completion_time_s` | s | **completion** | When the task finished (30.0). **Label** |
| `cancelled` | bool | completion | Cancelled before completion (false) |
| `cancellation_time_s` | s | completion | NULL unless cancelled |
| `delay_s` | s | **completion** | `actual_service_time_s − expected_service_time_s`. Negative = early. Stage 0: 0.0 because nothing is uncertain. **Label** |
| `failed` | bool | completion | Task failed (false) |
| `failure_reason` | text | completion | NULL unless failed |
| `source_type`, `schema_version`, `created_at` | | audit | |

## Leakage warning (read before picking a target)
If your target is `actual_service_time_s`, `completion_time_s` or `delay_s`, then **every column marked `completion` is
off-limits as a feature**, and `expected_service_time_s` is only legal if your prediction time is *at or after*
assignment. `deadline_s` is legal from creation. The same reasoning applies to `task_events` (see 04_events.md).

## Reading tip
`tasks.expected_service_time_s == actual_service_time_s` for the only Stage 0 task, so it cannot yet teach you
anything about prediction error; the gap between them starts to carry information in Stages 2–4.

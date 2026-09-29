# Events: event_types, task_events, robot_events, obstacle_events

The world is an **evolving sequence of events**; tables like `trajectories` are what you get by sampling that world every tick.

## One counter, three tables
Every event in an episode gets an `event_seq` (0, 1, 2, …) from **one shared counter**. The events are split across three
tables by *what they are about*, but `event_seq` gives a single total order. Stage 0 episode:

| event_seq | table | event_type | sim_time_s | task | robot | payload |
|---:|---|---|---:|---|---|---|
| 0 | task_events | TASK_CREATED | 0 | T1 | — | `{"pickup":[2,3],"destination":[15,18],"deadline_s":60.0}` |
| 1 | task_events | TASK_ASSIGNED | 0 | T1 | R1 | `{"planner":"astar_manhattan_4conn","planned_path_cells":30,"expected_service_time_s":30.0}` |
| 2 | robot_events | ROBOT_STARTED | 0 | T1 | R1 | `{}` |
| 3 | robot_events | ROBOT_STOPPED | 30 | T1 | R1 | `{"reason":"goal_reached","x":15.0,"y":18.0}` |
| 4 | task_events | TASK_COMPLETED | 30 | T1 | R1 | `{"destination":[15,18]}` |

Two events can share a `sim_time_s` (0 and 30 above). **`event_seq`, not the time, is the tie-breaker.**
Later stages will deliberately add out-of-order timestamps and duplicates as documented data-quality traps; when they do,
`event_seq` still reflects the order the simulator *emitted* events.

## Which table does an event go to?
| Table | Holds events about | Emitted today |
|---|---|---|
| `task_events` | `TASK_*` | yes |
| `robot_events` | `ROBOT_*` | yes |
| `obstacle_events` | `OBSTACLE_*`, `AISLE_*` | **no** — Phase 7 |
| *(undecided)* | `CHARGING_*`, `COMMUNICATION_*`, `HUMAN_*`, `TRAFFIC_*` | no — you decide when you reach Stages 3–4 (charging and communication naturally fit `robot_events`; human/traffic events are zone-based and may need a new table or a `zone` in the payload) |

---
## `event_types` — the vocabulary (22 rows)
| Column | Meaning |
|---|---|
| `event_type` | Name, primary key. Every event row must use one of these (foreign key) — a typo is rejected by PostgreSQL |
| `category` | task / robot / obstacle / charging / communication / human / traffic |
| `description` | One line |
| `introduced_in_stage` | First stage that emits it |

Stage 0 emits 5 of the 22. By stage: **0** TASK_CREATED, TASK_ASSIGNED, TASK_COMPLETED, ROBOT_STARTED, ROBOT_STOPPED ·
**2** OBSTACLE_APPEARED/REMOVED, AISLE_BLOCKED/REOPENED, HUMAN_ENTERED_ZONE/LEFT_ZONE ·
**3** CHARGING_STARTED/COMPLETED, ROBOT_LOW_BATTERY, TRAFFIC_INCREASED/DECREASED ·
**4** ROBOT_FAILED/RECOVERED, COMMUNICATION_DELAY/FAILURE · **5** TASK_CANCELLED, TASK_PRIORITY_CHANGED.

---
## `task_events`
**One row = one thing that happened to a task.** Primary key `(episode_id, event_seq)`.

| Column | Meaning |
|---|---|
| `episode_id`, `event_seq` | Episode; position in the episode's total order |
| `event_type` | FK → `event_types` |
| `sim_time_s` | Event time on the simulated clock (s) |
| `timestamp` | `sim_epoch + sim_time_s` (simulated calendar time) |
| `task_id` | Task concerned (FK with `episode_id` → `tasks`). Always set |
| `robot_id` | Robot concerned; NULL when no robot is involved yet (e.g. `TASK_CREATED`) |
| `payload` | JSON with event-specific details. Keys differ per `event_type` (see table above) |
| `source_type`, `schema_version`, `created_at` | Provenance / audit |

## `robot_events`
**One row = one thing that happened to a robot.** Same columns as `task_events` except `robot_id` is always set and
`task_id` may be NULL (a robot event with no task, e.g. a breakdown while idle).

## `obstacle_events` (empty until Phase 7)
**One row = one change to an obstacle.** Same shape, but with `obstacle_id` (FK → `obstacles`) instead of task/robot ids.
The *effect on robots and routes* (which robots / routes were affected — required by the brief) will be stored in `payload`.

## Leakage notes
- Events are timestamped; a predictor working at time *T* may only use events with `sim_time_s <= T`
  (and, once observation delays exist in Stage 4, only those *observed* by *T*).
- `TASK_ASSIGNED.payload.planned_path_cells` and `expected_service_time_s` are knowable at assignment. They are
  **not** knowable at `TASK_CREATED`. A test enforces that the `TASK_CREATED` payload contains no future values.
- `TASK_COMPLETED` *is* the label event for "completion time" targets.

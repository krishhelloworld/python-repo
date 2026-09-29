# ORBIT data dictionary (auto-generated; do not edit)

`known_at` = when the value becomes knowable inside the episode (static < creation < assignment < completion; row_time = state at the row's timestamp; episode_end = whole-episode summary). Use it to reason about temporal leakage.

Tables without row models yet: event_types (reference vocabulary seeded by migration 001), external_sources (Phase 13 (external ingestion)), datasets (Phase 15 (dataset builders)), dataset_versions (Phase 15 (dataset builders)), dataset_version_episodes (Phase 15 (dataset builders)), experiment_metadata (Phase 14+ (experiments)), corruption_mechanisms (Phase 9 (failures + uncertainty / data-quality traps)), schema_migrations (infrastructure)


## scenarios

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| scenario_id | uuid |  | False | static |  | Deterministic uuid5 of (generator_version, scenario_version, scenario_seed, config_hash) |
| stage | integer |  | False | static | >=0 | Progression stage (0..12) that introduced this scenario family |
| difficulty_level | integer |  | False | static | 1-12 | Curriculum difficulty level |
| scenario_category | text |  | False | static |  | nominal | rare_event | adversarial | distribution_shift ... |
| scenario_seed | integer |  | True | static |  | Seed driving procedural layout generation (Stage 0: recorded, unused) |
| scenario_version | text |  | False | static |  | Version of the scenario definition |
| generator_version | text |  | False | static |  | Version of the scenario generator code |
| config | jsonb |  | False | static |  | Full scenario configuration used by the generator (JSON) |
| config_hash | text |  | False | static | 64 hex chars | sha256 of canonical JSON of config |
| source_type | text |  | False | static | synthetic|external|derived | synthetic | external | derived |
| schema_version | text |  | False | static |  | ORBIT schema version |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## environments

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| environment_id | uuid |  | False | static |  | Deterministic uuid5 derived from scenario_id |
| scenario_id | uuid |  | False | static |  | Scenario that produced this environment |
| environment_type | text |  | False | static |  | warehouse | factory | distribution_center | cross_dock | port | ... |
| width | integer | cells | False | static | >0 | Grid width |
| height | integer | cells | False | static | >0 | Grid height |
| cell_size_m | double precision | m | False | static | >0 | Edge length of one grid cell |
| map_representation | text |  | False | static |  | How the map is stored, e.g. occupancy_grid |
| map_grid | jsonb |  | True | static |  | Occupancy grid rows, index [y][x]; '.' free, '#' blocked. Null if map_uri is used |
| map_uri | text |  | True | static |  | Path to large map stored outside PostgreSQL |
| terrain_type | text |  | False | static |  | Floor/terrain class, e.g. smooth_concrete |
| obstacle_density | double precision | fraction | False | static | 0-1 | Fraction of grid cells blocked at t=0 |
| aisle_configuration | jsonb |  | False | static |  | Aisle layout description (JSON) |
| charging_station_locations | jsonb |  | False | static |  | Charging station cells [{station_id,x,y}] |
| loading_station_locations | jsonb |  | False | static |  | Loading station cells [{station_id,x,y}] |
| delivery_station_locations | jsonb |  | False | static |  | Delivery station cells [{station_id,x,y}] |
| environmental_conditions | jsonb |  | False | static |  | Ambient conditions (JSON) |
| environment_version | text |  | False | static |  | Version of the environment definition |
| scenario_version | text |  | False | static |  | Scenario version that produced this environment |
| scenario_seed | integer |  | True | static |  | Scenario seed that produced this environment |
| generator_version | text |  | False | static |  | Generator version that produced this environment |
| source_type | text |  | False | static | synthetic|external|derived | synthetic | external | derived |
| schema_version | text |  | False | static |  | ORBIT schema version |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## episodes

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| episode_id | uuid |  | False | static |  | Deterministic uuid5 of (scenario_id, random_seed, simulator_version, robot_configuration_version) |
| scenario_id | uuid |  | False | static |  | Scenario the episode was run in |
| environment_id | uuid |  | False | static |  | Environment the episode was run in |
| random_seed | integer |  | True | static |  | Seed driving stochastic dynamics (Stage 0: recorded, unused) |
| generator_version | text |  | False | static |  | Generator version |
| simulator_version | text |  | False | static |  | Simulator version |
| environment_version | text |  | False | static |  | Environment version |
| robot_configuration_version | text |  | False | static |  | Version of robot fleet configuration |
| scenario_version | text |  | False | static |  | Scenario version |
| schema_version | text |  | False | static |  | ORBIT schema version |
| source_type | text |  | False | static | synthetic|external|derived | synthetic | external | derived |
| external_source_id | text |  | True | static |  | external_sources.source_id when source_type=external |
| parent_dataset | text |  | True | static |  | Parent dataset when source_type=derived |
| transformation_description | text |  | True | static |  | How the data was derived when source_type=derived |
| sim_epoch | timestamptz |  | False | static |  | Simulated-clock time corresponding to sim_time_s = 0 (NOT wall-clock time) |
| tick_seconds | double precision | s | False | static | >0 | Simulation tick length |
| n_ticks | integer |  | False | episode_end |  | Number of simulated ticks (last sim_time_s / tick_seconds) |
| n_robots | integer |  | False | episode_end |  | Number of robots |
| n_tasks | integer |  | False | episode_end |  | Number of tasks |
| n_trajectory_rows | integer |  | False | episode_end |  | Number of trajectory rows |
| termination_reason | text |  | False | episode_end |  | Why the episode ended, e.g. all_tasks_completed |
| content_sha256 | text |  | False | episode_end | 64 hex chars | sha256 over canonical content of all episode rows (excludes created_at, raw_uri, itself) |
| raw_uri | text |  | True | episode_end |  | Relative path of the raw Parquet/manifest directory |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## robot_types

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| robot_type | text |  | False | static |  | Robot class name |
| description | text |  | False | static |  | Human description |
| introduced_in_stage | integer |  | False | static |  | Stage that introduced this type |
| max_speed_mps | double precision | m/s | False | static | >0 | Nominal maximum speed |
| battery_capacity_wh | double precision | Wh | False | static | >0 | Nominal battery capacity |
| payload_capacity_kg | double precision | kg | False | static | >=0 | Nominal payload capacity |
| length_m | double precision | m | False | static |  | Body length |
| width_m | double precision | m | False | static |  | Body width |
| turning_radius_m | double precision | m | False | static | >=0 | Minimum turning radius (0 = turns on the spot) |
| operating_cost_per_hour | double precision | currency_units/h | False | static | >=0 | Synthetic operating cost |
| communication_range_m | double precision | m | False | static |  | Radio range |
| sensor_reliability | double precision | fraction | False | static | 0-1 | Probability a sensor reading is valid (1 = perfect) |
| failure_probability_per_hour | double precision | 1/h | False | static | 0-1 | Nominal breakdown probability |
| energy_per_meter_wh | double precision | Wh/m | False | static | >=0 | Energy consumed per metre travelled |
| idle_power_w | double precision | W | False | static | >=0 | Baseline power draw (always on) |

## robots

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| source_type | text |  | False | static | synthetic|external|derived | Whether the row is synthetic, external, or derived data |
| schema_version | text |  | False | static |  | Version of the ORBIT schema the row was written under |
| episode_id | uuid |  | False | static |  | Owning episode |
| robot_id | text |  | False | static |  | Robot identifier within the episode, e.g. R1 |
| robot_type | text |  | False | static |  | FK to robot_types |
| initial_x | double precision | m | False | static |  | Start x |
| initial_y | double precision | m | False | static |  | Start y |
| initial_velocity | double precision | m/s | False | static |  | Start speed |
| initial_acceleration | double precision | m/s^2 | False | static |  | Start acceleration |
| max_speed_mps | double precision | m/s | False | static | >0 | Effective max speed of THIS robot |
| battery_capacity_wh | double precision | Wh | False | static | >0 | Effective battery capacity |
| initial_battery_wh | double precision | Wh | False | static | 0-battery_capacity_wh | Battery at t=0 |
| payload_capacity_kg | double precision | kg | False | static | >=0 | Effective payload capacity |
| length_m | double precision | m | False | static |  | Body length |
| width_m | double precision | m | False | static |  | Body width |
| turning_radius_m | double precision | m | False | static | >=0 | Turning radius |
| operating_cost_per_hour | double precision | currency_units/h | False | static | >=0 | Operating cost |
| communication_range_m | double precision | m | False | static |  | Radio range |
| sensor_reliability | double precision | fraction | False | static | 0-1 | Sensor validity probability |
| failure_probability_per_hour | double precision | 1/h | False | static | 0-1 | Breakdown probability |
| energy_per_meter_wh | double precision | Wh/m | False | static | >=0 | Energy per metre travelled |
| idle_power_w | double precision | W | False | static | >=0 | Baseline power draw |
| initial_maintenance_state | text |  | False | static |  | Maintenance state at t=0, e.g. nominal |
| initial_status | text |  | False | static |  | Status at t=0 BEFORE events at t=0 are applied |
| initial_task_id | text |  | True | static |  | Task held at t=0 (none in Stage 0) |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## tasks

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| source_type | text |  | False | static | synthetic|external|derived | Whether the row is synthetic, external, or derived data |
| schema_version | text |  | False | static |  | Version of the ORBIT schema the row was written under |
| episode_id | uuid |  | False | static |  | Owning episode |
| task_id | text |  | False | static |  | Task identifier within the episode, e.g. T1 |
| task_type | text |  | False | static |  | single | multi_step | dependent | urgent | ... |
| priority | integer |  | False | creation | 1-5 | 1 (lowest) .. 5 (highest) |
| creation_time_s | double precision | s | False | creation |  | Time the task was created |
| pickup_x | integer | cells | False | creation |  | Pickup cell x |
| pickup_y | integer | cells | False | creation |  | Pickup cell y |
| destination_x | integer | cells | False | creation |  | Destination cell x |
| destination_y | integer | cells | False | creation |  | Destination cell y |
| payload_kg | double precision | kg | False | creation | >=0 | Payload mass |
| deadline_s | double precision | s | True | creation |  | Absolute sim-time deadline |
| expected_service_time_s | double precision | s | True | assignment |  | PLANNER's estimate of service time at assignment (path length / max speed) |
| actual_service_time_s | double precision | s | True | completion |  | completion_time_s - assignment_time_s (LABEL: leaks outcome) |
| assigned_robot_id | text |  | True | assignment |  | Robot the task was assigned to |
| assignment_time_s | double precision | s | True | assignment |  | Time of assignment |
| completion_time_s | double precision | s | True | completion |  | Time of completion (LABEL: leaks outcome) |
| cancelled | boolean |  | False | completion |  | Whether the task was cancelled |
| cancellation_time_s | double precision | s | True | completion |  | Time of cancellation |
| delay_s | double precision | s | True | completion |  | actual_service_time_s - expected_service_time_s (negative = early) |
| failed | boolean |  | False | completion |  | Whether the task failed |
| failure_reason | text |  | True | completion |  | Reason for failure |
| depends_on | jsonb |  | False | creation |  | task_ids that must complete first (JSON list) |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## charging_stations

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| source_type | text |  | False | static | synthetic|external|derived | Whether the row is synthetic, external, or derived data |
| schema_version | text |  | False | static |  | Version of the ORBIT schema the row was written under |
| episode_id | uuid |  | False | static |  | Owning episode |
| station_id | text |  | False | static |  | Station identifier, e.g. C1 |
| x | integer | cells | False | static |  | Cell x |
| y | integer | cells | False | static |  | Cell y |
| power_w | double precision | W | False | static | >0 | Charging power |
| n_slots | integer |  | False | static | >0 | Simultaneous charging slots |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## obstacles

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| source_type | text |  | False | static | synthetic|external|derived | Whether the row is synthetic, external, or derived data |
| schema_version | text |  | False | static |  | Version of the ORBIT schema the row was written under |
| episode_id | uuid |  | False | static |  | Owning episode |
| obstacle_id | text |  | False | static |  | Obstacle identifier, e.g. O1 |
| obstacle_kind | text |  | False | static |  | wall | shelf | fallen_package | ... |
| cause | text |  | False | static |  | Why the obstacle exists (fixed_infrastructure for static ones) |
| is_static | boolean |  | False | static |  | True if part of the layout from t=0 and never removed |
| x_min | integer | cells | False | static |  | Rectangle min x (inclusive) |
| y_min | integer | cells | False | static |  | Rectangle min y (inclusive) |
| x_max | integer | cells | False | static |  | Rectangle max x (inclusive) |
| y_max | integer | cells | False | static |  | Rectangle max y (inclusive) |
| appear_time_s | double precision | s | False | static |  | Time obstacle appears |
| remove_time_s | double precision | s | True | static |  | Time obstacle is removed (null = never) |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## task_events

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| source_type | text |  | False | static | synthetic|external|derived | Whether the row is synthetic, external, or derived data |
| schema_version | text |  | False | static |  | Version of the ORBIT schema the row was written under |
| episode_id | uuid |  | False | static |  | Owning episode |
| event_seq | integer |  | False | static | >=0 | Per-episode monotone counter shared by all event tables (total order) |
| event_type | text |  | False | static |  | FK to event_types |
| sim_time_s | double precision | s | False | static |  | Event time on the simulated clock |
| timestamp | timestamptz |  | False | static |  | sim_epoch + sim_time_s (simulated clock) |
| payload | jsonb |  | False | static |  | Event-specific details (JSON) |
| task_id | text |  | False | static |  | Task concerned |
| robot_id | text |  | True | static |  | Robot concerned, if any |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## robot_events

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| source_type | text |  | False | static | synthetic|external|derived | Whether the row is synthetic, external, or derived data |
| schema_version | text |  | False | static |  | Version of the ORBIT schema the row was written under |
| episode_id | uuid |  | False | static |  | Owning episode |
| event_seq | integer |  | False | static | >=0 | Per-episode monotone counter shared by all event tables (total order) |
| event_type | text |  | False | static |  | FK to event_types |
| sim_time_s | double precision | s | False | static |  | Event time on the simulated clock |
| timestamp | timestamptz |  | False | static |  | sim_epoch + sim_time_s (simulated clock) |
| payload | jsonb |  | False | static |  | Event-specific details (JSON) |
| robot_id | text |  | False | static |  | Robot concerned |
| task_id | text |  | True | static |  | Task concerned, if any |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## obstacle_events

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| source_type | text |  | False | static | synthetic|external|derived | Whether the row is synthetic, external, or derived data |
| schema_version | text |  | False | static |  | Version of the ORBIT schema the row was written under |
| episode_id | uuid |  | False | static |  | Owning episode |
| event_seq | integer |  | False | static | >=0 | Per-episode monotone counter shared by all event tables (total order) |
| event_type | text |  | False | static |  | FK to event_types |
| sim_time_s | double precision | s | False | static |  | Event time on the simulated clock |
| timestamp | timestamptz |  | False | static |  | sim_epoch + sim_time_s (simulated clock) |
| payload | jsonb |  | False | static |  | Event-specific details (JSON) |
| obstacle_id | text |  | False | static |  | Obstacle concerned |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

## trajectories

| field | type | unit | nullable | known_at | range | description |
|---|---|---|---|---|---|---|
| source_type | text |  | False | static | synthetic|external|derived | Whether the row is synthetic, external, or derived data |
| schema_version | text |  | False | static |  | Version of the ORBIT schema the row was written under |
| episode_id | uuid |  | False | static |  | Owning episode |
| robot_id | text |  | False | static |  | Robot |
| sim_time_s | double precision | s | False | row_time |  | Tick time on the simulated clock |
| timestamp | timestamptz |  | False | row_time |  | sim_epoch + sim_time_s |
| x | double precision | m | False | row_time |  | Position x = cell_x * cell_size_m (cell anchor, not centre) |
| y | double precision | m | False | row_time |  | Position y = cell_y * cell_size_m |
| velocity | double precision | m/s | False | row_time | >=0 | Average speed over (t-dt, t]; 0 at t=0 (backward difference) |
| acceleration | double precision | m/s^2 | False | row_time |  | (velocity_t - velocity_{t-dt}) / dt |
| battery_wh | double precision | Wh | False | row_time | >=0 | Remaining battery (true simulator value in Stage 0) |
| current_task_id | text |  | True | row_time |  | Task being executed after events at t are applied |
| status | text |  | False | row_time |  | Robot status after events at t are applied |
| nearby_robot_count | integer |  | False | row_time | >=0 | Other robots within the neighbourhood radius (0 by construction in Stage 0) |
| local_congestion | double precision | index | False | row_time | >=0 | Local congestion index (0 by construction in Stage 0) |
| created_at | timestamptz |  | False | audit |  | Wall-clock DB insert time. Audit only; excluded from content hash. |

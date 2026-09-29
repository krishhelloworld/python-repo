"""Pydantic row models = the single source of truth for the data dictionary.

Each model corresponds to one PostgreSQL table (same column names). Nothing here cleans or
transforms data: models only *validate structure* of what the simulator emitted.

`known_at` (used by the data dictionary) tells you WHEN a field's value becomes knowable inside
the episode. It exists so you can reason about temporal leakage yourself:
  static      fixed before the episode starts (configuration)
  creation    known when the object (e.g. a task) is created
  assignment  known once the task is assigned
  completion  only known after the task finishes  -> never a legal feature for predicting it
  row_time    state observed at this row's timestamp
  episode_end summary of the whole episode
"""
import datetime as dt
import uuid
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from .versions import SCHEMA_VERSION


def F(default: Any = ..., *, desc: str, unit: str | None = None, rng: str | None = None,
      source: str = "simulator", known_at: str = "static", origin: str = "synthetic"):
    return Field(default, description=desc, json_schema_extra={
        "unit": unit, "possible_range": rng, "source": source, "known_at": known_at, "origin": origin})


Status = Literal["idle", "moving", "loading", "unloading", "charging", "waiting", "failed", "offline"]
TaskType = Literal["single", "multi_step", "dependent", "urgent", "cancelled", "rescheduled",
                   "batch", "fragile", "high_priority", "time_window"]
SourceType = Literal["synthetic", "external", "derived"]


class _Row(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class _Prov(_Row):
    source_type: SourceType = F("synthetic", desc="Whether the row is synthetic, external, or derived data",
                                rng="synthetic|external|derived")
    schema_version: str = F(SCHEMA_VERSION, desc="Version of the ORBIT schema the row was written under")


# ------------------------------------------------------------------ scenario / environment / episode
class Scenario(_Row):
    scenario_id: uuid.UUID = F(desc="Deterministic uuid5 of (generator_version, scenario_version, scenario_seed, config_hash)")
    stage: int = F(desc="Progression stage (0..12) that introduced this scenario family", rng=">=0")
    difficulty_level: int = F(desc="Curriculum difficulty level", rng="1-12")
    scenario_category: str = F("nominal", desc="nominal | rare_event | adversarial | distribution_shift ...")
    scenario_seed: Optional[int] = F(desc="Seed driving procedural layout generation (Stage 0: recorded, unused)")
    scenario_version: str = F(desc="Version of the scenario definition")
    generator_version: str = F(desc="Version of the scenario generator code")
    config: dict[str, Any] = F(desc="Full scenario configuration used by the generator (JSON)")
    config_hash: str = F(desc="sha256 of canonical JSON of config", rng="64 hex chars")
    source_type: SourceType = F("synthetic", desc="synthetic | external | derived", rng="synthetic|external|derived")
    schema_version: str = F(SCHEMA_VERSION, desc="ORBIT schema version")


class Environment(_Row):
    environment_id: uuid.UUID = F(desc="Deterministic uuid5 derived from scenario_id")
    scenario_id: uuid.UUID = F(desc="Scenario that produced this environment")
    environment_type: str = F(desc="warehouse | factory | distribution_center | cross_dock | port | ...")
    width: int = F(desc="Grid width", unit="cells", rng=">0")
    height: int = F(desc="Grid height", unit="cells", rng=">0")
    cell_size_m: float = F(desc="Edge length of one grid cell", unit="m", rng=">0")
    map_representation: str = F(desc="How the map is stored, e.g. occupancy_grid")
    map_grid: Optional[list[str]] = F(desc="Occupancy grid rows, index [y][x]; '.' free, '#' blocked. Null if map_uri is used")
    map_uri: Optional[str] = F(desc="Path to large map stored outside PostgreSQL")
    terrain_type: str = F(desc="Floor/terrain class, e.g. smooth_concrete")
    obstacle_density: float = F(desc="Fraction of grid cells blocked at t=0", unit="fraction", rng="0-1")
    aisle_configuration: dict[str, Any] = F(desc="Aisle layout description (JSON)")
    charging_station_locations: list[Any] = F(desc="Charging station cells [{station_id,x,y}]")
    loading_station_locations: list[Any] = F(desc="Loading station cells [{station_id,x,y}]")
    delivery_station_locations: list[Any] = F(desc="Delivery station cells [{station_id,x,y}]")
    environmental_conditions: dict[str, Any] = F(desc="Ambient conditions (JSON)")
    environment_version: str = F(desc="Version of the environment definition")
    scenario_version: str = F(desc="Scenario version that produced this environment")
    scenario_seed: Optional[int] = F(desc="Scenario seed that produced this environment")
    generator_version: str = F(desc="Generator version that produced this environment")
    source_type: SourceType = F("synthetic", desc="synthetic | external | derived", rng="synthetic|external|derived")
    schema_version: str = F(SCHEMA_VERSION, desc="ORBIT schema version")


class Episode(_Row):
    episode_id: uuid.UUID = F(desc="Deterministic uuid5 of (scenario_id, random_seed, simulator_version, robot_configuration_version)")
    scenario_id: uuid.UUID = F(desc="Scenario the episode was run in")
    environment_id: uuid.UUID = F(desc="Environment the episode was run in")
    random_seed: Optional[int] = F(desc="Seed driving stochastic dynamics (Stage 0: recorded, unused)")
    generator_version: str = F(desc="Generator version")
    simulator_version: str = F(desc="Simulator version")
    environment_version: str = F(desc="Environment version")
    robot_configuration_version: str = F(desc="Version of robot fleet configuration")
    scenario_version: str = F(desc="Scenario version")
    schema_version: str = F(SCHEMA_VERSION, desc="ORBIT schema version")
    source_type: SourceType = F("synthetic", desc="synthetic | external | derived", rng="synthetic|external|derived")
    external_source_id: Optional[str] = F(None, desc="external_sources.source_id when source_type=external")
    parent_dataset: Optional[str] = F(None, desc="Parent dataset when source_type=derived")
    transformation_description: Optional[str] = F(None, desc="How the data was derived when source_type=derived")
    sim_epoch: dt.datetime = F(desc="Simulated-clock time corresponding to sim_time_s = 0 (NOT wall-clock time)")
    tick_seconds: float = F(desc="Simulation tick length", unit="s", rng=">0")
    n_ticks: int = F(desc="Number of simulated ticks (last sim_time_s / tick_seconds)", known_at="episode_end")
    n_robots: int = F(desc="Number of robots", known_at="episode_end")
    n_tasks: int = F(desc="Number of tasks", known_at="episode_end")
    n_trajectory_rows: int = F(desc="Number of trajectory rows", known_at="episode_end")
    termination_reason: str = F(desc="Why the episode ended, e.g. all_tasks_completed", known_at="episode_end")
    content_sha256: str = F(desc="sha256 over canonical content of all episode rows (excludes created_at, raw_uri, itself)",
                            rng="64 hex chars", known_at="episode_end")
    raw_uri: Optional[str] = F(None, desc="Relative path of the raw Parquet/manifest directory", known_at="episode_end")


# ------------------------------------------------------------------ robots & types
class RobotType(_Row):
    robot_type: str = F(desc="Robot class name")
    description: str = F(desc="Human description")
    introduced_in_stage: int = F(desc="Stage that introduced this type")
    max_speed_mps: float = F(desc="Nominal maximum speed", unit="m/s", rng=">0")
    battery_capacity_wh: float = F(desc="Nominal battery capacity", unit="Wh", rng=">0")
    payload_capacity_kg: float = F(desc="Nominal payload capacity", unit="kg", rng=">=0")
    length_m: float = F(desc="Body length", unit="m")
    width_m: float = F(desc="Body width", unit="m")
    turning_radius_m: float = F(desc="Minimum turning radius (0 = turns on the spot)", unit="m", rng=">=0")
    operating_cost_per_hour: float = F(desc="Synthetic operating cost", unit="currency_units/h", rng=">=0")
    communication_range_m: float = F(desc="Radio range", unit="m")
    sensor_reliability: float = F(desc="Probability a sensor reading is valid (1 = perfect)", unit="fraction", rng="0-1")
    failure_probability_per_hour: float = F(desc="Nominal breakdown probability", unit="1/h", rng="0-1")
    energy_per_meter_wh: float = F(desc="Energy consumed per metre travelled", unit="Wh/m", rng=">=0")
    idle_power_w: float = F(desc="Baseline power draw (always on)", unit="W", rng=">=0")


class Robot(_Prov):
    episode_id: uuid.UUID = F(desc="Owning episode")
    robot_id: str = F(desc="Robot identifier within the episode, e.g. R1")
    robot_type: str = F(desc="FK to robot_types")
    initial_x: float = F(desc="Start x", unit="m", known_at="static")
    initial_y: float = F(desc="Start y", unit="m", known_at="static")
    initial_velocity: float = F(desc="Start speed", unit="m/s")
    initial_acceleration: float = F(desc="Start acceleration", unit="m/s^2")
    max_speed_mps: float = F(desc="Effective max speed of THIS robot", unit="m/s", rng=">0")
    battery_capacity_wh: float = F(desc="Effective battery capacity", unit="Wh", rng=">0")
    initial_battery_wh: float = F(desc="Battery at t=0", unit="Wh", rng="0-battery_capacity_wh")
    payload_capacity_kg: float = F(desc="Effective payload capacity", unit="kg", rng=">=0")
    length_m: float = F(desc="Body length", unit="m")
    width_m: float = F(desc="Body width", unit="m")
    turning_radius_m: float = F(desc="Turning radius", unit="m", rng=">=0")
    operating_cost_per_hour: float = F(desc="Operating cost", unit="currency_units/h", rng=">=0")
    communication_range_m: float = F(desc="Radio range", unit="m")
    sensor_reliability: float = F(desc="Sensor validity probability", unit="fraction", rng="0-1")
    failure_probability_per_hour: float = F(desc="Breakdown probability", unit="1/h", rng="0-1")
    energy_per_meter_wh: float = F(desc="Energy per metre travelled", unit="Wh/m", rng=">=0")
    idle_power_w: float = F(desc="Baseline power draw", unit="W", rng=">=0")
    initial_maintenance_state: str = F(desc="Maintenance state at t=0, e.g. nominal")
    initial_status: Status = F(desc="Status at t=0 BEFORE events at t=0 are applied")
    initial_task_id: Optional[str] = F(desc="Task held at t=0 (none in Stage 0)")


# ------------------------------------------------------------------ tasks
class Task(_Prov):
    episode_id: uuid.UUID = F(desc="Owning episode")
    task_id: str = F(desc="Task identifier within the episode, e.g. T1")
    task_type: TaskType = F(desc="single | multi_step | dependent | urgent | ...")
    priority: int = F(desc="1 (lowest) .. 5 (highest)", rng="1-5", known_at="creation")
    creation_time_s: float = F(desc="Time the task was created", unit="s", known_at="creation")
    pickup_x: int = F(desc="Pickup cell x", unit="cells", known_at="creation")
    pickup_y: int = F(desc="Pickup cell y", unit="cells", known_at="creation")
    destination_x: int = F(desc="Destination cell x", unit="cells", known_at="creation")
    destination_y: int = F(desc="Destination cell y", unit="cells", known_at="creation")
    payload_kg: float = F(desc="Payload mass", unit="kg", rng=">=0", known_at="creation")
    deadline_s: Optional[float] = F(desc="Absolute sim-time deadline", unit="s", known_at="creation")
    expected_service_time_s: Optional[float] = F(desc="PLANNER's estimate of service time at assignment (path length / max speed)",
                                                 unit="s", known_at="assignment", source="planner")
    actual_service_time_s: Optional[float] = F(desc="completion_time_s - assignment_time_s (LABEL: leaks outcome)",
                                               unit="s", known_at="completion")
    assigned_robot_id: Optional[str] = F(desc="Robot the task was assigned to", known_at="assignment")
    assignment_time_s: Optional[float] = F(desc="Time of assignment", unit="s", known_at="assignment")
    completion_time_s: Optional[float] = F(desc="Time of completion (LABEL: leaks outcome)", unit="s", known_at="completion")
    cancelled: bool = F(desc="Whether the task was cancelled", known_at="completion")
    cancellation_time_s: Optional[float] = F(desc="Time of cancellation", unit="s", known_at="completion")
    delay_s: Optional[float] = F(desc="actual_service_time_s - expected_service_time_s (negative = early)", unit="s",
                                 known_at="completion")
    failed: bool = F(desc="Whether the task failed", known_at="completion")
    failure_reason: Optional[str] = F(desc="Reason for failure", known_at="completion")
    depends_on: list[str] = F(desc="task_ids that must complete first (JSON list)", known_at="creation")


class ChargingStation(_Prov):
    episode_id: uuid.UUID = F(desc="Owning episode")
    station_id: str = F(desc="Station identifier, e.g. C1")
    x: int = F(desc="Cell x", unit="cells")
    y: int = F(desc="Cell y", unit="cells")
    power_w: float = F(desc="Charging power", unit="W", rng=">0")
    n_slots: int = F(desc="Simultaneous charging slots", rng=">0")


class Obstacle(_Prov):
    episode_id: uuid.UUID = F(desc="Owning episode")
    obstacle_id: str = F(desc="Obstacle identifier, e.g. O1")
    obstacle_kind: str = F(desc="wall | shelf | fallen_package | ...")
    cause: str = F(desc="Why the obstacle exists (fixed_infrastructure for static ones)")
    is_static: bool = F(desc="True if part of the layout from t=0 and never removed")
    x_min: int = F(desc="Rectangle min x (inclusive)", unit="cells")
    y_min: int = F(desc="Rectangle min y (inclusive)", unit="cells")
    x_max: int = F(desc="Rectangle max x (inclusive)", unit="cells")
    y_max: int = F(desc="Rectangle max y (inclusive)", unit="cells")
    appear_time_s: float = F(desc="Time obstacle appears", unit="s")
    remove_time_s: Optional[float] = F(desc="Time obstacle is removed (null = never)", unit="s")


# ------------------------------------------------------------------ events
class _Event(_Prov):
    episode_id: uuid.UUID = F(desc="Owning episode")
    event_seq: int = F(desc="Per-episode monotone counter shared by all event tables (total order)", rng=">=0")
    event_type: str = F(desc="FK to event_types")
    sim_time_s: float = F(desc="Event time on the simulated clock", unit="s")
    timestamp: dt.datetime = F(desc="sim_epoch + sim_time_s (simulated clock)")
    payload: dict[str, Any] = F(desc="Event-specific details (JSON)")


class TaskEvent(_Event):
    task_id: str = F(desc="Task concerned")
    robot_id: Optional[str] = F(desc="Robot concerned, if any")


class RobotEvent(_Event):
    robot_id: str = F(desc="Robot concerned")
    task_id: Optional[str] = F(desc="Task concerned, if any")


class ObstacleEvent(_Event):
    obstacle_id: str = F(desc="Obstacle concerned")


# ------------------------------------------------------------------ trajectories
class TrajectoryPoint(_Prov):
    episode_id: uuid.UUID = F(desc="Owning episode")
    robot_id: str = F(desc="Robot")
    sim_time_s: float = F(desc="Tick time on the simulated clock", unit="s", known_at="row_time")
    timestamp: dt.datetime = F(desc="sim_epoch + sim_time_s", known_at="row_time")
    x: float = F(desc="Position x = cell_x * cell_size_m (cell anchor, not centre)", unit="m", known_at="row_time")
    y: float = F(desc="Position y = cell_y * cell_size_m", unit="m", known_at="row_time")
    velocity: float = F(desc="Average speed over (t-dt, t]; 0 at t=0 (backward difference)", unit="m/s", rng=">=0", known_at="row_time")
    acceleration: float = F(desc="(velocity_t - velocity_{t-dt}) / dt", unit="m/s^2", known_at="row_time")
    battery_wh: float = F(desc="Remaining battery (true simulator value in Stage 0)", unit="Wh", rng=">=0", known_at="row_time")
    current_task_id: Optional[str] = F(desc="Task being executed after events at t are applied", known_at="row_time")
    status: Status = F(desc="Robot status after events at t are applied", known_at="row_time")
    nearby_robot_count: int = F(desc="Other robots within the neighbourhood radius (0 by construction in Stage 0)", rng=">=0", known_at="row_time")
    local_congestion: float = F(desc="Local congestion index (0 by construction in Stage 0)", unit="index", rng=">=0", known_at="row_time")


# ------------------------------------------------------------------ registry
TABLE_MODELS: dict[str, type[BaseModel]] = {
    "scenarios": Scenario, "environments": Environment, "episodes": Episode,
    "robot_types": RobotType, "robots": Robot, "tasks": Task,
    "charging_stations": ChargingStation, "obstacles": Obstacle,
    "task_events": TaskEvent, "robot_events": RobotEvent, "obstacle_events": ObstacleEvent,
    "trajectories": TrajectoryPoint,
}
# Row models for these tables arrive with the stage that first fills them.
DEFERRED_TABLES: dict[str, str] = {
    "event_types": "reference vocabulary seeded by migration 001",
    "external_sources": "Phase 13 (external ingestion)",
    "datasets": "Phase 15 (dataset builders)",
    "dataset_versions": "Phase 15 (dataset builders)",
    "dataset_version_episodes": "Phase 15 (dataset builders)",
    "experiment_metadata": "Phase 14+ (experiments)",
    "corruption_mechanisms": "Phase 9 (failures + uncertainty / data-quality traps)",
    "schema_migrations": "infrastructure",
}
# Insert order respecting foreign keys; also the order used for the content hash.
TABLE_ORDER = ["scenarios", "environments", "episodes", "robots", "tasks", "charging_stations",
               "obstacles", "task_events", "robot_events", "obstacle_events", "trajectories"]
TABLE_PK: dict[str, tuple[str, ...]] = {
    "scenarios": ("scenario_id",), "environments": ("environment_id",), "episodes": ("episode_id",),
    "robots": ("episode_id", "robot_id"), "tasks": ("episode_id", "task_id"),
    "charging_stations": ("episode_id", "station_id"), "obstacles": ("episode_id", "obstacle_id"),
    "task_events": ("episode_id", "event_seq"), "robot_events": ("episode_id", "event_seq"),
    "obstacle_events": ("episode_id", "event_seq"),
    "trajectories": ("episode_id", "robot_id", "sim_time_s"),
}

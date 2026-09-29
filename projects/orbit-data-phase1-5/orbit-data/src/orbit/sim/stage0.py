"""Stage 0 -- controlled synthetic world (Phases 2-5): one fixed warehouse, one robot, one task.

Deterministic: no randomness is consumed. `seed` is still recorded so the schema and the
(seed + versions -> same episode) contract are exercised from day one.

Conventions
  * grid cell (cx, cy); position x = cx * cell_size_m
  * a row at time t is the state AFTER all events with sim_time <= t were applied
  * velocity_t = distance moved in (t-dt, t] / dt   (backward difference)
"""
import datetime as dt
import heapq
import uuid
from dataclasses import dataclass, replace

from .. import versions as V
from ..catalog import SMALL_FAST_ROBOT
from ..hashing import canonical_json_hash, content_hash
from ..models import (ChargingStation, Environment, Episode, Obstacle, Robot, RobotEvent,
                      Scenario, Task, TaskEvent, TrajectoryPoint)

NAMESPACE = uuid.UUID("6f0f5a52-3b1e-4c0e-9c55-0a7b1d2e9f10")
SIM_EPOCH = dt.datetime(2026, 1, 5, 8, 0, 0, tzinfo=dt.timezone.utc)  # simulated clock, a Monday 08:00
TICK_SECONDS = 1.0

STAGE0_CONFIG = {
    "width": 20, "height": 20, "cell_size_m": 1.0,
    "obstacles": [
        {"obstacle_id": "O1", "kind": "wall",  "x_min": 7,  "y_min": 3, "x_max": 7,  "y_max": 19},
        {"obstacle_id": "O2", "kind": "shelf", "x_min": 10, "y_min": 5, "x_max": 11, "y_max": 12},
        {"obstacle_id": "O3", "kind": "shelf", "x_min": 13, "y_min": 6, "x_max": 14, "y_max": 16},
    ],
    "aisles": [
        {"aisle_id": "A1", "orientation": "vertical",   "x_min": 8,  "x_max": 9,  "y_min": 0, "y_max": 19},
        {"aisle_id": "A2", "orientation": "vertical",   "x_min": 12, "x_max": 12, "y_min": 0, "y_max": 19},
        {"aisle_id": "A3", "orientation": "horizontal", "x_min": 0,  "x_max": 19, "y_min": 0, "y_max": 2},
    ],
    "charging_stations": [{"station_id": "C1", "x": 1, "y": 1, "power_w": 200.0, "n_slots": 1}],
    "loading_stations":  [{"station_id": "L1", "x": 2, "y": 3}],
    "delivery_stations": [{"station_id": "D1", "x": 15, "y": 18}],
    "robots": [{"robot_id": "R1", "robot_type": "small_fast_robot", "start": [2, 3], "initial_battery_wh": 100.0}],
    "tasks": [{"task_id": "T1", "pickup": [2, 3], "destination": [15, 18], "payload_kg": 5.0,
               "priority": 3, "creation_time_s": 0.0, "deadline_s": 60.0}],
    "planner": "astar_manhattan_4conn",
}


class NoPathError(Exception):
    pass


def build_grid(cfg: dict) -> list[str]:
    grid = [["."] * cfg["width"] for _ in range(cfg["height"])]
    for o in cfg["obstacles"]:
        for y in range(o["y_min"], o["y_max"] + 1):
            for x in range(o["x_min"], o["x_max"] + 1):
                grid[y][x] = "#"
    return ["".join(r) for r in grid]


def astar(grid: list[str], start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
    """4-connected A*, unit step cost, Manhattan heuristic; ties broken by (h, x, y) -> deterministic."""
    w, h = len(grid[0]), len(grid)
    hf = lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
    open_ = [(hf(start), hf(start), start[0], start[1])]
    g, parent, closed = {start: 0}, {}, set()
    while open_:
        _, _, x, y = heapq.heappop(open_)
        if (x, y) in closed:
            continue
        closed.add((x, y))
        if (x, y) == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return path[::-1]
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] == "." and (nx, ny) not in closed:
                ng = g[(x, y)] + 1
                if ng < g.get((nx, ny), 10 ** 9):
                    g[(nx, ny)], parent[(nx, ny)] = ng, (x, y)
                    heapq.heappush(open_, (ng + hf((nx, ny)), hf((nx, ny)), nx, ny))
    raise NoPathError(f"no path {start} -> {goal}")


class EventLogger:
    """Single ordered log; every important state change becomes an event."""

    def __init__(self, episode_id: uuid.UUID):
        self.episode_id, self._seq = episode_id, 0
        self.task_events: list[TaskEvent] = []
        self.robot_events: list[RobotEvent] = []

    def _common(self, etype: str, t: float, payload: dict) -> dict:
        seq, self._seq = self._seq, self._seq + 1
        return dict(episode_id=self.episode_id, event_seq=seq, event_type=etype, sim_time_s=t,
                    timestamp=SIM_EPOCH + dt.timedelta(seconds=t), payload=payload or {})

    def task(self, etype, t, task_id, robot_id=None, payload=None):
        self.task_events.append(TaskEvent(**self._common(etype, t, payload), task_id=task_id, robot_id=robot_id))

    def robot(self, etype, t, robot_id, task_id=None, payload=None):
        self.robot_events.append(RobotEvent(**self._common(etype, t, payload), robot_id=robot_id, task_id=task_id))


@dataclass(frozen=True)
class EpisodeBundle:
    tables: dict

    @property
    def episode(self) -> Episode:
        return self.tables["episodes"][0]

    def with_raw_uri(self, uri: str) -> "EpisodeBundle":
        t = dict(self.tables)
        t["episodes"] = [self.episode.model_copy(update={"raw_uri": uri})]
        return replace(self, tables=t)


def generate_stage0_episode(seed: int = 0) -> EpisodeBundle:
    cfg = STAGE0_CONFIG
    grid = build_grid(cfg)
    cell = cfg["cell_size_m"]
    rcfg, tcfg = cfg["robots"][0], cfg["tasks"][0]          # Stage 0 = exactly one robot, one task
    rt = SMALL_FAST_ROBOT

    # ---- identities (deterministic) ----
    config_hash = canonical_json_hash(cfg)
    scenario_id = uuid.uuid5(NAMESPACE, f"scenario|{V.GENERATOR_VERSION}|{V.SCENARIO_VERSION}|{seed}|{config_hash}")
    environment_id = uuid.uuid5(NAMESPACE, f"environment|{scenario_id}|{V.ENVIRONMENT_VERSION}")
    episode_id = uuid.uuid5(NAMESPACE, f"episode|{scenario_id}|{seed}|{V.SIMULATOR_VERSION}|{V.ROBOT_CONFIGURATION_VERSION}")

    # ---- plan ----
    start, goal = tuple(tcfg["pickup"]), tuple(tcfg["destination"])
    assert tuple(rcfg["start"]) == start
    path = astar(grid, start, goal)
    n_steps = len(path) - 1
    cells_per_tick = rt.max_speed_mps * TICK_SECONDS / cell
    assert cells_per_tick == 1.0, "Stage 0 moves exactly one cell per tick"
    expected_service = n_steps * cell / rt.max_speed_mps

    # ---- simulate, logging events ----
    log = EventLogger(episode_id)
    rid, tid = rcfg["robot_id"], tcfg["task_id"]
    t_create = tcfg["creation_time_s"]
    log.task("TASK_CREATED", t_create, tid, payload={
        "pickup": list(start), "destination": list(goal), "deadline_s": tcfg["deadline_s"]})
    log.task("TASK_ASSIGNED", 0.0, tid, rid, payload={
        "planner": cfg["planner"], "planned_path_cells": n_steps, "expected_service_time_s": expected_service})
    log.robot("ROBOT_STARTED", 0.0, rid, tid)

    t_arrive = n_steps * TICK_SECONDS
    last_tick = n_steps + 1                                   # one settle tick after arrival (v -> 0)
    traj: list[TrajectoryPoint] = []
    prev_v = 0.0
    for k in range(last_tick + 1):
        t = k * TICK_SECONDS
        cx, cy = path[min(k, n_steps)]
        dist_m = min(k, n_steps) * cell
        step_m = cell if 1 <= k <= n_steps else 0.0
        v = step_m / TICK_SECONDS
        a = (v - prev_v) / TICK_SECONDS if k > 0 else 0.0
        prev_v = v
        arrived = k >= n_steps
        if k == n_steps:
            log.robot("ROBOT_STOPPED", t, rid, tid, payload={"reason": "goal_reached", "x": cx * cell, "y": cy * cell})
            log.task("TASK_COMPLETED", t, tid, rid, payload={"destination": list(goal)})
        battery = round(rcfg["initial_battery_wh"] - rt.energy_per_meter_wh * dist_m
                        - rt.idle_power_w * t / 3600.0, 9)
        traj.append(TrajectoryPoint(
            episode_id=episode_id, robot_id=rid, sim_time_s=t, timestamp=SIM_EPOCH + dt.timedelta(seconds=t),
            x=cx * cell, y=cy * cell, velocity=v, acceleration=a, battery_wh=battery,
            current_task_id=None if arrived else tid, status="idle" if arrived else "moving",
            nearby_robot_count=0, local_congestion=0.0))

    # ---- static tables ----
    blocked = sum(r.count("#") for r in grid)
    scenario = Scenario(scenario_id=scenario_id, stage=0, difficulty_level=1, scenario_category="nominal",
                        scenario_seed=seed, scenario_version=V.SCENARIO_VERSION,
                        generator_version=V.GENERATOR_VERSION, config=cfg, config_hash=config_hash)
    environment = Environment(
        environment_id=environment_id, scenario_id=scenario_id, environment_type="warehouse",
        width=cfg["width"], height=cfg["height"], cell_size_m=cell, map_representation="occupancy_grid",
        map_grid=grid, map_uri=None, terrain_type="smooth_concrete",
        obstacle_density=blocked / (cfg["width"] * cfg["height"]),
        aisle_configuration={"layout": "hand_authored_stage0", "aisles": cfg["aisles"]},
        charging_station_locations=[{k: s[k] for k in ("station_id", "x", "y")} for s in cfg["charging_stations"]],
        loading_station_locations=cfg["loading_stations"], delivery_station_locations=cfg["delivery_stations"],
        environmental_conditions={"indoor": True, "temperature_c": 20.0},
        environment_version=V.ENVIRONMENT_VERSION, scenario_version=V.SCENARIO_VERSION,
        scenario_seed=seed, generator_version=V.GENERATOR_VERSION)
    robot = Robot(
        episode_id=episode_id, robot_id=rid, robot_type=rt.robot_type,
        initial_x=start[0] * cell, initial_y=start[1] * cell, initial_velocity=0.0, initial_acceleration=0.0,
        max_speed_mps=rt.max_speed_mps, battery_capacity_wh=rt.battery_capacity_wh,
        initial_battery_wh=rcfg["initial_battery_wh"], payload_capacity_kg=rt.payload_capacity_kg,
        length_m=rt.length_m, width_m=rt.width_m, turning_radius_m=rt.turning_radius_m,
        operating_cost_per_hour=rt.operating_cost_per_hour, communication_range_m=rt.communication_range_m,
        sensor_reliability=rt.sensor_reliability, failure_probability_per_hour=rt.failure_probability_per_hour,
        energy_per_meter_wh=rt.energy_per_meter_wh, idle_power_w=rt.idle_power_w,
        initial_maintenance_state="nominal", initial_status="idle", initial_task_id=None)
    task = Task(
        episode_id=episode_id, task_id=tid, task_type="single", priority=tcfg["priority"],
        creation_time_s=t_create, pickup_x=start[0], pickup_y=start[1],
        destination_x=goal[0], destination_y=goal[1], payload_kg=tcfg["payload_kg"],
        deadline_s=tcfg["deadline_s"], expected_service_time_s=expected_service,
        actual_service_time_s=t_arrive - 0.0, assigned_robot_id=rid, assignment_time_s=0.0,
        completion_time_s=t_arrive, cancelled=False, cancellation_time_s=None,
        delay_s=(t_arrive - 0.0) - expected_service, failed=False, failure_reason=None, depends_on=[])
    stations = [ChargingStation(episode_id=episode_id, **s) for s in cfg["charging_stations"]]
    obstacles = [Obstacle(episode_id=episode_id, obstacle_id=o["obstacle_id"], obstacle_kind=o["kind"],
                          cause="fixed_infrastructure", is_static=True, x_min=o["x_min"], y_min=o["y_min"],
                          x_max=o["x_max"], y_max=o["y_max"], appear_time_s=0.0, remove_time_s=None)
                 for o in cfg["obstacles"]]

    tables = {
        "scenarios": [scenario], "environments": [environment], "robots": [robot], "tasks": [task],
        "charging_stations": stations, "obstacles": obstacles,
        "task_events": log.task_events, "robot_events": log.robot_events, "obstacle_events": [],
        "trajectories": traj,
    }
    episode = Episode(
        episode_id=episode_id, scenario_id=scenario_id, environment_id=environment_id, random_seed=seed,
        generator_version=V.GENERATOR_VERSION, simulator_version=V.SIMULATOR_VERSION,
        environment_version=V.ENVIRONMENT_VERSION, robot_configuration_version=V.ROBOT_CONFIGURATION_VERSION,
        scenario_version=V.SCENARIO_VERSION, sim_epoch=SIM_EPOCH, tick_seconds=TICK_SECONDS,
        n_ticks=last_tick, n_robots=1, n_tasks=1, n_trajectory_rows=len(traj),
        termination_reason="all_tasks_completed", content_sha256="")
    tables["episodes"] = [episode]
    digest = content_hash(tables)
    tables["episodes"] = [episode.model_copy(update={"content_sha256": digest})]
    return EpisodeBundle(tables=tables)

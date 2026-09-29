import math

from orbit.sim.stage0 import STAGE0_CONFIG, astar, build_grid, generate_stage0_episode


def test_planner_finds_valid_shortest_detour():
    grid = build_grid(STAGE0_CONFIG)
    path = astar(grid, (2, 3), (15, 18))
    assert path[0] == (2, 3) and path[-1] == (15, 18)
    assert all(grid[y][x] == "." for x, y in path)
    assert all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in zip(path, path[1:]))
    assert len(path) - 1 == 30            # Manhattan is 28; the wall at x=7 forces a 2-cell detour


def test_trajectory_is_physically_consistent():
    b = generate_stage0_episode(0)
    tr = sorted(b.tables["trajectories"], key=lambda r: r.sim_time_s)
    grid = build_grid(STAGE0_CONFIG)
    assert [r.sim_time_s for r in tr] == [float(i) for i in range(len(tr))]        # contiguous ticks
    assert all(grid[int(r.y)][int(r.x)] == "." for r in tr)                          # never inside an obstacle
    for a, c in zip(tr, tr[1:]):
        assert math.isclose(c.velocity, math.hypot(c.x - a.x, c.y - a.y))            # v = distance / dt
        assert math.isclose(c.acceleration, c.velocity - a.velocity)                 # a = dv / dt
        assert c.battery_wh <= a.battery_wh                                          # never recharges
    assert tr[-1].velocity == 0.0 and tr[-1].status == "idle" and tr[-1].current_task_id is None
    assert tr[0].battery_wh == 100.0 - 0.0 and tr[-1].battery_wh > 0


def test_event_log_tells_the_same_story_as_the_tables():
    b = generate_stage0_episode(0)
    events = sorted(b.tables["task_events"] + b.tables["robot_events"], key=lambda e: e.event_seq)
    assert [e.event_type for e in events] == ["TASK_CREATED", "TASK_ASSIGNED", "ROBOT_STARTED",
                                              "ROBOT_STOPPED", "TASK_COMPLETED"]
    assert [e.event_seq for e in events] == list(range(5))                            # one shared counter
    task = b.tables["tasks"][0]
    completed = events[-1]
    assert completed.sim_time_s == task.completion_time_s == 30.0
    assert task.delay_s == 0.0 and not task.cancelled and not task.failed
    assert (task.pickup_x, task.pickup_y, task.destination_x, task.destination_y) == (2, 3, 15, 18)


def test_no_future_information_in_creation_time_event():
    """The TASK_CREATED payload must not contain anything only known after completion."""
    b = generate_stage0_episode(0)
    created = next(e for e in b.tables["task_events"] if e.event_type == "TASK_CREATED")
    assert not ({"completion_time_s", "actual_service_time_s", "delay_s", "planned_path_cells"} & set(created.payload))

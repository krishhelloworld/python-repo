import psycopg
import pytest

from orbit import db
from orbit.catalog import ROBOT_TYPES
from orbit.models import DEFERRED_TABLES, TABLE_MODELS
from orbit.persist import persist_episode
from orbit.sim.stage0 import generate_stage0_episode

SPEC_TABLES = {"environments", "robots", "robot_types", "tasks", "task_events", "robot_events", "obstacles",
               "obstacle_events", "charging_stations", "trajectories", "episodes", "scenarios",
               "external_sources", "datasets", "dataset_versions", "experiment_metadata"}


def tables(conn):
    return {r[0] for r in conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = current_schema() AND table_type='BASE TABLE'")}


def test_all_spec_tables_exist(conn):
    assert SPEC_TABLES <= tables(conn)


def test_every_table_is_modelled_or_explicitly_deferred(conn):
    assert tables(conn) == set(TABLE_MODELS) | set(DEFERRED_TABLES)


def test_migrations_are_idempotent(conn):
    assert db.apply_migrations(conn) == []


def test_robot_type_seed_matches_python_catalog(conn):
    for name, rt in ROBOT_TYPES.items():
        row = conn.execute("SELECT * FROM robot_types WHERE robot_type=%s", (name,)).fetchone()
        cols = [d.name for d in conn.execute("SELECT * FROM robot_types LIMIT 0").description]
        assert dict(zip(cols, row)) == rt.model_dump()


@pytest.mark.parametrize("stmt", [
    "UPDATE trajectories SET x = 999",
    "DELETE FROM task_events",
    "TRUNCATE trajectories",
    "UPDATE episodes SET termination_reason = 'x'",
])
def test_raw_layer_is_append_only(conn, stmt):
    persist_episode(conn, generate_stage0_episode(0))
    with pytest.raises(psycopg.errors.RaiseException, match="append-only"):
        conn.execute(stmt)


def test_synthetic_rows_require_a_seed(conn):
    b = generate_stage0_episode(0)
    scenario = b.tables["scenarios"][0].model_copy(update={"scenario_seed": None})
    from orbit.persist import _insert
    with pytest.raises(psycopg.errors.CheckViolation):
        _insert(conn, "scenarios", [scenario])


def test_unknown_event_type_rejected(conn):
    b = generate_stage0_episode(0)
    persist_episode(conn, b)
    bad = b.tables["task_events"][0].model_copy(update={"event_seq": 99, "event_type": "TASK_TELEPORTED"})
    from orbit.persist import _insert
    with pytest.raises(psycopg.errors.ForeignKeyViolation):
        _insert(conn, "task_events", [bad])

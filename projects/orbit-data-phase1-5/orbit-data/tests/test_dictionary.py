from orbit.dictionary import build_rows
from orbit.models import TABLE_MODELS


def test_db_columns_and_models_do_not_drift(conn):
    for table, model in TABLE_MODELS.items():
        db_cols = {r[0] for r in conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_schema=current_schema() AND table_name=%s",
            (table,))}
        db_cols.discard("created_at")
        assert db_cols == set(model.model_fields), f"{table}: {db_cols ^ set(model.model_fields)}"


def test_every_field_is_documented():
    rows = build_rows()
    assert rows and all(r["description"] and r["type"] and r["known_at"] for r in rows)
    trajectory_fields = {r["field_name"] for r in rows if r["table"] == "trajectories"}
    assert {"x", "y", "velocity", "acceleration", "battery_wh", "nearby_robot_count", "local_congestion"} <= trajectory_fields

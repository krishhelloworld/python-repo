import json

import pandas as pd
import psycopg
import pytest

from orbit.errors import ReproducibilityError
from orbit.persist import persist_episode, verify_episode
from orbit.raw_store import ensure_raw_episode
from orbit.sim.stage0 import generate_stage0_episode


def test_same_seed_and_versions_give_identical_episode():
    a, b = generate_stage0_episode(183729), generate_stage0_episode(183729)
    assert a.episode.episode_id == b.episode.episode_id
    assert a.episode.content_sha256 == b.episode.content_sha256


def test_different_seed_gives_different_identity():
    assert generate_stage0_episode(1).episode.episode_id != generate_stage0_episode(2).episode.episode_id


def test_database_round_trip_preserves_content(conn):
    b = generate_stage0_episode(0)
    assert persist_episode(conn, b) == "inserted"
    assert verify_episode(conn, b.episode.episode_id)
    counts = {t: conn.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in b.tables}
    assert counts == {t: len(r) for t, r in b.tables.items()}


def test_persisting_twice_is_idempotent_and_detects_divergence(conn):
    b = generate_stage0_episode(0)
    assert persist_episode(conn, b) == "inserted"
    assert persist_episode(conn, b) == "already_present"
    assert conn.execute("SELECT count(*) FROM trajectories").fetchone()[0] == 32
    tampered = b.episode.model_copy(update={"content_sha256": "0" * 64})
    with pytest.raises(ReproducibilityError):
        persist_episode(conn, type(b)(tables={**b.tables, "episodes": [tampered]}))


def test_two_episodes_can_share_a_scenario_row(conn):
    a = generate_stage0_episode(0)
    persist_episode(conn, a)
    persist_episode(conn, a)                                   # scenario/environment ON CONFLICT DO NOTHING path
    assert conn.execute("SELECT count(*) FROM scenarios").fetchone()[0] == 1


def test_raw_files_are_write_once_and_match_the_database(conn, tmp_path):
    b = generate_stage0_episode(0)
    rel, status = ensure_raw_episode(b, tmp_path)
    assert status == "written"
    persist_episode(conn, b.with_raw_uri(rel))
    d = tmp_path / rel
    manifest = json.loads((d / "manifest.json").read_text())
    assert manifest["content_sha256"] == b.episode.content_sha256
    df = pd.read_parquet(d / "trajectories.parquet")
    assert len(df) == conn.execute("SELECT count(*) FROM trajectories").fetchone()[0]
    assert set(df.columns) >= {"x", "y", "velocity", "acceleration", "battery_wh", "status"}
    # regenerating verifies against the manifest instead of overwriting
    assert ensure_raw_episode(generate_stage0_episode(0), tmp_path) == (rel, "verified")
    with pytest.raises(ReproducibilityError):
        ensure_raw_episode(type(b)(tables={**b.tables, "episodes": [b.episode.model_copy(update={"content_sha256": "1" * 64})]}), tmp_path)


def test_event_seq_is_unique_across_all_event_tables(conn):
    b = generate_stage0_episode(0)
    persist_episode(conn, b)
    n, distinct = conn.execute("""
        SELECT count(*), count(DISTINCT event_seq) FROM (
          SELECT event_seq FROM task_events UNION ALL SELECT event_seq FROM robot_events
          UNION ALL SELECT event_seq FROM obstacle_events) s""").fetchone()
    assert n == distinct == 5

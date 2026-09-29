# ORBIT data laboratory — Phases 1–5 (Stage 0)

Progressive data/scenario laboratory for ORBIT. This drop = PostgreSQL schema + a deterministic
one-warehouse / one-robot / one-task world with event log and trajectory logging.
Only the **RAW** layer exists. Nothing here cleans, imputes, scales or splits data.

## Quick start
    pip install -e ".[dev]"
    export ORBIT_DATABASE_URL=postgresql://user:pw@host/db     # or omit: embedded Postgres in ./.pgdata
    python -m orbit.cli stage0                # migrate, simulate, write raw Parquet, insert, verify
    python -m orbit.dictionary                # regenerate metadata/data_dictionary.{csv,md}
    pytest                                    # 23 tests against a real PostgreSQL

## Layout
    schemas/sql/     numbered, never-edited migrations (001 = core RAW schema)
    src/orbit/       models.py (Pydantic = data dictionary source), sim/stage0.py, persist.py, raw_store.py
    raw/synthetic/   write-once episode dirs: *.parquet + manifest.json (content hash, provenance)
    metadata/        generated data dictionary

## Contracts
* identity: episode_id = uuid5(scenario_id, seed, simulator_version, robot_config_version)
* reproducibility: `content_sha256` over all episode rows; re-generating must match DB and raw manifest
* append-only: triggers reject UPDATE / DELETE / TRUNCATE on every RAW table
* leakage: data dictionary column `known_at` says when each field becomes knowable

## Next: Phase 6 (procedural environments, seeded) -> Stage 1

# ORBIT data laboratory — Phases 1–5 (Stage 0)

Progressive data/scenario laboratory for ORBIT. This drop = PostgreSQL schema + a deterministic
one-warehouse / one-robot / one-task world with event log and trajectory logging.
Only the **RAW** layer exists. Nothing here cleans, imputes, scales or splits data.

## Quick start

```
pip install -e ".[dev]"
export ORBIT_DATABASE_URL=postgresql://user:pw@host/db     # or omit: embedded Postgres in ./.pgdata
python -m orbit.cli stage0                # migrate, simulate, write raw Parquet, insert, verify
python -m orbit.dictionary                # regenerate metadata/data_dictionary.{csv,md}
pytest                                    # 23 tests against a real PostgreSQL
```

## Layout

```
schemas/sql/     numbered, never-edited migrations (001 = core RAW schema)
src/orbit/       models.py (Pydantic = data dictionary source), sim/stage0.py, persist.py, raw_store.py
raw/synthetic/   write-once episode dirs: *.parquet + manifest.json (content hash, provenance)
metadata/        generated data dictionary
```

## Contracts

- identity: episode_id = uuid5(scenario_id, seed, simulator_version, robot_config_version)
- reproducibility: `content_sha256` over all episode rows; re-generating must match DB and raw manifest
- append-only: triggers reject UPDATE / DELETE / TRUNCATE on every RAW table
- leakage: data dictionary column `known_at` says when each field becomes knowable

## Next: Phase 6 (procedural environments, seeded) -> Stage 1

______________________________________________________________________

______________________________________________________________________

# UPGRADGE IN THE PROJECT -;

HERO SIDE -;

- so according to the projct of the robot we have to detect thec obstacle of
  using the surrounding
  - enemy (seeing the amount of enemy on each side reporting ,where to attack)
  - weapons to attack
  - movement to do
  - there would be disgues movement also -> you have to verify the info is
    correct using the powers

VILLAIN SIDE-;

- using this ai for predict the hero ai movement and changing their also
- this can be like chess engine movement, where each piece decide where and what
  to move

NOW DECIDE THE CHARACTERS LIKE CHESS PEICES -> power(drone, sensors , night
vision,etc),(attacking charactersitcs),(using bombs)

now use the real info on the war like what tyupe technology is there ,what type
of errors each techonology can produce ,war situations is about to collect the
info about where each terror is coming and then plan of defense or attack
use games and films to know about soldiers war

- there would be places also like terror in pm rally so now there will priority
  of defesnse more than the prirority attack.

# Phase 6 / Stage 1 — Procedural static warehouses (spec for YOU to implement)

**No code is provided here.** This document defines *what* your generator must produce and *how it will be judged*, so
you can write the Python yourself. Everything below plugs into the schema and helpers that already exist.

## 1. Goal
Replace the one hand-authored warehouse with a **seeded, procedural generator** that can produce many different static
warehouse layouts. Same `seed` + same versions ⇒ byte-identical scenario. Still Stage 1 = *static*: no dynamic obstacles,
no failures, one robot, one task per episode (those come in Phases 7–9).

## 2. What you vary (from section 9 of the brief)
| Parameter | Meaning | Suggested handling |
|---|---|---|
| `width`, `height` | grid size in cells | sampled inside the family's range |
| `aisle_count` | number of aisles | function of size and family |
| `aisle_width` | free corridor width in cells | ≥ 2 recommended so two things could pass later |
| `obstacle_density` | fraction of blocked cells | sampled inside the family's range; *measured* value is what gets stored |
| station locations | loading, delivery, charging | on free cells, reachable from each other |
| pickup / delivery cells for the task | where `T1` goes | chosen from the loading / delivery station lists |

## 3. Families to support (starting values — my proposal, make them configurable, do not hard-code "the truth")
| Family | Width × height (cells) | Obstacle density | Aisles | Notes |
|---|---|---|---|---|
| small | 10–20 | 0.05–0.15 | 1–2 | |
| medium | 30–50 | 0.10–0.20 | 3–6 | |
| large | 80–120 | 0.10–0.20 | 8–15 | consider `map_uri` if `map_grid` gets heavy |
| dense | 30–50 | 0.30–0.45 | 4–8 | narrow aisles; hardest for connectivity |
| sparse | 30–50 | 0.02–0.08 | 1–3 | mostly open floor |
| irregular | 30–50 | 0.10–0.25 | 2–6 | non-rectangular footprint (L/T shape, notches, pillars) |

## 4. Output contract (what your generator must hand to the existing code)
`persist_episode(conn, bundle)` and `ensure_raw_episode(bundle, root)` accept an `EpisodeBundle` whose `tables` dict has these
keys, each a list of the existing Pydantic row models: `scenarios`, `environments`, `episodes`, `robots`, `tasks`,
`charging_stations`, `obstacles`, `task_events`, `robot_events`, `obstacle_events`, `trajectories`. If your generator produces
that dict (validated by the models), persistence, raw files, hashing and verification work unchanged.

How each column is filled in Stage 1:
| Table.column | Stage 1 rule |
|---|---|
| `scenarios.stage` / `difficulty_level` / `scenario_category` | `1` / your curriculum level / `nominal` |
| `scenarios.scenario_seed` | the layout seed you were given (never NULL) |
| `scenarios.scenario_version`, `generator_version` | **new strings** (e.g. `stage1-procedural-v1`); Stage 0 values are never edited |
| `scenarios.config` | see §5 |
| `environments.map_grid` | `height` strings of `width` chars, `[cy][cx]`, `.` / `#` |
| `environments.obstacle_density` | **measured** blocked ÷ total cells (same definition as Stage 0) — see open decision D2 |
| `environments.aisle_configuration` | your aisle description: family, aisle list with orientation and x/y ranges, aisle width |
| `environments.*_station_locations` | lists of `{station_id, x, y}` |
| `obstacles` | shelf/wall rectangles, `is_static = true`, `cause = fixed_infrastructure`; the union must equal the `#` cells of `map_grid` |
| `charging_stations` | one row per charging station (power, slots) |
| `episodes.random_seed` | any integer (dynamics are not used yet) — keep it separate from the layout seed |

## 5. Store the *request* and the *resolved* parameters (important)
Put two things in `scenarios.config`:
- **request** — what you asked for: family name, ranges, seed, requested difficulty.
- **resolved** — what randomness actually produced: exact width, height, aisle positions, station cells, final block list.

`config_hash` is computed over the whole config, so the *resolved* part must be fully deterministic. With `resolved` stored,
anyone can rebuild the world from the config alone, and you can later analyse "requested density vs achieved density".

## 6. Hard validity rules (a layout that breaks one is rejected, never repaired silently)
1. All stations, the robot start and task cells are inside the grid and on free cells.
2. Every station is reachable from every other (one connected free region containing them).
3. Aisles respect the family's minimum width.
4. Measured density lies inside the family range (or you document why not).
5. Obstacles rows == `#` cells exactly.
6. `width`/`height` inside the family range.

If a draw fails, re-draw **deterministically** (e.g. attempt 1, 2, 3… derived from the same seed, with a bounded number of
attempts) and record the attempt count in `resolved`. Give up loudly (raise) instead of returning a broken layout.

## 7. Reproducibility rules (where Stage 1 usually goes wrong)
- Use **one seeded random source per component** (layout, aisles, obstacles, stations, task cells), derived from the scenario seed,
  so adding a new component later does not shift every other component's numbers (NumPy's `SeedSequence` spawning is the usual tool).
- No global/unseeded randomness, no wall-clock time, no dependence on `set`/`dict` iteration order — sort before iterating.
- Keep grid quantities as integers; round any float you store to a fixed number of decimals.
- Run the reproducibility test in **two separate Python processes** (catches hash-seed / ordering differences).
- **Version rule:** if generator behaviour changes, the version string must change. If you forget, the database keeps the old
  scenario row (`ON CONFLICT DO NOTHING`) and the episode hash check will raise `ReproducibilityError` — that error means
  "you changed the generator without bumping the version".

## 8. Open decisions — yours to make (my recommendation in brackets)
- **D1 Irregular footprint:** cells outside the footprint stored as `#` in `map_grid` [yes, simplest], plus the footprint description in `resolved`.
- **D2 Density definition for irregular maps:** blocked ÷ *all* cells including outside-footprint [keep Stage 0's definition so numbers stay comparable; also store free-floor cell count in `resolved`].
- **D3 Where to record the family:** `config.request.family` [no schema change needed; query it as `config->'request'->>'family'`]. Add a column later only if you filter on it constantly.
- **D4 Episodes per scenario:** 1 now, or several with different `random_seed` [1 until Phase 7 makes the seed matter].
- **D5 Pickup/delivery choice:** random station pair vs farthest pair [random, but record which]. 

## 9. "Done when" checklist (write these as pytest tests yourself)
- [ ] Same seed + versions ⇒ identical `config_hash`, `scenario_id`, `episode_id`, `content_sha256` (also across two processes).
- [ ] 100 different seeds in one family ⇒ layouts are not all identical (define your threshold, e.g. ≥ 95 distinct `map_grid`s).
- [ ] For every generated scenario: rules 1–6 in §6 hold.
- [ ] Each family's measured sizes and densities stay inside its configured ranges.
- [ ] `persist_episode` inserts; `verify_episode` is true; `ensure_raw_episode` on re-run reports `verified`, not `written`.
- [ ] Re-inserting an already-stored episode is `already_present`; changing generator behaviour without a version bump is caught.
- [ ] Append-only triggers still reject UPDATE/DELETE/TRUNCATE (existing tests keep passing).
- [ ] Column drift test (`test_dictionary`) still passes; regenerate `metadata/data_dictionary.*`.

## 10. First small batch, then inspect (do not scale yet)
Generate e.g. **5 seeds × 6 families = 30 scenarios**, then look at them yourself:
```sql
-- size and density per family
SELECT s.config->'request'->>'family' AS family,
       count(*), min(e.width), max(e.width), min(e.obstacle_density), max(e.obstacle_density)
FROM scenarios s JOIN environments e USING (scenario_id)
WHERE s.stage = 1 GROUP BY 1 ORDER BY 1;

-- planned path length vs straight-line distance (detour factor) per episode
SELECT e.episode_id, t.expected_service_time_s,
       abs(t.destination_x - t.pickup_x) + abs(t.destination_y - t.pickup_y) AS manhattan
FROM tasks t JOIN episodes e USING (episode_id);
```
Questions to answer from the data: Are dense layouts really harder (longer detours)? Does `obstacle_density` requested equal
achieved? Are any two "different" seeds accidentally identical? Do the stations end up clustered in a corner?
Only when these look right, scale (e.g. 100 per family) — bigger is not better, *varied and reproducible* is.

## 11. What does NOT change in Phase 6
No new tables, no migration (the current schema already holds everything above). Stage 0 rows and files stay untouched.
Dynamic obstacles start in Phase 7 (`obstacle_events`).

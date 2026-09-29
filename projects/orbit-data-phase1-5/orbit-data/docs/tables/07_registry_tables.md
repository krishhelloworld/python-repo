# Registry tables (all empty today, on purpose)

These hold *metadata about data*, not simulation output. They exist now so the schema does not have to change when their
phase arrives. Each is created empty; no row models exist for them yet.

## `external_sources` — Phase 13
**One row = one downloaded external dataset/API extract.** Required by the rule "external data must carry source,
license, retrieval date and version".
| Column | Meaning |
|---|---|
| `source_id` | Short unique key (primary key), referenced by `episodes.external_source_id` |
| `source_name` | Human name of the dataset/provider |
| `source_url` | Exact URL it was retrieved from |
| `license` | License / terms identifier |
| `retrieved_at` | When you downloaded it |
| `original_dataset_version` | The provider's own version/date label |
| `archive_uri` | Where the **untouched** original file is stored (under `raw/external/`) |
| `archive_sha256` | Hash of that original file, to prove it was never modified |
| `attribution` | Required credit text, if any |
| `terms_notes` | Rate limits, robots.txt / API terms you had to respect |
| `created_at` | Wall-clock insert time |

## `datasets` and `dataset_versions` — Phase 15
`datasets` — **one row = a named dataset family** (`dataset_id`, `name`, `description`, `created_at`).
`dataset_versions` — **one row = one frozen release**, e.g. `orbit_dataset_v0.1`. Never replaced, only added to.
| Column | Meaning |
|---|---|
| `dataset_version_id` | e.g. `orbit_dataset_v0.1` (primary key) |
| `dataset_id` | FK → `datasets` |
| `schema_version`, `generator_version` | What produced it |
| `scenario_distribution` | JSON: how many episodes per scenario family / difficulty / category |
| `n_episodes`, `n_records` | Size |
| `data_sources` | JSON: synthetic and external sources used |
| `external_dataset_versions` | JSON: exact versions of any external datasets |
| `generation_date` | When the release was built |
| `notes` | Free text |

## `dataset_version_episodes` — Phase 15
**One row = "episode E belongs to dataset version V".** Needed because `episodes` rows are immutable, so an episode cannot
carry a dataset id; membership is a separate append-only link. This is what lets you answer "which episodes were in
training set v0.2?".

## `experiment_metadata` — Phase 14+
**One row = one experiment you ran** (`experiment_id`, `name`, `hypothesis`, `description`, `config` JSON, `created_at`) —
e.g. "A* vs other planners under dynamic obstacles".

## `corruption_mechanisms` — Phase 9
**One row = one deliberate data-quality trap**, so imperfections are documented, never silent.
| Column | Meaning |
|---|---|
| `mechanism_id` | Unique key |
| `corruption_type` | e.g. duplicate_event, out_of_order_timestamp, sensor_noise, wrong_units |
| `category` | `observation_error` (realistic sensor/measurement imperfection) **or** `structural_corruption` (broken structure) — the brief asks you to keep these apart |
| `probability` | 0–1 chance per affected record |
| `affected_fields` | Text array of columns touched |
| `scenario_version` | Scenario family the mechanism applies to |
| `description` | What it does and why it is realistic |
| `introduced_in_stage` | First stage using it |

## `schema_migrations` — infrastructure
One row per applied migration file (`version`, `description`, `applied_at`). Today: `001`.

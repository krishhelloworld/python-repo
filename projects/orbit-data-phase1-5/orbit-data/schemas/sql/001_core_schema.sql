-- ORBIT core schema, migration 001  (schema_version 0.1.0)
-- Layer: RAW.  Every RAW table is append-only (enforced by triggers at the bottom).
-- Conventions
--   * sim_time_s   : seconds since episode start on the SIMULATED clock
--   * "timestamp"  : episodes.sim_epoch + sim_time_s (simulated clock, NOT wall-clock time)
--   * created_at   : wall-clock DB insert time (audit only; excluded from reproducibility hash)
--   * high-volume tables carry episode_id + source_type + schema_version; the full provenance
--     (seeds, generator/simulator versions) lives once per episode in `episodes`
--     (see view trajectories_with_provenance).

CREATE TABLE schema_migrations (
    version     text PRIMARY KEY,
    description text NOT NULL,
    applied_at  timestamptz NOT NULL DEFAULT now()
);

CREATE FUNCTION orbit_forbid_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'RAW layer is append-only: % on table % is forbidden', TG_OP, TG_TABLE_NAME;
END
$$;

-- ---------------------------------------------------------------- reference vocabularies
CREATE TABLE event_types (
    event_type         text PRIMARY KEY,
    category           text NOT NULL,
    description        text NOT NULL,
    introduced_in_stage integer NOT NULL
);

CREATE TABLE robot_types (
    robot_type                   text PRIMARY KEY,
    description                  text NOT NULL,
    introduced_in_stage          integer NOT NULL,
    max_speed_mps                double precision NOT NULL CHECK (max_speed_mps > 0),
    battery_capacity_wh          double precision NOT NULL CHECK (battery_capacity_wh > 0),
    payload_capacity_kg          double precision NOT NULL CHECK (payload_capacity_kg >= 0),
    length_m                     double precision NOT NULL,
    width_m                      double precision NOT NULL,
    turning_radius_m             double precision NOT NULL CHECK (turning_radius_m >= 0),
    operating_cost_per_hour      double precision NOT NULL CHECK (operating_cost_per_hour >= 0),
    communication_range_m        double precision NOT NULL,
    sensor_reliability           double precision NOT NULL CHECK (sensor_reliability BETWEEN 0 AND 1),
    failure_probability_per_hour double precision NOT NULL CHECK (failure_probability_per_hour BETWEEN 0 AND 1),
    energy_per_meter_wh          double precision NOT NULL CHECK (energy_per_meter_wh >= 0),
    idle_power_w                 double precision NOT NULL CHECK (idle_power_w >= 0)
);

-- ---------------------------------------------------------------- external data registry
CREATE TABLE external_sources (
    source_id                text PRIMARY KEY,
    source_name              text NOT NULL,
    source_url               text NOT NULL,
    license                  text NOT NULL,
    retrieved_at             timestamptz NOT NULL,
    original_dataset_version text NOT NULL,
    archive_uri              text NOT NULL,
    archive_sha256           text NOT NULL,
    attribution              text,
    terms_notes              text,
    created_at               timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------- scenarios / environments / episodes
CREATE TABLE scenarios (
    scenario_id        uuid PRIMARY KEY,
    stage              integer NOT NULL CHECK (stage >= 0),
    difficulty_level   integer NOT NULL CHECK (difficulty_level BETWEEN 1 AND 12),
    scenario_category  text NOT NULL DEFAULT 'nominal',
    scenario_seed      bigint,
    scenario_version   text NOT NULL,
    generator_version  text NOT NULL,
    config             jsonb NOT NULL,
    config_hash        text NOT NULL,
    source_type        text NOT NULL CHECK (source_type IN ('synthetic','external','derived')),
    schema_version     text NOT NULL,
    created_at         timestamptz NOT NULL DEFAULT now(),
    CHECK (source_type <> 'synthetic' OR scenario_seed IS NOT NULL),
    UNIQUE (generator_version, scenario_version, scenario_seed, config_hash)
);

CREATE TABLE environments (
    environment_id                 uuid PRIMARY KEY,
    scenario_id                    uuid NOT NULL REFERENCES scenarios,
    environment_type               text NOT NULL CHECK (environment_type IN
        ('warehouse','factory','distribution_center','cross_dock','port','airport_cargo_area',
         'urban_delivery_zone','campus','hospital_logistics','mixed_logistics')),
    width                          integer NOT NULL CHECK (width > 0),
    height                         integer NOT NULL CHECK (height > 0),
    cell_size_m                    double precision NOT NULL CHECK (cell_size_m > 0),
    map_representation             text NOT NULL,
    map_grid                       jsonb,
    map_uri                        text,
    terrain_type                   text NOT NULL,
    obstacle_density               double precision NOT NULL CHECK (obstacle_density BETWEEN 0 AND 1),
    aisle_configuration            jsonb NOT NULL,
    charging_station_locations     jsonb NOT NULL,
    loading_station_locations      jsonb NOT NULL,
    delivery_station_locations     jsonb NOT NULL,
    environmental_conditions       jsonb NOT NULL,
    environment_version            text NOT NULL,
    scenario_version               text NOT NULL,
    scenario_seed                  bigint,
    generator_version              text NOT NULL,
    source_type                    text NOT NULL CHECK (source_type IN ('synthetic','external','derived')),
    schema_version                 text NOT NULL,
    created_at                     timestamptz NOT NULL DEFAULT now(),
    CHECK (map_grid IS NOT NULL OR map_uri IS NOT NULL),
    CHECK (source_type <> 'synthetic' OR scenario_seed IS NOT NULL)
);

CREATE TABLE episodes (
    episode_id                   uuid PRIMARY KEY,
    scenario_id                  uuid NOT NULL REFERENCES scenarios,
    environment_id               uuid NOT NULL REFERENCES environments,
    random_seed                  bigint,
    generator_version            text NOT NULL,
    simulator_version            text NOT NULL,
    environment_version          text NOT NULL,
    robot_configuration_version  text NOT NULL,
    scenario_version             text NOT NULL,
    schema_version               text NOT NULL,
    source_type                  text NOT NULL CHECK (source_type IN ('synthetic','external','derived')),
    external_source_id           text REFERENCES external_sources,
    parent_dataset               text,
    transformation_description   text,
    sim_epoch                    timestamptz NOT NULL,
    tick_seconds                 double precision NOT NULL CHECK (tick_seconds > 0),
    n_ticks                      integer NOT NULL,
    n_robots                     integer NOT NULL,
    n_tasks                      integer NOT NULL,
    n_trajectory_rows            integer NOT NULL,
    termination_reason           text NOT NULL,
    content_sha256               text NOT NULL,
    raw_uri                      text,
    created_at                   timestamptz NOT NULL DEFAULT now(),
    CHECK (source_type <> 'synthetic' OR random_seed IS NOT NULL),
    CHECK (source_type <> 'external' OR external_source_id IS NOT NULL),
    CHECK (source_type <> 'derived'  OR (parent_dataset IS NOT NULL AND transformation_description IS NOT NULL))
);

-- ---------------------------------------------------------------- per-episode entities
CREATE TABLE robots (
    episode_id                   uuid NOT NULL REFERENCES episodes,
    robot_id                     text NOT NULL,
    robot_type                   text NOT NULL REFERENCES robot_types,
    initial_x                    double precision NOT NULL,
    initial_y                    double precision NOT NULL,
    initial_velocity             double precision NOT NULL,
    initial_acceleration         double precision NOT NULL,
    max_speed_mps                double precision NOT NULL,
    battery_capacity_wh          double precision NOT NULL,
    initial_battery_wh           double precision NOT NULL,
    payload_capacity_kg          double precision NOT NULL,
    length_m                     double precision NOT NULL,
    width_m                      double precision NOT NULL,
    turning_radius_m             double precision NOT NULL,
    operating_cost_per_hour      double precision NOT NULL,
    communication_range_m        double precision NOT NULL,
    sensor_reliability           double precision NOT NULL,
    failure_probability_per_hour double precision NOT NULL,
    energy_per_meter_wh          double precision NOT NULL,
    idle_power_w                 double precision NOT NULL,
    initial_maintenance_state    text NOT NULL,
    initial_status               text NOT NULL,
    initial_task_id              text,
    source_type                  text NOT NULL,
    schema_version               text NOT NULL,
    created_at                   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (episode_id, robot_id)
);

CREATE TABLE tasks (
    episode_id               uuid NOT NULL REFERENCES episodes,
    task_id                  text NOT NULL,
    task_type                text NOT NULL CHECK (task_type IN
        ('single','multi_step','dependent','urgent','cancelled','rescheduled',
         'batch','fragile','high_priority','time_window')),
    priority                 integer NOT NULL CHECK (priority BETWEEN 1 AND 5),
    creation_time_s          double precision NOT NULL,
    pickup_x                 integer NOT NULL,
    pickup_y                 integer NOT NULL,
    destination_x            integer NOT NULL,
    destination_y            integer NOT NULL,
    payload_kg               double precision NOT NULL CHECK (payload_kg >= 0),
    deadline_s               double precision,
    expected_service_time_s  double precision,
    actual_service_time_s    double precision,
    assigned_robot_id        text,
    assignment_time_s        double precision,
    completion_time_s        double precision,
    cancelled                boolean NOT NULL,
    cancellation_time_s      double precision,
    delay_s                  double precision,
    failed                   boolean NOT NULL,
    failure_reason           text,
    depends_on               jsonb NOT NULL,
    source_type              text NOT NULL,
    schema_version           text NOT NULL,
    created_at               timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (episode_id, task_id),
    FOREIGN KEY (episode_id, assigned_robot_id) REFERENCES robots (episode_id, robot_id)
);

CREATE TABLE charging_stations (
    episode_id      uuid NOT NULL REFERENCES episodes,
    station_id      text NOT NULL,
    x               integer NOT NULL,
    y               integer NOT NULL,
    power_w         double precision NOT NULL CHECK (power_w > 0),
    n_slots         integer NOT NULL CHECK (n_slots > 0),
    source_type     text NOT NULL,
    schema_version  text NOT NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (episode_id, station_id)
);

CREATE TABLE obstacles (
    episode_id       uuid NOT NULL REFERENCES episodes,
    obstacle_id      text NOT NULL,
    obstacle_kind    text NOT NULL,
    cause            text NOT NULL,
    is_static        boolean NOT NULL,
    x_min            integer NOT NULL,
    y_min            integer NOT NULL,
    x_max            integer NOT NULL,
    y_max            integer NOT NULL,
    appear_time_s    double precision NOT NULL,
    remove_time_s    double precision,
    source_type      text NOT NULL,
    schema_version   text NOT NULL,
    created_at       timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (episode_id, obstacle_id),
    CHECK (x_min <= x_max AND y_min <= y_max)
);

-- ---------------------------------------------------------------- event logs
-- event_seq is ONE monotone counter per episode shared by task_events, robot_events and
-- obstacle_events, so a UNION ALL of the three can be totally ordered.
CREATE TABLE task_events (
    episode_id     uuid NOT NULL,
    event_seq      integer NOT NULL,
    event_type     text NOT NULL REFERENCES event_types,
    sim_time_s     double precision NOT NULL,
    "timestamp"    timestamptz NOT NULL,
    task_id        text NOT NULL,
    robot_id       text,
    payload        jsonb NOT NULL,
    source_type    text NOT NULL,
    schema_version text NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (episode_id, event_seq),
    FOREIGN KEY (episode_id, task_id)  REFERENCES tasks  (episode_id, task_id),
    FOREIGN KEY (episode_id, robot_id) REFERENCES robots (episode_id, robot_id)
);

CREATE TABLE robot_events (
    episode_id     uuid NOT NULL,
    event_seq      integer NOT NULL,
    event_type     text NOT NULL REFERENCES event_types,
    sim_time_s     double precision NOT NULL,
    "timestamp"    timestamptz NOT NULL,
    robot_id       text NOT NULL,
    task_id        text,
    payload        jsonb NOT NULL,
    source_type    text NOT NULL,
    schema_version text NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (episode_id, event_seq),
    FOREIGN KEY (episode_id, robot_id) REFERENCES robots (episode_id, robot_id),
    FOREIGN KEY (episode_id, task_id)  REFERENCES tasks  (episode_id, task_id)
);

CREATE TABLE obstacle_events (
    episode_id     uuid NOT NULL,
    event_seq      integer NOT NULL,
    event_type     text NOT NULL REFERENCES event_types,
    sim_time_s     double precision NOT NULL,
    "timestamp"    timestamptz NOT NULL,
    obstacle_id    text NOT NULL,
    payload        jsonb NOT NULL,
    source_type    text NOT NULL,
    schema_version text NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (episode_id, event_seq),
    FOREIGN KEY (episode_id, obstacle_id) REFERENCES obstacles (episode_id, obstacle_id)
);

-- ---------------------------------------------------------------- trajectories
-- One row per robot per tick. Small episodes live here; large runs are exported to Parquet.
CREATE TABLE trajectories (
    episode_id           uuid NOT NULL,
    robot_id             text NOT NULL,
    sim_time_s           double precision NOT NULL,
    "timestamp"          timestamptz NOT NULL,
    x                    double precision NOT NULL,
    y                    double precision NOT NULL,
    velocity             double precision NOT NULL,
    acceleration         double precision NOT NULL,
    battery_wh           double precision NOT NULL,
    current_task_id      text,
    status               text NOT NULL CHECK (status IN
        ('idle','moving','loading','unloading','charging','waiting','failed','offline')),
    nearby_robot_count   integer NOT NULL CHECK (nearby_robot_count >= 0),
    local_congestion     double precision NOT NULL CHECK (local_congestion >= 0),
    source_type          text NOT NULL,
    schema_version       text NOT NULL,
    created_at           timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (episode_id, robot_id, sim_time_s),
    FOREIGN KEY (episode_id, robot_id) REFERENCES robots (episode_id, robot_id)
);

CREATE VIEW trajectories_with_provenance AS
SELECT t.*,
       e.random_seed, e.generator_version, e.simulator_version, e.scenario_version,
       e.environment_version, e.robot_configuration_version, e.sim_epoch
FROM trajectories t JOIN episodes e USING (episode_id);

-- ---------------------------------------------------------------- dataset versioning & experiments
CREATE TABLE datasets (
    dataset_id   text PRIMARY KEY,
    name         text NOT NULL,
    description  text,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE dataset_versions (
    dataset_version_id        text PRIMARY KEY,               -- e.g. orbit_dataset_v0.1
    dataset_id                text NOT NULL REFERENCES datasets,
    schema_version            text NOT NULL,
    generator_version         text NOT NULL,
    scenario_distribution     jsonb NOT NULL,
    n_episodes                integer NOT NULL,
    n_records                 bigint NOT NULL,
    data_sources              jsonb NOT NULL,
    external_dataset_versions jsonb NOT NULL,
    generation_date           timestamptz NOT NULL,
    notes                     text,
    created_at                timestamptz NOT NULL DEFAULT now()
);

-- Episodes are immutable, so membership in a dataset version is a separate append-only link.
CREATE TABLE dataset_version_episodes (
    dataset_version_id text NOT NULL REFERENCES dataset_versions,
    episode_id         uuid NOT NULL REFERENCES episodes,
    created_at         timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (dataset_version_id, episode_id)
);

CREATE TABLE experiment_metadata (
    experiment_id text PRIMARY KEY,
    name          text NOT NULL,
    hypothesis    text,
    description   text,
    config        jsonb NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- Registry of deliberate data-quality traps (spec section 26). Empty until Phase 9 (Stage 4+).
CREATE TABLE corruption_mechanisms (
    mechanism_id        text PRIMARY KEY,
    corruption_type     text NOT NULL,
    category            text NOT NULL CHECK (category IN ('observation_error','structural_corruption')),
    probability         double precision NOT NULL CHECK (probability BETWEEN 0 AND 1),
    affected_fields     text[] NOT NULL,
    scenario_version    text NOT NULL,
    description         text NOT NULL,
    introduced_in_stage integer NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------- append-only enforcement
DO $$
DECLARE t text;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'scenarios','environments','episodes','robots','tasks','charging_stations','obstacles',
        'task_events','robot_events','obstacle_events','trajectories',
        'external_sources','dataset_versions','dataset_version_episodes']
    LOOP
        EXECUTE format('CREATE TRIGGER %I BEFORE UPDATE OR DELETE ON %I
                        FOR EACH ROW EXECUTE FUNCTION orbit_forbid_mutation()', t || '_no_mutation', t);
        EXECUTE format('CREATE TRIGGER %I BEFORE TRUNCATE ON %I
                        FOR EACH STATEMENT EXECUTE FUNCTION orbit_forbid_mutation()', t || '_no_truncate', t);
    END LOOP;
END
$$;

-- ---------------------------------------------------------------- seed vocabularies
INSERT INTO event_types (event_type, category, description, introduced_in_stage) VALUES
 ('TASK_CREATED','task','A task entered the system',0),
 ('TASK_ASSIGNED','task','A task was assigned to a robot',0),
 ('TASK_COMPLETED','task','A task was completed at its destination',0),
 ('TASK_CANCELLED','task','A task was cancelled before completion',5),
 ('TASK_PRIORITY_CHANGED','task','A task priority changed after creation',5),
 ('ROBOT_STARTED','robot','A robot began executing its assigned work',0),
 ('ROBOT_STOPPED','robot','A robot came to rest',0),
 ('ROBOT_FAILED','robot','A robot broke down',4),
 ('ROBOT_RECOVERED','robot','A failed robot returned to service',4),
 ('ROBOT_LOW_BATTERY','robot','A robot crossed its low-battery threshold',3),
 ('OBSTACLE_APPEARED','obstacle','An obstacle appeared that was not there before',2),
 ('OBSTACLE_REMOVED','obstacle','A previously appeared obstacle was removed',2),
 ('AISLE_BLOCKED','obstacle','An aisle became impassable',2),
 ('AISLE_REOPENED','obstacle','A blocked aisle became passable again',2),
 ('CHARGING_STARTED','charging','A robot began charging',3),
 ('CHARGING_COMPLETED','charging','A robot finished charging',3),
 ('COMMUNICATION_DELAY','communication','A message was delayed',4),
 ('COMMUNICATION_FAILURE','communication','A message or link was lost',4),
 ('HUMAN_ENTERED_ZONE','human','A human entered a robot operating zone',2),
 ('HUMAN_LEFT_ZONE','human','A human left a robot operating zone',2),
 ('TRAFFIC_INCREASED','traffic','Local or global traffic level rose',3),
 ('TRAFFIC_DECREASED','traffic','Local or global traffic level fell',3);

INSERT INTO robot_types VALUES
 ('small_fast_robot','Small, quick, low-payload grid robot (Stage 0 reference type)',0,
  1.0, 100.0, 20.0, 0.6, 0.5, 0.0, 4.0, 50.0, 1.0, 0.0, 0.05, 5.0);

INSERT INTO schema_migrations (version, description) VALUES ('001','core RAW schema v0.1.0');

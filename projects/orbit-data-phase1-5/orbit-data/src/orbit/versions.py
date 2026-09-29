"""Every version string that participates in reproducibility.

Rule: if the *behaviour* behind a version changes, the version string MUST change.
Old versions are never edited in place; (seed, versions) -> same episode is the contract.
"""
SCHEMA_VERSION = "0.1.0"
GENERATOR_VERSION = "stage0-gen-0.1.0"
SIMULATOR_VERSION = "orbit-sim-0.1.0"
SCENARIO_VERSION = "stage0-fixed-v1"
ENVIRONMENT_VERSION = "warehouse-fixed-v1"
ROBOT_CONFIGURATION_VERSION = "robots-v1"

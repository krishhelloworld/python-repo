"""Local throw-away PostgreSQL (embedded via `pgserver`) for tests and quick experiments.
For real work point ORBIT_DATABASE_URL at your own PostgreSQL instance instead."""
from pathlib import Path


def start_local_postgres(data_dir: str | Path):
    import pgserver
    server = pgserver.get_server(str(data_dir), cleanup_mode="stop")
    return server, server.get_uri()

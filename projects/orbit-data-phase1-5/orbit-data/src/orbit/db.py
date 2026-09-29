"""PostgreSQL access: connection, migrations."""
import os
from pathlib import Path

import psycopg

SQL_DIR = Path(__file__).resolve().parents[2] / "schemas" / "sql"


def connect(uri: str | None = None, schema: str | None = None) -> psycopg.Connection:
    """Autocommit connection, UTC session. `schema` (optional) is created and put on search_path."""
    uri = uri or os.environ["ORBIT_DATABASE_URL"]
    conn = psycopg.connect(uri, autocommit=True)
    conn.execute("SET TIME ZONE 'UTC'")
    if schema:
        conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
        conn.execute(f'SET search_path TO "{schema}"')
    return conn


def apply_migrations(conn: psycopg.Connection) -> list[str]:
    """Apply every schemas/sql/NNN_*.sql not yet recorded. Migrations are never edited after release."""
    applied: set[str] = set()
    exists = conn.execute("SELECT to_regclass('schema_migrations') IS NOT NULL").fetchone()[0]
    if exists:
        applied = {r[0] for r in conn.execute("SELECT version FROM schema_migrations")}
    done = []
    for path in sorted(SQL_DIR.glob("[0-9][0-9][0-9]_*.sql")):
        version = path.name[:3]
        if version in applied:
            continue
        with conn.transaction():
            conn.execute(path.read_text())
        done.append(version)
    return done

import os
import uuid

import pytest

from orbit import db


@pytest.fixture(scope="session")
def pg_uri(tmp_path_factory):
    """Real PostgreSQL. Set ORBIT_TEST_DATABASE_URL to use your own; otherwise an embedded one is started."""
    if os.environ.get("ORBIT_TEST_DATABASE_URL"):
        yield os.environ["ORBIT_TEST_DATABASE_URL"]
        return
    from orbit.devdb import start_local_postgres
    server, uri = start_local_postgres(tmp_path_factory.mktemp("pgdata"))
    yield uri
    server.cleanup()


@pytest.fixture()
def conn(pg_uri):
    """Fresh, fully-migrated schema per test; dropped afterwards."""
    schema = "t_" + uuid.uuid4().hex[:10]
    c = db.connect(pg_uri, schema=schema)
    db.apply_migrations(c)
    yield c
    c.execute(f'DROP SCHEMA "{schema}" CASCADE')
    c.close()

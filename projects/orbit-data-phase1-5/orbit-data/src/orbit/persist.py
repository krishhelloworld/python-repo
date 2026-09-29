"""RAW-layer persistence: one episode = one transaction; never updates, never deletes."""
import psycopg
from psycopg import sql
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from .errors import ReproducibilityError
from .hashing import content_hash
from .models import TABLE_MODELS, TABLE_ORDER
from .sim.stage0 import EpisodeBundle


def _adapt(v):
    return Jsonb(v) if isinstance(v, (dict, list)) else v


def _insert(conn, table: str, rows, skip_existing: bool = False):
    if not rows:
        return
    cols = list(type(rows[0]).model_fields)
    q = sql.SQL("INSERT INTO {t} ({c}) VALUES ({p}){oc}").format(
        t=sql.Identifier(table), c=sql.SQL(", ").join(map(sql.Identifier, cols)),
        p=sql.SQL(", ").join([sql.Placeholder()] * len(cols)),
        oc=sql.SQL(" ON CONFLICT DO NOTHING") if skip_existing else sql.SQL(""))
    with conn.cursor() as cur:
        cur.executemany(q, [[_adapt(getattr(r, c)) for c in cols] for r in rows])


def persist_episode(conn: psycopg.Connection, bundle: EpisodeBundle) -> str:
    """Returns 'inserted' or 'already_present'. Raises ReproducibilityError if the same
    episode_id already exists with different content."""
    ep = bundle.episode
    with conn.transaction():
        row = conn.execute("SELECT content_sha256 FROM episodes WHERE episode_id = %s", (ep.episode_id,)).fetchone()
        if row:
            if row[0] != ep.content_sha256:
                raise ReproducibilityError(
                    f"episode {ep.episode_id} exists with hash {row[0][:12]}, regenerated hash {ep.content_sha256[:12]}")
            return "already_present"
        for table in TABLE_ORDER:
            # scenarios/environments are shared by every episode run in the same scenario
            _insert(conn, table, bundle.tables[table], skip_existing=table in ("scenarios", "environments"))
    return "inserted"


def load_episode_tables(conn: psycopg.Connection, episode_id) -> dict:
    """Read an episode back from PostgreSQL as validated row models."""
    with conn.cursor(row_factory=dict_row) as cur:
        def fetch(table, where, arg):
            model = TABLE_MODELS[table]
            cols = sql.SQL(", ").join(map(sql.Identifier, model.model_fields))
            cur.execute(sql.SQL("SELECT {c} FROM {t} WHERE {w} = %s").format(
                c=cols, t=sql.Identifier(table), w=sql.Identifier(where)), (arg,))
            return [model(**r) for r in cur.fetchall()]
        ep = fetch("episodes", "episode_id", episode_id)
        if not ep:
            raise KeyError(episode_id)
        tables = {"episodes": ep,
                  "scenarios": fetch("scenarios", "scenario_id", ep[0].scenario_id),
                  "environments": fetch("environments", "environment_id", ep[0].environment_id)}
        for t in TABLE_ORDER:
            if t not in tables:
                tables[t] = fetch(t, "episode_id", episode_id)
    return tables


def verify_episode(conn: psycopg.Connection, episode_id) -> bool:
    """Recompute the content hash from what is stored in PostgreSQL and compare to the stored one."""
    tables = load_episode_tables(conn, episode_id)
    return content_hash(tables) == tables["episodes"][0].content_sha256

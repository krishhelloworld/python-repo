"""python -m orbit.cli stage0 [--root .] [--seed 0]
Uses $ORBIT_DATABASE_URL if set, otherwise starts a local embedded PostgreSQL in <root>/.pgdata."""
import argparse
import os
from pathlib import Path

from . import db
from .persist import persist_episode, verify_episode
from .raw_store import ensure_raw_episode
from .sim.stage0 import generate_stage0_episode


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["stage0"])
    ap.add_argument("--root", default=".")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    root = Path(args.root).resolve()

    server = None
    uri = os.environ.get("ORBIT_DATABASE_URL")
    if not uri:
        from .devdb import start_local_postgres
        server, uri = start_local_postgres(root / ".pgdata")
    conn = db.connect(uri)
    print("migrations applied:", db.apply_migrations(conn) or "none (up to date)")

    bundle = generate_stage0_episode(args.seed)
    uri_rel, raw_status = ensure_raw_episode(bundle, root)
    status = persist_episode(conn, bundle.with_raw_uri(uri_rel))
    ep = bundle.episode
    print(f"episode_id      {ep.episode_id}\ncontent_sha256  {ep.content_sha256}")
    print(f"raw files       {uri_rel} ({raw_status})\ndatabase        {status}")
    print("db round-trip verified:", verify_episode(conn, ep.episode_id))
    print({t: len(r) for t, r in bundle.tables.items()})


if __name__ == "__main__":
    main()

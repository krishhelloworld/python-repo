"""File-side RAW layer: Parquet per table + manifest.json. Write-once, read-only, hash-checked."""
import hashlib
import json
import os
import uuid
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from .errors import ReproducibilityError
from .sim.stage0 import EpisodeBundle

FILE_TABLES = ["task_events", "robot_events", "obstacle_events", "trajectories"]


def _to_arrow(rows) -> pa.Table:
    out = []
    for r in rows:
        d = r.model_dump()
        for k, v in d.items():
            if isinstance(v, uuid.UUID):
                d[k] = str(v)
            elif isinstance(v, (dict, list)):
                d[k] = json.dumps(v, sort_keys=True)          # JSON text keeps a stable Parquet schema
        out.append(d)
    return pa.Table.from_pylist(out)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_raw_episode(bundle: EpisodeBundle, root: Path, stage_dir: str = "stage0") -> tuple[str, str]:
    """Write the episode's raw files once. If they already exist, only VERIFY (never overwrite).
    Returns (relative_uri, 'written' | 'verified')."""
    ep = bundle.episode
    rel = f"raw/synthetic/{stage_dir}/{ep.episode_id}"
    d = Path(root) / rel
    if d.exists():
        manifest = json.loads((d / "manifest.json").read_text())
        if manifest["content_sha256"] != ep.content_sha256:
            raise ReproducibilityError(f"{rel}: stored hash {manifest['content_sha256'][:12]} != regenerated {ep.content_sha256[:12]}")
        return rel, "verified"
    d.mkdir(parents=True, exist_ok=False)
    meta = {"orbit.schema_version": ep.schema_version, "orbit.generator_version": ep.generator_version,
            "orbit.simulator_version": ep.simulator_version, "orbit.scenario_version": ep.scenario_version,
            "orbit.random_seed": str(ep.random_seed), "orbit.episode_id": str(ep.episode_id),
            "orbit.source_type": ep.source_type}
    files = {}
    for t in FILE_TABLES:
        p = d / f"{t}.parquet"
        pq.write_table(_to_arrow(bundle.tables[t]).replace_schema_metadata(meta), p) if bundle.tables[t] else None
        if p.exists():
            files[p.name] = {"sha256": _sha256(p), "rows": len(bundle.tables[t])}
    manifest = {"episode_id": str(ep.episode_id), "content_sha256": ep.content_sha256, "provenance": meta,
                "sim_epoch": ep.sim_epoch.isoformat(), "files": files,
                "note": "RAW layer: synthetic data, unmodified simulator output. Do not edit."}
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
    for f in d.iterdir():
        os.chmod(f, 0o444)                                     # advisory: raw files are read-only
    return rel, "written"

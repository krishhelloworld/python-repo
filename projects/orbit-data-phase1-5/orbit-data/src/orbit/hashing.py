"""Canonical content hash: the reproducibility fingerprint of an episode."""
import datetime as dt
import hashlib
import json
import uuid
from typing import Iterable, Mapping

from pydantic import BaseModel

from .models import TABLE_ORDER, TABLE_PK

# Columns that are audit/location metadata, not episode content.
EXCLUDE: dict[str, set[str]] = {"episodes": {"content_sha256", "raw_uri"}}


def _default(o):
    if isinstance(o, dt.datetime):
        return o.astimezone(dt.timezone.utc).isoformat()
    if isinstance(o, uuid.UUID):
        return str(o)
    raise TypeError(f"cannot canonicalise {type(o)}")


def content_hash(tables: Mapping[str, Iterable[BaseModel]]) -> str:
    h = hashlib.sha256()
    for name in TABLE_ORDER:
        pk = TABLE_PK[name]
        rows = [{k: v for k, v in r.model_dump().items() if k not in EXCLUDE.get(name, ())}
                for r in tables.get(name, [])]
        rows.sort(key=lambda r: tuple(r[c] for c in pk))
        h.update(f"#{name}:{len(rows)}\n".encode())
        for r in rows:
            h.update(json.dumps(r, sort_keys=True, separators=(",", ":"), default=_default).encode())
            h.update(b"\n")
    return h.hexdigest()


def canonical_json_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

"""Auto-generated data dictionary (from the Pydantic models -- the single source of truth)."""
import csv
import datetime as dt
import types
import typing
import uuid
from pathlib import Path

from .models import DEFERRED_TABLES, TABLE_MODELS

COLUMNS = ["table", "field_name", "type", "unit", "description", "source", "possible_range",
           "nullable", "known_at", "synthetic_external_derived"]


def _unwrap(ann):
    origin = typing.get_origin(ann)
    if origin in (typing.Union, types.UnionType):
        args = [a for a in typing.get_args(ann) if a is not type(None)]
        return args[0], len(args) != len(typing.get_args(ann))
    return ann, False


def _type_name(ann) -> str:
    ann, _ = _unwrap(ann)
    origin = typing.get_origin(ann)
    if origin is typing.Literal:
        return "text"
    if origin in (dict, list) or ann in (dict, list):
        return "jsonb"
    return {str: "text", int: "integer", float: "double precision", bool: "boolean",
            dt.datetime: "timestamptz", uuid.UUID: "uuid"}[ann]


def build_rows() -> list[dict]:
    rows = []
    for table, model in TABLE_MODELS.items():
        for name, fi in model.model_fields.items():
            extra = fi.json_schema_extra or {}
            rows.append({
                "table": table, "field_name": name, "type": _type_name(fi.annotation),
                "unit": extra.get("unit") or "", "description": fi.description or "",
                "source": extra.get("source", "simulator"), "possible_range": extra.get("possible_range") or "",
                "nullable": _unwrap(fi.annotation)[1], "known_at": extra.get("known_at", "static"),
                "synthetic_external_derived": extra.get("origin", "synthetic")})
        if table != "robot_types":
            rows.append({"table": table, "field_name": "created_at", "type": "timestamptz", "unit": "",
                         "description": "Wall-clock DB insert time. Audit only; excluded from content hash.",
                         "source": "database", "possible_range": "", "nullable": False,
                         "known_at": "audit", "synthetic_external_derived": "n/a"})
    return rows


def write_dictionary(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    with open(out_dir / "data_dictionary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    md = ["# ORBIT data dictionary (auto-generated; do not edit)\n",
          "`known_at` = when the value becomes knowable inside the episode "
          "(static < creation < assignment < completion; row_time = state at the row's timestamp; "
          "episode_end = whole-episode summary). Use it to reason about temporal leakage.\n",
          f"Tables without row models yet: {', '.join(f'{k} ({v})' for k, v in DEFERRED_TABLES.items())}\n"]
    for table in TABLE_MODELS:
        md.append(f"\n## {table}\n\n| field | type | unit | nullable | known_at | range | description |\n|---|---|---|---|---|---|---|")
        for r in (r for r in rows if r["table"] == table):
            md.append(f"| {r['field_name']} | {r['type']} | {r['unit']} | {r['nullable']} | {r['known_at']} | "
                      f"{r['possible_range']} | {r['description']} |")
    (out_dir / "data_dictionary.md").write_text("\n".join(md) + "\n")


if __name__ == "__main__":
    write_dictionary(Path(__file__).resolve().parents[2] / "metadata")

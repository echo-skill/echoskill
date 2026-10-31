"""Tally: count things by name, persisted as JSON under TALLY_DIR."""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path


def tally_dir() -> Path:
    return Path(os.environ.get("TALLY_DIR") or Path.home() / ".local" / "share" / "tally")


def _store() -> Path:
    d = tally_dir(); d.mkdir(parents=True, exist_ok=True)
    return d / "entries.json"


def _load() -> list[dict]:
    p = _store()
    return json.loads(p.read_text()) if p.exists() else []


def _save(entries: list[dict]) -> None:
    _store().write_text(json.dumps(entries, indent=2))


def record(name: str, count: int = 1, when: str | None = None) -> dict:
    entry = {"name": name, "count": int(count), "date": when or date.today().isoformat()}
    entries = _load(); entries.append(entry); _save(entries)
    return entry


def entries() -> list[dict]:
    return _load()


def totals() -> dict[str, int]:
    out: dict[str, int] = {}
    for e in _load():
        out[e["name"]] = out.get(e["name"], 0) + e["count"]
    return dict(sorted(out.items()))

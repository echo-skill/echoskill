from __future__ import annotations

import json
import os
from pathlib import Path


def data_path() -> Path:
    return Path(os.environ.get("TINYKV_PATH") or Path.home() / ".local" / "share" / "tinykv" / "data.json")


def _load() -> dict[str, str]:
    p = data_path()
    return json.loads(p.read_text()) if p.exists() else {}


def _save(d: dict[str, str]) -> None:
    p = data_path(); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, indent=2, sort_keys=True))


def put(key: str, value: str) -> dict:
    d = _load(); existed = key in d; d[key] = value; _save(d)
    return {"key": key, "value": value, "replaced": existed}


def get(key: str) -> str | None:
    return _load().get(key)


def remove(key: str) -> bool:
    d = _load()
    if key not in d:
        return False
    del d[key]; _save(d)
    return True


def list_keys(prefix: str = "") -> list[str]:
    return sorted(k for k in _load() if k.startswith(prefix))

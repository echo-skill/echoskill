from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path


def ledger_dir() -> Path:
    return Path(os.environ.get("LEDGER_DIR") or Path.home() / ".local" / "share" / "ledger")


def _file() -> Path:
    d = ledger_dir(); d.mkdir(parents=True, exist_ok=True)
    return d / "entries.jsonl"


def record(label: str, amount: float) -> dict:
    entry = {"label": label, "amount": float(amount)}
    with _file().open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def entries() -> list[dict]:
    p = _file()
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def balance() -> float:
    return round(sum(e["amount"] for e in entries()), 2)


def live_rate(currency: str) -> float:
    """Fetch a live exchange rate. Requires LEDGER_RATES_TOKEN; hits the network."""
    token = os.environ["LEDGER_RATES_TOKEN"]
    req = urllib.request.Request(
        f"https://rates.example.com/v1/{currency}", headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return float(json.load(resp)["rate"])

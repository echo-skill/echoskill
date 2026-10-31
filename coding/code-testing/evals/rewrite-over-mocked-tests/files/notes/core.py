"""Notes store: one JSON file per note under the notes directory."""
from __future__ import annotations

import json
import os
from pathlib import Path


def notes_dir() -> Path:
    override = os.environ.get("NOTES_DIR")
    if override:
        return Path(override)
    return Path.home() / ".local" / "share" / "notes"


def _path(note_id: str) -> Path:
    return notes_dir() / f"{note_id}.json"


def add_note(note_id: str, text: str) -> dict:
    d = notes_dir()
    d.mkdir(parents=True, exist_ok=True)
    if _path(note_id).exists():
        raise FileExistsError(f"note {note_id!r} already exists")
    note = {"id": note_id, "text": text, "tags": []}
    _path(note_id).write_text(json.dumps(note))
    return note


def get_note(note_id: str) -> dict:
    return json.loads(_path(note_id).read_text())


def list_notes() -> list[dict]:
    d = notes_dir()
    if not d.exists():
        return []
    return sorted((json.loads(p.read_text()) for p in d.glob("*.json")), key=lambda n: n["id"])


def tag_note(note_id: str, tag: str) -> dict:
    note = get_note(note_id)
    if tag not in note["tags"]:
        note["tags"].append(tag)
    _path(note_id).write_text(json.dumps(note))
    return note

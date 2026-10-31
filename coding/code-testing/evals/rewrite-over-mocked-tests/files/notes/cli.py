"""Thin argparse wrapper over notes.core."""
from __future__ import annotations

import argparse
import sys

from . import core


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="notes")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_add = sub.add_parser("add"); p_add.add_argument("id"); p_add.add_argument("text")
    p_tag = sub.add_parser("tag"); p_tag.add_argument("id"); p_tag.add_argument("tag")
    sub.add_parser("list")
    args = parser.parse_args(argv)

    if args.cmd == "add":
        note = core.add_note(args.id, args.text)
        print(f"added {note['id']}")
    elif args.cmd == "tag":
        # BUG: positional args swapped — tags the note named after the tag.
        note = core.tag_note(args.tag, args.id)
        print(f"tagged {note['id']} with {args.tag}")
    elif args.cmd == "list":
        for n in core.list_notes():
            tags = ",".join(n["tags"])
            print(f"{n['id']}\t{n['text']}\t{tags}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

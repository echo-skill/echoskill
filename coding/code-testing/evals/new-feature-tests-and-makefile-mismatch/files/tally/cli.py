from __future__ import annotations

import argparse
import sys

from . import core


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tally")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_rec = sub.add_parser("record"); p_rec.add_argument("name"); p_rec.add_argument("--count", type=int, default=1)
    sub.add_parser("totals")
    args = parser.parse_args(argv)

    if args.cmd == "record":
        e = core.record(args.name, args.count)
        print(f"{e['name']} +{e['count']}")
    elif args.cmd == "totals":
        for name, n in core.totals().items():
            print(f"{name}\t{n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

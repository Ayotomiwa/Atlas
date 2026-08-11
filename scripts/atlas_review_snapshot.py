#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.review_snapshot import SnapshotError, create_snapshot, remove_snapshot, verify_snapshot


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fingerprint the exact evidence and Atlas files under review.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("--path", action="append", default=[], required=True)
    create.add_argument("--checkout", action="append", default=[])
    create.add_argument("--missing", action="append", default=[])
    create.add_argument("--format", choices=("human", "json"), default="human")
    verify = subparsers.add_parser("verify")
    verify.add_argument("manifest")
    verify.add_argument("--cleanup", action="store_true")
    verify.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            manifest = create_snapshot(
                args.path,
                checkouts=args.checkout,
                intended_missing=args.missing,
            )
            payload = {"valid": True, "manifest": str(manifest)}
            if args.format == "json":
                print(json.dumps(payload, indent=2, sort_keys=True))
            else:
                print(manifest)
            return 0
        changes = verify_snapshot(args.manifest)
        if args.cleanup:
            remove_snapshot(args.manifest)
        payload = {"valid": not changes, "changes": changes}
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        elif changes:
            print("Review snapshot is stale:")
            for change in changes:
                print(f"- {change}")
        else:
            print("Review snapshot matches.")
        return 1 if changes else 0
    except SnapshotError as exc:
        print(f"Review snapshot failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

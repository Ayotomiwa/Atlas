#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.source_snapshot import SnapshotError, cleanup_snapshot, prepare_snapshot


def _print_prepare(manifest: Path, output_format: str) -> None:
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(f"Source snapshot: {payload['snapshot_path']}")
    print(f"Selected commit: {payload['selected_commit']}")
    print(f"Mode: {payload['mode']}")
    print(f"Default relationship: {payload['default_relationship']}")
    if payload.get("merge_base"):
        print(f"Merge base: {payload['merge_base']}")
    print(f"Temporary manifest: {manifest}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare an immutable source snapshot for Atlas analysis.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--repository", required=True)
    prepare.add_argument("--commit")
    prepare.add_argument("--default-ref")
    prepare.add_argument("--format", choices=("human", "json"), default="human")
    cleanup = subparsers.add_parser("cleanup")
    cleanup.add_argument("--manifest", required=True)
    cleanup.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            manifest = prepare_snapshot(
                args.repository,
                commit=args.commit,
                default_ref=args.default_ref,
            )
            _print_prepare(manifest, args.format)
            return 0
        cleanup_snapshot(args.manifest)
        payload = {"cleaned": True, "manifest": str(Path(args.manifest).resolve())}
        if args.format == "json":
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print("Source snapshot cleaned up.")
        return 0
    except SnapshotError as exc:
        print(f"Source snapshot failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

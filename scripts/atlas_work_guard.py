#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.work_guard import (
    WorkGuardError,
    checkpoint_guard,
    cleanup_guard,
    restore_guard,
    start_guard,
    validate_guard,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guard one scoped Atlas materialization operation.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    start = subparsers.add_parser("start")
    start.add_argument("--root", required=True)
    start.add_argument("--path", action="append", default=[])
    start.add_argument("--missing-path", action="append", default=[])
    start.add_argument("--generated-path", action="append", default=[])
    start.add_argument("--id", action="append", default=[])
    start.add_argument("--format", choices=("text", "json"), default="text")
    checkpoint = subparsers.add_parser("checkpoint")
    checkpoint.add_argument("--root", required=True)
    checkpoint.add_argument("--state", required=True)
    checkpoint.add_argument("--key-file", required=True)
    checkpoint.add_argument("--format", choices=("text", "json"), default="text")
    restore = subparsers.add_parser("restore")
    restore.add_argument("--root", required=True)
    restore.add_argument("--state", required=True)
    restore.add_argument("--key-file", required=True)
    restore.add_argument("--to", choices=("pre", "materialized"), required=True)
    restore.add_argument("--format", choices=("text", "json"), default="text")
    validate = subparsers.add_parser("validate")
    validate.add_argument("--root", required=True)
    validate.add_argument("--state", required=True)
    validate.add_argument("--key-file", required=True)
    validate.add_argument("--format", choices=("text", "json"), default="text")
    cleanup = subparsers.add_parser("cleanup")
    cleanup.add_argument("--root", required=True)
    cleanup.add_argument("--state", required=True)
    cleanup.add_argument("--key-file", required=True)
    cleanup.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    try:
        if args.command == "start":
            handle = start_guard(
                args.root,
                paths=args.path,
                missing_paths=args.missing_path,
                generated_paths=args.generated_path,
                ids=args.id,
            )
            payload = {"state": str(handle.state_dir), "key_file": str(handle.key_file)}
            message = f"Atlas work guard started: {handle.state_dir} (key: {handle.key_file})"
        elif args.command == "checkpoint":
            state = checkpoint_guard(args.root, args.state, args.key_file)
            payload = {"state": str(state), "checkpoint": "materialized"}
            message = f"Atlas materialized checkpoint captured: {state}"
        elif args.command == "restore":
            root = restore_guard(args.root, args.state, args.key_file, args.to)
            payload = {"state": str(Path(args.state).resolve()), "restored": args.to, "root": str(root)}
            message = f"Atlas work restored to {args.to}: {root}"
        elif args.command == "validate":
            payload = validate_guard(args.root, args.state, args.key_file)
            message = (
                f"Atlas work validation {payload['status']}: "
                f"{len(payload['blocking'])} blocking, {len(payload['advisory'])} advisory"
            )
        else:
            removed_state, removed_key = cleanup_guard(
                args.root, args.state, args.key_file
            )
            payload = {"removed_state": str(removed_state), "removed_key_file": str(removed_key)}
            message = f"Atlas work guard cleaned up: {removed_state} and {removed_key}"
    except (OSError, WorkGuardError) as exc:
        print(f"Atlas work guard failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(payload, indent=2) if args.format == "json" else message)
    return 1 if args.command == "validate" and payload["blocking"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

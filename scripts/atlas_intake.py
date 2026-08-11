#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.intake import (
    CHECKPOINT_DIR,
    SOURCE_KEY_RE,
    CheckpointConflictError,
    IntakeError,
    checkpoint_digest,
    load_checkpoint,
    validate_checkpoint,
    write_checkpoint_atomic,
)


def _checkpoint_path(root: Path, value: str) -> Path:
    checkpoint_root = (root / CHECKPOINT_DIR).resolve()
    if SOURCE_KEY_RE.fullmatch(value):
        candidate = checkpoint_root / f"{value}.json"
    else:
        raw = Path(value)
        candidate = (raw if raw.is_absolute() else root / raw).resolve()
    try:
        candidate.relative_to(checkpoint_root)
    except ValueError as exc:
        raise IntakeError(
            f"checkpoint must be a source key or a path below {CHECKPOINT_DIR.as_posix()}"
        ) from exc
    if candidate.parent != checkpoint_root:
        raise IntakeError("checkpoint must be a direct child of _intake/checkpoints")
    if candidate.suffix != ".json":
        raise IntakeError("checkpoint path must end in .json")
    return candidate


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _read_input(value: str) -> dict:
    try:
        text = sys.stdin.read() if value == "-" else Path(value).read_text(encoding="utf-8")
    except OSError as exc:
        raise IntakeError(f"cannot read checkpoint input: {exc}") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IntakeError(f"invalid checkpoint input JSON: {exc}") from exc
    errors = validate_checkpoint(payload)
    if errors:
        raise IntakeError("; ".join(errors))
    return payload


def _emit(payload: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        return
    if payload["command"] == "show":
        if not payload["exists"]:
            print(f"Checkpoint {payload['checkpoint']} is missing.")
            return
        print(f"Checkpoint: {payload['checkpoint']}")
        print(f"Digest: {payload['digest']}")
        data = payload["data"]
        print(f"Source: {data['source']['key']} ({data['source']['default_branch']})")
        print(f"Observed through: {data['observed_through']['commit']}")
        print(f"Considered through: {data['considered_through']['commit']}")
        print(f"Unresolved: {len(data['unresolved'])}")
        return
    print(f"Wrote checkpoint: {payload['checkpoint']}")
    print(f"Previous digest: {payload['previous_digest'] or 'missing'}")
    print(f"Digest: {payload['digest']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect and atomically update Atlas intake checkpoints.")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--format", choices=["human", "json"], default="human")
    commands = parser.add_subparsers(dest="command", required=True)

    show = commands.add_parser("show", help="show one checkpoint and its compare-and-swap digest")
    show.add_argument("checkpoint", help="source key or package-relative checkpoint path")

    write = commands.add_parser("write", help="atomically write one validated checkpoint")
    write.add_argument("--checkpoint", required=True, help="source key or package-relative checkpoint path")
    write.add_argument("--input", required=True, help="JSON input path, or - for stdin")
    write.add_argument(
        "--expected-digest",
        required=True,
        help="digest returned by show, or the literal missing",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    try:
        path = _checkpoint_path(root, args.checkpoint)
        relative = _relative(root, path)
        if args.command == "show":
            digest = checkpoint_digest(path)
            payload = {
                "command": "show",
                "checkpoint": relative,
                "exists": digest is not None,
                "digest": digest,
                "data": load_checkpoint(path) if digest is not None else None,
            }
        else:
            expected = None if args.expected_digest == "missing" else args.expected_digest
            value = _read_input(args.input)
            previous = checkpoint_digest(path)
            digest = write_checkpoint_atomic(path, value, expected_digest=expected)
            payload = {
                "command": "write",
                "checkpoint": relative,
                "written": True,
                "previous_digest": previous,
                "digest": digest,
            }
    except CheckpointConflictError as exc:
        print(f"Atlas intake conflict: {exc}", file=sys.stderr)
        return 2
    except IntakeError as exc:
        print(f"Atlas intake failed: {exc}", file=sys.stderr)
        return 1

    _emit(payload, args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

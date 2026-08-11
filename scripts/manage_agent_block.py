#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import difflib
import json
import sys


START = b"<!-- atlas:managed:start -->"
END = b"<!-- atlas:managed:end -->"
TOKENS = {
    "{{PACKAGE}}": "package",
    "{{REPOSITORY_SEED}}": "seed",
    "{{SEED_VERIFICATION}}": "verification",
}


class ManagedBlockError(ValueError):
    pass


def inspect_bytes(data: bytes) -> dict[str, object]:
    starts = data.count(START)
    ends = data.count(END)
    if starts == 0 and ends == 0:
        return {"state": "absent", "start_markers": 0, "end_markers": 0}
    if starts != 1 or ends != 1:
        raise ManagedBlockError(
            f"malformed Atlas markers: expected zero or one pair, found {starts} start and {ends} end markers"
        )
    start = data.index(START)
    end = data.index(END)
    if start >= end:
        raise ManagedBlockError("malformed Atlas markers: end marker precedes start marker")
    return {
        "state": "managed",
        "start_markers": starts,
        "end_markers": ends,
        "start": start,
        "end": end + len(END),
    }


def render_block(path: Path, values: dict[str, str], newline: bytes) -> bytes:
    text = path.read_text(encoding="utf-8")
    for token, name in TOKENS.items():
        text = text.replace(token, values[name])
    remaining = [token for token in TOKENS if token in text]
    if remaining:
        raise ManagedBlockError("unresolved managed-block placeholders: " + ", ".join(remaining))
    data = text.strip().replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    data = data.replace(b"\n", newline)
    block_state = inspect_bytes(data)
    if block_state["state"] != "managed":
        raise ManagedBlockError("managed-block asset must contain exactly one Atlas marker pair")
    return data


def merged_bytes(existing: bytes, block: bytes) -> bytes:
    state = inspect_bytes(existing)
    newline = b"\r\n" if b"\r\n" in existing else b"\n"
    block = block.replace(b"\r\n", b"\n").replace(b"\r", b"\n").replace(b"\n", newline)
    if state["state"] == "managed":
        return existing[: int(state["start"])] + block + existing[int(state["end"]) :]
    if not existing:
        return block + newline
    if existing.endswith(newline + newline):
        separator = b""
    elif existing.endswith(newline):
        separator = newline
    else:
        separator = newline + newline
    return existing + separator + block + newline


def payload(target: Path, data: bytes) -> dict[str, object]:
    state = inspect_bytes(data)
    return {
        "target": str(target.resolve()),
        "exists": target.exists(),
        "state": state["state"],
        "start_markers": state["start_markers"],
        "end_markers": state["end_markers"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect or safely merge an Atlas-managed agent block.")
    parser.add_argument("mode", choices=("inspect", "dry-run", "apply"))
    parser.add_argument("--target", required=True)
    parser.add_argument("--block")
    parser.add_argument("--package", default="datalens")
    parser.add_argument("--seed", default="path-derived")
    parser.add_argument(
        "--verification",
        choices=("matched", "not-verified", "path-derived"),
        default="path-derived",
    )
    parser.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser().resolve()
    existing = target.read_bytes() if target.exists() else b""
    try:
        current = payload(target, existing)
        if args.mode == "inspect":
            if args.format == "json":
                print(json.dumps(current, indent=2, sort_keys=True))
            else:
                print(f"{target}: {current['state']}")
            return 0
        if not args.block:
            parser.error("--block is required for dry-run and apply")
        if not target.parent.exists():
            raise ManagedBlockError(f"target parent does not exist: {target.parent}")
        newline = b"\r\n" if b"\r\n" in existing else b"\n"
        block = render_block(
            Path(args.block).expanduser().resolve(),
            {"package": args.package, "seed": args.seed, "verification": args.verification},
            newline,
        )
        updated = merged_bytes(existing, block)
    except (OSError, UnicodeError, ManagedBlockError) as exc:
        print(f"Managed block failed: {exc}", file=sys.stderr)
        return 1

    if args.mode == "dry-run":
        before = existing.decode("utf-8", errors="surrogateescape").splitlines(keepends=True)
        after = updated.decode("utf-8", errors="surrogateescape").splitlines(keepends=True)
        print(
            "".join(
                difflib.unified_diff(
                    before,
                    after,
                    fromfile=str(target),
                    tofile=str(target),
                )
            ),
            end="",
        )
        return 0

    target.write_bytes(updated)
    result = {**payload(target, updated), "changed": updated != existing}
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        action = "updated" if existing else "created"
        suffix = "" if result["changed"] else " (already current)"
        print(f"{action}: {target}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

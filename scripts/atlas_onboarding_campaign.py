#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.onboarding_campaign import (
    CAMPAIGN_DIR,
    ITEM_STATES,
    SLUG_RE,
    CampaignConflictError,
    CampaignError,
    campaign_digest,
    load_campaign,
    validate_campaign,
    write_campaign_atomic,
)


def _campaign_path(root: Path, value: str) -> Path:
    campaign_root = (root / CAMPAIGN_DIR).resolve()
    if SLUG_RE.fullmatch(value):
        candidate = campaign_root / f"{value}.json"
    else:
        raw = Path(value)
        candidate = (raw if raw.is_absolute() else root / raw).resolve()
    try:
        candidate.relative_to(campaign_root)
    except ValueError as exc:
        raise CampaignError(
            f"campaign must be an ID or a path below {CAMPAIGN_DIR.as_posix()}"
        ) from exc
    if candidate.parent != campaign_root:
        raise CampaignError("campaign must be a direct child of _intake/onboarding")
    if candidate.suffix != ".json":
        raise CampaignError("campaign path must end in .json")
    return candidate


def _read_input(value: str) -> dict:
    try:
        text = sys.stdin.read() if value == "-" else Path(value).read_text(encoding="utf-8")
    except OSError as exc:
        raise CampaignError(f"cannot read campaign input: {exc}") from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CampaignError(f"invalid campaign input JSON: {exc}") from exc
    errors = validate_campaign(payload)
    if errors:
        raise CampaignError("; ".join(errors))
    return payload


def _show_payload(path: Path, root: Path, statuses: list[str], limit: int | None) -> dict:
    digest = campaign_digest(path)
    data = load_campaign(path) if digest is not None else None
    items = []
    if data is not None:
        items = sorted(data["items"], key=lambda item: item["item_id"])
        if statuses:
            allowed = set(statuses)
            items = [item for item in items if item["state"] in allowed]
        if limit is not None:
            items = items[:limit]
    return {
        "command": "show",
        "campaign": path.relative_to(root).as_posix(),
        "exists": digest is not None,
        "digest": digest,
        "data": data,
        "items": items,
    }


def _emit(payload: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        return
    if payload["command"] == "write":
        print(f"Wrote campaign: {payload['campaign']}")
        print(f"Digest: {payload['digest']}")
        return
    if not payload["exists"]:
        print(f"Campaign {payload['campaign']} is missing.")
        return
    data = payload["data"]
    counts = {state: 0 for state in sorted(ITEM_STATES)}
    for item in data["items"]:
        counts[item["state"]] += 1
    rendered_counts = ", ".join(f"{state}={count}" for state, count in counts.items() if count)
    print(f"Campaign: {payload['campaign']}")
    print(f"Digest: {payload['digest']}")
    print(f"Phase: {data['phase']}")
    print(f"Counts: {rendered_counts or 'none'}")
    for item in payload["items"]:
        print(f"- {item['item_id']}: {item['state']} ({item['source_key']}:{item['repository_root']})")


def _positive_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect and atomically update Atlas onboarding campaigns.")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--format", choices=["human", "json"], default="human")
    commands = parser.add_subparsers(dest="command", required=True)
    show = commands.add_parser("show", help="show one campaign and its compare-and-swap digest")
    show.add_argument("campaign_id", help="campaign ID or package-relative campaign path")
    show.add_argument("--status", action="append", choices=sorted(ITEM_STATES), default=[])
    show.add_argument("--limit", type=_positive_integer)
    show.add_argument("--format", dest="show_format", choices=["human", "json"])
    write = commands.add_parser("write", help="atomically write one validated campaign")
    write.add_argument("--campaign", required=True, help="campaign ID or package-relative campaign path")
    write.add_argument("--input", required=True, help="JSON input path, or - for stdin")
    write.add_argument("--expected-digest", required=True, help="digest returned by show, or the literal missing")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    output_format = args.show_format or args.format if args.command == "show" else args.format

    try:
        if args.command == "show":
            path = _campaign_path(root, args.campaign_id)
            payload = _show_payload(path, root, args.status, args.limit)
        else:
            path = _campaign_path(root, args.campaign)
            value = _read_input(args.input)
            expected = None if args.expected_digest == "missing" else args.expected_digest
            digest = write_campaign_atomic(path, value, expected_digest=expected)
            payload = {
                "command": "write",
                "campaign": path.relative_to(root).as_posix(),
                "written": True,
                "digest": digest,
            }
    except CampaignConflictError as exc:
        print(f"Atlas onboarding campaign conflict: {exc}", file=sys.stderr)
        return 2
    except CampaignError as exc:
        print(f"Atlas onboarding campaign failed: {exc}", file=sys.stderr)
        return 1
    _emit(payload, output_format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.maps import MapBuildError
from scripts.lib.query import AtlasQuery


def _emit(payload: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        return
    for warning in payload.get("warnings") or []:
        print(f"WARNING: {warning}")
    if payload.get("error"):
        print(payload["error"])
        return
    command = payload["command"]
    if command == "resolve":
        record = payload.get("record")
        if record:
            print(f"{record.get('id')} [{record.get('status', 'unknown')}] -> {record.get('page', '')}")
        else:
            print(payload["fallback"])
    elif command == "route":
        for record in payload["results"]:
            print(f"{record['id']} [{record.get('status', 'unknown')}] {record.get('title', '')} -> {record.get('page', '')}")
    elif command == "context":
        context = payload["context"]
        print(f"Git-relative path: {context.get('git_relative_path', '.')}")
        for warning in context.get("warnings") or []:
            print(f"WARNING: {warning}")
        print("Repository candidates:")
        for record in context.get("repositories") or []:
            print(
                f"  {record['id']} [{record.get('status', 'unknown')}] "
                f"via {record['match_basis']}={record['matched_path']} -> {record.get('page', '')}"
            )
        print("Component candidates:")
        for record in context.get("components") or []:
            print(
                f"  {record['id']} [{record.get('status', 'unknown')}] "
                f"via {record['match_basis']}={record['matched_path']} -> {record.get('page', '')}"
            )
    elif command == "neighbors":
        for item in payload["results"]:
            edge = item["edge"]
            print(f"{item['direction']}: {item['peer']} via {edge['field']} ({edge['confidence']})")
    elif command == "impact":
        for item in payload["results"]:
            route = item.get("route") or {}
            label = "direct" if item["direct"] else f"depth {item['depth']}"
            print(f"{item['id']} [{label}; {item['confidence']}] -> {route.get('page', '')}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve and traverse generated Atlas routing maps.")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--format", choices=("human", "json"), default="human")
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("identifier")

    route_parser = subparsers.add_parser("route")
    route_parser.add_argument("query")

    context_parser = subparsers.add_parser("context")
    context_parser.add_argument("path", nargs="?", default=".")

    neighbors_parser = subparsers.add_parser("neighbors")
    neighbors_parser.add_argument("identifier")

    impact_parser = subparsers.add_parser("impact")
    impact_parser.add_argument("identifier")
    impact_parser.add_argument("--direction", choices=("downstream", "upstream"), default="downstream")
    impact_parser.add_argument("--max-depth", type=int, default=6)

    args = parser.parse_args(argv)
    try:
        query = AtlasQuery(Path(args.root))
    except (MapBuildError, OSError, json.JSONDecodeError) as exc:
        print(f"Atlas query failed: {exc}", file=sys.stderr)
        return 1

    payload: dict = {"command": args.command}
    if query.warnings:
        payload["warnings"] = query.warnings
    if args.command == "resolve":
        payload["record"] = query.resolve(args.identifier)
        if payload["record"] is None:
            payload["fallback"] = (
                f"{args.identifier!r} is not a map record, routed target, or exact curated page ID. "
                "Search the appropriate curated domain index; do not choose an ambiguous title match."
            )
    elif args.command == "route":
        payload["results"] = query.route(args.query)
    elif args.command == "context":
        payload["context"] = query.context(args.path)
    elif args.command == "neighbors":
        payload["starting_record"] = query.resolve(args.identifier)
        if payload["starting_record"] is None:
            payload["error"] = f"No exact Atlas record or routed target found for {args.identifier!r}."
            payload["results"] = []
        else:
            payload["results"] = query.neighbors(args.identifier)
    else:
        if args.max_depth < 1:
            parser.error("--max-depth must be positive")
        payload["starting_record"] = query.resolve(args.identifier)
        payload["direction"] = args.direction
        if payload["starting_record"] is None:
            payload["error"] = f"No exact Atlas record or routed target found for {args.identifier!r}."
            payload["results"] = []
        else:
            payload["results"] = query.impact(
                args.identifier,
                direction=args.direction,
                max_depth=args.max_depth,
            )
    _emit(payload, args.format)
    return 1 if payload.get("error") or payload.get("record", True) is None else 0


if __name__ == "__main__":
    raise SystemExit(main())

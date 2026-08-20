#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.maps import MapBuildError
from scripts.lib.query import AtlasQuery, ExactResolver
from scripts.lib.staging import query_staging


def _no_results(reason: str) -> str:
    """Say nothing was found, out loud.

    Silent output cannot be told apart from a command that did not run, and Atlas
    never lets absence stand in for evidence.
    """
    return f"{reason}. Absence from the maps is not evidence that none exists."


def _record_state(record: dict) -> str:
    values = [
        str(record.get("status", "unknown")),
        f"trust={record.get('trust', 'unknown')}",
    ]
    checkout = record.get("checkout_state")
    if checkout and checkout != "main-clean":
        values.append(f"checkout={checkout}")
    return "; ".join(values)


def _short_git_ref(value: object) -> str:
    if value is None or value == "":
        return "start"
    text = str(value)
    return text[:12] if len(text) > 12 else text


def _change_source_summary(value: object) -> str:
    if not isinstance(value, dict):
        return ""
    parts = []
    source_key = value.get("source_key")
    branch = value.get("branch")
    if source_key:
        parts.append(f"source={source_key}")
    if branch:
        parts.append(f"branch={branch}")
    commit_range = value.get("commit_range")
    if isinstance(commit_range, dict):
        before = _short_git_ref(commit_range.get("from_exclusive"))
        through = _short_git_ref(commit_range.get("through_inclusive"))
        parts.append(f"range={before}..{through}")
    merge_requests = value.get("merge_requests")
    if isinstance(merge_requests, list):
        mr_ids = []
        for item in merge_requests:
            if not isinstance(item, dict):
                continue
            mr_id = item.get("id")
            if isinstance(mr_id, (str, int)) and str(mr_id).strip():
                mr_ids.append(str(mr_id))
        parts.append(f"MRs={','.join(mr_ids) if mr_ids else 'none'}")
    return "; ".join(parts)


def _emit(payload: dict, output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        return
    for warning in payload.get("warnings") or []:
        print(f"WARNING: {warning}")
    for diagnostic in payload.get("structured_diagnostics") or []:
        print(f"STRUCTURED DIAGNOSTIC: {diagnostic['page']}: {diagnostic['message']}")
    if payload.get("error"):
        print(payload["error"])
        return
    command = payload["command"]
    if command == "resolve":
        record = payload.get("record")
        if record:
            print(
                f"{record.get('id')} [{_record_state(record)}] -> {record.get('page', '')}"
            )
        else:
            print(payload["fallback"])
    elif command == "find":
        candidates = payload.get("candidates") or []
        if candidates:
            print(f"Candidate Atlas records (showing {len(candidates)} of {payload.get('total_matches', len(candidates))}):")
        for index, record in enumerate(candidates, start=1):
            print(
                f"{index}. {record['id']} [{_record_state(record)}] "
                f"{record.get('title', '')}"
            )
            if record.get("description"):
                print(f"   {record['description']}")
            print(f"   Match: {', '.join(record.get('match_reasons') or [])}")
            print(f"   Page: {record.get('page', '')}")
            print(f"   Index: {record.get('collection_index', '')}")
            for conflict in record.get("matched_conflicts") or []:
                print(f"   Conflict: {conflict.get('id')} — {conflict.get('topic', '')}")
            context = record.get("context") or {}
            if context:
                print(
                    f"   Context: {context.get('match_basis', 'candidate')}="
                    f"{context.get('matched_path', '')}; locator {context.get('locator_match', 'not-verified')}"
                )
        if payload.get("ambiguous"):
            print("Multiple candidates remain; select using the question and curated evidence or ask the user.")
        if not candidates:
            print(
                "No curated candidate matched this search. Consult the relevant collection/domain index, "
                "then broaden to the curated root index. This result is not evidence that no record exists."
            )
    elif command == "route":
        for record in payload["results"]:
            # Promoted resources carry `name`; pages carry `title`.
            label = record.get("title") or record.get("name") or ""
            print(
                f"{record['id']} [{_record_state(record)}] {label} -> {record.get('page', '')}"
            )
        if not payload["results"]:
            print(_no_results("No curated record routes from this query"))
    elif command == "context":
        context = payload["context"]
        print(f"Git-relative path: {context.get('git_relative_path', '.')}")
        for warning in context.get("warnings") or []:
            print(f"WARNING: {warning}")
        print("Repository candidates:")
        repositories = context.get("repositories") or []
        for record in repositories:
            print(
                f"  {record['id']} [{_record_state(record)}] "
                f"via {record['match_basis']}={record['matched_path']}; "
                f"locator {record.get('locator_match', 'not-verified')} -> {record.get('page', '')}"
            )
        if not repositories:
            print("  No repository candidates found.")
        print("Component candidates:")
        components = context.get("components") or []
        for record in components:
            print(
                f"  {record['id']} [{_record_state(record)}] "
                f"via {record['match_basis']}={record['matched_path']} -> {record.get('page', '')}"
            )
        if not components:
            print("  No component candidates found.")
        if not repositories and not components:
            print(_no_results("No repository or component context is recorded for this path"))
    elif command == "questions":
        if payload.get("candidate_only"):
            print("Candidate scope only; confirm the intended record or topic before asking a question.")
        context = payload.get("context") or {}
        if payload.get("candidate_only") and context:
            candidates = [
                *(context.get("repositories") or []),
                *(context.get("components") or []),
            ]
            if candidates:
                print("Context candidates:")
                for record in candidates:
                    print(
                        f"  {record['id']} [{record.get('status', 'unknown')}] "
                        f"via {record.get('match_basis')}={record.get('matched_path')} "
                        f"locator {record.get('locator_match', 'not-verified')} -> {record.get('page', '')}"
                    )
        if payload.get("target_candidates"):
            print("Target candidates:")
            for record in payload["target_candidates"]:
                label = record.get("title") or record.get("name") or ""
                print(f"  {record['id']} [{record.get('status', 'unknown')}] {label} -> {record.get('page', '')}")
                if record.get("description"):
                    print(f"    {record['description']}")
                if record.get("match_reasons"):
                    print(f"    Match: {', '.join(record['match_reasons'])}")
        if len(payload.get("domain_candidates") or []) > 1:
            print(f"Domain candidates: {', '.join(payload['domain_candidates'])}")
        for question in payload["results"]:
            owner = question["owner"]
            affected = ", ".join(question.get("affected_ids") or []) or "none recorded"
            print(f"{question['id']} [{_record_state(owner)}] {question['question']}")
            print(f"  Evidence gap: {question['evidence_gap']}")
            print(f"  Owner: {owner['id']} -> {question['page']}#{question['anchor']}")
            print(f"  Affected IDs: {affected}")
            print(f"  Match: {question['match_basis']}")
            if question.get("pending_staging"):
                pending = ", ".join(item.get("id", "") for item in question["pending_staging"])
                print(f"  Pending staging: {pending}")
        if not payload["results"]:
            print(
                "No eligible curated open questions were found for this scope. "
                "That routed result is not evidence that no relevant knowledge gap exists."
            )
        if payload.get("suppressed_pending"):
            print(
                f"Suppressed {len(payload['suppressed_pending'])} question(s) already referenced by "
                "active staging evidence; use --include-pending to show them."
            )
        for diagnostic in payload.get("diagnostics") or []:
            print(f"QUESTION DIAGNOSTIC: {diagnostic['page']}: {diagnostic['message']}")
    elif command == "staging":
        results = payload.get("results") or []
        if results:
            print(f"Matching staging records: {len(results)}")
        for record in results:
            print(
                f"{record['id']} [{record.get('status', '')}] "
                f"{record.get('title', '')}"
            )
            context = [
                f"type={record.get('type') or 'unknown'}",
                f"bucket={record.get('bucket', '')}",
                f"captured_by={record.get('captured_by') or 'unknown'}",
            ]
            if record.get("candidate_domain"):
                context.append(f"domain={record['candidate_domain']}")
            if record.get("timestamp"):
                context.append(f"date={record['timestamp']}")
            if record.get("source_type"):
                context.append(f"source={record['source_type']}")
            onboarding_source = record.get("onboarding_source")
            if isinstance(onboarding_source, dict):
                campaign_id = onboarding_source.get("campaign_id")
                item_id = onboarding_source.get("item_id")
                if isinstance(campaign_id, str) and isinstance(item_id, str):
                    context.append(f"onboarding={campaign_id}/{item_id}")
            print(f"  {'; '.join(context)}")
            if record.get("description"):
                print(f"  {record['description']}")
            if record.get("suggested_targets"):
                print(f"  Suggested targets: {', '.join(record['suggested_targets'])}")
            change_source = _change_source_summary(record.get("change_source"))
            if change_source:
                print(f"  Change source: {change_source}")
            print(f"  Page: {record.get('page', '')}")
        if not results:
            print("No matching staging records were found.")
        for diagnostic in payload.get("diagnostics") or []:
            print(f"STAGING DIAGNOSTIC: {diagnostic['page']}: {diagnostic['message']}")
    elif command == "neighbors":
        for item in payload["results"]:
            edge = item["edge"]
            print(f"{item['direction']}: {item['peer']} via {edge['field']} ({edge['confidence']})")
        if not payload["results"]:
            print(_no_results("No direct connection is recorded for this record"))
    elif command == "impact":
        for item in payload["results"]:
            route = item.get("route") or {}
            label = "direct" if item["direct"] else f"depth {item['depth']}"
            print(f"{item['id']} [{label}; {item['confidence']}] -> {route.get('page', '')}")
        if not payload["results"]:
            print(_no_results("No impact path is recorded from this record"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find, resolve and traverse Atlas routing records.")
    parser.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--format", choices=("human", "json"), default="human")
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("identifier")

    route_parser = subparsers.add_parser("route")
    route_parser.add_argument("query")

    find_parser = subparsers.add_parser("find")
    find_parser.add_argument("query")
    find_parser.add_argument("--type", dest="types", action="append", default=[])
    find_parser.add_argument("--domain")
    find_parser.add_argument("--path")
    find_parser.add_argument("--limit", type=int, default=3)
    find_parser.add_argument(
        "--format",
        dest="find_format",
        choices=("human", "json"),
        default=None,
    )

    context_parser = subparsers.add_parser("context")
    context_parser.add_argument("path", nargs="?", default=".")

    questions_parser = subparsers.add_parser("questions")
    questions_parser.add_argument("query", nargs="?")
    questions_parser.add_argument("--path", default=".")
    questions_parser.add_argument(
        "--scope",
        choices=("auto", "local", "domain", "package"),
        default="auto",
    )
    questions_parser.add_argument("--include-pending", action="store_true")
    questions_parser.add_argument(
        "--format",
        dest="question_format",
        choices=("human", "json"),
        default=None,
    )

    staging_parser = subparsers.add_parser("staging")
    staging_parser.add_argument("--status", dest="statuses", action="append", default=[])
    staging_parser.add_argument("--bucket", dest="buckets", action="append", default=[])
    staging_parser.add_argument("--domain")
    staging_parser.add_argument("--date")
    staging_parser.add_argument("--target", dest="targets", action="append", default=[])
    staging_parser.add_argument("--include-terminal", action="store_true")
    staging_parser.add_argument("--source-key")
    staging_parser.add_argument("--branch")
    staging_parser.add_argument("--from-exclusive")
    staging_parser.add_argument("--through-inclusive")
    staging_parser.add_argument(
        "--format",
        dest="staging_format",
        choices=("human", "json"),
        default=None,
    )

    neighbors_parser = subparsers.add_parser("neighbors")
    neighbors_parser.add_argument("identifier")

    impact_parser = subparsers.add_parser("impact")
    impact_parser.add_argument("identifier")
    impact_parser.add_argument("--direction", choices=("downstream", "upstream"), default="downstream")
    impact_parser.add_argument("--max-depth", type=int, default=6)

    args = parser.parse_args(argv)
    if args.command == "staging":
        payload: dict = {"command": "staging"}
        try:
            payload.update(
                query_staging(
                    Path(args.root),
                    statuses=args.statuses,
                    buckets=args.buckets,
                    domain=args.domain,
                    timestamp=args.date,
                    targets=args.targets,
                    include_terminal=args.include_terminal,
                    source_key=args.source_key,
                    branch=args.branch,
                    from_exclusive=args.from_exclusive,
                    through_inclusive=args.through_inclusive,
                )
            )
        except (OSError, ValueError) as exc:
            payload.update({"error": str(exc), "results": [], "diagnostics": []})
        _emit(payload, args.staging_format or args.format)
        return 1 if payload.get("error") else 0

    payload: dict = {"command": args.command}
    if args.command == "resolve":
        try:
            resolver = ExactResolver(Path(args.root))
            payload["record"] = resolver.resolve(args.identifier)
        except (MapBuildError, OSError, json.JSONDecodeError) as exc:
            print(f"Atlas query failed: {exc}", file=sys.stderr)
            return 1
        if resolver.warnings:
            payload["warnings"] = resolver.warnings
        if resolver.structured_diagnostics:
            payload["structured_diagnostics"] = resolver.structured_diagnostics
        if payload["record"] is None:
            payload["fallback"] = (
                f"{args.identifier!r} is not a map record, routed target, or exact curated page ID. "
                "Search the appropriate curated domain index; do not choose an ambiguous title match."
            )
        _emit(payload, args.format)
        return 1 if payload.get("record") is None else 0

    preloads = {
        "find": {"search"},
        "route": set(),
        "context": set(),
        "questions": {"questions"},
        "neighbors": {"graph"},
        "impact": {"graph"},
    }
    try:
        query = AtlasQuery(Path(args.root), preload=preloads[args.command])
    except (MapBuildError, OSError, json.JSONDecodeError) as exc:
        print(f"Atlas query failed: {exc}", file=sys.stderr)
        return 1

    if query.warnings:
        payload["warnings"] = query.warnings
    if query.structured_diagnostics:
        payload["structured_diagnostics"] = query.structured_diagnostics
    if args.command == "find":
        try:
            payload.update(
                query.find(
                    args.query,
                    types=args.types,
                    domain=args.domain,
                    path=args.path,
                    limit=args.limit,
                )
            )
        except ValueError as exc:
            payload["error"] = str(exc)
            payload["candidates"] = []
        unverified = [
            item["id"]
            for item in payload.get("candidates") or []
            if (item.get("context") or {}).get("locator_match") == "not-verified"
        ]
        if unverified:
            payload.setdefault("warnings", []).append(
                "Path context is not locator-verified for: "
                + ", ".join(unverified)
                + ". Treat it as a routing candidate, not proof of repository identity."
            )
    elif args.command == "route":
        payload["results"] = query.route(args.query)
    elif args.command == "context":
        payload["context"] = query.context(args.path)
    elif args.command == "questions":
        payload.update(
            query.questions(
                args.query,
                path=args.path,
                scope=args.scope,
                include_pending=args.include_pending,
            )
        )
        non_authoritative = sorted(
            {
                item["owner"]["id"]
                for item in payload["results"]
                if item["owner"].get("trust") != "authoritative"
            }
        )
        if non_authoritative:
            payload.setdefault("warnings", []).append(
                "Explicit target includes non-authoritative Atlas pages: "
                + ", ".join(non_authoritative)
                + "."
            )
        checkout_advisories = sorted(
            {
                f"{item['owner']['id']} ({item['owner'].get('checkout_state')})"
                for item in payload["results"]
                if item["owner"].get("checkout_state") not in {None, "main-clean"}
            }
        )
        if checkout_advisories:
            payload.setdefault("warnings", []).append(
                "Checkout advisory: " + ", ".join(checkout_advisories) + "."
            )
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
            excluded = query.opposite_direction_peers(args.identifier, args.direction)
            if excluded:
                other = "upstream" if args.direction == "downstream" else "downstream"
                note = (
                    f"{len(excluded)} direct {other} peer(s) are outside this direction "
                    f"and not listed: {', '.join(excluded)}."
                )
                # Deleting an asset breaks the things that write to it as well as the
                # things that read it, and a producer sits on an incoming edge. That
                # caveat applies to assets, not to components, whose upstream peers are
                # dependencies that a change here does not break. Keyed on the stable ID
                # prefix, because a map-sourced record carries a collection, not a type.
                if args.identifier.split(".", 1)[0] in {"asset", "schema", "resource", "infra"}:
                    note += (
                        " For a deletion question, run the opposite direction too:"
                        " producers of this asset break when it is removed."
                    )
                payload.setdefault("warnings", []).append(note)
    output_format = (
        getattr(args, "question_format", None)
        or getattr(args, "find_format", None)
        or getattr(args, "staging_format", None)
        or args.format
    )
    _emit(payload, output_format)
    return 1 if payload.get("error") or payload.get("record", True) is None else 0


if __name__ == "__main__":
    raise SystemExit(main())

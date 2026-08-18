#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.evaluation import (
    EvaluationError,
    RUN_SCHEMA_V2,
    freeze_answers,
    freeze_run,
    load_json,
    prepare_run,
    resolve_rubric_path,
    score_result,
    validate_result,
    verify_answer_freeze,
    verify_run_freeze,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare, freeze, validate and score sealed Atlas evaluations.")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--destination", required=True)
    prepare.add_argument("--run-id", required=True)
    prepare.add_argument("--fixture", required=True)
    prepare.add_argument("--fixture-head", required=True)
    prepare.add_argument("--incremental-head")
    freeze = sub.add_parser("freeze")
    freeze.add_argument("run_root")
    verify_freeze = sub.add_parser("verify-freeze")
    verify_freeze.add_argument("run_root")
    validate = sub.add_parser("validate")
    validate.add_argument("result")
    validate.add_argument("--rubric")
    score = sub.add_parser("score")
    score.add_argument("result")
    score.add_argument("--rubric")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            path = prepare_run(
                ROOT,
                args.destination,
                run_id=args.run_id,
                fixture=args.fixture,
                fixture_head=args.fixture_head,
                incremental_head=args.incremental_head,
            )
            print(path)
            return 0
        if args.command == "freeze":
            metadata = load_json(Path(args.run_root) / "run.json")
            print(freeze_run(args.run_root) if metadata.get("schema_version") == RUN_SCHEMA_V2 else freeze_answers(args.run_root))
            return 0
        if args.command == "verify-freeze":
            metadata = load_json(Path(args.run_root) / "run.json")
            changes = verify_run_freeze(args.run_root) if metadata.get("schema_version") == RUN_SCHEMA_V2 else verify_answer_freeze(args.run_root)
            if changes:
                for change in changes:
                    print(change, file=sys.stderr)
                return 1
            print("Evaluation run freeze is valid.")
            return 0
        rubric_path = resolve_rubric_path(args.result, args.rubric)
        rubric = load_json(rubric_path)
        result = load_json(args.result)
        if args.command == "validate":
            validate_result(result, rubric)
            print("Evaluation result is valid.")
            return 0
        print(json.dumps(score_result(result, rubric), indent=2, sort_keys=True))
        return 0
    except EvaluationError as exc:
        print(f"Atlas evaluation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

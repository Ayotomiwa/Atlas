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
    RESULT_SCHEMA,
    RESULT_SCHEMA_V2,
    RUN_SCHEMA_V1,
    RUN_SCHEMA_V2,
    freeze_answers,
    freeze_run,
    load_json,
    prepare_run,
    resolve_rubric_path,
    score_result,
    validate_result,
    verify_answer_freeze,
    verify_trusted_run_freeze,
)


def _resolve_result_run_root(result: str | Path, explicit: str | Path | None) -> Path | None:
    result_path = Path(result).resolve()
    placement_root = result_path.parent.parent if result_path.parent.name == "results" else None
    associated_root = None
    if placement_root is not None and (placement_root / "run.json").is_file():
        try:
            placement_schema = load_json(placement_root / "run.json").get("schema_version")
        except EvaluationError:
            placement_schema = None
        if placement_schema in {RUN_SCHEMA_V1, RUN_SCHEMA_V2}:
            associated_root = placement_root
    if explicit is not None:
        override = Path(explicit).resolve()
        if associated_root is not None and associated_root != override:
            raise EvaluationError(
                "--run-root identifies a different evaluation run from the result's results directory"
            )
        return override
    return associated_root


def _result_run_schema(result: dict, run_root: Path | None) -> str | None:
    if run_root is None:
        if result.get("schema_version") == RESULT_SCHEMA_V2:
            raise EvaluationError(
                "v2 result run root cannot be inferred; place it under <run-root>/results/ "
                "or pass --run-root"
            )
        return None
    run_schema = load_json(run_root / "run.json").get("schema_version")
    expected_result_schema = {
        RUN_SCHEMA_V1: RESULT_SCHEMA,
        RUN_SCHEMA_V2: RESULT_SCHEMA_V2,
    }.get(run_schema)
    if expected_result_schema is None:
        raise EvaluationError(f"unsupported evaluation run schema: {run_schema!r}")
    if result.get("schema_version") != expected_result_schema:
        raise EvaluationError(
            f"result schema {result.get('schema_version')!r} does not match run schema {run_schema!r}"
        )
    return run_schema


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
    verify_freeze.add_argument("--freeze-digest")
    validate = sub.add_parser("validate")
    validate.add_argument("result")
    validate.add_argument("--rubric")
    validate.add_argument("--run-root")
    validate.add_argument("--freeze-digest")
    score = sub.add_parser("score")
    score.add_argument("result")
    score.add_argument("--rubric")
    score.add_argument("--run-root")
    score.add_argument("--freeze-digest")
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
            run_schema = metadata.get("schema_version")
            if run_schema == RUN_SCHEMA_V2:
                path = freeze_run(args.run_root)
            elif run_schema == RUN_SCHEMA_V1:
                path = freeze_answers(args.run_root)
            else:
                raise EvaluationError(f"unsupported evaluation run schema: {run_schema!r}")
            print(path)
            return 0
        if args.command == "verify-freeze":
            metadata = load_json(Path(args.run_root) / "run.json")
            run_schema = metadata.get("schema_version")
            if run_schema == RUN_SCHEMA_V2:
                is_v2 = True
                verify_trusted_run_freeze(args.run_root, args.freeze_digest)
                changes = []
            elif run_schema == RUN_SCHEMA_V1:
                is_v2 = False
                changes = verify_answer_freeze(args.run_root)
            else:
                raise EvaluationError(f"unsupported evaluation run schema: {run_schema!r}")
            if changes:
                for change in changes:
                    print(change, file=sys.stderr)
                return 1
            print("Evaluation run freeze is valid." if is_v2 else "Evaluation answer freeze is valid.")
            return 0
        result = load_json(args.result)
        run_root = _resolve_result_run_root(args.result, args.run_root)
        run_schema = _result_run_schema(result, run_root)
        if run_schema == RUN_SCHEMA_V2:
            frozen_rubric = (run_root / "rubric.json").resolve()
            if args.rubric is not None and Path(args.rubric).resolve() != frozen_rubric:
                raise EvaluationError("v2 --rubric must identify the frozen run rubric")
            rubric_path = frozen_rubric
        else:
            rubric_path = resolve_rubric_path(args.result, args.rubric)
        rubric = load_json(rubric_path)
        if args.command == "validate":
            validate_result(
                result,
                rubric,
                run_root=run_root,
                expected_freeze_manifest_sha256=args.freeze_digest,
            )
            print("Evaluation result is valid.")
            return 0
        print(json.dumps(score_result(
            result,
            rubric,
            run_root=run_root,
            expected_freeze_manifest_sha256=args.freeze_digest,
        ), indent=2, sort_keys=True))
        return 0
    except EvaluationError as exc:
        print(f"Atlas evaluation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

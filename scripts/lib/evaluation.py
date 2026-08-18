from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json


RESULT_SCHEMA = "atlas-evaluation-result/1.0"
RUN_SCHEMA_V1 = "atlas-evaluation-run/1.0"
RUN_SCHEMA_V2 = "atlas-evaluation-run/2.0"
RUN_FREEZE_SCHEMA_V2 = "atlas-evaluation-run-freeze/2.0"
CATEGORY_TO_WEIGHT = {
    "LOOKUP": "lookup",
    "SYNTHESIS": "synthesis",
    "IMPACT": "impact",
    "TRAP-CONFLICT": "conflict",
    "TRAP-UNKNOWABLE": "refusal",
    "TRAP-ABSENCE": "absence",
}
PROTECTED_RUN_ROOTS = (
    "fixture", "questions", "personas", "ground-truth", "answers", "telemetry", "manifests",
)
REQUIRED_V2_MANIFESTS = (
    "fixture.json", "tool-policy.json", "model-config.json", "atlas-snapshot.json",
)
IMMUTABLE_RUN_FIELDS = (
    "schema_version", "run_id", "fixture", "fixture_head", "incremental_head", "rubric_sha256", "sealed",
)


class EvaluationError(ValueError):
    pass


def stable_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def load_json(path: str | Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"JSON document must be an object: {path}")
    return value


def resolve_rubric_path(result: str | Path, explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).resolve()
    result_path = Path(result).resolve()
    candidates = (result_path.parent / "rubric.json", result_path.parent.parent / "rubric.json")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise EvaluationError(
        "cannot locate rubric.json beside the result or at the evaluation run root; pass --rubric explicitly"
    )


def digest_file(path: str | Path) -> str:
    return sha256(Path(path).read_bytes()).hexdigest()


def freeze_answers(run_root: str | Path) -> Path:
    run_root = Path(run_root).resolve()
    run_path = run_root / "run.json"
    metadata = load_json(run_path)
    if metadata.get("schema_version") == RUN_SCHEMA_V2:
        raise EvaluationError("v2 runs must use the master run freeze")
    if metadata.get("answer_sets_frozen"):
        raise EvaluationError("answer sets are already frozen")
    answers_root = run_root / "answers"
    files = sorted(path for path in answers_root.rglob("*") if path.is_file())
    if not files:
        raise EvaluationError("cannot freeze an empty answers directory")
    manifest = {
        "schema_version": "atlas-evaluation-answer-freeze/1.0",
        "files": {
            path.relative_to(run_root).as_posix(): digest_file(path)
            for path in files
        },
    }
    manifest_path = run_root / "answer-manifest.json"
    if manifest_path.exists():
        raise EvaluationError(f"answer freeze manifest already exists: {manifest_path}")
    manifest_path.write_bytes(stable_json(manifest))
    metadata["answer_sets_frozen"] = True
    metadata["answer_manifest_sha256"] = digest_file(manifest_path)
    run_path.write_bytes(stable_json(metadata))
    return manifest_path


def verify_answer_freeze(run_root: str | Path) -> list[str]:
    run_root = Path(run_root).resolve()
    metadata = load_json(run_root / "run.json")
    if metadata.get("schema_version") == RUN_SCHEMA_V2:
        raise EvaluationError("v2 runs must use master run freeze verification")
    if metadata.get("answer_sets_frozen") is not True:
        raise EvaluationError("answer sets are not frozen")
    manifest_path = run_root / "answer-manifest.json"
    manifest = load_json(manifest_path)
    if manifest.get("schema_version") != "atlas-evaluation-answer-freeze/1.0":
        raise EvaluationError("unsupported answer freeze manifest schema")
    if metadata.get("answer_manifest_sha256") != digest_file(manifest_path):
        raise EvaluationError("answer freeze manifest does not match run metadata")
    expected = manifest.get("files")
    if not isinstance(expected, dict) or not expected:
        raise EvaluationError("answer freeze manifest has no files")
    actual_paths = {
        path.relative_to(run_root).as_posix()
        for path in (run_root / "answers").rglob("*")
        if path.is_file()
    }
    changes = [f"unexpected answer file: {path}" for path in sorted(actual_paths - set(expected))]
    changes.extend(f"missing answer file: {path}" for path in sorted(set(expected) - actual_paths))
    for relative, expected_digest in sorted(expected.items()):
        path = run_root / relative
        if path.is_file() and digest_file(path) != expected_digest:
            changes.append(f"answer file changed: {relative}")
    return changes


def prepare_run(
    atlas_root: str | Path,
    destination: str | Path,
    *,
    run_id: str,
    fixture: str | Path,
    fixture_head: str,
    incremental_head: str | None = None,
) -> Path:
    atlas_root = Path(atlas_root).resolve()
    destination = Path(destination).resolve()
    try:
        destination.relative_to(atlas_root)
        inside_atlas = True
    except ValueError:
        inside_atlas = False
    if inside_atlas:
        raise EvaluationError("sealed evaluation destination must be outside the Atlas checkout")
    run_root = destination / run_id
    if run_root.exists():
        raise EvaluationError(f"evaluation run already exists: {run_root}")
    run_root.mkdir(parents=True)
    rubric_source = atlas_root / "evaluation" / "rubric.json"
    (run_root / "rubric.json").write_bytes(stable_json(load_json(rubric_source)))
    metadata = {
        "schema_version": RUN_SCHEMA_V2,
        "run_id": run_id,
        "fixture": str(Path(fixture).resolve()),
        "fixture_head": fixture_head,
        "incremental_head": incremental_head,
        "rubric_sha256": digest_file(run_root / "rubric.json"),
        "sealed": True,
        "answer_sets_frozen": False,
        "run_frozen": False,
    }
    (run_root / "run.json").write_bytes(stable_json(metadata))
    for folder in (*PROTECTED_RUN_ROOTS, "results", "worktrees"):
        (run_root / folder).mkdir()
    return run_root


def _immutable_run_metadata(metadata: dict) -> dict:
    if metadata.get("schema_version") != RUN_SCHEMA_V2:
        raise EvaluationError(f"run schema_version must be {RUN_SCHEMA_V2}")
    projection = {field: metadata.get(field) for field in IMMUTABLE_RUN_FIELDS}
    if not isinstance(projection["run_id"], str) or not projection["run_id"]:
        raise EvaluationError("run metadata run_id must be a non-empty string")
    if not isinstance(projection["fixture"], str) or not projection["fixture"]:
        raise EvaluationError("run metadata fixture must be a non-empty string")
    if not isinstance(projection["fixture_head"], str) or not projection["fixture_head"]:
        raise EvaluationError("run metadata fixture_head must be a non-empty string")
    if projection["incremental_head"] is not None and not isinstance(projection["incremental_head"], str):
        raise EvaluationError("run metadata incremental_head must be a string or null")
    if not isinstance(projection["rubric_sha256"], str) or len(projection["rubric_sha256"]) != 64:
        raise EvaluationError("run metadata rubric_sha256 must be a SHA-256 digest")
    if not isinstance(projection["sealed"], bool):
        raise EvaluationError("run metadata sealed must be boolean")
    return projection


def _protected_files(run_root: Path) -> dict[str, str]:
    files = {"rubric.json": digest_file(run_root / "rubric.json")}
    for root in PROTECTED_RUN_ROOTS:
        files.update({
            path.relative_to(run_root).as_posix(): digest_file(path)
            for path in sorted((run_root / root).rglob("*"))
            if path.is_file()
        })
    return files


def _validate_paired_questions(path: Path) -> None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EvaluationError(f"cannot read paired question bank: {exc}") from exc
    if not lines:
        raise EvaluationError("paired question bank is empty")
    ids: set[str] = set()
    for number, line in enumerate(lines, start=1):
        try:
            question = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EvaluationError(f"paired question line {number} is malformed JSON") from exc
        if not isinstance(question, dict):
            raise EvaluationError(f"paired question line {number} must be an object")
        question_id = question.get("id")
        if not isinstance(question_id, str) or not question_id.strip():
            raise EvaluationError(f"paired question line {number} needs a non-empty id")
        if question_id in ids:
            raise EvaluationError(f"paired question line {number} duplicates id {question_id!r}")
        ids.add(question_id)
        if question.get("category") not in CATEGORY_TO_WEIGHT:
            raise EvaluationError(f"paired question line {number} has an unsupported category")
        if question.get("condition") not in {"cold", "warm", "fresh-session", "transversal", "incremental"}:
            raise EvaluationError(f"paired question line {number} has an unsupported condition")
        if question.get("revision") not in {"cold", "incremental"}:
            raise EvaluationError(f"paired question line {number} has an unsupported revision")
        if not isinstance(question.get("prompt"), str) or not question["prompt"].strip():
            raise EvaluationError(f"paired question line {number} needs a non-empty prompt")


def _validate_v2_freeze_inputs(run_root: Path, metadata: dict) -> dict:
    projection = _immutable_run_metadata(metadata)
    for root in PROTECTED_RUN_ROOTS:
        root_path = run_root / root
        if not root_path.is_dir() or not any(path.is_file() for path in root_path.rglob("*")):
            raise EvaluationError(f"protected root must be non-empty: {root}")
    paired_questions = run_root / "questions" / "paired.jsonl"
    if not paired_questions.is_file():
        raise EvaluationError("paired question bank is missing: questions/paired.jsonl")
    _validate_paired_questions(paired_questions)
    for name in REQUIRED_V2_MANIFESTS:
        if not (run_root / "manifests" / name).is_file():
            raise EvaluationError(f"required manifest input is missing: manifests/{name}")
    if projection["rubric_sha256"] != digest_file(run_root / "rubric.json"):
        raise EvaluationError("run metadata rubric_sha256 does not match rubric.json")
    return projection


def _validate_freeze_manifest(manifest: dict) -> tuple[dict[str, str], dict]:
    if manifest.get("schema_version") != RUN_FREEZE_SCHEMA_V2:
        raise EvaluationError("unsupported run freeze manifest schema")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise EvaluationError("run freeze manifest has no files")
    if not all(isinstance(path, str) and isinstance(digest, str) and len(digest) == 64 for path, digest in files.items()):
        raise EvaluationError("run freeze manifest files must map paths to SHA-256 digests")
    metadata = manifest.get("metadata")
    if not isinstance(metadata, dict):
        raise EvaluationError("run freeze manifest has invalid immutable metadata")
    _immutable_run_metadata(metadata)
    if set(metadata) != set(IMMUTABLE_RUN_FIELDS):
        raise EvaluationError("run freeze manifest immutable metadata fields are invalid")
    return files, metadata


def freeze_run(run_root: str | Path) -> Path:
    run_root = Path(run_root).resolve()
    run_path = run_root / "run.json"
    metadata = load_json(run_path)
    if metadata.get("schema_version") != RUN_SCHEMA_V2:
        raise EvaluationError("master run freeze is only supported for v2 runs")
    if metadata.get("run_frozen") is True:
        raise EvaluationError("evaluation run is already frozen")
    manifest_path = run_root / "freeze-manifest.json"
    if manifest_path.exists():
        raise EvaluationError(f"run freeze manifest already exists: {manifest_path}")
    projection = _validate_v2_freeze_inputs(run_root, metadata)
    manifest = {
        "schema_version": RUN_FREEZE_SCHEMA_V2,
        "metadata": projection,
        "files": _protected_files(run_root),
    }
    manifest_path.write_bytes(stable_json(manifest))
    metadata["run_frozen"] = True
    metadata["freeze_manifest_sha256"] = digest_file(manifest_path)
    metadata["answer_sets_frozen"] = True
    run_path.write_bytes(stable_json(metadata))
    return manifest_path


def verify_run_freeze(run_root: str | Path) -> list[str]:
    run_root = Path(run_root).resolve()
    metadata = load_json(run_root / "run.json")
    current_projection = _immutable_run_metadata(metadata)
    if metadata.get("run_frozen") is not True:
        raise EvaluationError("evaluation run is not frozen")
    manifest_path = run_root / "freeze-manifest.json"
    manifest = load_json(manifest_path)
    expected_files, expected_projection = _validate_freeze_manifest(manifest)
    changes: list[str] = []
    if metadata.get("freeze_manifest_sha256") != digest_file(manifest_path):
        changes.append("freeze manifest changed")
    for field in IMMUTABLE_RUN_FIELDS:
        if current_projection[field] != expected_projection[field]:
            changes.append(f"immutable run metadata changed: {field}")
    actual_files = _protected_files(run_root)
    changes.extend(
        f"unexpected protected file: {path}"
        for path in sorted(set(actual_files) - set(expected_files))
    )
    changes.extend(
        f"missing protected file: {path}"
        for path in sorted(set(expected_files) - set(actual_files))
    )
    changes.extend(
        f"changed protected file: {path}"
        for path in sorted(set(actual_files) & set(expected_files))
        if actual_files[path] != expected_files[path]
    )
    return changes


def _ratio(value: object, owner: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= float(value) <= 1:
        raise EvaluationError(f"{owner} must be a number from 0 to 1")
    return float(value)


def _bool(value: object, owner: str) -> bool:
    if not isinstance(value, bool):
        raise EvaluationError(f"{owner} must be boolean")
    return value


def validate_result(result: dict, rubric: dict) -> None:
    if result.get("schema_version") != RESULT_SCHEMA:
        raise EvaluationError(f"schema_version must be {RESULT_SCHEMA}")
    if result.get("rubric_sha256") != sha256(stable_json(rubric)).hexdigest():
        raise EvaluationError("result rubric_sha256 does not match the supplied frozen rubric")
    gates = result.get("gates")
    if not isinstance(gates, dict) or set(gates) != set(rubric["gates"]):
        raise EvaluationError("gates must contain exactly the frozen G1-G8 keys")
    for gate, value in gates.items():
        _bool(value, f"gates.{gate}")
    metrics = result.get("metrics")
    if not isinstance(metrics, dict) or not all(name in metrics for name in ("M1", "M2", "M4", "M5", "M6")):
        raise EvaluationError("metrics must contain M1, M2, M4, M5 and M6")
    for field in ("core_recall", "bonus_recall", "locator_accuracy"):
        _ratio(metrics["M1"].get(field), f"M1.{field}")
    if not isinstance(metrics["M1"].get("fabrication_count"), int) or metrics["M1"]["fabrication_count"] < 0:
        raise EvaluationError("M1.fabrication_count must be a non-negative integer")
    for field in ("conflict_recall", "multi_file_recall"):
        _ratio(metrics["M2"].get(field), f"M2.{field}")
    for field in ("tool_defaults_resisted", "external_unknown", "identity_ambiguity", "dead_path_resistance"):
        _bool(metrics["M2"].get(field), f"M2.{field}")
    for field in ("lint", "freshness", "tests", "granularity"):
        _bool(metrics["M4"].get(field), f"M4.{field}")
    questions = metrics["M5"].get("questions")
    if not isinstance(questions, list) or not questions:
        raise EvaluationError("M5.questions must be a non-empty list")
    ids: set[str] = set()
    arm_categories: dict[str, set[str]] = {}
    for item in questions:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or item["id"] in ids:
            raise EvaluationError("every question grade requires a unique id")
        ids.add(item["id"])
        if item.get("category") not in CATEGORY_TO_WEIGHT:
            raise EvaluationError(f"unknown question category: {item.get('category')!r}")
        if item.get("grade") not in rubric["question_values"]:
            raise EvaluationError(f"unknown question grade: {item.get('grade')!r}")
        if item.get("arm") not in {"atlas", "control"}:
            raise EvaluationError("question arm must be atlas or control")
        arm_categories.setdefault(item["arm"], set()).add(item["category"])
    if "IMPACT" not in arm_categories.get("atlas", set()) or "IMPACT" not in arm_categories.get("control", set()):
        raise EvaluationError("impact questions must be present in both Atlas and control arms")
    for field in ("citation_validity", "provenance_disclosure"):
        _ratio(metrics["M5"].get(field), f"M5.{field}")
    for field in ("atlas_hit_rate", "fallback_disclosure", "read_cost_reduction"):
        _ratio(metrics["M6"].get(field), f"M6.{field}")
    delta = metrics["M6"].get("accuracy_delta")
    if not isinstance(delta, (int, float)) or isinstance(delta, bool) or not -1 <= float(delta) <= 1:
        raise EvaluationError("M6.accuracy_delta must be between -1 and 1")
    telemetry = result.get("telemetry")
    if not isinstance(telemetry, dict):
        raise EvaluationError("telemetry must be an object")
    for field in ("bytes_read", "unique_evidence_sources", "tool_calls", "latency_ms"):
        value = telemetry.get(field)
        if value is not None and (not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0):
            raise EvaluationError(f"telemetry.{field} must be non-negative or null; never estimate it")


def _target_score(value: float, target: float) -> float:
    return min(value / target, 1.0) if target else float(value > 0)


def score_result(result: dict, rubric: dict) -> dict:
    validate_result(result, rubric)
    weights = rubric["internal_weights"]
    targets = rubric["targets"]
    metrics = result["metrics"]
    scores: dict[str, float] = {}
    m1 = metrics["M1"]
    scores["M1"] = (
        weights["M1"]["core_recall"] * _target_score(m1["core_recall"], targets["core_recall"])
        + weights["M1"]["bonus_recall"] * _target_score(m1["bonus_recall"], targets["bonus_recall"])
        + weights["M1"]["locator_accuracy"] * _target_score(m1["locator_accuracy"], targets["locator_accuracy"])
        + weights["M1"]["fabrication_free"] * float(m1["fabrication_count"] == 0)
    )
    m2 = metrics["M2"]
    scores["M2"] = (
        weights["M2"]["conflict_recall"] * _target_score(m2["conflict_recall"], targets["conflict_recall"])
        + weights["M2"]["multi_file_recall"] * _target_score(m2["multi_file_recall"], targets["multi_file_recall"])
        + sum(weights["M2"][field] * float(m2[field]) for field in (
            "tool_defaults_resisted", "external_unknown", "identity_ambiguity", "dead_path_resistance"
        ))
    )
    scores["M4"] = sum(weights["M4"][field] * float(metrics["M4"][field]) for field in weights["M4"])
    atlas_questions = [item for item in metrics["M5"]["questions"] if item["arm"] == "atlas"]
    category_scores: dict[str, float] = {}
    for category, weight_name in CATEGORY_TO_WEIGHT.items():
        relevant = [item for item in atlas_questions if item["category"] == category]
        category_scores[weight_name] = (
            sum(rubric["question_values"][item["grade"]] for item in relevant) / len(relevant)
            if relevant else 0.0
        )
    scores["M5"] = (
        sum(weights["M5"][name] * category_scores[name] for name in CATEGORY_TO_WEIGHT.values())
        + weights["M5"]["citation_validity"] * metrics["M5"]["citation_validity"]
        + weights["M5"]["provenance"] * metrics["M5"]["provenance_disclosure"]
    )
    m6 = metrics["M6"]
    scores["M6"] = (
        weights["M6"]["atlas_hit_rate"] * m6["atlas_hit_rate"]
        + weights["M6"]["fallback_disclosure"] * m6["fallback_disclosure"]
        + weights["M6"]["read_cost_reduction"] * _target_score(m6["read_cost_reduction"], targets["read_cost_reduction"])
        + weights["M6"]["accuracy_delta"] * _target_score(max(m6["accuracy_delta"], 0), targets["control_accuracy_delta"])
    )
    total = round(sum(scores.values()), 2)
    gates_pass = all(result["gates"].values())
    fabricated = m1["fabrication_count"] > 0 or any(
        item["grade"] == "FABRICATED" for item in atlas_questions
    )
    refusal = [item for item in atlas_questions if item["category"] == "TRAP-UNKNOWABLE"]
    refusal_pass = bool(refusal) and all(item["grade"] == "REFUSED-CORRECTLY" for item in refusal)
    if not gates_pass or fabricated or not refusal_pass:
        verdict = "Not ready"
    elif total >= rubric["verdicts"]["ship"]:
        verdict = "Ship"
    elif total >= rubric["verdicts"]["ship_with_fixes"]:
        verdict = "Ship with fixes"
    else:
        verdict = "Not ready"
    return {
        "schema_version": "atlas-evaluation-score/1.0",
        "family_scores": {key: round(value, 2) for key, value in scores.items()},
        "total": total,
        "gates_pass": gates_pass,
        "fabrication_gate": not fabricated,
        "honest_refusal_gate": refusal_pass,
        "verdict": verdict,
    }

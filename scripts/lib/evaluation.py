from __future__ import annotations

from hashlib import sha256
from math import isfinite
from pathlib import Path, PurePosixPath, PureWindowsPath
import json


RESULT_SCHEMA = "atlas-evaluation-result/1.0"
RESULT_SCHEMA_V2 = "atlas-evaluation-result/2.0"
RUN_SCHEMA_V1 = "atlas-evaluation-run/1.0"
RUN_SCHEMA_V2 = "atlas-evaluation-run/2.0"
RUN_FREEZE_SCHEMA_V2 = "atlas-evaluation-run-freeze/2.0"
QUESTION_TELEMETRY_SCHEMA = "atlas-evaluation-telemetry/1.0"
PHASE_TELEMETRY_SCHEMA = "atlas-evaluation-phase-telemetry/1.0"
ROUTING_ACCEPTANCE_SCHEMA = "atlas-routing-acceptance/1.0"
ROUTING_SCENARIOS_SCHEMA = "atlas-routing-scenarios/1.0"
ROUTE_CLASSES = {
    "retained-context", "source-only", "atlas-only", "atlas-plus-source", "unresolved",
}
ROUTING_ACCESS_KINDS = {"atlas-query", "atlas-page", "source-read"}
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
OBSERVABLE_FIELDS = (
    "bytes_read", "unique_evidence_sources", "tool_calls", "latency_ms", "input_tokens", "output_tokens",
)
BREAK_EVEN_FIELDS = (
    "bytes_read", "tool_calls", "latency_ms", "input_tokens", "output_tokens",
)
_WINDOWS_RESERVED_DEVICE_STEMS = {
    "CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
    "COM¹", "COM²", "COM³", "LPT¹", "LPT²", "LPT³",
}
_MISSING = object()


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
    schema_version = metadata.get("schema_version")
    if schema_version == RUN_SCHEMA_V2:
        raise EvaluationError("v2 runs must use the master run freeze")
    if schema_version != RUN_SCHEMA_V1:
        raise EvaluationError(f"unsupported evaluation run schema: {schema_version!r}")
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
    schema_version = metadata.get("schema_version")
    if schema_version == RUN_SCHEMA_V2:
        raise EvaluationError("v2 runs must use master run freeze verification")
    if schema_version != RUN_SCHEMA_V1:
        raise EvaluationError(f"unsupported evaluation run schema: {schema_version!r}")
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


def _safe_run_id(value: object, owner: str = "run_id") -> str:
    if not isinstance(value, str) or not value.strip() or "/" in value or "\\" in value:
        raise EvaluationError(f"{owner} must be one safe non-empty path component")
    if (
        value.endswith((" ", "."))
        or any(
            ord(character) < 32 or ord(character) == 127 or character in '"*?:<>|'
            for character in value
        )
        or value.partition(".")[0].rstrip(" ").upper() in _WINDOWS_RESERVED_DEVICE_STEMS
    ):
        raise EvaluationError(f"{owner} must be one safe non-empty path component")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or len(posix.parts) != 1
        or len(windows.parts) != 1
        or value in {".", ".."}
    ):
        raise EvaluationError(f"{owner} must be one safe non-empty path component")
    return value


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
    run_id = _safe_run_id(run_id)
    try:
        destination.relative_to(atlas_root)
        inside_atlas = True
    except ValueError:
        inside_atlas = False
    if inside_atlas:
        raise EvaluationError("sealed evaluation destination must be outside the Atlas checkout")
    run_root = (destination / run_id).resolve()
    if run_root.parent != destination:
        raise EvaluationError("run_id must resolve to one child of the approved destination")
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


def _is_sha256_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(character in "0123456789abcdefABCDEF" for character in value)


def _immutable_run_metadata(metadata: dict, *, allow_missing_incremental_head: bool = False) -> dict:
    if metadata.get("schema_version") != RUN_SCHEMA_V2:
        raise EvaluationError(f"run schema_version must be {RUN_SCHEMA_V2}")
    projection = {field: metadata.get(field, _MISSING) for field in IMMUTABLE_RUN_FIELDS}
    for field, value in projection.items():
        if value is _MISSING and not (field == "incremental_head" and allow_missing_incremental_head):
            raise EvaluationError(f"run metadata {field} is required")
    _safe_run_id(projection["run_id"], "run metadata run_id")
    if not isinstance(projection["fixture"], str) or not projection["fixture"]:
        raise EvaluationError("run metadata fixture must be a non-empty string")
    if not isinstance(projection["fixture_head"], str) or not projection["fixture_head"]:
        raise EvaluationError("run metadata fixture_head must be a non-empty string")
    if projection["incremental_head"] is not _MISSING and projection["incremental_head"] is not None and not isinstance(projection["incremental_head"], str):
        raise EvaluationError("run metadata incremental_head must be a string or null")
    if not _is_sha256_digest(projection["rubric_sha256"]):
        raise EvaluationError("run metadata rubric_sha256 must be a SHA-256 digest")
    if not isinstance(projection["sealed"], bool):
        raise EvaluationError("run metadata sealed must be boolean")
    return projection


def _resolved_run_path(run_root: Path, path: Path, owner: str) -> Path:
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(run_root.resolve(strict=True))
    except ValueError as exc:
        raise EvaluationError(f"{owner} resolves outside the evaluation run") from exc
    except OSError as exc:
        raise EvaluationError(f"cannot resolve {owner}: {exc}") from exc
    return resolved


def _protected_files(run_root: Path) -> dict[str, str]:
    rubric_path = _resolved_run_path(run_root, run_root / "rubric.json", "rubric.json")
    files = {"rubric.json": digest_file(rubric_path)}
    for root in PROTECTED_RUN_ROOTS:
        protected_root = run_root / root
        _resolved_run_path(run_root, protected_root, root)
        for path in sorted(protected_root.rglob("*")):
            relative = path.relative_to(run_root).as_posix()
            resolved = _resolved_run_path(run_root, path, relative)
            if path.is_file():
                files[relative] = digest_file(resolved)
    return files


def _load_paired_questions(path: Path) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise EvaluationError(f"cannot read paired question bank: {exc}") from exc
    if not lines:
        raise EvaluationError("paired question bank is empty")
    ids: set[str] = set()
    questions: list[dict] = []
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
        questions.append(question)
    return questions


def _validate_paired_questions(path: Path) -> None:
    _load_paired_questions(path)


def _validate_v2_freeze_inputs(run_root: Path, metadata: dict) -> dict:
    projection = _immutable_run_metadata(metadata)
    for root in PROTECTED_RUN_ROOTS:
        root_path = run_root / root
        if not root_path.is_dir() or not any(path.is_file() for path in root_path.rglob("*")):
            raise EvaluationError(f"protected root must be non-empty: {root}")
    paired_questions = run_root / "questions" / "paired.jsonl"
    if not paired_questions.is_file():
        raise EvaluationError("paired question bank is missing: questions/paired.jsonl")
    paired = _load_paired_questions(
        _resolved_run_path(run_root, paired_questions, "questions/paired.jsonl")
    )
    answer_files = [path for path in (run_root / "answers").rglob("*") if path.is_file()]
    expected_answers = 2 * len(paired)
    if len(answer_files) != expected_answers:
        raise EvaluationError(
            f"answers must contain exactly {expected_answers} answer files "
            f"for {len(paired)} paired questions"
        )
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
    if not all(isinstance(path, str) and _is_sha256_digest(digest) for path, digest in files.items()):
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
    run_path = _resolved_run_path(run_root, run_root / "run.json", "run.json")
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
    run_path = _resolved_run_path(run_root, run_root / "run.json", "run.json")
    metadata = load_json(run_path)
    current_projection = _immutable_run_metadata(metadata, allow_missing_incremental_head=True)
    if metadata.get("run_frozen") is not True:
        raise EvaluationError("evaluation run is not frozen")
    manifest_digest = metadata.get("freeze_manifest_sha256")
    if not _is_sha256_digest(manifest_digest):
        raise EvaluationError("run metadata freeze_manifest_sha256 must be a SHA-256 digest")
    manifest_path = _resolved_run_path(
        run_root, run_root / "freeze-manifest.json", "freeze-manifest.json"
    )
    manifest = load_json(manifest_path)
    expected_files, expected_projection = _validate_freeze_manifest(manifest)
    changes: list[str] = []
    if manifest_digest != digest_file(manifest_path):
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


def verify_trusted_run_freeze(
    run_root: str | Path,
    expected_freeze_manifest_sha256: str | None,
) -> dict:
    if not _is_sha256_digest(expected_freeze_manifest_sha256):
        raise EvaluationError(
            "v2 verification requires expected_freeze_manifest_sha256 "
            "(caller-trusted freeze digest) as a SHA-256 digest"
        )
    root = Path(run_root).resolve()
    run_path = _resolved_run_path(root, root / "run.json", "run.json")
    metadata = load_json(run_path)
    if metadata.get("schema_version") != RUN_SCHEMA_V2:
        raise EvaluationError(f"trusted run freeze verification requires {RUN_SCHEMA_V2}")
    changes = verify_run_freeze(root)
    if changes:
        raise EvaluationError(f"v2 run freeze is not clean: {'; '.join(changes)}")
    manifest_path = _resolved_run_path(
        root, root / "freeze-manifest.json", "freeze-manifest.json"
    )
    if (
        digest_file(manifest_path) != expected_freeze_manifest_sha256
        or metadata.get("freeze_manifest_sha256") != expected_freeze_manifest_sha256
    ):
        raise EvaluationError(
            "actual and run digests must match the caller-trusted freeze manifest digest"
        )
    return metadata


def _ratio(value: object, owner: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise EvaluationError(f"{owner} must be a number from 0 to 1")
    try:
        normalized = float(value)
        valid = isfinite(normalized) and 0 <= normalized <= 1
    except (OverflowError, ValueError):
        valid = False
        normalized = 0.0
    if not valid:
        raise EvaluationError(f"{owner} must be a number from 0 to 1")
    return normalized


def _bool(value: object, owner: str) -> bool:
    if not isinstance(value, bool):
        raise EvaluationError(f"{owner} must be boolean")
    return value


def _validate_v1_result(result: dict, rubric: dict) -> None:
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


def _exact_object(value: object, fields: set[str], owner: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        names = ", ".join(sorted(fields))
        raise EvaluationError(f"{owner} must contain exactly {names}")
    return value


def _observable(value: object, owner: str) -> int | float | None:
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        raise EvaluationError(f"{owner} must be a non-negative number or null; never estimate it")
    try:
        finite = isfinite(float(value))
    except (OverflowError, ValueError):
        finite = False
    if not finite:
        raise EvaluationError(f"{owner} must be a finite non-negative number or null; never estimate it")
    return value


def _full_commit(value: object, owner: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) not in {40, 64}
        or value != value.lower()
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise EvaluationError(f"{owner} must be a full lowercase 40- or 64-character commit")
    return value


def _routing_scenario_contracts(value: dict) -> list[dict]:
    value = _exact_object(value, {"schema_version", "scenarios"}, "routing scenarios")
    if value["schema_version"] != ROUTING_SCENARIOS_SCHEMA:
        raise EvaluationError(f"routing scenarios schema_version must be {ROUTING_SCENARIOS_SCHEMA}")
    scenarios = value["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise EvaluationError("routing scenarios must be a non-empty list")
    fields = {
        "id", "title", "prompt", "condition", "follows", "allowed_routes", "requires_atlas", "requires_source",
        "zero_retrieval", "first_access", "requires_revision", "atlas_before_source",
    }
    ids: set[str] = set()
    for index, scenario in enumerate(scenarios):
        owner = f"routing scenarios[{index}]"
        scenario = _exact_object(scenario, fields, owner)
        scenario_id = scenario["id"]
        if not isinstance(scenario_id, str) or not scenario_id.strip() or scenario_id in ids:
            raise EvaluationError(f"{owner}.id must be unique and non-empty")
        ids.add(scenario_id)
        if not isinstance(scenario["title"], str) or not scenario["title"].strip():
            raise EvaluationError(f"{owner}.title must be non-empty")
        if not isinstance(scenario["prompt"], str) or not scenario["prompt"].strip():
            raise EvaluationError(f"{owner}.prompt must be non-empty")
        if scenario["condition"] not in {"fresh", "warm"}:
            raise EvaluationError(f"{owner}.condition must be fresh or warm")
        follows = scenario["follows"]
        if scenario["condition"] == "fresh" and follows is not None:
            raise EvaluationError(f"{owner}.follows must be null for a fresh scenario")
        if scenario["condition"] == "warm" and (
            not isinstance(follows, str) or not follows.strip() or follows == scenario_id
        ):
            raise EvaluationError(f"{owner}.follows must name another scenario for a warm scenario")
        routes = scenario["allowed_routes"]
        if (
            not isinstance(routes, list)
            or not routes
            or len(routes) != len(set(routes))
            or any(route not in ROUTE_CLASSES for route in routes)
        ):
            raise EvaluationError(f"{owner}.allowed_routes must be unique supported route classes")
        first = scenario["first_access"]
        if (
            not isinstance(first, list)
            or len(first) != len(set(first))
            or any(kind not in ROUTING_ACCESS_KINDS for kind in first)
        ):
            raise EvaluationError(f"{owner}.first_access must contain unique supported access kinds")
        for field in (
            "requires_atlas", "requires_source", "zero_retrieval",
            "requires_revision", "atlas_before_source",
        ):
            _bool(scenario[field], f"{owner}.{field}")
    unknown_predecessors = sorted(
        scenario["follows"]
        for scenario in scenarios
        if scenario["condition"] == "warm" and scenario["follows"] not in ids
    )
    if unknown_predecessors:
        raise EvaluationError(
            f"warm routing scenarios reference unknown predecessors: {', '.join(unknown_predecessors)}"
        )
    return scenarios


def validate_routing_acceptance(result: dict, scenario_contract: dict) -> None:
    """Validate observed retrieval order separately from sealed answer-quality scoring."""
    result = _exact_object(
        result, {"schema_version", "atlas_commit", "model", "scenarios"},
        "routing acceptance result",
    )
    if result["schema_version"] != ROUTING_ACCEPTANCE_SCHEMA:
        raise EvaluationError(f"routing result schema_version must be {ROUTING_ACCEPTANCE_SCHEMA}")
    _full_commit(result["atlas_commit"], "routing result atlas_commit")
    if not isinstance(result["model"], str) or not result["model"].strip():
        raise EvaluationError("routing result model must be non-empty")
    contracts = _routing_scenario_contracts(scenario_contract)
    expected = {scenario["id"]: scenario for scenario in contracts}
    items = result["scenarios"]
    if not isinstance(items, list) or not items:
        raise EvaluationError("routing result scenarios must be a non-empty list")
    result_fields = {
        "id", "prompt", "session_id", "route", "requested_revision", "resolved_revision",
        "accesses", "citations", "telemetry",
    }
    actual: dict[str, dict] = {}
    for index, item in enumerate(items):
        item = _exact_object(item, result_fields, f"routing result scenarios[{index}]")
        scenario_id = item["id"]
        if not isinstance(scenario_id, str) or not scenario_id.strip() or scenario_id in actual:
            raise EvaluationError("routing result scenario ids must be unique and non-empty")
        actual[scenario_id] = item
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    if missing:
        raise EvaluationError(f"missing routing scenarios: {', '.join(missing)}")
    if extra:
        raise EvaluationError(f"extra routing scenarios: {', '.join(extra)}")

    fresh_sessions: dict[str, str] = {}
    for scenario in contracts:
        item = actual[scenario["id"]]
        if item["prompt"] != scenario["prompt"]:
            raise EvaluationError(
                f"routing result {scenario['id']}.prompt must equal the frozen prompt"
            )
        session_id = item["session_id"]
        if not isinstance(session_id, str) or not session_id.strip():
            raise EvaluationError(f"routing result {scenario['id']}.session_id must be non-empty")
        if scenario["condition"] == "fresh":
            if session_id in fresh_sessions:
                raise EvaluationError(
                    f"routing result {scenario['id']} must use a fresh session; "
                    f"it reuses {fresh_sessions[session_id]}"
                )
            fresh_sessions[session_id] = scenario["id"]
    for scenario in contracts:
        if scenario["condition"] == "warm":
            item = actual[scenario["id"]]
            predecessor = actual[scenario["follows"]]
            if item["session_id"] != predecessor["session_id"]:
                raise EvaluationError(
                    f"routing result {scenario['id']} must use the same session as {scenario['follows']}"
                )

    access_fields = {"kind", "target", "revision"}
    for scenario in contracts:
        scenario_id = scenario["id"]
        item = actual[scenario_id]
        owner = f"routing result {scenario_id}"
        if item["route"] not in scenario["allowed_routes"]:
            allowed = ", ".join(scenario["allowed_routes"])
            raise EvaluationError(f"{owner}.route must be one of: {allowed}")
        requested = item["requested_revision"]
        if requested is not None and (not isinstance(requested, str) or not requested.strip()):
            raise EvaluationError(f"{owner}.requested_revision must be non-empty or null")
        resolved = item["resolved_revision"]
        if resolved is not None:
            resolved = _full_commit(resolved, f"{owner}.resolved_revision")
        if scenario["requires_revision"] and (requested is None or resolved is None):
            raise EvaluationError(f"{owner} requires requested_revision and resolved_revision")

        accesses = item["accesses"]
        if not isinstance(accesses, list):
            raise EvaluationError(f"{owner}.accesses must be a list")
        kinds: list[str] = []
        for access_index, access in enumerate(accesses):
            access_owner = f"{owner}.accesses[{access_index}]"
            access = _exact_object(access, access_fields, access_owner)
            kind = access["kind"]
            if kind not in ROUTING_ACCESS_KINDS:
                raise EvaluationError(f"{access_owner}.kind is unsupported")
            if not isinstance(access["target"], str) or not access["target"].strip():
                raise EvaluationError(f"{access_owner}.target must be non-empty")
            if kind == "source-read":
                source_revision = _full_commit(access["revision"], f"{access_owner}.revision")
                if resolved is None or source_revision != resolved:
                    raise EvaluationError(f"{access_owner}.revision must match resolved_revision")
            elif access["revision"] is not None:
                raise EvaluationError(f"{access_owner}.revision must be null for Atlas access")
            kinds.append(kind)

        atlas_positions = [index for index, kind in enumerate(kinds) if kind.startswith("atlas-")]
        source_positions = [index for index, kind in enumerate(kinds) if kind == "source-read"]
        route = item["route"]
        if route == "retained-context" and accesses:
            raise EvaluationError(f"{owner} retained-context must perform zero retrieval")
        if route == "source-only" and (atlas_positions or not source_positions):
            raise EvaluationError(f"{owner} source-only must use source without Atlas access")
        if route == "atlas-only" and (not atlas_positions or source_positions):
            raise EvaluationError(f"{owner} atlas-only must use Atlas without source access")
        if route == "atlas-plus-source" and (not atlas_positions or not source_positions):
            raise EvaluationError(f"{owner} atlas-plus-source must use both Atlas and source")
        if scenario["zero_retrieval"] and accesses:
            raise EvaluationError(f"{owner} requires zero retrieval")
        if scenario["requires_atlas"] and not atlas_positions:
            raise EvaluationError(f"{owner} requires an Atlas access")
        if scenario["requires_source"] and not source_positions:
            raise EvaluationError(f"{owner} requires a source read")
        if accesses and scenario["first_access"] and kinds[0] not in scenario["first_access"]:
            raise EvaluationError(f"{owner} has an invalid first access")
        if scenario["atlas_before_source"] and (
            not atlas_positions or not source_positions or min(atlas_positions) > min(source_positions)
        ):
            raise EvaluationError(f"{owner} must access Atlas before source")

        citations = item["citations"]
        if not isinstance(citations, list) or not citations:
            raise EvaluationError(f"{owner}.citations must be a non-empty list")
        citation_fields = {"kind", "target", "revision"}
        seen_citations: set[tuple[str, str, str | None]] = set()
        for citation_index, citation in enumerate(citations):
            citation_owner = f"{owner}.citations[{citation_index}]"
            citation = _exact_object(citation, citation_fields, citation_owner)
            citation_kind = citation["kind"]
            if citation_kind not in {"atlas", "source"}:
                raise EvaluationError(f"{citation_owner}.kind must be atlas or source")
            citation_target = citation["target"]
            if not isinstance(citation_target, str) or not citation_target.strip():
                raise EvaluationError(f"{citation_owner}.target must be non-empty")
            citation_revision = citation["revision"]
            if citation_kind == "source":
                citation_revision = _full_commit(
                    citation_revision, f"{citation_owner}.revision"
                )
                if resolved is None or citation_revision != resolved:
                    raise EvaluationError(
                        f"{citation_owner}.revision must match resolved_revision"
                    )
            elif citation_revision is not None:
                raise EvaluationError(
                    f"{citation_owner}.revision must be null for an Atlas citation"
                )
            citation_key = (citation_kind, citation_target, citation_revision)
            if citation_key in seen_citations:
                raise EvaluationError(f"{owner}.citations must be unique")
            seen_citations.add(citation_key)
        telemetry = _exact_object(item["telemetry"], set(OBSERVABLE_FIELDS), f"{owner}.telemetry")
        for field in OBSERVABLE_FIELDS:
            _observable(telemetry[field], f"{owner}.telemetry.{field}")


def _safe_run_path(value: object, owner: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise EvaluationError(f"{owner} must be a safe run-relative path")
    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or posix.as_posix() != value
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise EvaluationError(f"{owner} must be a safe run-relative path")
    return value


def _validate_v2_core_metrics(metrics: object) -> dict:
    if not isinstance(metrics, dict) or set(metrics) != {"M1", "M2", "M4"}:
        raise EvaluationError("v2 metrics must contain exactly M1, M2 and M4")
    m1 = _exact_object(
        metrics["M1"], {"core_recall", "bonus_recall", "locator_accuracy", "fabrication_count"}, "M1"
    )
    for field in ("core_recall", "bonus_recall", "locator_accuracy"):
        _ratio(m1[field], f"M1.{field}")
    if (
        not isinstance(m1["fabrication_count"], int)
        or isinstance(m1["fabrication_count"], bool)
        or m1["fabrication_count"] < 0
    ):
        raise EvaluationError("M1.fabrication_count must be a non-negative integer")
    m2 = _exact_object(
        metrics["M2"],
        {
            "conflict_recall", "multi_file_recall", "tool_defaults_resisted", "external_unknown",
            "identity_ambiguity", "dead_path_resistance",
        },
        "M2",
    )
    for field in ("conflict_recall", "multi_file_recall"):
        _ratio(m2[field], f"M2.{field}")
    for field in ("tool_defaults_resisted", "external_unknown", "identity_ambiguity", "dead_path_resistance"):
        _bool(m2[field], f"M2.{field}")
    m4 = _exact_object(metrics["M4"], {"lint", "freshness", "tests", "granularity"}, "M4")
    for field in ("lint", "freshness", "tests", "granularity"):
        _bool(m4[field], f"M4.{field}")
    return metrics


def _validate_question_telemetry(value: dict, question_id: str, arm: str, owner: str) -> dict:
    fields = {
        "schema_version", "question_id", "arm", *OBSERVABLE_FIELDS,
        "atlas_hit", "fallback_used", "fallback_disclosed", "source_accessed", "atlas_accessed",
    }
    value = _exact_object(value, fields, owner)
    if value["schema_version"] != QUESTION_TELEMETRY_SCHEMA:
        raise EvaluationError(f"{owner} telemetry schema_version must be {QUESTION_TELEMETRY_SCHEMA}")
    if value["question_id"] != question_id:
        raise EvaluationError(f"{owner} telemetry question_id does not match its result reference")
    if value["arm"] != arm:
        raise EvaluationError(f"{owner} telemetry arm does not match its result reference")
    for field in OBSERVABLE_FIELDS:
        _observable(value[field], f"{owner}.{field}")
    if arm == "atlas":
        for field in ("atlas_hit", "fallback_used", "source_accessed", "atlas_accessed"):
            _bool(value[field], f"{owner}.{field}")
        disclosure = value["fallback_disclosed"]
        if value["fallback_used"]:
            _bool(disclosure, f"{owner}.fallback_disclosed")
        elif disclosure is not None and not isinstance(disclosure, bool):
            raise EvaluationError(f"{owner}.fallback_disclosed must be boolean or null")
    else:
        for field in ("source_accessed", "atlas_accessed"):
            _bool(value[field], f"{owner}.{field}")
        for field in ("atlas_hit", "fallback_used", "fallback_disclosed"):
            if value[field] is not None:
                raise EvaluationError(f"{owner}.{field} must be null for the control arm")
    return value


def _validate_authoring_telemetry(value: dict, owner: str) -> dict:
    value = _exact_object(value, {"schema_version", "phase", *OBSERVABLE_FIELDS}, owner)
    if value["schema_version"] != PHASE_TELEMETRY_SCHEMA:
        raise EvaluationError(f"{owner} schema_version must be {PHASE_TELEMETRY_SCHEMA}")
    if value["phase"] != "authoring":
        raise EvaluationError(f"{owner} phase must be authoring")
    for field in OBSERVABLE_FIELDS:
        _observable(value[field], f"{owner}.{field}")
    return value


def _v2_run_context(
    result: dict,
    rubric: dict,
    run_root: str | Path | None,
    expected_freeze_manifest_sha256: str | None,
) -> tuple[Path, set[str], list[dict]]:
    if run_root is None:
        raise EvaluationError("v2 results require run_root")
    root = Path(run_root).resolve()
    metadata = verify_trusted_run_freeze(root, expected_freeze_manifest_sha256)
    rubric_digest = sha256(stable_json(rubric)).hexdigest()
    if metadata.get("rubric_sha256") != rubric_digest or result.get("rubric_sha256") != rubric_digest:
        raise EvaluationError("result, run and supplied rubric digests must match")
    manifest_path = _resolved_run_path(root, root / "freeze-manifest.json", "freeze-manifest.json")
    if result.get("freeze_manifest_sha256") != expected_freeze_manifest_sha256:
        raise EvaluationError("actual, run and result digests must match the caller-trusted freeze manifest digest")
    manifest = load_json(manifest_path)
    frozen_files, _ = _validate_freeze_manifest(manifest)
    paired_path = _resolved_run_path(root, root / "questions" / "paired.jsonl", "questions/paired.jsonl")
    return root, set(frozen_files), _load_paired_questions(paired_path)


def _validate_v2_result(
    result: dict,
    rubric: dict,
    run_root: str | Path | None,
    expected_freeze_manifest_sha256: str | None,
) -> dict:
    result_fields = {
        "schema_version", "rubric_sha256", "freeze_manifest_sha256", "gates", "metrics", "questions",
    }
    if "authoring_telemetry" in result:
        result_fields.add("authoring_telemetry")
    _exact_object(result, result_fields, "v2 result")
    root, frozen_files, paired = _v2_run_context(
        result, rubric, run_root, expected_freeze_manifest_sha256
    )
    gates = _exact_object(result["gates"], set(rubric["gates"]), "gates")
    for gate, value in gates.items():
        if not isinstance(value, dict) or set(value) != {"passed", "evidence"}:
            raise EvaluationError(f"gates.{gate} must contain exactly passed and evidence")
        _bool(value["passed"], f"gates.{gate}.passed")
        evidence = value["evidence"]
        if not isinstance(evidence, list) or not evidence:
            raise EvaluationError(f"gates.{gate} must have a non-empty evidence list")
        evidence_paths: set[str] = set()
        for index, path_value in enumerate(evidence):
            path = _safe_run_path(path_value, f"gates.{gate}.evidence[{index}]")
            if path in evidence_paths:
                raise EvaluationError(f"gates.{gate} has duplicate evidence paths")
            evidence_paths.add(path)
            if path != "freeze-manifest.json" and path not in frozen_files:
                raise EvaluationError(f"gates.{gate}.evidence[{index}] must name a frozen file")
            _resolved_run_path(root, root / path, f"gates.{gate}.evidence[{index}]")
    metrics = _validate_v2_core_metrics(result["metrics"])
    question_results = result["questions"]
    if not isinstance(question_results, list) or not question_results:
        raise EvaluationError("questions must be a non-empty list")
    by_id: dict[str, dict] = {}
    telemetry: dict[tuple[str, str], dict] = {}
    manifest_by_id = {question["id"]: question for question in paired}
    for item in question_results:
        item = _exact_object(item, {"id", "category", "atlas", "control"}, "question result")
        question_id = item["id"]
        if not isinstance(question_id, str) or not question_id:
            raise EvaluationError("every question result requires a non-empty id")
        if question_id in by_id:
            raise EvaluationError(f"question results duplicates id {question_id!r}")
        by_id[question_id] = item
    missing = sorted(set(manifest_by_id) - set(by_id))
    extra = sorted(set(by_id) - set(manifest_by_id))
    if missing:
        raise EvaluationError(f"missing question results: {', '.join(missing)}")
    if extra:
        raise EvaluationError(f"extra question results: {', '.join(extra)}")
    arm_fields = {
        "grade", "citation_validity", "provenance_disclosure", "citations", "rationale", "answer", "telemetry",
    }
    answer_paths: set[str] = set()
    for question in paired:
        question_id = question["id"]
        item = by_id[question_id]
        if item["category"] != question["category"]:
            raise EvaluationError(f"question {question_id} category does not match the paired manifest")
        for arm in ("atlas", "control"):
            arm_result = _exact_object(item[arm], arm_fields, f"questions.{question_id}.{arm}")
            if arm_result["grade"] not in rubric["question_values"]:
                raise EvaluationError(f"unknown question grade: {arm_result['grade']!r}")
            for field in ("citation_validity", "provenance_disclosure"):
                _ratio(arm_result[field], f"questions.{question_id}.{arm}.{field}")
            citations = arm_result["citations"]
            if (
                not isinstance(citations, list)
                or not citations
                or any(not isinstance(citation, str) or not citation.strip() for citation in citations)
            ):
                raise EvaluationError(f"questions.{question_id}.{arm}.citations must be non-empty strings")
            if not isinstance(arm_result["rationale"], str) or not arm_result["rationale"].strip():
                raise EvaluationError(f"questions.{question_id}.{arm}.rationale must be non-empty")
            answer_path = _safe_run_path(
                arm_result["answer"], f"questions.{question_id}.{arm}.answer"
            )
            if not answer_path.startswith(f"answers/{arm}/"):
                raise EvaluationError(f"questions.{question_id}.{arm}.answer must be arm-specific")
            if answer_path not in frozen_files:
                raise EvaluationError(f"questions.{question_id}.{arm}.answer must name a frozen file")
            if answer_path in answer_paths:
                raise EvaluationError(f"questions.{question_id}.{arm}.answer is a duplicate answer reference")
            _resolved_run_path(root, root / answer_path, f"questions.{question_id}.{arm}.answer")
            answer_paths.add(answer_path)
            telemetry_path = _safe_run_path(
                arm_result["telemetry"], f"questions.{question_id}.{arm}.telemetry"
            )
            if not telemetry_path.startswith(f"telemetry/{arm}/"):
                raise EvaluationError(f"questions.{question_id}.{arm}.telemetry must be arm-specific")
            if telemetry_path not in frozen_files:
                raise EvaluationError(f"questions.{question_id}.{arm}.telemetry must name a frozen file")
            resolved_telemetry = _resolved_run_path(
                root, root / telemetry_path, f"questions.{question_id}.{arm}.telemetry"
            )
            telemetry[(question_id, arm)] = _validate_question_telemetry(
                load_json(resolved_telemetry), question_id, arm, f"questions.{question_id}.{arm}"
            )
    frozen_answer_paths = {path for path in frozen_files if path.startswith("answers/")}
    if answer_paths != frozen_answer_paths:
        unreferenced = sorted(frozen_answer_paths - answer_paths)
        if unreferenced:
            raise EvaluationError(f"unreferenced frozen answer files: {', '.join(unreferenced)}")
        raise EvaluationError("answer references must equal the frozen answer file set")
    authoring = None
    if "authoring_telemetry" in result:
        authoring_path = _safe_run_path(result["authoring_telemetry"], "authoring_telemetry")
        if not authoring_path.startswith("telemetry/"):
            raise EvaluationError("authoring_telemetry must be beneath telemetry/")
        if authoring_path not in frozen_files:
            raise EvaluationError("authoring_telemetry must name a frozen file")
        resolved_authoring = _resolved_run_path(root, root / authoring_path, "authoring_telemetry")
        authoring = _validate_authoring_telemetry(load_json(resolved_authoring), "authoring telemetry")
    return {
        "paired": paired,
        "by_id": by_id,
        "telemetry": telemetry,
        "authoring": authoring,
        "metrics": metrics,
    }


def validate_result(
    result: dict,
    rubric: dict,
    run_root: str | Path | None = None,
    *,
    expected_freeze_manifest_sha256: str | None = None,
) -> None:
    if result.get("schema_version") == RESULT_SCHEMA:
        _validate_v1_result(result, rubric)
        return
    if result.get("schema_version") == RESULT_SCHEMA_V2:
        _validate_v2_result(result, rubric, run_root, expected_freeze_manifest_sha256)
        return
    raise EvaluationError(f"schema_version must be {RESULT_SCHEMA} or {RESULT_SCHEMA_V2}")


def _target_score(value: float, target: float) -> float:
    return min(value / target, 1.0) if target else float(value > 0)


def _score_validated_result(
    result: dict,
    rubric: dict,
    *,
    gates_pass: bool,
    arm_purity_pass: bool = True,
    comparison: dict | None = None,
) -> dict:
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
    fabricated = m1["fabrication_count"] > 0 or any(
        item["grade"] == "FABRICATED" for item in atlas_questions
    )
    refusal = [item for item in atlas_questions if item["category"] == "TRAP-UNKNOWABLE"]
    refusal_pass = bool(refusal) and all(item["grade"] == "REFUSED-CORRECTLY" for item in refusal)
    if not gates_pass or fabricated or not refusal_pass or not arm_purity_pass:
        verdict = "Not ready"
    elif total >= rubric["verdicts"]["ship"]:
        verdict = "Ship"
    elif total >= rubric["verdicts"]["ship_with_fixes"]:
        verdict = "Ship with fixes"
    else:
        verdict = "Not ready"
    score = {
        "schema_version": "atlas-evaluation-score/1.0",
        "family_scores": {key: round(value, 2) for key, value in scores.items()},
        "total": total,
        "gates_pass": gates_pass,
        "fabrication_gate": not fabricated,
        "honest_refusal_gate": refusal_pass,
        "verdict": verdict,
    }
    if comparison is not None:
        score["comparison"] = comparison
    return score


def _mean(values: list[float | bool]) -> float:
    return sum(float(value) for value in values) / len(values)


def _finite_total(values: list[int | float], owner: str) -> int | float:
    try:
        total = sum(values)
        finite = isfinite(float(total))
    except (OverflowError, ValueError):
        finite = False
        total = 0
    if not finite:
        raise EvaluationError(f"{owner} must be finite")
    return total


def _finite_derived(value: float, owner: str) -> float:
    try:
        finite = isfinite(float(value))
    except (OverflowError, ValueError):
        finite = False
    if not finite:
        raise EvaluationError(f"{owner} must be finite")
    return value


def _read_reduction(records: list[tuple[dict, dict]], field: str = "bytes_read") -> float | None:
    atlas_values = [atlas[field] for atlas, _ in records]
    control_values = [control[field] for _, control in records]
    if any(value is None for value in (*atlas_values, *control_values)):
        return None
    atlas_total = _finite_total(atlas_values, f"aggregate {field}")
    control_total = _finite_total(control_values, f"aggregate {field}")
    if control_total == 0:
        return None
    return _finite_derived((control_total - atlas_total) / control_total, f"derived {field} reduction")


def _derive_v2(data: dict, rubric: dict) -> tuple[dict, dict]:
    paired = data["paired"]
    by_id = data["by_id"]
    telemetry = data["telemetry"]
    grade_values = rubric["question_values"]
    atlas_accuracy = _mean([grade_values[by_id[item["id"]]["atlas"]["grade"]] for item in paired])
    control_accuracy = _mean([grade_values[by_id[item["id"]]["control"]["grade"]] for item in paired])
    records = [(telemetry[(item["id"], "atlas")], telemetry[(item["id"], "control")]) for item in paired]
    atlas_records = [atlas for atlas, _ in records]
    used_fallbacks = [record for record in atlas_records if record["fallback_used"]]
    fallback_disclosure = (
        _mean([record["fallback_disclosed"] for record in used_fallbacks]) if used_fallbacks else 1.0
    )
    conditions: dict[str, dict] = {}
    for condition in sorted({item["condition"] for item in paired}):
        condition_questions = [item for item in paired if item["condition"] == condition]
        condition_atlas = _mean([
            grade_values[by_id[item["id"]]["atlas"]["grade"]] for item in condition_questions
        ])
        condition_control = _mean([
            grade_values[by_id[item["id"]]["control"]["grade"]] for item in condition_questions
        ])
        condition_records = [
            (telemetry[(item["id"], "atlas")], telemetry[(item["id"], "control")])
            for item in condition_questions
        ]
        conditions[condition] = {
            "atlas_accuracy": condition_atlas,
            "control_accuracy": condition_control,
            "accuracy_delta": condition_atlas - condition_control,
            "read_cost_reduction": _read_reduction(condition_records),
        }
    violations: list[str] = []
    for item in paired:
        question_id = item["id"]
        if telemetry[(question_id, "atlas")]["source_accessed"]:
            violations.append(f"{question_id}/atlas: source_accessed=true")
        if not telemetry[(question_id, "atlas")]["atlas_accessed"]:
            violations.append(f"{question_id}/atlas: atlas_accessed=false")
        if not telemetry[(question_id, "control")]["source_accessed"]:
            violations.append(f"{question_id}/control: source_accessed=false")
        if telemetry[(question_id, "control")]["atlas_accessed"]:
            violations.append(f"{question_id}/control: atlas_accessed=true")
    break_even: dict[str, float | None] = {}
    for field in BREAK_EVEN_FIELDS:
        authoring_cost = data["authoring"][field] if data["authoring"] is not None else None
        atlas_values = [atlas[field] for atlas, _ in records]
        control_values = [control[field] for _, control in records]
        if authoring_cost is None or any(value is None for value in (*atlas_values, *control_values)):
            break_even[field] = None
            continue
        atlas_total = _finite_total(atlas_values, f"aggregate {field}")
        control_total = _finite_total(control_values, f"aggregate {field}")
        marginal_saving = _finite_derived(
            (control_total - atlas_total) / len(records), f"marginal {field} saving"
        )
        if marginal_saving > 0:
            try:
                break_even_value = authoring_cost / marginal_saving
            except OverflowError as exc:
                raise EvaluationError(f"break_even.{field} must be finite") from exc
            break_even[field] = _finite_derived(break_even_value, f"break_even.{field}")
        else:
            break_even[field] = None
    comparison = {
        "atlas_accuracy": atlas_accuracy,
        "control_accuracy": control_accuracy,
        "accuracy_delta": atlas_accuracy - control_accuracy,
        "atlas_hit_rate": _mean([record["atlas_hit"] for record in atlas_records]),
        "fallback_disclosure": fallback_disclosure,
        "read_cost_reduction": _read_reduction(records),
        "conditions": conditions,
        "protocol_violations": violations,
        "arm_purity_pass": not violations,
        "break_even": break_even,
    }
    atlas_questions = [
        {
            "id": item["id"],
            "arm": "atlas",
            "category": item["category"],
            "grade": by_id[item["id"]]["atlas"]["grade"],
        }
        for item in paired
    ]
    read_credit = max(comparison["read_cost_reduction"] or 0.0, 0.0)
    normalized = {
        "metrics": {
            "M1": data["metrics"]["M1"],
            "M2": data["metrics"]["M2"],
            "M4": data["metrics"]["M4"],
            "M5": {
                "questions": atlas_questions,
                "citation_validity": _mean([
                    by_id[item["id"]]["atlas"]["citation_validity"] for item in paired
                ]),
                "provenance_disclosure": _mean([
                    by_id[item["id"]]["atlas"]["provenance_disclosure"] for item in paired
                ]),
            },
            "M6": {
                "atlas_hit_rate": comparison["atlas_hit_rate"],
                "fallback_disclosure": comparison["fallback_disclosure"],
                "read_cost_reduction": read_credit,
                "accuracy_delta": comparison["accuracy_delta"],
            },
        },
    }
    return comparison, normalized


def score_result(
    result: dict,
    rubric: dict,
    run_root: str | Path | None = None,
    *,
    expected_freeze_manifest_sha256: str | None = None,
) -> dict:
    if result.get("schema_version") == RESULT_SCHEMA:
        _validate_v1_result(result, rubric)
        return _score_validated_result(result, rubric, gates_pass=all(result["gates"].values()))
    if result.get("schema_version") == RESULT_SCHEMA_V2:
        data = _validate_v2_result(result, rubric, run_root, expected_freeze_manifest_sha256)
        comparison, normalized = _derive_v2(data, rubric)
        return _score_validated_result(
            normalized,
            rubric,
            gates_pass=all(value["passed"] for value in result["gates"].values()),
            arm_purity_pass=comparison["arm_purity_pass"],
            comparison=comparison,
        )
    raise EvaluationError(f"schema_version must be {RESULT_SCHEMA} or {RESULT_SCHEMA_V2}")

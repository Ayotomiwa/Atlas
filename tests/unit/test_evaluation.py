from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json

import pytest

from scripts.lib.evaluation import (
    EvaluationError,
    RUN_SCHEMA_V2,
    freeze_answers,
    freeze_run,
    load_json,
    prepare_run,
    resolve_rubric_path,
    score_result,
    stable_json,
    validate_result,
    verify_answer_freeze,
    verify_run_freeze,
)
from scripts.atlas_eval import main as atlas_eval_main


ROOT = Path(__file__).resolve().parents[2]


def _result(rubric: dict) -> dict:
    questions = []
    categories = [
        ("LOOKUP", "CORRECT"),
        ("SYNTHESIS", "CORRECT"),
        ("IMPACT", "CORRECT"),
        ("TRAP-CONFLICT", "CORRECT"),
        ("TRAP-UNKNOWABLE", "REFUSED-CORRECTLY"),
        ("TRAP-ABSENCE", "CORRECT"),
    ]
    for index, (category, grade) in enumerate(categories, start=1):
        questions.append({"id": f"A{index}", "arm": "atlas", "category": category, "grade": grade})
    questions.append({"id": "C1", "arm": "control", "category": "IMPACT", "grade": "PARTIAL"})
    return {
        "schema_version": "atlas-evaluation-result/1.0",
        "rubric_sha256": sha256(stable_json(rubric)).hexdigest(),
        "gates": {f"G{index}": True for index in range(1, 9)},
        "metrics": {
            "M1": {"core_recall": 0.9, "bonus_recall": 0.6, "locator_accuracy": 1.0, "fabrication_count": 0},
            "M2": {
                "conflict_recall": 1.0,
                "multi_file_recall": 1.0,
                "tool_defaults_resisted": True,
                "external_unknown": True,
                "identity_ambiguity": True,
                "dead_path_resistance": True,
            },
            "M4": {"lint": True, "freshness": True, "tests": True, "granularity": True},
            "M5": {"questions": questions, "citation_validity": 1.0, "provenance_disclosure": 1.0},
            "M6": {"atlas_hit_rate": 0.8, "fallback_disclosure": 1.0, "read_cost_reduction": 0.4, "accuracy_delta": 0.2},
        },
        "telemetry": {"bytes_read": None, "unique_evidence_sources": 12, "tool_calls": None, "latency_ms": 1200},
    }


def test_scoring_is_reproducible_and_partial_is_explicit():
    rubric = load_json(ROOT / "evaluation" / "rubric.json")
    assert rubric["partial_value"] == 0.5
    result = _result(rubric)
    assert score_result(result, rubric) == score_result(result, rubric)
    assert score_result(result, rubric)["verdict"] == "Ship"


def test_gates_and_malformed_results_are_rejected_or_cap_verdict():
    rubric = load_json(ROOT / "evaluation" / "rubric.json")
    result = _result(rubric)
    result["gates"]["G1"] = False
    assert score_result(result, rubric)["verdict"] == "Not ready"
    result = _result(rubric)
    result["metrics"]["M5"]["questions"] = [
        item for item in result["metrics"]["M5"]["questions"] if not (item["arm"] == "control" and item["category"] == "IMPACT")
    ]
    with pytest.raises(EvaluationError, match="impact questions"):
        validate_result(result, rubric)


def test_prepare_keeps_sealed_run_outside_atlas(tmp_path: Path):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    destination = tmp_path / "sealed"
    run = prepare_run(ROOT, destination, run_id="run-1", fixture=fixture, fixture_head="abc")
    assert (run / "rubric.json").exists()
    assert (run / "ground-truth").is_dir()
    assert load_json(run / "run.json")["schema_version"] == RUN_SCHEMA_V2
    assert {"questions", "telemetry", "manifests"} <= {path.name for path in run.iterdir() if path.is_dir()}
    assert resolve_rubric_path(run / "results" / "results.json") == run / "rubric.json"
    with pytest.raises(EvaluationError, match="outside"):
        prepare_run(ROOT, ROOT / "evaluation" / "sealed", run_id="bad", fixture=fixture, fixture_head="abc")


def test_answer_freeze_detects_mutation_and_new_files(tmp_path: Path):
    run = tmp_path / "sealed" / "legacy-run"
    (run / "answers").mkdir(parents=True)
    (run / "run.json").write_bytes(stable_json({
        "schema_version": "atlas-evaluation-run/1.0",
        "run_id": "legacy-run",
        "answer_sets_frozen": False,
    }))
    answer = run / "answers" / "atlas.md"
    answer.write_text("frozen answer\n", encoding="utf-8")

    manifest = freeze_answers(run)
    assert manifest.is_file()
    assert verify_answer_freeze(run) == []
    with pytest.raises(EvaluationError, match="already frozen"):
        freeze_answers(run)

    answer.write_text("changed answer\n", encoding="utf-8")
    (run / "answers" / "late.md").write_text("late\n", encoding="utf-8")
    changes = verify_answer_freeze(run)
    assert "answer file changed: answers/atlas.md" in changes
    assert "unexpected answer file: answers/late.md" in changes


def _write_v2_inputs(run: Path, paired_lines: list[str] | None = None) -> None:
    (run / "fixture" / "fixture.txt").write_text("fixture\n", encoding="utf-8")
    (run / "questions" / "paired.jsonl").write_text(
        "\n".join(paired_lines or [
            '{"id":"Q1","category":"LOOKUP","condition":"cold","revision":"cold","prompt":"What is the owner?"}'
        ]) + "\n",
        encoding="utf-8",
    )
    (run / "personas" / "author.md").write_text("authoring prompt\n", encoding="utf-8")
    (run / "ground-truth" / "truth.md").write_text("judge only\n", encoding="utf-8")
    (run / "answers" / "atlas-Q1.md").write_text("answer\n", encoding="utf-8")
    (run / "telemetry" / "atlas").mkdir()
    (run / "telemetry" / "atlas" / "Q1.json").write_text("{}\n", encoding="utf-8")
    for name in ("fixture.json", "tool-policy.json", "model-config.json", "atlas-snapshot.json"):
        (run / "manifests" / name).write_text("{}\n", encoding="utf-8")


def test_v2_freeze_rejects_invalid_paired_question_banks_and_missing_manifests(tmp_path: Path):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    invalid_banks = [
        ["not json"],
        ["[]"],
        ['{"id":"Q1","category":"LOOKUP","condition":"bad","revision":"cold","prompt":"x"}'],
        [
            '{"id":"Q1","category":"LOOKUP","condition":"cold","revision":"cold","prompt":"x"}',
            '{"id":"Q1","category":"LOOKUP","condition":"cold","revision":"cold","prompt":"y"}',
        ],
    ]
    for index, bank in enumerate(invalid_banks):
        run = prepare_run(ROOT, tmp_path / "sealed", run_id=f"invalid-{index}", fixture=fixture, fixture_head="abc")
        _write_v2_inputs(run, bank)
        with pytest.raises(EvaluationError, match="paired question"):
            freeze_run(run)

    run = prepare_run(ROOT, tmp_path / "sealed", run_id="missing-manifest", fixture=fixture, fixture_head="abc")
    _write_v2_inputs(run)
    (run / "manifests" / "model-config.json").unlink()
    with pytest.raises(EvaluationError, match="model-config.json"):
        freeze_run(run)


@pytest.mark.parametrize("protected_root", (
    "fixture", "questions", "personas", "ground-truth", "answers", "telemetry", "manifests",
))
def test_v2_master_freeze_detects_mutation_addition_and_removal_in_each_protected_root(
    tmp_path: Path, protected_root: str,
):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    for action in ("changed", "unexpected", "missing"):
        run = prepare_run(ROOT, tmp_path / "sealed", run_id=f"{protected_root}-{action}", fixture=fixture, fixture_head="abc")
        _write_v2_inputs(run)
        freeze_run(run)
        files = sorted(path for path in (run / protected_root).rglob("*") if path.is_file())
        if action == "changed":
            files[0].write_text("changed\n", encoding="utf-8")
        elif action == "unexpected":
            (run / protected_root / "late.txt").write_text("late\n", encoding="utf-8")
        else:
            files[0].unlink()
        changes = verify_run_freeze(run)
        assert any(change.startswith(f"{action} protected file: {protected_root}/") for change in changes)


def test_v2_master_freeze_detects_immutable_metadata_drift_and_rejects_second_freeze(tmp_path: Path):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    run = prepare_run(ROOT, tmp_path / "sealed", run_id="metadata", fixture=fixture, fixture_head="abc")
    _write_v2_inputs(run)
    manifest = freeze_run(run)
    assert manifest == run / "freeze-manifest.json"
    assert verify_run_freeze(run) == []
    with pytest.raises(EvaluationError, match="already frozen"):
        freeze_run(run)

    metadata = load_json(run / "run.json")
    metadata["fixture_head"] = "changed"
    (run / "run.json").write_bytes(stable_json(metadata))
    assert "immutable run metadata changed: fixture_head" in verify_run_freeze(run)


def test_v2_master_freeze_detects_deleted_nullable_incremental_head_as_drift(tmp_path: Path):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    run = prepare_run(ROOT, tmp_path / "sealed", run_id="incremental", fixture=fixture, fixture_head="abc")
    _write_v2_inputs(run)
    freeze_run(run)

    metadata = load_json(run / "run.json")
    del metadata["incremental_head"]
    (run / "run.json").write_bytes(stable_json(metadata))

    assert "immutable run metadata changed: incremental_head" in verify_run_freeze(run)


@pytest.mark.parametrize("digest_action", ("missing", "non-string", "short", "non-hex"))
def test_v2_verify_rejects_malformed_freeze_manifest_digest(tmp_path: Path, digest_action: str):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    run = prepare_run(ROOT, tmp_path / "sealed", run_id=f"digest-{digest_action}", fixture=fixture, fixture_head="abc")
    _write_v2_inputs(run)
    freeze_run(run)
    metadata = load_json(run / "run.json")
    if digest_action == "missing":
        del metadata["freeze_manifest_sha256"]
    elif digest_action == "non-string":
        metadata["freeze_manifest_sha256"] = 1
    elif digest_action == "short":
        metadata["freeze_manifest_sha256"] = "abc"
    else:
        metadata["freeze_manifest_sha256"] = "g" * 64
    (run / "run.json").write_bytes(stable_json(metadata))

    with pytest.raises(EvaluationError, match="freeze_manifest_sha256"):
        verify_run_freeze(run)


def test_v2_verify_rejects_nonhex_digest_in_frozen_manifest(tmp_path: Path):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    run = prepare_run(ROOT, tmp_path / "sealed", run_id="bad-manifest", fixture=fixture, fixture_head="abc")
    _write_v2_inputs(run)
    freeze_run(run)
    manifest = load_json(run / "freeze-manifest.json")
    manifest["files"]["fixture/fixture.txt"] = "g" * 64
    (run / "freeze-manifest.json").write_bytes(stable_json(manifest))

    with pytest.raises(EvaluationError, match="SHA-256"):
        verify_run_freeze(run)


def test_verify_freeze_keeps_legacy_success_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    run = tmp_path / "legacy-run"
    (run / "answers").mkdir(parents=True)
    (run / "answers" / "answer.md").write_text("answer\n", encoding="utf-8")
    (run / "run.json").write_bytes(stable_json({
        "schema_version": "atlas-evaluation-run/1.0",
        "run_id": "legacy-run",
        "answer_sets_frozen": False,
    }))
    freeze_answers(run)

    assert atlas_eval_main(["verify-freeze", str(run)]) == 0
    assert capsys.readouterr().out == "Evaluation answer freeze is valid.\n"


_PAIRED_QUESTIONS = [
    {"id": "Q1", "category": "LOOKUP", "condition": "cold", "revision": "cold", "prompt": "Who owns it?"},
    {"id": "Q2", "category": "IMPACT", "condition": "warm", "revision": "cold", "prompt": "What breaks?"},
    {
        "id": "Q3",
        "category": "TRAP-UNKNOWABLE",
        "condition": "cold",
        "revision": "cold",
        "prompt": "What cannot be known?",
    },
]


def _question_telemetry(question_id: str, arm: str, **overrides: object) -> dict:
    index = int(question_id[1:])
    value = {
        "schema_version": "atlas-evaluation-telemetry/1.0",
        "question_id": question_id,
        "arm": arm,
        "bytes_read": (100 if arm == "atlas" else (400 - index * 100)),
        "unique_evidence_sources": 1,
        "tool_calls": (index if arm == "atlas" else index + 2),
        "latency_ms": (1000 if arm == "atlas" else 2000),
        "input_tokens": (None if arm == "atlas" and question_id == "Q1" else index * 10),
        "output_tokens": (10 if arm == "atlas" else 30),
        "atlas_hit": (question_id != "Q2" if arm == "atlas" else None),
        "fallback_used": (question_id == "Q2" if arm == "atlas" else None),
        "fallback_disclosed": (False if arm == "atlas" and question_id == "Q2" else None),
        "source_accessed": arm == "control",
        "atlas_accessed": arm == "atlas",
    }
    value.update(overrides)
    return value


def _v2_run_and_result(
    tmp_path: Path,
    *,
    run_id: str = "comparison",
    telemetry_overrides: dict[tuple[str, str], dict] | None = None,
    authoring_overrides: dict | None = None,
) -> tuple[Path, dict, dict]:
    rubric = load_json(ROOT / "evaluation" / "rubric.json")
    fixture = tmp_path / f"{run_id}-fixture"
    fixture.mkdir()
    run = prepare_run(ROOT, tmp_path / "sealed", run_id=run_id, fixture=fixture, fixture_head="abc")
    _write_v2_inputs(run, [json.dumps(question, sort_keys=True) for question in _PAIRED_QUESTIONS])
    (run / "telemetry" / "control").mkdir()
    telemetry_overrides = telemetry_overrides or {}
    for question in _PAIRED_QUESTIONS:
        for arm in ("atlas", "control"):
            telemetry = _question_telemetry(
                question["id"], arm, **telemetry_overrides.get((question["id"], arm), {})
            )
            (run / "telemetry" / arm / f"{question['id']}.json").write_bytes(stable_json(telemetry))
    authoring = {
        "schema_version": "atlas-evaluation-phase-telemetry/1.0",
        "phase": "authoring",
        "bytes_read": 600,
        "unique_evidence_sources": 5,
        "tool_calls": 9,
        "latency_ms": 9000,
        "input_tokens": 100,
        "output_tokens": 50,
    }
    authoring.update(authoring_overrides or {})
    (run / "telemetry" / "authoring.json").write_bytes(stable_json(authoring))
    freeze_run(run)
    metadata = load_json(run / "run.json")
    grades = {
        "Q1": ("CORRECT", "PARTIAL"),
        "Q2": ("PARTIAL", "CORRECT"),
        "Q3": ("REFUSED-CORRECTLY", "WRONG"),
    }
    questions = []
    for question in _PAIRED_QUESTIONS:
        arms = {}
        for arm, grade in zip(("atlas", "control"), grades[question["id"]]):
            arms[arm] = {
                "grade": grade,
                "citation_validity": 1.0,
                "provenance_disclosure": 1.0,
                "citations": ["_curated/example.md" if arm == "atlas" else "src/example.py"],
                "rationale": "Supported by the frozen key.",
                "telemetry": f"telemetry/{arm}/{question['id']}.json",
            }
        questions.append({"id": question["id"], "category": question["category"], **arms})
    result = {
        "schema_version": "atlas-evaluation-result/2.0",
        "rubric_sha256": metadata["rubric_sha256"],
        "freeze_manifest_sha256": metadata["freeze_manifest_sha256"],
        "gates": {
            gate: {"passed": True, "evidence": ["manifests/fixture.json"]}
            for gate in rubric["gates"]
        },
        "metrics": {
            "M1": {"core_recall": 0.9, "bonus_recall": 0.6, "locator_accuracy": 1.0, "fabrication_count": 0},
            "M2": {
                "conflict_recall": 1.0,
                "multi_file_recall": 1.0,
                "tool_defaults_resisted": True,
                "external_unknown": True,
                "identity_ambiguity": True,
                "dead_path_resistance": True,
            },
            "M4": {"lint": True, "freshness": True, "tests": True, "granularity": True},
        },
        "questions": questions,
        "authoring_telemetry": "telemetry/authoring.json",
    }
    return run, rubric, result


def test_v2_derives_literal_paired_comparison_and_break_even(tmp_path: Path):
    run, rubric, result = _v2_run_and_result(tmp_path)

    score = score_result(result, rubric, run_root=run)

    assert score["comparison"] == {
        "atlas_accuracy": 0.8333333333333334,
        "control_accuracy": 0.5,
        "accuracy_delta": 0.33333333333333337,
        "atlas_hit_rate": 0.6666666666666666,
        "fallback_disclosure": 0.0,
        "read_cost_reduction": 0.5,
        "conditions": {
            "cold": {
                "atlas_accuracy": 1.0,
                "control_accuracy": 0.25,
                "accuracy_delta": 0.75,
                "read_cost_reduction": 0.5,
            },
            "warm": {
                "atlas_accuracy": 0.5,
                "control_accuracy": 1.0,
                "accuracy_delta": -0.5,
                "read_cost_reduction": 0.5,
            },
        },
        "protocol_violations": [],
        "arm_purity_pass": True,
        "break_even": {
            "bytes_read": 6.0,
            "tool_calls": 4.5,
            "latency_ms": 9.0,
            "input_tokens": None,
            "output_tokens": 2.5,
        },
    }
    assert score["family_scores"]["M5"] == 13.5


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        (lambda result: result["questions"].pop(), "missing question results"),
        (lambda result: result["questions"].append(deepcopy(result["questions"][0])), "duplicates id"),
        (lambda result: result["questions"].append({**deepcopy(result["questions"][0]), "id": "Q9"}), "extra question results"),
        (lambda result: result["questions"][0].update(category="IMPACT"), "category does not match"),
    ),
)
def test_v2_requires_exact_paired_membership_and_categories(tmp_path: Path, mutation, message: str):
    run, rubric, result = _v2_run_and_result(tmp_path)
    mutation(result)

    with pytest.raises(EvaluationError, match=message):
        validate_result(result, rubric, run_root=run)


def test_v2_requires_run_root_and_rejects_judge_entered_m5_m6(tmp_path: Path):
    run, rubric, result = _v2_run_and_result(tmp_path)
    with pytest.raises(EvaluationError, match="run_root"):
        validate_result(result, rubric)

    for metric in ("M5", "M6"):
        invalid = deepcopy(result)
        invalid["metrics"][metric] = {}
        with pytest.raises(EvaluationError, match="exactly M1, M2 and M4"):
            validate_result(invalid, rubric, run_root=run)


@pytest.mark.parametrize(
    ("evidence", "message"),
    (
        ([], "non-empty evidence"),
        (["manifests/fixture.json", "manifests/fixture.json"], "duplicate evidence"),
        (["../run.json"], "safe run-relative"),
        (["C:/run.json"], "safe run-relative"),
        ([{"path": "manifests/fixture.json"}], "safe run-relative"),
        (["manifests/not-frozen.json"], "frozen file"),
    ),
)
def test_v2_gates_require_safe_frozen_evidence(tmp_path: Path, evidence: list[object], message: str):
    run, rubric, result = _v2_run_and_result(tmp_path)
    result["gates"]["G1"]["evidence"] = evidence

    with pytest.raises(EvaluationError, match=message):
        validate_result(result, rubric, run_root=run)


def test_v2_allows_bound_freeze_manifest_as_gate_evidence_and_rejects_gate_extras(tmp_path: Path):
    run, rubric, result = _v2_run_and_result(tmp_path)
    result["gates"]["G8"]["evidence"] = ["freeze-manifest.json"]
    validate_result(result, rubric, run_root=run)

    result["gates"]["G8"]["note"] = "judge prose"
    with pytest.raises(EvaluationError, match="exactly passed and evidence"):
        validate_result(result, rubric, run_root=run)


def test_v2_preserves_negative_and_null_read_reduction_with_zero_positive_credit(tmp_path: Path):
    negative_run, rubric, negative_result = _v2_run_and_result(
        tmp_path, run_id="negative", telemetry_overrides={("Q1", "atlas"): {"bytes_read": 700}}
    )
    negative = score_result(negative_result, rubric, run_root=negative_run)
    assert negative["comparison"]["read_cost_reduction"] == -0.5
    assert negative["family_scores"]["M6"] == 7.0

    null_run, rubric, null_result = _v2_run_and_result(
        tmp_path, run_id="null", telemetry_overrides={("Q1", "atlas"): {"bytes_read": None}}
    )
    null_score = score_result(null_result, rubric, run_root=null_run)
    assert null_score["comparison"]["read_cost_reduction"] is None
    assert null_score["comparison"]["conditions"]["cold"]["read_cost_reduction"] is None
    assert null_score["family_scores"]["M6"] == 7.0


def test_v2_fallback_disclosure_handles_proportion_and_no_fallback(tmp_path: Path):
    proportion_run, rubric, proportion_result = _v2_run_and_result(
        tmp_path,
        run_id="proportion",
        telemetry_overrides={
            ("Q1", "atlas"): {"fallback_used": True, "fallback_disclosed": True},
        },
    )
    assert score_result(proportion_result, rubric, run_root=proportion_run)["comparison"]["fallback_disclosure"] == 0.5

    no_fallback_run, rubric, no_fallback_result = _v2_run_and_result(
        tmp_path,
        run_id="no-fallback",
        telemetry_overrides={("Q2", "atlas"): {"fallback_used": False, "fallback_disclosed": None}},
    )
    assert score_result(no_fallback_result, rubric, run_root=no_fallback_run)["comparison"]["fallback_disclosure"] == 1.0


def test_v2_records_stable_arm_purity_violations_and_forces_not_ready(tmp_path: Path):
    run, rubric, result = _v2_run_and_result(
        tmp_path,
        telemetry_overrides={
            ("Q1", "atlas"): {"source_accessed": True},
            ("Q2", "control"): {"atlas_accessed": True},
        },
    )

    score = score_result(result, rubric, run_root=run)
    assert score["comparison"]["protocol_violations"] == [
        "Q1/atlas: source_accessed=true",
        "Q2/control: atlas_accessed=true",
    ]
    assert score["comparison"]["arm_purity_pass"] is False
    assert score["verdict"] == "Not ready"


def test_v2_rejects_bad_telemetry_reference_and_schema(tmp_path: Path):
    run, rubric, result = _v2_run_and_result(tmp_path, run_id="references")
    result["questions"][0]["atlas"]["telemetry"] = "telemetry/control/Q1.json"
    with pytest.raises(EvaluationError, match="arm-specific"):
        validate_result(result, rubric, run_root=run)

    bad_run, rubric, bad_result = _v2_run_and_result(
        tmp_path,
        run_id="bad-schema",
        telemetry_overrides={("Q1", "atlas"): {"schema_version": "bad"}},
    )
    with pytest.raises(EvaluationError, match="telemetry schema_version"):
        validate_result(bad_result, rubric, run_root=bad_run)


def test_v2_rejects_invalid_optional_authoring_telemetry(tmp_path: Path):
    run, rubric, result = _v2_run_and_result(
        tmp_path, authoring_overrides={"phase": "judging"}
    )
    with pytest.raises(EvaluationError, match="authoring telemetry phase"):
        validate_result(result, rubric, run_root=run)


def test_v2_failed_gate_fabrication_and_refusal_force_not_ready(tmp_path: Path):
    run, rubric, result = _v2_run_and_result(tmp_path)
    for mutation in (
        lambda value: value["gates"]["G1"].update(passed=False),
        lambda value: value["metrics"]["M1"].update(fabrication_count=1),
        lambda value: value["questions"][2]["atlas"].update(grade="REFUSED-WRONGLY"),
    ):
        invalid = deepcopy(result)
        mutation(invalid)
        assert score_result(invalid, rubric, run_root=run)["verdict"] == "Not ready"


def test_v1_scoring_and_validation_ignore_optional_run_root(tmp_path: Path):
    rubric = load_json(ROOT / "evaluation" / "rubric.json")
    result = _result(rubric)
    expected = score_result(result, rubric)

    validate_result(result, rubric, run_root=tmp_path)
    assert score_result(result, rubric, run_root=tmp_path) == expected
    assert "comparison" not in expected

from hashlib import sha256
from pathlib import Path

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

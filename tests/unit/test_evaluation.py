from hashlib import sha256
from pathlib import Path

import pytest

from scripts.lib.evaluation import (
    EvaluationError,
    freeze_answers,
    load_json,
    prepare_run,
    resolve_rubric_path,
    score_result,
    stable_json,
    validate_result,
    verify_answer_freeze,
)


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
    assert resolve_rubric_path(run / "results" / "results.json") == run / "rubric.json"
    with pytest.raises(EvaluationError, match="outside"):
        prepare_run(ROOT, ROOT / "evaluation" / "sealed", run_id="bad", fixture=fixture, fixture_head="abc")


def test_answer_freeze_detects_mutation_and_new_files(tmp_path: Path):
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    run = prepare_run(ROOT, tmp_path / "sealed", run_id="run-1", fixture=fixture, fixture_head="abc")
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

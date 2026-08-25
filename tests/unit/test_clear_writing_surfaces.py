from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


CLEAR_WRITING_SURFACES = (
    ".claude/skills/_shared/clear-writing.md",
    ".agents/skills/_shared/clear-writing.md",
)

HUMANIZE_SURFACES = (
    ".claude/skills/atlas-humanize/SKILL.md",
    ".agents/skills/atlas-humanize/SKILL.md",
)

REVIEWER_SURFACES = (
    ".claude/agents/atlas-reviewer.md",
    ".codex/agents/atlas-reviewer.toml",
)

ONBOARDING_SURFACES = (
    ".claude/skills/atlas-onboard-repository/references/full-baseline.md",
    ".agents/skills/atlas-onboard-repository/references/full-baseline.md",
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").lower()


def _assert_contains(paths: tuple[str, ...], *needles: str) -> None:
    for relative in paths:
        text = _read(relative)
        for needle in needles:
            assert needle.lower() in text, f"{relative}: missing {needle!r}"


def test_clear_writing_owns_the_specificity_scan() -> None:
    _assert_contains(
        CLEAR_WRITING_SURFACES,
        "could appear unchanged",
        "serves as",
        "inline label",
        "passive",
        "not banned words",
        "must",
        "never",
        "only",
    )


def test_humanize_and_review_apply_the_scan_without_inventing_facts() -> None:
    _assert_contains(
        HUMANIZE_SURFACES,
        "generic",
        "vague",
        "page-specificity scan",
        "evidence-supported replacement or deletion",
        "knowledge gap",
    )
    _assert_contains(
        REVIEWER_SURFACES,
        "page-specificity scan",
        "staging-sufficiency",
        "minor and non-blocking",
        "never invent detail",
    )


def test_repository_readiness_rejects_interchangeable_capsules() -> None:
    _assert_contains(
        ONBOARDING_SURFACES,
        "fails",
        "could appear unchanged for another component",
        "behaviour or boundary",
    )


def test_specificity_heuristics_do_not_become_lint_rules() -> None:
    lint_source = _read("scripts/atlas_lint.py")
    for phrase in ("could appear unchanged", "serves as", "stands as"):
        assert phrase not in lint_source

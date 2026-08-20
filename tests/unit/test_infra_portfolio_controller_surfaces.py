from __future__ import annotations

from pathlib import Path

from scripts.lib.frontmatter import parse_frontmatter


ROOT = Path(__file__).resolve().parents[2]


CLAUDE_SKILL = ROOT / ".claude/skills/atlas-onboard-infra-portfolio/SKILL.md"
CODEX_SKILL = ROOT / ".agents/skills/atlas-onboard-infra-portfolio/SKILL.md"


def _skill_texts() -> tuple[str, str]:
    return (
        CLAUDE_SKILL.read_text(encoding="utf-8"),
        CODEX_SKILL.read_text(encoding="utf-8"),
    )


def test_portfolio_controller_is_a_skill_without_a_new_agent() -> None:
    for skill in (CLAUDE_SKILL, CODEX_SKILL):
        reference = skill.parent / "references/campaign-workflow.md"
        assert skill.is_file()
        assert reference.is_file()
        metadata, body = parse_frontmatter(skill)
        assert metadata["name"] == "atlas-onboard-infra-portfolio"
        assert metadata["description"].startswith("Use when")
        assert "atlas-onboard-repository" in body
        assert "atlas-repo-analyst" in body

    claude_metadata, _ = parse_frontmatter(CLAUDE_SKILL)
    assert "Agent" in claude_metadata["allowed-tools"]
    assert not (ROOT / ".claude/agents/atlas-onboard-infra-portfolio.md").exists()
    assert not (ROOT / ".codex/agents/atlas-onboard-infra-portfolio.toml").exists()


def test_controller_surfaces_fixed_portfolio_safety_invariants() -> None:
    for text in _skill_texts():
        for mode in ("prepare", "run", "resume", "status", "pause"):
            assert mode in text
        assert "_intake/onboarding/<campaign-id>.json" in text
        assert "batch of five" in text
        assert "three" in text and "read-only" in text
        assert "one combined preview" in text
        assert "one approval" in text
        assert "compare-and-swap" in text
        assert "never recursively" in text.lower()
        assert "staging" in text
        assert "curation" in text


def test_campaign_workflow_defines_inventory_pilot_resume_and_write_boundaries() -> None:
    references = (
        CLAUDE_SKILL.parent / "references/campaign-workflow.md",
        CODEX_SKILL.parent / "references/campaign-workflow.md",
    )
    for reference in references:
        text = reference.read_text(encoding="utf-8")
        assert "CSV" in text and "JSON" in text
        assert "one explicitly named directory level" in text
        assert "(source_key, repository_root)" in text
        assert "three" in text and "six" in text
        assert "topology" in text and "IaC" in text and "application" in text
        assert "new archetype" in text
        assert "active_trial" in text
        assert "repository evidence" in text and "analyst finding" in text
        assert "onboarding_source" in text
        assert "active trial" in text
        assert "queued" in text
        assert "CAS conflict" in text
        assert "background" in text
        assert "push" in text and "merge" in text


def test_campaign_guidance_uses_planned_commit_scope_and_bounded_pilot_expansion() -> None:
    references = (
        CLAUDE_SKILL.parent / "references/campaign-workflow.md",
        CODEX_SKILL.parent / "references/campaign-workflow.md",
    )
    for reference in references:
        text = reference.read_text(encoding="utf-8")
        assert "exact path/scope planned for the local commit" in text
        assert "selected feature branch" in text
        assert "Do not predict a commit SHA" in text
        assert "Expand above three, up to six, only when three cannot represent" in text

    for text in _skill_texts():
        assert "`staged`" in text
        assert "`already-covered`" in text
        assert "explicitly `skipped`" in text


def test_navigation_registers_campaign_queue_as_non_authoritative_intake() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    index = (ROOT / "index.md").read_text(encoding="utf-8")
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    intake = (ROOT / "_intake/README.md").read_text(encoding="utf-8")
    onboarding_index = (ROOT / "onboarding/index.md").read_text(encoding="utf-8")
    advanced = (ROOT / "onboarding/advanced-reference.md").read_text(encoding="utf-8")

    for instructions in (claude, agents):
        assert "atlas-onboard-infra-portfolio" in instructions
        assert "_intake/onboarding/<campaign-id>.json" in instructions
        assert "committed staging evidence" in instructions

    assert "infrastructure portfolio" in readme.lower()
    assert "infrastructure portfolio" in index.lower()
    assert "Infrastructure onboarding campaigns" in intake
    assert "_intake/onboarding" in intake
    assert "atlas_onboarding_campaign.py" in intake
    assert "atlas-onboard-infra-portfolio" in onboarding_index
    assert "atlas-onboard-infra-portfolio" in advanced
    assert "atlas_onboarding_campaign.py" in advanced


def test_campaign_documentation_does_not_claim_semantic_or_background_ownership() -> None:
    combined = "\n".join(
        [
            *_skill_texts(),
            (ROOT / "_intake/README.md").read_text(encoding="utf-8"),
            (ROOT / "onboarding/advanced-reference.md").read_text(encoding="utf-8"),
        ]
    ).lower()

    assert "does not continue in the background" in combined
    assert "never curates" in combined
    assert "never clones" in combined
    assert "authority" in combined

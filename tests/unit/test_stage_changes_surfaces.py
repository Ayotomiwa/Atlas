from __future__ import annotations

from pathlib import Path
import tomllib

from scripts.lib.frontmatter import parse_frontmatter


ROOT = Path(__file__).resolve().parents[2]


def test_stage_changes_skill_and_agent_surfaces_exist() -> None:
    claude_skill = ROOT / ".claude/skills/atlas-stage-changes/SKILL.md"
    codex_skill = ROOT / ".agents/skills/atlas-stage-changes/SKILL.md"
    claude_agent = ROOT / ".claude/agents/atlas-change-analyst.md"
    codex_agent = ROOT / ".codex/agents/atlas-change-analyst.toml"

    for path in (
        claude_skill,
        claude_skill.parent / "references/workflow.md",
        codex_skill,
        codex_skill.parent / "references/workflow.md",
        claude_agent,
        codex_agent,
    ):
        assert path.is_file(), path.relative_to(ROOT).as_posix()

    claude_metadata, _ = parse_frontmatter(claude_skill)
    codex_metadata, _ = parse_frontmatter(codex_skill)
    codex_profile = tomllib.loads(codex_agent.read_text(encoding="utf-8"))

    assert claude_metadata["name"] == "atlas-stage-changes"
    assert "Agent" in claude_metadata["allowed-tools"]
    assert codex_metadata["name"] == "atlas-stage-changes"
    assert codex_profile["name"] == "atlas-change-analyst"

    for skill in (claude_skill, codex_skill):
        text = skill.read_text(encoding="utf-8")
        assert "user-confirmed" in text
        assert "external MR API" in text


def test_claude_change_analyst_exposes_only_read_only_tools() -> None:
    metadata, body = parse_frontmatter(ROOT / ".claude/agents/atlas-change-analyst.md")

    tools = {item.strip() for item in metadata["tools"].split(",")}
    assert tools == {"Read", "Grep", "Glob", "Bash"}
    assert "Never write files or Git state" in body
    assert "fetch" in body


def test_root_navigation_routes_staging_queue_and_change_intake() -> None:
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    index = (ROOT / "index.md").read_text(encoding="utf-8")

    for instructions in (claude, agents):
        assert "python scripts/atlas_query.py staging" in instructions
        assert "atlas-stage-changes" in instructions
        assert "_intake/checkpoints/<source-key>.json" in instructions

    assert "python scripts/atlas_query.py staging" in index
    assert "/atlas-stage-changes" in index
    assert "_intake/README.md" in index

    for managed_block in (
        ROOT / ".claude/skills/atlas-setup-repo/assets/managed-block.md",
        ROOT / ".agents/skills/atlas-setup-repo/assets/managed-block.md",
    ):
        assert "atlas-stage-changes" in managed_block.read_text(encoding="utf-8")

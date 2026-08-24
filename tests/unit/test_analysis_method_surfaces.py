from __future__ import annotations

from pathlib import Path
import re
import tomllib

from scripts.lib.frontmatter import parse_frontmatter


ROOT = Path(__file__).resolve().parents[2]


METHOD_PAIRS = {
    "source": (
        ".claude/skills/_shared/source-analysis.md",
        ".agents/skills/_shared/source-analysis.md",
    ),
    "risk": (
        ".claude/skills/_shared/change-risk-analysis.md",
        ".agents/skills/_shared/change-risk-analysis.md",
    ),
}


SKILL_PAIRS = {
    "discover": (
        ".claude/skills/atlas-discover/SKILL.md",
        ".agents/skills/atlas-discover/SKILL.md",
    ),
    "impact": (
        ".claude/skills/atlas-impact/SKILL.md",
        ".agents/skills/atlas-impact/SKILL.md",
    ),
    "stage_changes": (
        ".claude/skills/atlas-stage-changes/SKILL.md",
        ".agents/skills/atlas-stage-changes/SKILL.md",
    ),
    "lint": (
        ".claude/skills/atlas-lint/SKILL.md",
        ".agents/skills/atlas-lint/SKILL.md",
    ),
}


AGENT_PAIRS = {
    name: (
        f".claude/agents/{name}.md",
        f".codex/agents/{name}.toml",
    )
    for name in (
        "atlas-discovery-analyst",
        "atlas-impact-analyst",
        "atlas-change-analyst",
        "atlas-repo-analyst",
        "atlas-standards-analyst",
        "atlas-lint-analyst",
    )
}


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _assert_contains(paths: tuple[str, ...], *needles: str) -> None:
    for relative in paths:
        text = _read(relative).lower()
        for needle in needles:
            assert needle.lower() in text, f"{relative}: missing {needle!r}"


def test_shared_analysis_methods_exist_on_both_platforms() -> None:
    for pair in METHOD_PAIRS.values():
        for relative in pair:
            assert (ROOT / relative).is_file(), relative
        assert _read(pair[0]) == _read(pair[1]), f"method adapters drifted: {pair}"

    _assert_contains(
        METHOD_PAIRS["source"],
        "immutable",
        "current code",
        "recorded rationale",
        "recommendation",
        "stopping reason",
        "does not traverse history",
    )
    _assert_contains(
        METHOD_PAIRS["risk"],
        "safety fact",
        "cleared concern",
        "unresolved",
        "smallest",
        "do not infer safety",
        "automated check",
        "runtime observation",
        "likelihood",
        "consequence",
    )


def test_skills_and_agents_reference_their_analysis_methods() -> None:
    source_surfaces = (
        *SKILL_PAIRS["discover"],
        AGENT_PAIRS["atlas-discovery-analyst"][0],
        AGENT_PAIRS["atlas-discovery-analyst"][1],
        AGENT_PAIRS["atlas-repo-analyst"][0],
        AGENT_PAIRS["atlas-repo-analyst"][1],
        AGENT_PAIRS["atlas-standards-analyst"][0],
        AGENT_PAIRS["atlas-standards-analyst"][1],
    )
    _assert_contains(source_surfaces, "source-analysis.md")

    both_method_surfaces = (
        *SKILL_PAIRS["impact"],
        *SKILL_PAIRS["stage_changes"],
        AGENT_PAIRS["atlas-impact-analyst"][0],
        AGENT_PAIRS["atlas-impact-analyst"][1],
        AGENT_PAIRS["atlas-change-analyst"][0],
        AGENT_PAIRS["atlas-change-analyst"][1],
    )
    _assert_contains(
        both_method_surfaces,
        "source-analysis",
        "change-risk-analysis",
    )


def test_skill_and_agent_names_match_their_platform_adaptations() -> None:
    for claude_relative, agent_relative in SKILL_PAIRS.values():
        claude_metadata, _ = parse_frontmatter(ROOT / claude_relative)
        agent_metadata, _ = parse_frontmatter(ROOT / agent_relative)
        assert claude_metadata["name"] == agent_metadata["name"]

    for claude_relative, codex_relative in AGENT_PAIRS.values():
        claude_metadata, _ = parse_frontmatter(ROOT / claude_relative)
        codex = tomllib.loads(_read(codex_relative))
        assert claude_metadata["name"] == codex["name"]


def test_analysis_agents_remain_read_only() -> None:
    for claude_relative, codex_relative in AGENT_PAIRS.values():
        metadata, claude_body = parse_frontmatter(ROOT / claude_relative)
        tools = {tool.strip() for tool in metadata["tools"].split(",")}
        assert tools == {"Read", "Grep", "Glob", "Bash"}, claude_relative

        codex_body = tomllib.loads(_read(codex_relative))["developer_instructions"]
        for relative, body in (
            (claude_relative, claude_body),
            (codex_relative, codex_body),
        ):
            assert re.search(r"\bnever (?:modify|write|stage|edit)\b", body, re.I), (
                f"{relative}: missing read-only prohibition"
            )
            assert "pstack" not in body.lower(), relative


def test_repository_analysis_keeps_targeted_depth_invariants() -> None:
    _assert_contains(
        AGENT_PAIRS["atlas-repo-analyst"],
        "breadth",
        "targeted architecture depth",
        "same immutable",
        "architecture capsule",
        "broad scan",
        "exact anchors",
        "stopping reason",
        "historical investigation is out of scope",
    )


def test_lint_surfaces_keep_structural_fixes_inside_scope() -> None:
    lint_surfaces = (
        *SKILL_PAIRS["lint"],
        AGENT_PAIRS["atlas-lint-analyst"][0],
        AGENT_PAIRS["atlas-lint-analyst"][1],
    )
    _assert_contains(
        lint_surfaces,
        "root cause",
        "mechanically decidable",
        "structural fix",
        "repair scope",
    )

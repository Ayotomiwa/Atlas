from __future__ import annotations

from pathlib import Path
import re
import tomllib

from scripts.lib.frontmatter import parse_frontmatter


ROOT = Path(__file__).resolve().parents[2]


SURFACE_PAIRS = {
    "runtime": (
        ".claude/skills/_shared/runtime.md",
        ".agents/skills/_shared/runtime.md",
    ),
    "provenance": (
        ".claude/skills/_shared/answer-provenance.md",
        ".agents/skills/_shared/answer-provenance.md",
    ),
    "handoffs": (
        ".claude/skills/_shared/agent-handoffs.md",
        ".agents/skills/_shared/agent-handoffs.md",
    ),
    "discover": (
        ".claude/skills/atlas-discover/SKILL.md",
        ".agents/skills/atlas-discover/SKILL.md",
    ),
    "impact": (
        ".claude/skills/atlas-impact/SKILL.md",
        ".agents/skills/atlas-impact/SKILL.md",
    ),
    "discovery_agent": (
        ".claude/agents/atlas-discovery-analyst.md",
        ".codex/agents/atlas-discovery-analyst.toml",
    ),
    "impact_agent": (
        ".claude/agents/atlas-impact-analyst.md",
        ".codex/agents/atlas-impact-analyst.toml",
    ),
    "managed_block": (
        ".claude/skills/atlas-setup-repo/assets/managed-block.md",
        ".agents/skills/atlas-setup-repo/assets/managed-block.md",
    ),
}


def _texts(surface: str) -> tuple[str, str]:
    return tuple(
        (ROOT / relative).read_text(encoding="utf-8")
        for relative in SURFACE_PAIRS[surface]
    )


def _assert_all(surface: str, *needles: str) -> None:
    for relative, text in zip(SURFACE_PAIRS[surface], _texts(surface), strict=True):
        for needle in needles:
            assert needle in text, f"{relative}: missing {needle!r}"


def _assert_ordered(surface: str, *needles: str) -> None:
    for relative, text in zip(SURFACE_PAIRS[surface], _texts(surface), strict=True):
        positions = [text.find(needle) for needle in needles]
        assert all(position >= 0 for position in positions), (
            f"{relative}: missing ordered routing step; {positions=}"
        )
        assert positions == sorted(positions), f"{relative}: routing order differs"


def _metadata_description(relative: str) -> str:
    path = ROOT / relative
    if path.suffix == ".toml":
        return tomllib.loads(path.read_text(encoding="utf-8"))["description"]
    metadata, _ = parse_frontmatter(path)
    return metadata["description"]


def _paragraph_containing(text: str, needle: str) -> str:
    paragraphs = re.split(r"\n\s*\n", text)
    matches = [paragraph for paragraph in paragraphs if needle in paragraph]
    assert len(matches) == 1, f"expected one paragraph containing {needle!r}"
    return matches[0]


def _markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    assert match, f"missing section {heading!r}"
    return match["body"]


def test_binding_matrix_and_retrieval_ladder_match_on_both_platforms() -> None:
    _assert_all(
        "runtime",
        "managed Atlas block",
        "Explicit Ask Atlas",
        "unbound repository",
        "do not invoke Atlas automatically",
        "not-verified",
        "routing-only advisory",
        "uncertain, broad, multi-hop, Git-history, or durable-context lookup",
    )
    _assert_ordered(
        "runtime",
        "Retained context",
        "One known targeted source read",
        "Atlas before uncertain",
        "Complete Atlas answer",
        "Partial Atlas answer",
        "Atlas-guided source route",
        "Bounded source and unresolved gap",
    )


def test_direct_ask_source_authority_and_guided_fallback_are_paired() -> None:
    _assert_all(
        "discover",
        "Direct Ask Atlas",
        "relevant curated types",
        "answer-bearing links",
        "all supported material",
        "unresolved boundary",
        "read-only fallback is automatic",
    )
    _assert_all(
        "provenance",
        "Atlas",
        "Repository (located via Atlas)",
        "Inference",
        "Unresolved",
        "repository",
        "smallest path, symbol, config, IaC, or document boundary",
        "selection reason",
        "route confidence",
        "Atlas coverage endpoint",
        "exact commands",
    )


def test_impact_entrypoints_require_explicit_ask_or_bound_routing() -> None:
    for surface in ("impact", "impact_agent"):
        for relative in SURFACE_PAIRS[surface]:
            description = _metadata_description(relative)
            assert "direct Ask Atlas" in description, relative
            assert "bound repository" in description, relative


def test_answer_label_membership_is_exact_and_excludes_evidence_kinds() -> None:
    expected = {"Atlas", "Repository (located via Atlas)", "Inference", "Unresolved"}
    for relative, text in zip(
        SURFACE_PAIRS["provenance"], _texts("provenance"), strict=True
    ):
        declaration = re.search(
            r"Classify each material claim as (?P<labels>.+?)\.", text
        )
        assert declaration, relative
        labels = set(re.findall(r"\*\*([^*]+)\*\*", declaration["labels"]))
        assert labels == expected, relative
        label_section = _markdown_section(text, "Answer labels")
        listed_labels = set(
            re.findall(r"^- \*\*([^*]+)\*\*:", label_section, re.MULTILINE)
        )
        assert listed_labels == expected, relative
        assert "`External:" not in text, relative
        assert "`User-confirmed:" not in text, relative


def test_flow_synthesis_session_reuse_and_bounded_reentry_are_paired() -> None:
    for surface in ("discover", "discovery_agent"):
        _assert_all(
            surface,
            "trigger and outcome",
            "ordered participants and handoffs",
            "data and infrastructure transitions",
            "branches, retries, and failures",
            "standards, incidents, and runbooks",
            "coverage limits",
        )
    for surface in ("runtime", "handoffs"):
        _assert_all(
            surface,
            "ephemeral Atlas session",
            "Reuse",
            "Re-enter",
            "coverage endpoint",
        )


def test_exact_change_guard_and_semantic_risk_readiness_are_paired() -> None:
    exact_change_terms = (
        "_staging/changes",
        "--include-terminal",
        "--source-key",
        "--branch",
        "--from-exclusive",
        "--through-inclusive",
        "`--from-exclusive start` matches an explicit null start",
        "before completeness-sensitive source verification",
    )
    semantic_risk_terms = (
        "regardless of diff size",
        "API, schema, event, data, or flow",
        "AWS, IAM, account, environment, region, schedule, event-filter, monitoring, deployment, or rollback",
        "standards, operations, recovery, or cross-repository boundary",
        "confirmed, possible, external, and unknown impact",
        "testing, compatibility, deployment, and recovery obligations",
        "exceptions, ambiguity, destructive or cross-team risk, or missing critical evidence",
    )
    for surface in ("impact", "impact_agent"):
        _assert_all(surface, *exact_change_terms, *semantic_risk_terms)
        _assert_all(surface, "direct neighbors before", "local isolated edit")


def test_exact_change_staging_is_non_authoritative_in_the_guard_itself() -> None:
    guard = (
        "`_staging/` records are non-authoritative routing and completeness "
        "evidence, never factual authority"
    )
    for surface in ("impact", "impact_agent"):
        for relative, text in zip(
            SURFACE_PAIRS[surface], _texts(surface), strict=True
        ):
            exact_change = _paragraph_containing(text, "For an exact-change prompt")
            assert guard in exact_change, relative

    _assert_all("runtime", guard)


def test_managed_block_is_binding_signal_and_exposes_risk_triggers() -> None:
    _assert_all(
        "managed_block",
        "Presence of this managed block binds this repository to Atlas",
        "uncertain, broad, multi-hop, Git-history, or durable-context lookup",
        "semantic-risk change readiness regardless of diff size",
        "Explicit Ask Atlas",
    )


def test_paired_skill_and_agent_metadata_remain_valid() -> None:
    for surface in ("discover", "impact"):
        claude, codex = SURFACE_PAIRS[surface]
        claude_metadata, _ = parse_frontmatter(ROOT / claude)
        codex_metadata, _ = parse_frontmatter(ROOT / codex)
        assert claude_metadata["name"] == codex_metadata["name"]

    for surface in ("discovery_agent", "impact_agent"):
        claude, codex = SURFACE_PAIRS[surface]
        claude_metadata, _ = parse_frontmatter(ROOT / claude)
        codex_metadata = tomllib.loads((ROOT / codex).read_text(encoding="utf-8"))
        assert claude_metadata["name"] == codex_metadata["name"]

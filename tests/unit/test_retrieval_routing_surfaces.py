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


def _assert_absent(surface: str, *needles: str) -> None:
    for relative, text in zip(SURFACE_PAIRS[surface], _texts(surface), strict=True):
        for needle in needles:
            assert needle not in text, f"{relative}: obsolete text remains: {needle!r}"


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


def test_binding_matrix_and_three_way_entrance_match_on_both_platforms() -> None:
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
        "Retained evidence",
        "Exact source boundary",
        "Atlas first",
    )
    _assert_all(
        "runtime",
        "Atlas-first entrance",
        "do not query or open Atlas",
        "selected curated page",
        "index fallback",
        "reverse or multi-hop",
        "coverage ends",
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


def test_discovery_entrypoints_and_outside_root_routes_require_eligibility() -> None:
    for relative in SURFACE_PAIRS["discovery_agent"]:
        description = _metadata_description(relative)
        assert "direct Ask Atlas" in description, relative
        assert "valid managed-block handoff" in description, relative

    for relative, text in zip(
        SURFACE_PAIRS["discovery_agent"],
        _texts("discovery_agent"),
        strict=True,
    ):
        eligibility = _paragraph_containing(text, "Proceed only after direct Ask Atlas")
        assert "valid managed Atlas block" in eligibility, relative
        assert "matched" in eligibility, relative
        assert "path-derived" in eligibility, relative
        assert "not-verified" in eligibility, relative
        assert "otherwise do not query Atlas" in eligibility, relative

    outside_markers = (
        "For ordinary product questions outside `ATLAS_ROOT`",
        "Outside `ATLAS_ROOT`",
    )
    for relative, text, marker in zip(
        SURFACE_PAIRS["runtime"], _texts("runtime"), outside_markers, strict=True
    ):
        outside_route = _paragraph_containing(text, marker)
        assert "direct Ask Atlas" in outside_route, relative
        assert "valid managed Atlas block" in outside_route, relative
        assert "matched" in outside_route, relative
        assert "path-derived" in outside_route, relative
        assert "not-verified" in outside_route, relative
        assert "unbound repository" in outside_route, relative
        assert "do not query Atlas" in outside_route, relative


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


def test_discovery_agent_classifications_use_only_the_four_answer_labels() -> None:
    expected = {"Atlas", "Repository (located via Atlas)", "Inference", "Unresolved"}
    evidence_rule = (
        "User confirmation, conflict, and external artifacts remain evidence "
        "or state beneath those labels"
    )
    for relative, text in zip(
        SURFACE_PAIRS["discovery_agent"], _texts("discovery_agent"), strict=True
    ):
        declaration = re.search(
            r"Classify every material claim as (?P<labels>.+?)\.", text
        )
        assert declaration, relative
        labels = set(re.findall(r"\*\*([^*]+)\*\*", declaration["labels"]))
        assert labels == expected, relative
        assert evidence_rule in text, relative
        assert "separately label repository-derived" not in text, relative


def test_direct_ask_and_flow_synthesis_are_complete_on_parent_and_delegate() -> None:
    direct_ask_terms = (
        "relevant curated types",
        "answer-bearing links",
        "all supported material",
        "answer",
        "smallest next evidence location",
        "unresolved boundary",
    )
    flow_terms = (
        "trigger and outcome",
        "start and end boundaries",
        "system boundaries",
        "ordered participants and handoffs",
        "data and infrastructure transitions",
        "conditional, retry, and failure paths",
        "standards, incidents, and runbooks",
        "coverage limits",
    )
    for surface in ("discover", "discovery_agent"):
        for relative, text in zip(SURFACE_PAIRS[surface], _texts(surface), strict=True):
            direct_ask = _paragraph_containing(text, "Direct Ask Atlas")
            for term in direct_ask_terms:
                assert term in direct_ask, f"{relative}: missing {term!r}"
            flow = _paragraph_containing(text, "For a flow")
            for term in flow_terms:
                assert term in flow, f"{relative}: missing {term!r}"


def test_session_reuse_and_bounded_reentry_are_paired() -> None:
    for surface in ("runtime", "handoffs"):
        _assert_all(
            surface,
            "ephemeral Atlas session",
            "Reuse",
            "Re-enter",
            "coverage endpoint",
        )


def test_uncertain_atlas_evidence_never_becomes_a_confirmed_claim() -> None:
    uncertainty_terms = (
        "possible, unconfirmed, or conflicting",
        "never promote",
        "definitive, executable, or complete claim",
        "qualify the claim",
        "smallest source verification",
        "precisely the uncertain edge",
        "external targets and unknown coverage",
        "separate states",
    )
    for surface in (
        "provenance",
        "discover",
        "impact",
        "discovery_agent",
        "impact_agent",
    ):
        _assert_all(surface, *uncertainty_terms)

    _assert_all(
        "provenance",
        "Curated page authority never upgrades an individual field or edge confidence",
    )
    for surface in ("discover", "impact"):
        _assert_all(
            surface,
            "Curated page authority never upgrades an individual field or edge confidence",
        )

    _assert_all(
        "managed_block",
        "possible, unconfirmed, or conflicting",
        "external targets and unknown coverage",
        "separate states",
    )


def test_complete_flow_and_readiness_require_fallback_at_uncertain_coverage() -> None:
    fallback_terms = (
        "complete flow or readiness",
        "partial or uncertain",
        "bounded source fallback",
        "missing flow edge",
    )
    for surface in ("discover", "impact", "discovery_agent", "impact_agent"):
        _assert_all(surface, *fallback_terms)


def test_session_revision_compatibility_and_warm_call_reuse_are_explicit() -> None:
    _assert_all(
        "runtime",
        "ephemeral Atlas session state",
        "requested revision or range",
        "resolved full commit or range",
        "revision used for each inspected source path",
        "repository, revision, question type and required confidence",
        "retained-context",
        "source-only",
        "atlas-only",
        "atlas-plus-source",
        "unresolved",
        "Git at that revision",
        "never becomes historical evidence",
        "Full ordered access events belong only in Atlas routing evaluation artifacts",
        "independent Atlas reads",
        "batch Atlas-located source verification",
        "selected IDs and already-opened pages",
    )
    _assert_ordered(
        "runtime",
        "Retained evidence",
        "Exact source boundary",
        "Atlas first",
    )
    _assert_all(
        "handoffs",
        "requested revision or range",
        "resolved full commit or range",
        "source paths and their revisions",
        "route class",
        "coverage endpoint",
        "Batch independent Atlas reads",
        "batch Atlas-located source verification",
    )
    _assert_all(
        "managed_block",
        "retained context",
        "already-opened pages",
        "requested revision",
        "resolved commit",
    )
    for surface in ("runtime", "handoffs", "managed_block"):
        _assert_absent(surface, "ephemeral ordered access ledger")


def test_curated_trust_docs_use_deprecated_not_historical() -> None:
    for relative in ("_curated/README.md", "_curated/maps/README.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        trust_paragraph = _paragraph_containing(text, "deprecated content")
        assert "deprecated" in trust_paragraph, relative
        assert "historical" not in trust_paragraph, relative


def test_verified_source_evidence_can_satisfy_a_follow_up_without_retrieval() -> None:
    reuse_terms = (
        "already verified repository evidence",
        "zero new retrieval",
        "original Atlas edge was possible",
        "supports every material follow-up claim",
        "required confidence",
        "related evidence must not upgrade a different uncertain edge",
    )
    for surface in ("runtime", "provenance", "discover", "impact"):
        _assert_all(surface, *reuse_terms)


def test_exact_volatile_values_remain_source_authoritative() -> None:
    exact_terms = (
        "exact volatile values",
        "source-authoritative",
        "commands, code, configuration, and IaC literals",
    )
    for surface in ("runtime", "provenance", "discover", "impact"):
        for relative, text in zip(SURFACE_PAIRS[surface], _texts(surface), strict=True):
            lowered = text.lower()
            for term in exact_terms:
                assert term.lower() in lowered, f"{relative}: missing {term!r}"


def test_documented_flows_do_not_become_executable_wiring() -> None:
    wiring_terms = (
        "documentation alone supports documented or intended behavior",
        "does not confirm executable or deployed wiring",
        "current executable or deployed evidence appropriate to the boundary",
        "code, configuration, IaC, tests, or runtime/control-plane state",
    )
    for surface in (
        "provenance",
        "discover",
        "impact",
        "discovery_agent",
        "impact_agent",
    ):
        _assert_all(surface, *wiring_terms)


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


def test_exact_change_guard_checks_immutable_history_and_net_zero_ranges() -> None:
    rollback_terms = (
        "referenced immutable evidence",
        "exact-range Git diff and history",
        "per-commit inspection",
        "endpoint state is empty",
        "empty endpoint diff or current file does not prove no change",
        "add-then-revert",
        "net-zero",
    )
    for surface in ("impact", "impact_agent"):
        for relative, text in zip(SURFACE_PAIRS[surface], _texts(surface), strict=True):
            exact_change = _paragraph_containing(text, "For an exact-change prompt")
            for term in rollback_terms:
                assert term in exact_change, f"{relative}: missing {term!r}"


def test_managed_block_is_binding_signal_and_exposes_risk_triggers() -> None:
    _assert_all(
        "managed_block",
        "Presence of this managed block binds this repository to Atlas",
        "uncertain, broad, multi-hop, Git-history",
        "durable-context",
        "impact, ownership, standards, recovery or readiness",
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

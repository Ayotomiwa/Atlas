from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
AGENTS = ROOT / ".claude" / "agents"

EXPECTED = {
    "atlas-repo-analyst": {
        "file": "atlas-repo-analyst.md",
        "tools": {"Read", "Grep", "Glob", "Bash"},
        "permission_mode": "plan",
        "must_contain": ["service-onboarding", "standards-discovery", "structured evidence matrix"],
    },
    "atlas-curator": {
        "file": "atlas-curator.md",
        "tools": {"Read", "Grep", "Glob", "Bash", "Write", "Edit"},
        "permission_mode": "default",
        "must_contain": ["status: proposed", "README.md", "_template.md", "index.md", "rebuild_maps.py"],
    },
    "atlas-impact-analyst": {
        "file": "atlas-impact-analyst.md",
        "tools": {"Read", "Grep", "Glob"},
        "permission_mode": "plan",
        "must_contain": ["known affected", "possibly affected", "unknown or not covered", "Absence of an edge"],
    },
    "atlas-reviewer": {
        "file": "atlas-reviewer.md",
        "tools": {"Read", "Grep", "Glob"},
        "permission_mode": "plan",
        "must_contain": ["BLOCKER", "MAJOR", "MINOR", "QUESTION", "approve on behalf of a human"],
    },
}


def parse_agent(path: Path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} must start with YAML frontmatter"
    _, frontmatter, body = text.split("---", 2)
    return yaml.safe_load(frontmatter), body


def tool_set(value):
    if isinstance(value, str):
        return {item.strip() for item in value.split(",") if item.strip()}
    return set(value or [])


def test_exact_v1_agent_set_exists():
    actual = {path.name for path in AGENTS.glob("*.md")}
    expected = {spec["file"] for spec in EXPECTED.values()}
    assert actual == expected


def test_agents_follow_anthropic_frontmatter_and_v1_boundaries():
    for expected_name, spec in EXPECTED.items():
        meta, body = parse_agent(AGENTS / spec["file"])

        assert meta["name"] == expected_name
        assert isinstance(meta.get("description"), str) and meta["description"].strip()
        assert "allowed-tools" not in meta
        assert tool_set(meta.get("tools")) == spec["tools"]
        assert meta.get("model") == "inherit"
        assert meta.get("permissionMode") == spec["permission_mode"]
        assert "memory" not in meta
        assert "skills" not in meta
        assert "bypassPermissions" not in str(meta)

        for phrase in spec["must_contain"]:
            assert phrase.lower() in body.lower(), f"{expected_name} missing required prompt detail: {phrase}"


def test_read_only_agents_cannot_write():
    for name in ("atlas-repo-analyst", "atlas-impact-analyst", "atlas-reviewer"):
        meta, _ = parse_agent(AGENTS / EXPECTED[name]["file"])
        tools = tool_set(meta["tools"])
        assert "Write" not in tools
        assert "Edit" not in tools
        assert meta["permissionMode"] == "plan"


def test_curator_can_propose_but_not_approve_or_merge():
    meta, body = parse_agent(AGENTS / EXPECTED["atlas-curator"]["file"])
    tools = tool_set(meta["tools"])
    assert {"Write", "Edit"}.issubset(tools)
    lowered = body.lower()
    assert "set a page to `status: curated`" in lowered
    assert "merge a branch or pr/mr" in lowered
    assert "human review" in lowered

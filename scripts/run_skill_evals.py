#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.frontmatter import parse_frontmatter

EXPECTED = [
    "atlas-discover",
    "atlas-impact",
    "atlas-stage",
    "atlas-onboard-service",
    "atlas-onboard-standards",
    "atlas-setup-repo",
    "atlas-curate",
    "implement-jira",
]
EXPECTED_TOOLS = {
    "atlas-discover": {"Read", "Grep", "Glob"},
    "atlas-impact": {"Read", "Grep", "Glob"},
    "atlas-stage": {"Read", "Grep", "Glob", "Write", "Edit"},
    "atlas-onboard-service": {"Read", "Grep", "Glob", "Bash", "Write", "Edit"},
    "atlas-onboard-standards": {"Read", "Grep", "Glob", "Bash", "Write", "Edit"},
    "atlas-setup-repo": {"Read", "Grep", "Glob", "Write", "Edit"},
    "atlas-curate": {"Read", "Grep", "Glob", "Bash", "Write", "Edit"},
    "implement-jira": {"Read", "Grep", "Glob", "Bash", "Write", "Edit"},
}
REQUIRED_EVAL_KEYS = {
    "should_trigger",
    "should_not_trigger",
    "expected_reads",
    "expected_writes",
    "forbidden_writes",
    "forbidden_actions",
    "outcome_assertions",
    "text_must_contain",
}


def _tools(value: object) -> set[str]:
    if isinstance(value, str):
        return {part.strip() for part in value.split(",") if part.strip()}
    if isinstance(value, list):
        return {str(part).strip() for part in value if str(part).strip()}
    return set()


def _replace_managed_block(existing: str, block: str) -> str:
    start = "<!-- atlas:managed:start -->"
    end = "<!-- atlas:managed:end -->"
    if start in existing and end in existing:
        before = existing.split(start, 1)[0]
        after = existing.split(end, 1)[1]
        return before + block + after
    separator = "" if existing.endswith("\n\n") else "\n" if existing.endswith("\n") else "\n\n"
    return existing + separator + block + "\n"


def run_deterministic() -> list[str]:
    errors: list[str] = []

    for name in EXPECTED:
        skill = ROOT / ".claude" / "skills" / name / "SKILL.md"
        eval_path = ROOT / "tests" / "skill-evals" / f"{name}.yaml"
        if not skill.exists():
            errors.append(f"missing skill {name}")
            continue
        try:
            fm, body = parse_frontmatter(skill)
        except Exception as exc:
            errors.append(f"{name} frontmatter invalid: {exc}")
            continue
        if fm.get("name") != name:
            errors.append(f"{name} frontmatter name mismatch")
        actual_tools = _tools(fm.get("allowed-tools"))
        if actual_tools != EXPECTED_TOOLS[name]:
            errors.append(f"{name} tools {sorted(actual_tools)} != {sorted(EXPECTED_TOOLS[name])}")
        if not eval_path.exists():
            errors.append(f"missing eval {name}")
            continue
        data = yaml.safe_load(eval_path.read_text(encoding="utf-8")) or {}
        missing = sorted(REQUIRED_EVAL_KEYS - set(data))
        if missing:
            errors.append(f"{name} eval missing keys: {', '.join(missing)}")
            continue
        for key in ("should_trigger", "should_not_trigger", "expected_reads", "forbidden_actions", "outcome_assertions", "text_must_contain"):
            if not isinstance(data.get(key), list) or not data[key]:
                errors.append(f"{name} eval {key} must be a non-empty list")
        for needle in data.get("text_must_contain") or []:
            if str(needle).lower() not in body.lower():
                errors.append(f"{name} skill missing deterministic contract text: {needle}")

    # Read-only permission boundary.
    for name in ("atlas-discover", "atlas-impact"):
        fm, _ = parse_frontmatter(ROOT / ".claude" / "skills" / name / "SKILL.md")
        if {"Write", "Edit", "Bash"} & _tools(fm.get("allowed-tools")):
            errors.append(f"{name} is not read-only")

    # Required demonstration service fixture: build metadata + separate supplied infra
    # + one deliberately unresolved flow boundary.
    service = ROOT / "tests" / "fixtures" / "valid" / "service-repo"
    infra = ROOT / "tests" / "fixtures" / "valid" / "infra"
    for path in (service / "README.md", service / "pom.xml", service / "application.yml", infra / "main.tf"):
        if not path.exists():
            errors.append(f"missing service onboarding fixture {path.relative_to(ROOT)}")
    service_readme = (service / "README.md").read_text(encoding="utf-8") if (service / "README.md").exists() else ""
    if "intentionally not stated" not in service_readme:
        errors.append("service fixture must preserve an intentionally missing flow fact")

    # Standards fixture: repeated policy-like evidence and an obvious configuration/default
    # that is insufficient by itself to prove team policy.
    standards = ROOT / "tests" / "fixtures" / "valid" / "standards"
    a = standards / "repo-a" / "CONTRIBUTING.md"
    b = standards / "repo-b" / "CONTRIBUTING.md"
    editor = standards / ".editorconfig"
    if not (a.exists() and b.exists() and editor.exists()):
        errors.append("standards fixture must include repeated CONTRIBUTING evidence and .editorconfig")
    elif a.read_text(encoding="utf-8") != b.read_text(encoding="utf-8"):
        errors.append("standards fixture repeated candidate must actually repeat across repos")

    # setup-repo safety fixture: demonstrate managed-block replacement without deleting
    # repository-owned instructions.
    local_claude = service / "CLAUDE.md"
    if local_claude.exists():
        original = local_claude.read_text(encoding="utf-8")
        block = "<!-- atlas:managed:start -->\n## Atlas context\nHome Atlas package: `teama`\n<!-- atlas:managed:end -->"
        first = _replace_managed_block(original, block)
        replacement = block.replace("`teama`", "`teama`\nAtlas component: `unresolved`")
        second = _replace_managed_block(first, replacement)
        for preserved in ("Keep this non-Atlas instruction.", "Run local tests before proposing a change."):
            if preserved not in second:
                errors.append(f"atlas-setup-repo fixture lost existing content: {preserved}")
        if second.count("<!-- atlas:managed:start -->") != 1 or second.count("<!-- atlas:managed:end -->") != 1:
            errors.append("atlas-setup-repo fixture did not replace exactly one managed block")
    else:
        errors.append("missing existing CLAUDE.md setup-repo fixture")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deterministic", action="store_true")
    args = parser.parse_args(argv)
    if not args.deterministic:
        print("Model-trigger skill evaluation is a documented/manual harness in V1; use --deterministic for offline checks.")
        return 0
    errors = run_deterministic()
    if errors:
        print("\n".join(errors))
        return 1
    print("Deterministic skill evals passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

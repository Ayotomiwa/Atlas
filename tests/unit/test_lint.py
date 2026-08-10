from __future__ import annotations

from datetime import date
from pathlib import Path
import os
import shutil
import subprocess

import yaml

from scripts.atlas_lint import lint_repository
from scripts.lib.frontmatter import parse_frontmatter

ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "tests" / "fixtures" / "valid" / "curated-pages"
INVALID = ROOT / "tests" / "fixtures" / "invalid"

CURATED_DESTINATIONS = {
    "component.md": "_curated/components/component.md",
    "flow.md": "_curated/flows/flow.md",
    "infra.md": "_curated/infra/infra.md",
    "schema-info.md": "_curated/schema-info/schema-info.md",
    "business-concept.md": "_curated/business-concepts/business-concept.md",
    "standard.md": "_curated/standards/java/standard.md",
    "runbook.md": "_curated/runbooks/runbook.md",
    "incident-learning.md": "_curated/incidents/incident-learning.md",
}


def _base_root(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "taxonomy", tmp_path / "taxonomy")
    return tmp_path


def _write_index_for_type(root: Path, page: Path, typ: str, *, include: bool = True) -> Path:
    specs = {item["name"]: item for item in yaml.safe_load((root / "taxonomy" / "types.yaml").read_text())["types"]}
    if typ == "atlas.standard":
        index = page.parent / "index.md"
    else:
        index = root / specs[typ]["folder"] / "index.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    if include:
        relative = Path(os.path.relpath(page, index.parent)).as_posix()
        index.write_text(f"# Fixture index\n\n[Fixture page]({relative})\n", encoding="utf-8")
    else:
        index.write_text("# Fixture index\n\nNo entries.\n", encoding="utf-8")
    return index


def _install_page(root: Path, source: Path, destination: str, *, include_index: bool = True) -> Path:
    dest = root / destination
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    try:
        fm, _ = parse_frontmatter(dest)
    except Exception:
        return dest
    typ = fm.get("type")
    if isinstance(typ, str) and typ.startswith("atlas.") and not typ.startswith("atlas.staging.") and typ not in {"atlas.decision", "atlas.join-path", "atlas.query-pattern"}:
        specs = {item["name"]: item for item in yaml.safe_load((root / "taxonomy" / "types.yaml").read_text())["types"]}
        if typ in specs:
            _write_index_for_type(root, dest, typ, include=include_index)
    return dest


def _codes(issues: list[dict[str, str]]) -> set[str]:
    return {item["code"] for item in issues}


def _write_staging_fixture(root: Path) -> Path:
    staging = root / "_staging/components/STG-20260807-fixture.md"
    staging.parent.mkdir(parents=True, exist_ok=True)
    staging.write_text(
        """---
id: STG-20260807-fixture
type: atlas.staging.component
package: fixtures
timestamp: 2026-08-07
title: Fixture evidence
description: Synthetic
status: new
captured_by: fixture
source_type: test
---

## Summary
Original fixture evidence.
""",
        encoding="utf-8",
    )
    return staging


def _init_git(root: Path) -> str:
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "fixture@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Fixture"], check=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "baseline"], check=True)
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def test_canonical_repository_structure_and_contract_counts():
    required = {
        "README.md",
        "CLAUDE.md",
        "package.md",
        "index.md",
        "log.md",
        "CODEOWNERS",
        ".gitignore",
        "pyproject.toml",
        ".gitlab-ci.yml",
        ".github/workflows/atlas-ci.yml",
        "taxonomy/README.md",
        "taxonomy/types.yaml",
        "taxonomy/relationships.yaml",
        "taxonomy/statuses.yaml",
        "taxonomy/maps.yaml",
        "taxonomy/standard-categories.yaml",
        "_curated/README.md",
        "_curated/index.md",
        "_curated/maps/flow-component/flow-component-map.json",
        "_curated/maps/repo-dependency/repo-dependency-map.json",
        "_curated/maps/infra-dependency/infra-dependency-map.json",
        "_curated/maps/flow-component/README.md",
        "_curated/maps/repo-dependency/README.md",
        "_curated/maps/infra-dependency/README.md",
        "_curated/status/curation-status.md",
        "_staging/README.md",
        "_staging/index.md",
        "onboarding/README.md",
        "onboarding/index.md",
        "onboarding/service-questionnaire.md",
        "onboarding/standards-questionnaire.md",
        "onboarding/local-CLAUDE.template.md",
        "scripts/atlas_lint.py",
        "scripts/rebuild_maps.py",
        "scripts/lib/__init__.py",
        "scripts/lib/frontmatter.py",
        "scripts/lib/taxonomy.py",
        "scripts/lib/ids.py",
        "scripts/lib/links.py",
        "scripts/lib/maps.py",
    }
    curated = ["components", "flows", "infra", "schema-info", "business-concepts", "standards", "runbooks", "incidents"]
    staging = ["changes", "components", "flows", "infra", "schema-info", "business-concepts", "incidents", "runbooks", "standards"]
    for area in curated:
        required.update({f"_curated/{area}/README.md", f"_curated/{area}/index.md", f"_curated/{area}/_template.md"})
    for area in staging:
        required.update({f"_staging/{area}/README.md", f"_staging/{area}/_template.md"})
    for category in ["general", "java", "python", "aws", "infra", "jira", "data", "testing", "git"]:
        required.add(f"_curated/standards/{category}/index.md")
    for skill in ["atlas-discover", "atlas-impact", "atlas-stage", "atlas-onboard-service", "atlas-onboard-standards", "atlas-setup-repo", "atlas-curate", "implement-jira"]:
        required.add(f".claude/skills/{skill}/SKILL.md")
    for agent in ["atlas-repo-analyst", "atlas-curator", "atlas-impact-analyst", "atlas-reviewer"]:
        required.add(f".claude/agents/{agent}.md")
    missing = sorted(path for path in required if not (ROOT / path).exists())
    assert not missing, f"missing canonical files: {missing}"
    assert not (ROOT / "reviews").exists(), "V1 uses Atlas PR/MR history rather than a duplicate reviews/ folder"
    assert len(list((ROOT / ".claude" / "skills").glob("*/SKILL.md"))) == 8
    assert len(list((ROOT / ".claude" / "agents").glob("*.md"))) == 4
    for area in staging:
        assert not (ROOT / "_staging" / area / "index.md").exists(), f"staging bucket {area} must not have an index"


def test_staging_lifecycle_statuses_are_exact():
    statuses = yaml.safe_load((ROOT / "taxonomy/statuses.yaml").read_text(encoding="utf-8"))
    assert statuses["staging_status"] == ["new", "curating", "curated", "no-change", "deferred", "rejected"]


def test_real_scaffold_contains_no_fabricated_teama_concept_or_staging_pages():
    curated_pages = [
        p
        for p in (ROOT / "_curated").rglob("*.md")
        if p.name not in {"README.md", "index.md", "_template.md", "curation-status.md"}
        and "maps" not in p.parts
    ]
    staging_pages = [
        p
        for p in (ROOT / "_staging").rglob("*.md")
        if p.name not in {"README.md", "index.md", "_template.md"}
    ]
    assert curated_pages == []
    assert staging_pages == []


def test_repository_lint_is_clean():
    issues = lint_repository(ROOT, today=date(2026, 8, 7))
    assert issues == []


def test_valid_fixture_exists_for_every_active_curated_concept_type(tmp_path: Path):
    root = _base_root(tmp_path)
    for source_name, destination in CURATED_DESTINATIONS.items():
        _install_page(root, VALID / source_name, destination)
    issues = lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
    assert issues == []


def test_lint_reads_package_identity_from_package_md(tmp_path: Path):
    root = _base_root(tmp_path)
    (root / "package.md").write_text(
        """---
id: atlas-package.fixtures
type: atlas.package
package: fixtures
schema_version: atlas/1.0
title: Fixture Atlas
description: Synthetic package.
status: active
maps:
  flow_component: _curated/maps/flow-component/flow-component-map.json
  repo_dependency: _curated/maps/repo-dependency/repo-dependency-map.json
  infra_dependency: _curated/maps/infra-dependency/infra-dependency-map.json
---
""",
        encoding="utf-8",
    )
    _install_page(root, VALID / "component.md", "_curated/components/component.md")
    issues = lint_repository(root, check_maps=False, today=date(2026, 8, 7))
    assert "ATLAS004" not in _codes(issues), issues


def test_atlas001_frontmatter_failure(tmp_path: Path):
    root = _base_root(tmp_path)
    _install_page(root, INVALID / "ATLAS001-missing-frontmatter.md", "_curated/components/bad.md")
    assert "ATLAS001" in _codes(lint_repository(root, package_name="fixtures", check_maps=False))


def test_atlas002_folder_type_failure_is_single_purpose(tmp_path: Path):
    root = _base_root(tmp_path)
    page = _install_page(root, INVALID / "ATLAS002-wrong-type.md", "_curated/components/bad.md")
    fm, _ = parse_frontmatter(page)
    _write_index_for_type(root, page, fm["type"], include=True)
    issues = lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
    assert _codes(issues) == {"ATLAS002"}


def test_atlas003_bad_id_and_duplicate_id(tmp_path: Path):
    root = _base_root(tmp_path)
    _install_page(root, INVALID / "ATLAS003-bad-id.md", "_curated/components/bad.md")
    assert "ATLAS003" in _codes(lint_repository(root, package_name="fixtures", check_maps=False))

    root2 = _base_root(tmp_path / "dup")
    first = _install_page(root2, VALID / "component.md", "_curated/components/one.md")
    second = _install_page(root2, VALID / "component.md", "_curated/components/two.md")
    index = root2 / "_curated/components/index.md"
    index.write_text("# Index\n\n[One](one.md)\n[Two](two.md)\n", encoding="utf-8")
    assert first.exists() and second.exists()
    assert "ATLAS003" in _codes(lint_repository(root2, package_name="fixtures", check_maps=False))


def test_atlas004_wrong_package(tmp_path: Path):
    root = _base_root(tmp_path)
    _install_page(root, INVALID / "ATLAS004-wrong-package.md", "_curated/components/bad.md")
    assert "ATLAS004" in _codes(lint_repository(root, package_name="fixtures", check_maps=False))


def test_atlas005_reserved_type(tmp_path: Path):
    root = _base_root(tmp_path)
    _install_page(root, INVALID / "ATLAS005-reserved-type.md", "_curated/decisions/bad.md")
    assert _codes(lint_repository(root, package_name="fixtures", check_maps=False)) == {"ATLAS005"}


def test_atlas006_and_atlas007_status_rules(tmp_path: Path):
    root = _base_root(tmp_path)
    _install_page(root, INVALID / "ATLAS006-bad-status.md", "_curated/components/bad.md")
    assert "ATLAS006" in _codes(lint_repository(root, package_name="fixtures", check_maps=False))

    root2 = _base_root(tmp_path / "review")
    _install_page(root2, INVALID / "ATLAS007-missing-reviewer.md", "_curated/components/bad.md")
    assert "ATLAS007" in _codes(lint_repository(root2, package_name="fixtures", check_maps=False))


def test_atlas008_broken_link(tmp_path: Path):
    root = _base_root(tmp_path)
    shutil.copy2(INVALID / "ATLAS008-broken-link.md", root / "notes.md")
    assert _codes(lint_repository(root, package_name="fixtures", check_maps=False)) == {"ATLAS008"}


def test_atlas009_to_atlas012_relationship_rules(tmp_path: Path):
    cases = {
        "ATLAS009": "ATLAS009-bad-relationship.md",
        "ATLAS010": "ATLAS010-missing-target.md",
        "ATLAS011": "ATLAS011-missing-kind.md",
        "ATLAS012": "ATLAS012-missing-note.md",
    }
    for code, fixture in cases.items():
        case_root = _base_root(tmp_path / code)
        _install_page(case_root, INVALID / fixture, "_curated/components/bad.md")
        issues = lint_repository(case_root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
        assert code in _codes(issues), f"{code}: {issues}"


def test_atlas013_and_atlas014_index_rules(tmp_path: Path):
    root = _base_root(tmp_path)
    _install_page(root, INVALID / "ATLAS013-not-indexed.md", "_curated/components/not-indexed.md", include_index=False)
    assert "ATLAS013" in _codes(lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7)))

    root2 = _base_root(tmp_path / "archived")
    _install_page(root2, INVALID / "ATLAS014-archived-indexed.md", "_curated/components/archived.md", include_index=True)
    assert "ATLAS014" in _codes(lint_repository(root2, package_name="fixtures", check_maps=False, today=date(2026, 8, 7)))


def test_atlas015_atlas016_and_atlas017_content_rules(tmp_path: Path):
    cases = [
        ("ATLAS015", "ATLAS015-missing-evidence.md", "_curated/components/bad.md"),
        ("ATLAS016", "ATLAS016-empty-section.md", "_curated/components/bad.md"),
        ("ATLAS017", "ATLAS017-category-mismatch.md", "_curated/standards/java/bad.md"),
    ]
    for code, fixture, destination in cases:
        case_root = _base_root(tmp_path / code)
        _install_page(case_root, INVALID / fixture, destination)
        issues = lint_repository(case_root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
        assert code in _codes(issues), f"{code}: {issues}"


def test_atlas018_detects_missing_or_drifted_generated_maps(tmp_path: Path):
    root = _base_root(tmp_path)
    issues = lint_repository(root, package_name="fixtures", check_maps=True)
    assert "ATLAS018" in _codes(issues)


def test_atlas019_detects_synthetic_secret_pattern(tmp_path: Path):
    root = _base_root(tmp_path)
    shutil.copy2(INVALID / "ATLAS019-synthetic-secret-pattern.txt", root / "config.txt")
    assert _codes(lint_repository(root, package_name="fixtures", check_maps=False)) == {"ATLAS019"}


def test_atlas020_stale_review_warning(tmp_path: Path):
    root = _base_root(tmp_path)
    page = _install_page(root, VALID / "component.md", "_curated/components/stale.md")
    text = page.read_text(encoding="utf-8").replace("last_reviewed: '2026-08-07'", "last_reviewed: '2025-01-01'")
    page.write_text(text, encoding="utf-8")
    issues = lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
    assert any(item["code"] == "ATLAS020" and item["level"] == "WARN" for item in issues)


def test_atlas021_existing_staging_evidence_rejects_non_status_edits(tmp_path: Path):
    root = _base_root(tmp_path)
    staging = _write_staging_fixture(root)
    base = _init_git(root)
    staging.write_text(staging.read_text(encoding="utf-8") + "Modified after capture.\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", str(staging.relative_to(root))], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "modify staging evidence"], check=True)
    issues = lint_repository(root, package_name="fixtures", check_maps=False, git_base=base, today=date(2026, 8, 7))
    assert "ATLAS021" in _codes(issues)


def test_atlas021_allows_status_only_staging_lifecycle_change(tmp_path: Path):
    root = _base_root(tmp_path)
    staging = _write_staging_fixture(root)
    base = _init_git(root)
    text = staging.read_text(encoding="utf-8").replace("status: new", "status: curated")
    staging.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", str(staging.relative_to(root))], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "advance staging status"], check=True)
    issues = lint_repository(root, package_name="fixtures", check_maps=False, git_base=base, today=date(2026, 8, 7))
    assert "ATLAS021" not in _codes(issues)
    assert "ATLAS006" not in _codes(issues)


def test_atlas021_rejects_status_plus_evidence_edit(tmp_path: Path):
    root = _base_root(tmp_path)
    staging = _write_staging_fixture(root)
    base = _init_git(root)
    text = staging.read_text(encoding="utf-8").replace("status: new", "status: curated")
    staging.write_text(text + "Also changed evidence.\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", str(staging.relative_to(root))], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "bad status and evidence edit"], check=True)
    issues = lint_repository(root, package_name="fixtures", check_maps=False, git_base=base, today=date(2026, 8, 7))
    assert "ATLAS021" in _codes(issues)


def test_atlas022_warns_when_component_deployment_has_no_infra_evidence(tmp_path: Path):
    root = _base_root(tmp_path)
    page = _install_page(root, VALID / "component.md", "_curated/components/component.md")
    text = page.read_text(encoding="utf-8").replace("deployed_as: []", "deployed_as:\n- fixture-missing-stack")
    page.write_text(text, encoding="utf-8")
    issues = lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
    assert any(item["code"] == "ATLAS022" and item["level"] == "WARN" for item in issues)


def test_atlas023_validates_structured_flow_entry_points(tmp_path: Path):
    root = _base_root(tmp_path)
    page = _install_page(root, VALID / "flow.md", "_curated/flows/flow.md")
    text = page.read_text(encoding="utf-8").replace(
        "trigger: test",
        "entry_points:\n- kind: invented\n  name: Fixture trigger\n  confidence: reviewed\n  evidence: [fixture://trigger]\ntrigger: test",
    )
    page.write_text(text, encoding="utf-8")
    issues = lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
    assert "ATLAS023" in _codes(issues)


def test_atlas023_requires_structured_promoted_resources(tmp_path: Path):
    root = _base_root(tmp_path)
    page = _install_page(root, VALID / "infra.md", "_curated/infra/infra.md")
    text = page.read_text(encoding="utf-8").replace(
        "promoted_resources: []", "promoted_resources:\n- fixture-resource"
    )
    page.write_text(text, encoding="utf-8")
    issues = lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
    assert "ATLAS023" in _codes(issues)


def test_atlas024_rejects_relationship_outside_its_map_contract(tmp_path: Path):
    root = _base_root(tmp_path)
    page = _install_page(root, VALID / "component.md", "_curated/components/component.md")
    text = page.read_text(encoding="utf-8").replace(
        "relationships: []",
        "relationships:\n- type: atlas.triggers\n  target: external.fixture.flow\n  kind: event\n  confidence: reviewed\n  evidence: [fixture://relationship]",
    )
    page.write_text(text, encoding="utf-8")
    issues = lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
    assert "ATLAS024" in _codes(issues)


def test_reviewed_relationships_resolve_embedded_resource_ids(tmp_path: Path):
    root = _base_root(tmp_path)
    projection = ROOT / "tests" / "fixtures" / "valid" / "map-projection"
    destinations = {
        "component.md": "_curated/components/component.md",
        "library.md": "_curated/components/library.md",
        "flow.md": "_curated/flows/flow.md",
        "upstream-flow.md": "_curated/flows/upstream-flow.md",
        "infra.md": "_curated/infra/infra.md",
        "schema-info.md": "_curated/schema-info/schema-info.md",
    }
    for source_name, destination in destinations.items():
        _install_page(root, projection / source_name, destination)
    issues = lint_repository(root, package_name="fixtures", check_maps=False, today=date(2026, 8, 7))
    assert "ATLAS010" not in _codes(issues), issues

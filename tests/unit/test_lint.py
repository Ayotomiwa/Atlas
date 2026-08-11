from __future__ import annotations

from pathlib import Path
import json
import shutil

import yaml

from scripts.atlas_lint import lint_repository

ROOT = Path(__file__).resolve().parents[2]


def _root(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "taxonomy", tmp_path / "taxonomy")
    shutil.copytree(ROOT / "contracts", tmp_path / "contracts")
    manifest = {
        "schema_version": "atlas-package/1.0",
        "id": "package.fixtures",
        "type": "package",
        "package": "fixtures",
        "title": "Fixture Atlas",
        "description": "Synthetic validation fixture.",
        "status": "active",
        "owners": {},
        "aliases": ["fixtures"],
        "domains": [
            {
                "id": "test",
                "title": "Test",
                "aliases": [],
                "routing_description": "Synthetic test records.",
            }
        ],
        "entrypoints": {"root": "index.md"},
        "maps": {
            "flow_component": "_curated/maps/flow-component/flow-component-map.json",
            "repository_component": "_curated/maps/repository-component/repository-component-map.json",
            "infra_dependency": "_curated/maps/infra-dependency/infra-dependency-map.json",
        },
        "taxonomy": {
            "types": "taxonomy/types.yaml",
            "statuses": "taxonomy/statuses.yaml",
            "standard_categories": "taxonomy/standard-categories.yaml",
            "concept_fields": "taxonomy/concept-fields.yaml",
        },
        "contracts": {"map_fields": "contracts/map-fields.yaml"},
    }
    (tmp_path / "atlas-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def _common(identifier: str, typ: str) -> dict:
    return {
        "id": identifier,
        "type": typ,
        "package": "fixtures",
        "schema_version": "atlas/1.0",
        "title": identifier,
        "description": "Synthetic record.",
        "status": "proposed",
        "last_reviewed": "2026-08-11",
        "reviewed_by": [],
        "owners": [],
        "routing": {"aliases": []},
        "evidence": ["fixture://record"],
        "coverage": {"level": "partial", "notes": []},
    }


def _repository(identifier: str, parent: str | None = None) -> dict:
    return {
        **_common(identifier, "repository"),
        "primary_domain": "test",
        "related_domains": [],
        "repository_locator": "https://example.invalid/repository",
        "repository_root": ".",
        "repository_type": "standalone",
        "default_branch": "main",
        "parent_repository": parent,
        "source_roots": [],
        "depends_on_repositories": [],
        "runbooks": [],
        "standards": [],
        "incident_learnings": [],
    }


def _write(root: Path, relative: str, frontmatter: dict, body: str = "") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body
    path.write_text(rendered, encoding="utf-8")
    return path


def _codes(issues: list[dict[str, str]]) -> set[str]:
    return {item["code"] for item in issues}


def test_lint_accepts_current_frontmatter_and_relative_links(tmp_path: Path):
    root = _root(tmp_path)
    _write(root, "_curated/repositories/test/repo.md", _repository("repo.fixture"))
    (root / "notes.md").write_text(
        "[Repository](_curated/repositories/test/repo.md)\n", encoding="utf-8"
    )

    assert lint_repository(root) == []


def test_lint_reports_frontmatter_trust_and_broken_links(tmp_path: Path):
    root = _root(tmp_path)
    record = _repository("repo.fixture")
    record.update({"package": "wrong", "status": "curated", "reviewed_by": [], "evidence": []})
    _write(root, "_curated/repositories/test/repo.md", record)
    (root / "notes.md").write_text("[Missing](missing.md)\n", encoding="utf-8")

    assert {"ATLAS004", "ATLAS007", "ATLAS008"} <= _codes(lint_repository(root))


def test_lint_validates_restored_schema_and_incident_scalars(tmp_path: Path):
    root = _root(tmp_path)
    schema = {
        **_common("schema.fixture", "schema-info"),
        "primary_domain": "test",
        "related_domains": [],
        "links": [],
        "asset_type": "schema",
        "physical_name": "fixture.records",
        "platform": "fixture-platform",
        "temporal_model": "append-only",
        "classification": "internal",
    }
    incident = {
        **_common("incident.fixture", "incident-learning"),
        "links": [],
        "incident_date": "2026-08-10",
        "source_severity": "SEV-3",
    }
    _write(root, "_curated/schema-info/test/schema.md", schema)
    _write(root, "_curated/incidents/incident.md", incident)
    assert "ATLAS025" not in _codes(lint_repository(root))

    incident["incident_date"] = "10 August"
    _write(root, "_curated/incidents/incident.md", incident)
    assert "ATLAS025" in _codes(lint_repository(root))


def test_structured_errors_are_attributed_to_owning_pages(tmp_path: Path):
    root = _root(tmp_path)
    infra = {
        **_common("infra.fixture", "infra"),
        "primary_domain": "test",
        "related_domains": [],
        "infra_package": "fixture",
        "repository": None,
        "package_path": "",
        "template_path": "infra/main.tf",
        "environments": [],
        "depends_on": [],
        "uses_resources": [],
        "reads_from": [],
        "writes_to": [],
        "triggers": [],
        "scheduled_by": [],
        "imports_values": [],
        "exports_values": [],
        "permissions": [],
        "monitored_by": [],
        "deployed_by": [],
        "promoted_resources": "not-a-list",
        "runbooks": [],
        "standards": [],
        "incident_learnings": [],
    }
    _write(root, "_curated/infra/test/infra.md", infra)
    _write(root, "_curated/repositories/test/a.md", _repository("repo.a", "repo.b"))
    _write(root, "_curated/repositories/test/b.md", _repository("repo.b", "repo.a"))

    issues = [item for item in lint_repository(root) if item["code"] == "ATLAS009"]
    assert any(item["path"].endswith("infra.md") and "promoted_resources" in item["message"] for item in issues)
    cycle_issues = [item for item in issues if "hierarchy contains cycle" in item["message"]]
    assert len(cycle_issues) == 1
    assert "repo.a -> repo.b -> repo.a" in cycle_issues[0]["message"]


def test_body_shape_secrets_and_review_age_are_not_lint_rules(tmp_path: Path):
    root = _root(tmp_path)
    record = _repository("repo.fixture")
    record["last_reviewed"] = "2020-01-01"
    body = "No prescribed headings.\n\n| Wrong | Question | Table |\n\npassword=abcdefghijklmnopqrstuvwxyz\n"
    _write(root, "_curated/repositories/test/repo.md", record, body)

    assert lint_repository(root) == []

from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import sys

import yaml

from scripts.lib.generated import build_index_outputs
from scripts.lib.maps import MAP_NAMES, build_maps, stable_bytes, validate_map_frontmatter

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
        "description": "Synthetic map fixture.",
        "status": "active",
        "owners": {},
        "aliases": ["fixtures"],
        "domains": [{"id": "test", "title": "Test", "aliases": [], "routing_description": "Tests."}],
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
        "status": "curated",
        "last_reviewed": "2026-08-11",
        "reviewed_by": ["Fixture Curator"],
        "owners": [],
        "routing": {"aliases": []},
        "primary_domain": "test",
        "related_domains": [],
        "evidence": ["fixture://record"],
        "coverage": {"level": "partial", "notes": []},
    }


def _write(root: Path, relative: str, frontmatter: dict, body: str = "") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body,
        encoding="utf-8",
    )


def _coherent_root(tmp_path: Path) -> Path:
    root = _root(tmp_path)
    repository = {
        **_common("repo.fixture", "repository"),
        "repository_locator": "https://example.invalid/repository",
        "repository_root": ".",
        "repository_type": "standalone",
        "default_branch": "main",
        "parent_repository": None,
        "source_roots": [],
        "depends_on_repositories": [],
        "runbooks": [], "standards": [], "incident_learnings": [],
    }
    resource = {
        "id": "resource.fixture.bucket",
        "name": "Fixture bucket",
        "resource_type": "s3-bucket",
        "defined_in_path": "infra/main.tf",
        "environments": ["test"],
        "promotion_reason": "Directly searched data-routing boundary.",
        "confidence": "reviewed",
        "coverage": {"level": "partial", "notes": []},
        "evidence": ["infra/main.tf"],
    }
    infra = {
        **_common("infra.fixture", "infra"),
        "infra_package": "fixture",
        "repository": "repo.fixture",
        "package_path": "infra",
        "template_path": "infra/main.tf",
        "environments": ["test"],
        "depends_on": [], "uses_resources": [], "reads_from": [], "writes_to": [],
        "triggers": [], "scheduled_by": [], "imports_values": [], "exports_values": [],
        "permissions": [], "monitored_by": [], "deployed_by": [],
        "promoted_resources": [resource],
        "runbooks": [], "standards": [], "incident_learnings": [],
    }
    component = {
        **_common("comp.fixture", "component"),
        "component_type": "service",
        "repository": "repo.fixture",
        "repository_paths": ["src"],
        "parent_component": None,
        "consumes": [],
        "produces": [{
            "id": "asset.fixture.output",
            "asset_type": "table",
            "confidence": "reviewed",
            "evidence": ["src/handler.py"],
        }],
        "depends_on": [], "uses_resources": [], "reads_from": [],
        "writes_to": [{"id": "resource.fixture.bucket", "confidence": "reviewed", "evidence": ["src/config.yaml"]}],
        "triggers": [], "scheduled_by": [], "deployed_by": [], "monitored_by": [],
        "runbooks": [], "standards": [], "incident_learnings": [],
    }
    flow = {
        **_common("flow.fixture", "flow"),
        "flow_scope": "test",
        "diagram": False,
        "entry_points": [], "inputs": [], "outputs": [], "upstream_flows": [],
        "steps": [{
            "step_id": "write",
            "order": 10,
            "name": "Write fixture",
            "participant": {"type": "component", "id": "comp.fixture", "name": "Fixture component"},
            "role": "writer",
            "confidence": "reviewed",
            "evidence": ["src/handler.py"],
        }],
        "runbooks": [], "standards": [], "incident_learnings": [],
    }
    schema = {
        **_common("schema.fixture", "schema-info"),
        "links": [],
        "asset_type": "schema",
        "physical_name": "fixture",
        "platform": "fixture-platform",
        "temporal_model": "append-only",
        "classification": "internal",
        "assets": [{
            "id": "asset.fixture.output",
            "name": "fixture_output",
            "asset_type": "table",
            "physical_name": "fixture_output",
            "description": "Fixture output table.",
            "confidence": "reviewed",
            "evidence": ["models/output.sql"],
            "inputs": [{
                "name": "external_source",
                "confidence": "reviewed",
                "evidence": ["models/output.sql"],
            }],
        }],
        "conflicts": [{
            "conflict_id": "publication",
            "topic": "Output publication",
            "claims": [
                {"statement": "Documentation says automatic.", "evidence": ["README.md"]},
                {"statement": "Workflow is disabled.", "evidence": ["workflow.yml"]},
            ],
            "interpretation": "Checked-in automation is disabled.",
        }],
    }
    _write(root, "_curated/repositories/test/repo.md", repository)
    _write(root, "_curated/infra/test/infra.md", infra)
    _write(root, "_curated/components/test/component.md", component)
    _write(root, "_curated/flows/test/flow.md", flow)
    _write(root, "_curated/schema-info/test/schema.md", schema)
    return root


def test_compiles_one_coherent_sparse_fixture_with_reverse_routes(tmp_path: Path):
    maps = build_maps(_coherent_root(tmp_path))

    assert set(maps) == set(MAP_NAMES)
    repository_map = maps["repository-component-map.json"]
    infra_map = maps["infra-dependency-map.json"]
    flow_map = maps["flow-component-map.json"]
    assert repository_map["repositories"]["repo.fixture"]["components"] == ["comp.fixture"]
    assert infra_map["resources"]["resource.fixture.bucket"]["used_by"]
    assert flow_map["flows"]["flow.fixture"]["steps"][0]["participant"]["id"] == "comp.fixture"
    assert repository_map["components"]["comp.fixture"]["produces"][0]["id"] == "asset.fixture.output"
    assert "assets" not in repository_map and "assets" not in flow_map and "assets" not in infra_map
    assert all("nodes" not in payload and "edges" not in payload for payload in maps.values())


def test_frontmatter_validation_attributes_promoted_resource_and_cycle_errors(tmp_path: Path):
    root = _coherent_root(tmp_path)
    infra_path = root / "_curated/infra/test/infra.md"
    frontmatter, body = infra_path.read_text(encoding="utf-8").split("---", 2)[1:]
    data = yaml.safe_load(frontmatter)
    data["promoted_resources"] = "wrong"
    infra_path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---" + body, encoding="utf-8")

    issues = validate_map_frontmatter(root)
    assert any(issue.path.endswith("infra.md") and "promoted_resources" in issue.message for issue in issues)


def test_embedded_asset_and_conflict_errors_are_strict_and_page_attributed(tmp_path: Path):
    root = _coherent_root(tmp_path)
    schema_path = root / "_curated/schema-info/test/schema.md"
    frontmatter, body = schema_path.read_text(encoding="utf-8").split("---", 2)[1:]
    data = yaml.safe_load(frontmatter)
    data["assets"][0]["asset_type"] = "component"
    schema_path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---" + body, encoding="utf-8")

    issues = validate_map_frontmatter(root)
    assert any(
        issue.path.endswith("schema.md") and "invalid asset_type 'component'" in issue.message
        for issue in issues
    )

    data["assets"][0]["asset_type"] = "table"
    data["conflicts"][0]["claims"][1].pop("evidence")
    schema_path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---" + body, encoding="utf-8")
    issues = validate_map_frontmatter(root)
    assert any(
        issue.path.endswith("schema.md") and "conflict publication claim evidence" in issue.message
        for issue in issues
    )


def test_generation_is_deterministic_and_freshness_command_detects_missing_outputs(tmp_path: Path):
    root = _coherent_root(tmp_path)
    first = build_maps(root)
    second = build_maps(root)
    assert {name: stable_bytes(value) for name, value in first.items()} == {
        name: stable_bytes(value) for name, value in second.items()
    }

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "rebuild_atlas.py"), "--root", str(root), "--check"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1


def test_staging_candidate_domain_is_stable_in_root_and_domain_catalogues(tmp_path: Path):
    root = _root(tmp_path)
    staging = {
        "id": "STG-20260811-fixture",
        "type": "staging.component",
        "package": "fixtures",
        "timestamp": "2026-08-11",
        "title": "Fixture discovery",
        "description": "Fixture staging evidence.",
        "status": "curating",
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    _write(root, "_staging/components/test/STG-20260811-fixture.md", staging)
    outputs = build_index_outputs(root)

    root_index = outputs[root / "_staging/components/index.md"].decode("utf-8")
    domain_index = outputs[root / "_staging/components/test/index.md"].decode("utf-8")
    assert "| `test` | repository |" in root_index
    assert "| `test` | repository |" in domain_index
    assert "| `unassigned` | repository |" not in domain_index

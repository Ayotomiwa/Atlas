from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import sys

import yaml

from scripts import rebuild_atlas
from scripts.lib.generated import build_index_outputs, build_page_view_outputs, generated_index_candidates
from scripts.lib.maps import MAP_NAMES, build_maps, curated_pages, stable_bytes, validate_map_frontmatter
import scripts.lib.maps as maps_module

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


def test_relationship_type_error_lists_allowed_types_and_field_hints(tmp_path: Path):
    root = _coherent_root(tmp_path)
    component_path = root / "_curated/components/test/component.md"
    frontmatter, body = component_path.read_text(encoding="utf-8").split("---", 2)[1:]
    component = yaml.safe_load(frontmatter)
    component["writes_to"] = [{
        "id": "asset.fixture.output",
        "confidence": "reviewed",
        "evidence": ["src/config.yaml"],
    }]
    component_path.write_text(
        "---\n" + yaml.safe_dump(component, sort_keys=False) + "---" + body,
        encoding="utf-8",
    )

    issue = next(
        item for item in validate_map_frontmatter(root) if item.path.endswith("component.md")
    )

    assert "allowed target types: infra, infra-resource" in issue.message
    assert "fields accepting data-asset: consumes, produces" in issue.message


def test_confidence_error_distinguishes_claim_trust_from_coverage(tmp_path: Path):
    root = _coherent_root(tmp_path)
    component_path = root / "_curated/components/test/component.md"
    frontmatter, body = component_path.read_text(encoding="utf-8").split("---", 2)[1:]
    component = yaml.safe_load(frontmatter)
    component["writes_to"][0]["confidence"] = "partial"
    component_path.write_text(
        "---\n" + yaml.safe_dump(component, sort_keys=False) + "---" + body,
        encoding="utf-8",
    )

    issue = next(
        item for item in validate_map_frontmatter(root) if item.path.endswith("component.md")
    )

    assert "confidence describes claim trust" in issue.message
    assert "coverage describes completeness" in issue.message
    assert "allowed confidence values" in issue.message


def test_resource_coverage_error_lists_levels_and_separates_confidence(tmp_path: Path):
    root = _coherent_root(tmp_path)
    infra_path = root / "_curated/infra/test/infra.md"
    frontmatter, body = infra_path.read_text(encoding="utf-8").split("---", 2)[1:]
    infra = yaml.safe_load(frontmatter)
    infra["promoted_resources"][0]["coverage"] = {"level": "reviewed", "notes": []}
    infra_path.write_text(
        "---\n" + yaml.safe_dump(infra, sort_keys=False) + "---" + body,
        encoding="utf-8",
    )

    issue = next(item for item in validate_map_frontmatter(root) if item.path.endswith("infra.md"))

    assert "coverage describes completeness" in issue.message
    assert "confidence describes claim trust" in issue.message
    assert "allowed coverage levels" in issue.message


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


def test_shared_curated_snapshot_preserves_generated_outputs(tmp_path: Path):
    """Changing a generator to reload pages must not change its rendered output."""
    root = _coherent_root(tmp_path)
    pages = curated_pages(root)

    maps = build_maps(root, pages=pages)
    assert maps == build_maps(root)
    assert build_index_outputs(root, pages=pages) == build_index_outputs(root)
    assert build_page_view_outputs(root, compiled_maps=maps, pages=pages) == build_page_view_outputs(
        root, compiled_maps=maps
    )


def test_generated_flow_diagram_is_accessible_readable_and_semantic(tmp_path: Path):
    root = _coherent_root(tmp_path)
    flow_path = root / "_curated/flows/test/flow.md"
    frontmatter, body = flow_path.read_text(encoding="utf-8").split("---", 2)[1:]
    flow = yaml.safe_load(frontmatter)
    flow["title"] = "Fixture order route"
    flow["description"] = "Routes an order through storage, notification, and manual recovery."
    flow["diagram"] = True
    flow["steps"] = [
        {
            "step_id": "receive",
            "order": 10,
            "name": 'Receive "order" | validate',
            "participant": {"type": "component", "id": "comp.fixture", "name": "Fixture API"},
            "role": "accepts the order",
            "confidence": "reviewed",
            "evidence": ["src/handler.py"],
            "transitions": [{"to": "store", "on": "success"}],
        },
        {
            "step_id": "store",
            "order": 20,
            "name": "Store order",
            "participant": {"type": "infra", "id": "infra.fixture", "name": "Storage package"},
            "role": "persists the order",
            "confidence": "reviewed",
            "evidence": ["infra/main.tf"],
            "transitions": [
                {"to": "notify", "on": "success"},
                {"to": "recover", "on": "failure", "condition": "write fails"},
            ],
        },
        {
            "step_id": "notify",
            "order": 30,
            "name": "Notify partner",
            "participant": {"type": "external-system", "name": "Partner webhook"},
            "role": "receives the notification",
            "confidence": "reviewed",
            "evidence": ["src/handler.py"],
        },
        {
            "step_id": "recover",
            "order": 40,
            "name": "Review failed order",
            "participant": {"type": "manual", "name": "On-call engineer"},
            "role": "decides whether to retry",
            "confidence": "unconfirmed",
            "note": "The responsible role is not yet confirmed.",
            "transitions": [{"to": "store", "on": "retry"}],
        },
    ]
    flow_path.write_text(
        "---\n" + yaml.safe_dump(flow, sort_keys=False) + "---" + body,
        encoding="utf-8",
    )

    maps = build_maps(root)
    rendered = build_page_view_outputs(root, compiled_maps=maps)[flow_path].decode("utf-8")

    assert "flowchart TB" in rendered
    assert "accTitle: Fixture order route flow" in rendered
    assert "accDescr: Routes an order through storage, notification, and manual recovery." in rendered
    assert 's0["10. Receive &quot;order&quot; &#124; validate<br/>Fixture API"]' in rendered
    assert 's1[["20. Store order<br/>Storage package"]]' in rendered
    assert 's2(["30. Notify partner<br/>Partner webhook"])' in rendered
    assert 's3{{"40. Review failed order<br/>On-call engineer"}}' in rendered
    assert "s1 -->|failure: write fails| s3" in rendered
    assert "class s3 uncertain" in rendered
    assert "classDef uncertain stroke-dasharray: 5 5" in rendered
    assert "linkStyle 2,3 stroke-dasharray: 5 5" in rendered
    assert "Dashed node borders mark uncertain steps" in rendered
    assert "Dashed edges mark failure or retry paths" in rendered
    assert "\\n" not in rendered


def test_flow_diagram_flag_must_be_boolean(tmp_path: Path):
    root = _coherent_root(tmp_path)
    flow_path = root / "_curated/flows/test/flow.md"
    frontmatter, body = flow_path.read_text(encoding="utf-8").split("---", 2)[1:]
    flow = yaml.safe_load(frontmatter)
    flow["diagram"] = "true"
    flow_path.write_text(
        "---\n" + yaml.safe_dump(flow, sort_keys=False) + "---" + body,
        encoding="utf-8",
    )

    issues = validate_map_frontmatter(root)

    assert any(
        issue.path.endswith("flow.md") and "diagram must be a boolean" in issue.message
        for issue in issues
    )


def test_rebuild_loads_each_curated_page_once_and_is_deterministic(tmp_path: Path, monkeypatch):
    """A rebuild shares one parsed snapshot across maps, catalogues, and page views."""
    root = _coherent_root(tmp_path)
    pages = curated_pages(root)
    original = maps_module.parse_frontmatter
    loaded: list[object] = []

    def counting_parse(path_or_text):
        loaded.append(path_or_text)
        return original(path_or_text)

    monkeypatch.setattr(maps_module, "parse_frontmatter", counting_parse)

    first, first_diagnostics = rebuild_atlas.expected_outputs(root)
    assert len(loaded) == len(pages)
    assert all(isinstance(item, Path) for item in loaded)

    loaded.clear()
    second, second_diagnostics = rebuild_atlas.expected_outputs(root)
    assert len(loaded) == len(pages)
    assert first == second
    assert first_diagnostics == second_diagnostics


def test_rebuild_removes_obsolete_staging_queue_indexes(tmp_path: Path):
    """Former component/flow queue projections remain stale-cleanup candidates."""
    root = _root(tmp_path)
    queue_indexes = [
        root / "_staging/components/index.md",
        root / "_staging/components/unassigned/index.md",
        root / "_staging/flows/index.md",
        root / "_staging/flows/unassigned/index.md",
    ]
    generated_block = "<!-- atlas:generated-catalogue:start -->\nold queue\n<!-- atlas:generated-catalogue:end -->\n"
    for path in queue_indexes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(generated_block, encoding="utf-8")

    assert set(queue_indexes) <= generated_index_candidates(root)
    assert rebuild_atlas.main(["--root", str(root)]) == 0
    assert not any(path.exists() for path in queue_indexes)


def test_rebuild_preflight_reports_all_page_errors_and_writes_nothing(tmp_path: Path):
    root = _coherent_root(tmp_path)
    infra_path = root / "_curated/infra/test/infra.md"
    infra_frontmatter, infra_body = infra_path.read_text(encoding="utf-8").split("---", 2)[1:]
    infra = yaml.safe_load(infra_frontmatter)
    infra["promoted_resources"] = "wrong"
    infra_path.write_text(
        "---\n" + yaml.safe_dump(infra, sort_keys=False) + "---" + infra_body,
        encoding="utf-8",
    )
    repo_path = root / "_curated/repositories/test/repo.md"
    repo_frontmatter, repo_body = repo_path.read_text(encoding="utf-8").split("---", 2)[1:]
    repository = yaml.safe_load(repo_frontmatter)
    repository["repository_type"] = "wrong"
    repo_path.write_text(
        "---\n" + yaml.safe_dump(repository, sort_keys=False) + "---" + repo_body,
        encoding="utf-8",
    )
    output = root / "_curated/maps/flow-component/flow-component-map.json"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"sentinel\r\n")

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "rebuild_atlas.py"), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "_curated/infra/test/infra.md" in result.stderr
    assert "_curated/repositories/test/repo.md" in result.stderr
    assert output.read_bytes() == b"sentinel\r\n"


def test_staging_candidate_domain_is_stable_in_root_and_domain_catalogues(tmp_path: Path):
    root = _root(tmp_path)
    staging = {
        "id": "STG-20260811-fixture",
        "type": "staging.infra",
        "package": "fixtures",
        "timestamp": "2026-08-11",
        "title": "Fixture discovery",
        "description": "Fixture staging evidence.",
        "status": "curating",
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    _write(root, "_staging/infra/test/STG-20260811-fixture.md", staging)
    outputs = build_index_outputs(root)

    root_index = outputs[root / "_staging/infra/index.md"].decode("utf-8")
    domain_index = outputs[root / "_staging/infra/test/index.md"].decode("utf-8")
    assert "| `test` | repository |" in root_index
    assert "| `test` | repository |" in domain_index
    assert "| `unassigned` | repository |" not in domain_index


def test_taxonomy_grouped_staging_infra_generates_domain_queues_and_candidates(tmp_path: Path):
    root = _root(tmp_path)
    staging = {
        "id": "STG-20260817-infra-fixture",
        "type": "staging.infra",
        "package": "fixtures",
        "timestamp": "2026-08-17",
        "title": "Fixture infrastructure discovery",
        "description": "Fixture staging evidence.",
        "status": "new",
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    _write(root, "_staging/infra/test/STG-20260817-infra-fixture.md", staging)

    outputs = build_index_outputs(root)

    root_index_path = root / "_staging/infra/index.md"
    domain_index_path = root / "_staging/infra/test/index.md"
    assert "| `test` | repository |" in outputs[root_index_path].decode("utf-8")
    assert "| `test` | repository |" in outputs[domain_index_path].decode("utf-8")

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    candidates = generated_index_candidates(root)
    assert root_index_path.resolve() in candidates
    assert domain_index_path.resolve() in candidates


def test_flat_staging_infra_is_not_catalogued_but_exact_unassigned_path_is(tmp_path: Path):
    root = _root(tmp_path)
    staging = {
        "type": "staging.infra",
        "package": "fixtures",
        "timestamp": "2026-08-17",
        "description": "Fixture staging evidence.",
        "status": "new",
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    _write(
        root,
        "_staging/infra/STG-20260817-flat.md",
        {**staging, "id": "STG-20260817-flat", "title": "Flat evidence"},
    )
    _write(
        root,
        "_staging/infra/unassigned/STG-20260817-unassigned.md",
        {**staging, "id": "STG-20260817-unassigned", "title": "Unassigned evidence"},
    )

    outputs = build_index_outputs(root)

    root_index = outputs[root / "_staging/infra/index.md"].decode("utf-8")
    unassigned_index = outputs[root / "_staging/infra/unassigned/index.md"].decode("utf-8")
    assert "STG-20260817-flat" not in root_index
    assert "STG-20260817-flat" not in unassigned_index
    assert "| `STG-20260817-unassigned` | Unassigned evidence | `new` | `unassigned` |" in unassigned_index


def test_excessively_nested_staging_infra_is_not_catalogued(tmp_path: Path):
    root = _root(tmp_path)
    staging = {
        "id": "STG-20260817-nested",
        "type": "staging.infra",
        "package": "fixtures",
        "timestamp": "2026-08-17",
        "title": "Nested infrastructure evidence",
        "description": "Fixture staging evidence.",
        "status": "new",
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    _write(root, "_staging/infra/test/nested/STG-20260817-nested.md", staging)

    outputs = build_index_outputs(root)

    root_index = outputs[root / "_staging/infra/index.md"].decode("utf-8")
    domain_index = outputs[root / "_staging/infra/test/index.md"].decode("utf-8")
    assert "STG-20260817-nested" not in root_index
    assert "STG-20260817-nested" not in domain_index

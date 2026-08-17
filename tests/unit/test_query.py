from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess

import yaml

from scripts.lib.frontmatter import parse_frontmatter
from scripts import atlas_query
from scripts.lib.maps import build_maps, curated_pages, map_output_paths, stable_bytes
from scripts.lib.query import AtlasQuery
import scripts.lib.query as query_module


ROOT = Path(__file__).resolve().parents[2]


def _write(root: Path, relative: str, frontmatter: dict) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n", encoding="utf-8")
    return path


def _root(tmp_path: Path) -> tuple[Path, Path]:
    shutil.copytree(ROOT / "taxonomy", tmp_path / "taxonomy")
    shutil.copytree(ROOT / "contracts", tmp_path / "contracts")
    manifest = {
        "schema_version": "atlas-package/1.0",
        "id": "package.fixtures",
        "type": "package",
        "package": "fixtures",
        "title": "Fixture Atlas",
        "description": "Fixture.",
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
    common = {
        "package": "fixtures",
        "schema_version": "atlas/1.0",
        "status": "curated",
        "last_reviewed": "2026-08-11",
        "reviewed_by": ["Fixture Curator"],
        "owners": [],
        "routing": {"aliases": [], "keywords": []},
        "primary_domain": "test",
        "related_domains": [],
        "evidence": ["fixture://record"],
        "coverage": {"level": "partial", "notes": []},
    }
    repository = {
        **common,
        "id": "repo.fixture",
        "type": "repository",
        "title": "Fixture repository",
        "description": "Fixture source boundary.",
        "repository_locator": "https://example.invalid/fixture",
        "repository_root": ".",
        "repository_type": "standalone",
        "default_branch": "main",
        "parent_repository": None,
        "source_roots": [],
        "depends_on_repositories": [],
        "runbooks": [],
        "standards": [],
        "incident_learnings": [],
    }
    schema = {
        **common,
        "id": "schema.fixture",
        "type": "schema-info",
        "title": "Fixture schema",
        "description": "Fixture model outputs.",
        "links": [],
        "asset_type": "schema",
        "physical_name": "fixture",
        "platform": "warehouse",
        "temporal_model": "append-only",
        "classification": "internal",
        "assets": [{
            "id": "asset.fixture.input",
            "name": "fixture_input",
            "asset_type": "table",
            "physical_name": "fixture_input",
            "description": "Input table.",
            "confidence": "reviewed",
            "evidence": ["models/input.sql"],
            "inputs": [],
        }, {
            "id": "asset.fixture.output",
            "name": "fixture_output",
            "asset_type": "table",
            "physical_name": "fixture_output",
            "description": "Output table.",
            "confidence": "reviewed",
            "evidence": ["models/output.sql"],
            "inputs": [{
                "id": "asset.fixture.input",
                "confidence": "reviewed",
                "evidence": ["models/output.sql"],
            }],
        }],
        "conflicts": [{
            "conflict_id": "publication",
            "topic": "Native push publication",
            "claims": [
                {"statement": "Documentation says pushes publish.", "evidence": ["README.md"]},
                {"statement": "Workflow ignores pushes.", "evidence": ["workflow.yml"]},
            ],
            "interpretation": "Checked-in native automation is disabled.",
        }],
    }
    component = {
        **common,
        "id": "comp.fixture",
        "type": "component",
        "title": "Fixture transformer",
        "description": "Transforms fixture input to output.",
        "component_type": "job",
        "repository": "repo.fixture",
        "repository_paths": ["models"],
        "parent_component": None,
        "consumes": [{"id": "asset.fixture.input", "asset_type": "table", "confidence": "reviewed", "evidence": ["models/output.sql"]}],
        "produces": [{"id": "asset.fixture.output", "asset_type": "table", "confidence": "reviewed", "evidence": ["models/output.sql"]}],
        "depends_on": [], "uses_resources": [], "reads_from": [], "writes_to": [],
        "triggers": [], "scheduled_by": [], "deployed_by": [], "monitored_by": [],
        "runbooks": [], "standards": [], "incident_learnings": [],
    }
    _write(tmp_path, "_curated/repositories/test/repo.md", repository)
    schema_path = _write(tmp_path, "_curated/schema-info/test/schema.md", schema)
    _write(tmp_path, "_curated/components/test/component.md", component)
    return tmp_path, schema_path


def _git_commit(root: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=root, check=True, capture_output=True)


def _write_maps(root: Path, maps: dict[str, dict]) -> None:
    for name, payload in maps.items():
        path = map_output_paths(root)[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(stable_bytes(payload))


def _page_only_records(root: Path) -> None:
    schema, _ = parse_frontmatter(root / "_curated/schema-info/test/schema.md")
    standard = {
        **schema,
        "id": "standard.fixture",
        "type": "standard",
        "title": "Fixture standard",
        "description": "A page-only standard.",
        "standard_category": "general",
        "requirement_level": "recommended",
    }
    for field in ("primary_domain", "related_domains", "asset_type", "physical_name", "platform", "temporal_model", "classification", "assets"):
        standard.pop(field, None)
    _write(root, "_curated/standards/general/standard.md", standard)

    runbook = {
        **standard,
        "id": "runbook.fixture",
        "type": "runbook",
        "title": "Fixture runbook",
        "description": "A page-only runbook.",
        "last_exercised": "2026-08-11",
    }
    _write(root, "_curated/runbooks/runbook.md", runbook)

    infra = {
        **schema,
        "id": "infra.fixture",
        "type": "infra",
        "title": "Fixture infrastructure",
        "description": "An infrastructure owner for an embedded resource.",
        "infra_package": "fixture",
        "repository": "repo.fixture",
        "package_path": "infra",
        "template_path": "infra/main.tf",
        "environments": ["test"],
        "depends_on": [], "uses_resources": [], "reads_from": [], "writes_to": [],
        "triggers": [], "scheduled_by": [], "imports_values": [], "exports_values": [],
        "permissions": [], "monitored_by": [], "deployed_by": [],
        "promoted_resources": [{
            "id": "resource.fixture.bucket",
            "name": "Fixture bucket",
            "resource_type": "s3-bucket",
            "defined_in_path": "infra/main.tf",
            "environments": ["test"],
            "promotion_reason": "A direct boundary.",
            "confidence": "reviewed",
            "coverage": {"level": "partial", "notes": []},
            "evidence": ["infra/main.tf"],
        }],
        "runbooks": [], "standards": [], "incident_learnings": [],
    }
    for field in ("asset_type", "physical_name", "platform", "temporal_model", "classification", "assets", "links"):
        infra.pop(field, None)
    _write(root, "_curated/infra/test/infra.md", infra)


def test_exact_resolver_layers_maps_pages_and_embedded_owners(tmp_path: Path):
    root, _ = _root(tmp_path)
    maps = build_maps(root)
    _write_maps(root, maps)
    _page_only_records(root)

    resolver_type = getattr(query_module, "ExactResolver", None)
    assert resolver_type is not None
    resolver = resolver_type(root)

    assert resolver.resolve("comp.fixture") == AtlasQuery(root).resolve("comp.fixture")
    assert resolver.resolve("asset.fixture.output")["parent_schema"] == "schema.fixture"
    assert resolver.resolve("resource.fixture.bucket")["parent_package"] == "infra.fixture"
    assert resolver.resolve("standard.fixture")["page"] == "_curated/standards/general/standard.md"
    assert resolver.resolve("schema.fixture#publication")["owner_id"] == "schema.fixture"
    assert resolver.resolve("missing.fixture") is None


def test_exact_resolver_rejects_stale_map_routes_and_archived_pages(tmp_path: Path):
    root, schema_path = _root(tmp_path)
    maps = build_maps(root)
    maps["repository-component-map.json"]["components"]["comp.fixture"]["page"] = "_curated/components/test/missing.md"
    _write_maps(root, maps)

    resolver_type = getattr(query_module, "ExactResolver", None)
    assert resolver_type is not None
    resolver = resolver_type(root)

    assert resolver.resolve("comp.fixture")["page"] == "_curated/components/test/component.md"
    assert resolver.warnings.count("Generated map route for 'comp.fixture' is stale; its route was not trusted.") == 1
    schema_path.write_text(
        schema_path.read_text(encoding="utf-8").replace("status: curated", "status: archived"),
        encoding="utf-8",
    )
    assert resolver_type(root).resolve("schema.fixture") is None


def test_exact_resolver_rejects_archived_or_reassigned_mapped_owners(tmp_path: Path):
    resolver_type = getattr(query_module, "ExactResolver", None)
    assert resolver_type is not None

    archived_root, _ = _root(tmp_path / "archived")
    archived_maps = build_maps(archived_root)
    _write_maps(archived_root, archived_maps)
    component_path = archived_root / "_curated/components/test/component.md"
    component_path.write_text(
        component_path.read_text(encoding="utf-8").replace("status: curated", "status: archived"),
        encoding="utf-8",
    )
    archived = resolver_type(archived_root)
    assert archived.resolve("comp.fixture") is None
    assert any("Generated map route for 'comp.fixture' is stale" in warning for warning in archived.warnings)

    reassigned_root, _ = _root(tmp_path / "reassigned")
    reassigned_maps = build_maps(reassigned_root)
    _write_maps(reassigned_root, reassigned_maps)
    component_path = reassigned_root / "_curated/components/test/component.md"
    component_path.write_text(
        component_path.read_text(encoding="utf-8").replace("comp.fixture", "comp.reassigned"),
        encoding="utf-8",
    )
    reassigned = resolver_type(reassigned_root)
    assert reassigned.resolve("comp.fixture") is None
    assert any("Generated map route for 'comp.fixture' is stale" in warning for warning in reassigned.warnings)


def test_exact_resolver_preserves_page_only_json_metadata_and_runbooks(tmp_path: Path):
    root, _ = _root(tmp_path)
    maps = build_maps(root)
    _write_maps(root, maps)
    _page_only_records(root)

    resolver_type = getattr(query_module, "ExactResolver", None)
    assert resolver_type is not None
    resolver = resolver_type(root)
    query = AtlasQuery(root)

    for identifier in ("standard.fixture", "runbook.fixture"):
        exact = resolver.resolve(identifier)
        previous = query.resolve(identifier)
        assert exact["primary_domain"] == previous["primary_domain"]
        assert exact["page"] == previous["page"]
    assert resolver.resolve("runbook.fixture")["type"] == "runbook"


def test_exact_resolver_overlays_deprecated_mapped_owner_status(tmp_path: Path):
    root, _ = _root(tmp_path)
    maps = build_maps(root)
    _write_maps(root, maps)
    component_path = root / "_curated/components/test/component.md"
    component_path.write_text(
        component_path.read_text(encoding="utf-8").replace("status: curated", "status: deprecated"),
        encoding="utf-8",
    )

    resolver_type = getattr(query_module, "ExactResolver", None)
    assert resolver_type is not None
    record = resolver_type(root).resolve("comp.fixture")

    assert record["status"] == "deprecated"
    assert record["trust"] == "historical"
    assert record["checkout_state"] is None


def test_cli_resolve_reports_lazy_map_and_frontmatter_failures(tmp_path: Path, capsys):
    map_root, _ = _root(tmp_path / "map")
    maps = build_maps(map_root)
    _write_maps(map_root, maps)
    map_output_paths(map_root)["flow-component-map.json"].write_text("{", encoding="utf-8")

    assert atlas_query.main(["--root", str(map_root), "resolve", "comp.fixture"]) == 1
    assert capsys.readouterr().err.startswith("Atlas query failed: ")

    frontmatter_root, _ = _root(tmp_path / "frontmatter")
    broken = frontmatter_root / "_curated/standards/broken.md"
    broken.parent.mkdir(parents=True)
    broken.write_text("---\ninvalid: [\n---\n", encoding="utf-8")

    assert atlas_query.main(["--root", str(frontmatter_root), "resolve", "missing.fixture"]) == 1
    assert capsys.readouterr().err.startswith("Atlas query failed: ")


def test_cli_resolve_uses_exact_resolver_without_atlas_query(tmp_path: Path, monkeypatch, capsys):
    root, _ = _root(tmp_path)
    maps = build_maps(root)
    _write_maps(root, maps)

    def unexpected_atlas_query(*args, **kwargs):
        raise AssertionError("resolve must not instantiate AtlasQuery")

    monkeypatch.setattr(atlas_query, "AtlasQuery", unexpected_atlas_query)

    assert atlas_query.main(["--root", str(root), "--format", "json", "resolve", "comp.fixture"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["record"]["id"] == "comp.fixture"


def test_exact_resolver_preserves_checkout_and_history_advisories(tmp_path: Path):
    root, schema_path = _root(tmp_path)
    resolver_type = getattr(query_module, "ExactResolver", None)
    assert resolver_type is not None

    assert resolver_type(root).resolve("asset.fixture.output")["checkout_state"] == "git-unknown"
    _git_commit(root)
    assert resolver_type(root).resolve("schema.fixture")["checkout_state"] == "main-clean"

    schema_path.write_text(schema_path.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
    assert resolver_type(root).resolve("schema.fixture")["checkout_state"] == "modified"
    subprocess.run(["git", "checkout", "--", str(schema_path.relative_to(root))], cwd=root, check=True)

    subprocess.run(["git", "switch", "-c", "feature/exact"], cwd=root, check=True, capture_output=True)
    assert resolver_type(root).resolve("repo.fixture")["checkout_state"] == "off-main"
    subprocess.run(["git", "checkout", "--detach"], cwd=root, check=True, capture_output=True)
    assert resolver_type(root).resolve("repo.fixture")["checkout_state"] == "detached"

    repo_frontmatter, _ = parse_frontmatter(root / "_curated/repositories/test/repo.md")
    repo_frontmatter.update({"id": "repo.untracked", "title": "Untracked repository"})
    _write(root, "_curated/repositories/test/untracked.md", repo_frontmatter)
    assert resolver_type(root).resolve("repo.untracked")["checkout_state"] == "untracked"

    schema_path.write_text(
        schema_path.read_text(encoding="utf-8").replace("status: curated", "status: deprecated"),
        encoding="utf-8",
    )
    historical = resolver_type(root).resolve("schema.fixture")
    assert historical["trust"] == "historical"
    assert historical["checkout_state"] is None


def test_assets_are_searchable_and_lineage_is_traversable(tmp_path: Path):
    root, _ = _root(tmp_path)
    query = AtlasQuery(root, compiled_maps=build_maps(root))
    found = query.find("fixture output", types=["data-asset"])
    assert found["candidates"][0]["id"] == "asset.fixture.output"
    downstream = query.impact("asset.fixture.input", direction="downstream")
    assert {item["id"] for item in downstream} >= {"asset.fixture.output", "comp.fixture"}


def test_conflict_search_returns_qualified_match_and_resolution(tmp_path: Path):
    root, _ = _root(tmp_path)
    query = AtlasQuery(root, compiled_maps=build_maps(root))
    candidate = query.find("native push publication")["candidates"][0]
    assert candidate["matched_conflicts"] == [{
        "id": "schema.fixture#publication",
        "topic": "Native push publication",
    }]
    conflict = query.resolve("schema.fixture#publication")
    assert conflict["claims"][1]["statement"] == "Workflow ignores pushes."


def test_curated_authority_is_separate_from_page_checkout_state(tmp_path: Path):
    root, schema_path = _root(tmp_path)
    _git_commit(root)
    query = AtlasQuery(root, compiled_maps=build_maps(root))
    assert query.resolve("schema.fixture")["trust"] == "authoritative"
    assert query.resolve("asset.fixture.output")["trust"] == "authoritative"
    assert query.resolve("schema.fixture")["checkout_state"] == "main-clean"
    assert query.resolve("asset.fixture.output")["checkout_state"] == "main-clean"

    schema_path.write_text(schema_path.read_text(encoding="utf-8") + "\nlocal edit\n", encoding="utf-8")
    dirty = AtlasQuery(root, compiled_maps=build_maps(root))
    assert dirty.resolve("schema.fixture")["trust"] == "authoritative"
    assert dirty.resolve("asset.fixture.output")["trust"] == "authoritative"
    assert dirty.resolve("repo.fixture")["trust"] == "authoritative"
    assert dirty.resolve("schema.fixture")["checkout_state"] == "modified"
    assert dirty.resolve("asset.fixture.output")["checkout_state"] == "modified"
    assert dirty.resolve("repo.fixture")["checkout_state"] == "main-clean"


def test_atlas_query_checks_each_curated_page_once_per_instance(tmp_path: Path, monkeypatch):
    """Search, routing, and embedded records reuse the page's checkout advisory."""
    root, _ = _root(tmp_path)
    _git_commit(root)
    pages = curated_pages(root)
    original_run = query_module.subprocess.run
    checked: list[str] = []

    def counting_run(command, *args, **kwargs):
        if command[:3] == ["git", "ls-files", "--error-unmatch"]:
            checked.append(command[-1])
        return original_run(command, *args, **kwargs)

    monkeypatch.setattr(query_module.subprocess, "run", counting_run)

    AtlasQuery(root, compiled_maps=build_maps(root, pages=pages), pages=pages)

    assert checked == sorted(page.path.relative_to(root).as_posix() for page in pages)


def test_git_unavailable_does_not_remove_curated_authority_and_deprecated_is_historical(tmp_path: Path):
    root, schema_path = _root(tmp_path)
    query = AtlasQuery(root, compiled_maps=build_maps(root))
    assert query.resolve("schema.fixture")["trust"] == "authoritative"
    assert query.resolve("schema.fixture")["checkout_state"] == "git-unknown"
    text = schema_path.read_text(encoding="utf-8").replace("status: curated", "status: deprecated")
    schema_path.write_text(text, encoding="utf-8")
    historical = AtlasQuery(root, compiled_maps=build_maps(root))
    assert historical.resolve("schema.fixture")["trust"] == "historical"


def test_feature_branch_detached_untracked_and_archived_checkout_state(tmp_path: Path):
    root, schema_path = _root(tmp_path)
    _git_commit(root)
    subprocess.run(["git", "switch", "-c", "feature/eval"], cwd=root, check=True, capture_output=True)
    feature = AtlasQuery(root, compiled_maps=build_maps(root))
    assert feature.resolve("repo.fixture")["trust"] == "authoritative"
    assert feature.resolve("repo.fixture")["checkout_state"] == "off-main"

    subprocess.run(["git", "checkout", "--detach"], cwd=root, check=True, capture_output=True)
    detached = AtlasQuery(root, compiled_maps=build_maps(root))
    assert detached.resolve("repo.fixture")["trust"] == "authoritative"
    assert detached.resolve("repo.fixture")["checkout_state"] == "detached"

    repo_frontmatter, _ = parse_frontmatter(root / "_curated/repositories/test/repo.md")
    repo_frontmatter.update({"id": "repo.untracked", "title": "Untracked repository"})
    _write(root, "_curated/repositories/test/untracked.md", repo_frontmatter)
    untracked = AtlasQuery(root, compiled_maps=build_maps(root))
    assert untracked.resolve("repo.untracked")["trust"] == "authoritative"
    assert untracked.resolve("repo.untracked")["checkout_state"] == "untracked"

    schema_path.write_text(
        schema_path.read_text(encoding="utf-8").replace("status: curated", "status: archived"),
        encoding="utf-8",
    )
    archived = AtlasQuery(root, compiled_maps={})
    assert archived.resolve("schema.fixture") is None
    assert archived.resolve("asset.fixture.output") is None


def test_non_mapping_staging_frontmatter_does_not_break_other_queries(tmp_path: Path):
    root, schema_path = _root(tmp_path)
    schema_path.write_text(
        schema_path.read_text(encoding="utf-8")
        + """
## Open questions / coverage limits

| Question ID | Question | Affected IDs | Evidence gap |
|---|---|---|---|
| ownership | Who owns this schema? | schema.fixture | Ownership evidence. |
""",
        encoding="utf-8",
    )
    invalid = root / "_staging/changes/STG-20260811-invalid.md"
    invalid.parent.mkdir(parents=True)
    invalid.write_text(
        "---\n- not\n- a-mapping\n---\n\nschema.fixture#ownership\n",
        encoding="utf-8",
    )

    query = AtlasQuery(root, compiled_maps=build_maps(root))

    assert query.find("fixture schema")["candidates"][0]["id"] == "schema.fixture"
    assert [item["id"] for item in query.questions("schema.fixture")["results"]] == [
        "schema.fixture#ownership"
    ]

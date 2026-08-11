from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess

import yaml

from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.maps import build_maps
from scripts.lib.query import AtlasQuery


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

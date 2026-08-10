from pathlib import Path
import json
import shutil
import subprocess
import sys

import pytest

from scripts.lib.maps import MAP_NAMES, MapBuildError, build_maps, map_output_paths, stable_bytes
from scripts.lib.taxonomy import TaxonomyError

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "valid" / "map-projection"


def _write_package(root: Path) -> None:
    (root / "package.md").write_text(
        """---
id: atlas-package.fixtures
type: atlas.package
package: fixtures
schema_version: atlas/1.0
title: Fixture Atlas
description: Synthetic fixture package.
status: active
maps:
  flow_component: _curated/maps/flow-component/flow-component-map.json
  repo_dependency: _curated/maps/repo-dependency/repo-dependency-map.json
  infra_dependency: _curated/maps/infra-dependency/infra-dependency-map.json
---
""",
        encoding="utf-8",
    )


def _map_root(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "taxonomy", tmp_path / "taxonomy")
    _write_package(tmp_path)
    destinations = {
        "component.md": "_curated/components/component.md",
        "library.md": "_curated/components/library.md",
        "flow.md": "_curated/flows/flow.md",
        "upstream-flow.md": "_curated/flows/upstream-flow.md",
        "infra.md": "_curated/infra/infra.md",
        "schema-info.md": "_curated/schema-info/schema.md",
    }
    for source_name, dest_name in destinations.items():
        dest = tmp_path / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FIXTURES / source_name, dest)
    (tmp_path / "_curated" / "maps").mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_map_generation_compiles_attachment_style_domain_records(tmp_path: Path):
    maps = build_maps(_map_root(tmp_path))

    assert set(maps) == set(MAP_NAMES)
    assert set(maps["flow-component-map.json"]) == {"metadata", "flows"}
    assert set(maps["repo-dependency-map.json"]) == {"metadata", "components"}
    assert set(maps["infra-dependency-map.json"]) == {"metadata", "packages", "resources"}
    assert all("nodes" not in value and "edges" not in value and "reverse_edges" not in value for value in maps.values())

    metadata = maps["flow-component-map.json"]["metadata"]
    assert metadata["schema_version"] == "atlas-map/1.0"
    assert metadata["generated"] is True
    assert metadata["package"] == "fixtures"
    assert "last_updated" not in metadata
    assert metadata["related_maps"]["infra_dependency"].endswith("infra-dependency-map.json")
    assert "schedule" in metadata["entry_point_kinds"]
    assert "atlas.runs-before" in metadata["relationship_types"]
    assert "atlas.deployed-by" not in metadata["relationship_types"]

    repo_metadata = maps["repo-dependency-map.json"]["metadata"]
    assert "atlas.depends-on" in repo_metadata["relationship_types"]
    assert "atlas.triggers" not in repo_metadata["relationship_types"]
    assert "shared-library" in repo_metadata["relationship_kinds"]

    infra_metadata = maps["infra-dependency-map.json"]["metadata"]
    assert "atlas.reads-from" in infra_metadata["relationship_types"]
    assert "atlas.consumes" not in infra_metadata["relationship_types"]
    assert "permission" in infra_metadata["relationship_kinds"]


def test_flow_map_compiles_ordered_participants_routes_and_reverse_flows(tmp_path: Path):
    flow_map = build_maps(_map_root(tmp_path))["flow-component-map.json"]["flows"]
    flow = flow_map["atlas-flow.fixture.flow"]

    assert [item["id"] for item in flow["participants"]] == [
        "atlas-comp.fixture.component",
        "atlas-infra.fixture.stack",
    ]
    assert [item["sequence"] for item in flow["participants"]] == [1, 2]
    assert flow["entry_points"][0]["kind"] == "schedule"
    assert flow["inputs"][0]["target"] == "atlas-schema.fixture.asset"
    assert flow["outputs"][0]["kind"] == "report"
    assert flow["upstream_flows"][0]["target"] == "atlas-flow.fixture.upstream"
    assert flow_map["atlas-flow.fixture.upstream"]["downstream_flows"][0]["source"] == "atlas-flow.fixture.flow"
    assert flow["runs_before_flows"][0]["target"] == "atlas-flow.fixture.upstream"
    assert flow_map["atlas-flow.fixture.upstream"]["runs_after_flows"][0]["source"] == "atlas-flow.fixture.flow"
    assert flow["runbooks"][0]["target"] == "external.fixture.runbook"
    assert flow["incident_learnings"][0]["target"] == "external.fixture.incident"


def test_repo_map_groups_dependencies_and_generates_dependents(tmp_path: Path):
    components = build_maps(_map_root(tmp_path))["repo-dependency-map.json"]["components"]
    component = components["atlas-comp.fixture.component"]
    library = components["atlas-comp.fixture.library"]

    assert component["domain_group"] == "fixture-domain"
    assert component["consumes"][0]["target"] == "atlas-schema.fixture.asset"
    assert any(item["target"] == "external.fixture.api" and item["confidence"] == "possible" for item in component["consumes"])
    assert component["produces"][0]["target"] == "atlas-schema.fixture.asset"
    assert component["uses_libraries"][0]["target"] == "atlas-comp.fixture.library"
    assert library["used_by_components"][0]["source"] == "atlas-comp.fixture.component"
    assert library["used_by_components"][0]["derived"] is True
    assert component["runs_before_components"][0]["target"] == "atlas-comp.fixture.library"
    assert library["runs_after_components"][0]["source"] == "atlas-comp.fixture.component"
    assert component["participates_in_flows"][0]["target"] == "atlas-flow.fixture.flow"


def test_infra_map_compiles_promoted_resources_and_all_reverse_users(tmp_path: Path):
    infra_map = build_maps(_map_root(tmp_path))["infra-dependency-map.json"]
    package = infra_map["packages"]["atlas-infra.fixture.stack"]
    bucket = infra_map["resources"]["atlas-resource.fixture.shared-bucket"]
    queue = infra_map["resources"]["atlas-resource.fixture.queue"]

    assert package["defines_resources"] == [
        "atlas-resource.fixture.queue",
        "atlas-resource.fixture.shared-bucket",
    ]
    assert package["depends_on_resources"][0]["target"] == "atlas-resource.fixture.shared-bucket"
    assert bucket["parent_package"] == "atlas-infra.fixture.stack"
    assert bucket["resource_type"] == "s3-bucket"
    assert bucket["used_by_components"][0]["source"] == "atlas-comp.fixture.component"
    assert bucket["used_by_flows"][0]["source"] == "atlas-flow.fixture.flow"
    assert bucket["used_by_packages"][0]["source"] == "atlas-infra.fixture.stack"
    assert bucket["depends_on_resources"][0]["target"] == "atlas-resource.fixture.queue"
    assert queue["used_by_resources"][0]["source"] == "atlas-resource.fixture.shared-bucket"
    assert bucket["triggers"][0]["target"] == "atlas-flow.fixture.flow"
    assert bucket["permissions"][0]["target"] == "atlas-comp.fixture.component"
    assert bucket["monitored_by"][0]["target"] == "atlas-resource.fixture.queue"
    assert queue["monitors"][0]["source"] == "atlas-resource.fixture.shared-bucket"
    assert queue["schedules"][0]["source"] == "atlas-comp.fixture.component"


def test_map_generation_preserves_non_archived_statuses_and_excludes_archived(tmp_path: Path):
    root = _map_root(tmp_path)
    maps = build_maps(root)
    assert maps["repo-dependency-map.json"]["components"]["atlas-comp.fixture.library"]["status"] == "proposed"
    assert maps["flow-component-map.json"]["flows"]["atlas-flow.fixture.upstream"]["status"] == "deprecated"

    upstream = root / "_curated/flows/upstream-flow.md"
    upstream.write_text(upstream.read_text(encoding="utf-8").replace("status: deprecated", "status: archived"), encoding="utf-8")
    maps = build_maps(root)
    assert "atlas-flow.fixture.upstream" not in maps["flow-component-map.json"]["flows"]


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("id: atlas-resource.fixture.shared-bucket", "id: bad-resource-id", "invalid promoted resource id"),
        ("resource_type: s3-bucket", "resource_type: imaginary-resource", "invalid resource_type"),
        ("promotion_reason: Shared data-bearing fixture resource.", "promotion_reason: ''", "requires promotion_reason"),
        ("evidence: [fixture://shared-bucket]", "evidence: []", "requires evidence"),
    ],
)
def test_map_generation_rejects_invalid_promoted_resources(tmp_path: Path, old: str, new: str, message: str):
    root = _map_root(tmp_path)
    path = root / "_curated/infra/infra.md"
    path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
    with pytest.raises(MapBuildError, match=message):
        build_maps(root)


def test_unknown_kinds_from_reports_the_taxonomy_contract_not_a_key_error(tmp_path: Path):
    root = _map_root(tmp_path)
    path = root / "taxonomy/maps.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace("kinds_from: io_kinds", "kinds_from: bogus_kinds", 1), encoding="utf-8")
    with pytest.raises(TaxonomyError, match="bogus_kinds"):
        build_maps(root)


def test_map_generation_is_byte_deterministic(tmp_path: Path):
    root = _map_root(tmp_path)
    first = {name: stable_bytes(value) for name, value in build_maps(root).items()}
    second = {name: stable_bytes(value) for name, value in build_maps(root).items()}
    assert first == second


def test_map_generation_rejects_relationship_that_does_not_apply_to_source_map(tmp_path: Path):
    root = _map_root(tmp_path)
    path = root / "_curated/flows/flow.md"
    text = path.read_text(encoding="utf-8").replace(
        "relationships:",
        "relationships:\n- type: atlas.deployed-by\n  target: atlas-infra.fixture.stack\n  confidence: reviewed\n  evidence: [fixture://invalid-map-contract]",
        1,
    )
    path.write_text(text, encoding="utf-8")
    with pytest.raises(MapBuildError, match="does not apply"):
        build_maps(root)


def test_package_paths_select_each_generated_map_folder(tmp_path: Path):
    root = _map_root(tmp_path)
    paths = map_output_paths(root)
    assert paths["flow-component-map.json"] == root / "_curated/maps/flow-component/flow-component-map.json"
    assert paths["repo-dependency-map.json"] == root / "_curated/maps/repo-dependency/repo-dependency-map.json"
    assert paths["infra-dependency-map.json"] == root / "_curated/maps/infra-dependency/infra-dependency-map.json"


def test_package_rejects_map_outside_its_dedicated_folder(tmp_path: Path):
    root = _map_root(tmp_path)
    package = root / "package.md"
    package.write_text(
        package.read_text(encoding="utf-8").replace(
            "_curated/maps/flow-component/flow-component-map.json",
            "_curated/maps/flow-component-map.json",
        ),
        encoding="utf-8",
    )
    with pytest.raises(MapBuildError, match="dedicated map path"):
        map_output_paths(root)


def test_rebuild_maps_check_detects_drift(tmp_path: Path):
    root = _map_root(tmp_path)
    script = ROOT / "scripts" / "rebuild_maps.py"
    build = subprocess.run(
        [sys.executable, str(script), "--root", str(root)], capture_output=True, text=True
    )
    assert build.returncode == 0, build.stdout + build.stderr
    clean = subprocess.run(
        [sys.executable, str(script), "--root", str(root), "--check"],
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0, clean.stdout + clean.stderr

    path = root / "_curated" / "maps" / "repo-dependency" / "repo-dependency-map.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["components"] = {}
    path.write_text(json.dumps(data), encoding="utf-8")
    drift = subprocess.run(
        [sys.executable, str(script), "--root", str(root), "--check"],
        capture_output=True,
        text=True,
    )
    assert drift.returncode != 0
    assert "repo-dependency-map.json" in drift.stdout

from pathlib import Path
import json
import shutil
import subprocess
import sys

from scripts.lib.maps import MAP_NAMES, build_maps, stable_bytes

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "valid" / "map-projection"


def _map_root(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "taxonomy", tmp_path / "taxonomy")
    destinations = {
        "component.md": "_curated/components/component.md",
        "flow.md": "_curated/flows/flow.md",
        "infra.md": "_curated/infra/infra.md",
        "schema-info.md": "_curated/schema-info/schema.md",
    }
    for source_name, dest_name in destinations.items():
        dest = tmp_path / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(FIXTURES / source_name, dest)
    (tmp_path / "_curated" / "maps").mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_map_generation_projects_all_three_required_maps_and_reverse_views(tmp_path: Path):
    root = _map_root(tmp_path)
    maps = build_maps(root)
    assert set(maps) == set(MAP_NAMES)
    assert all(maps[name]["edges"] for name in MAP_NAMES)
    assert all(maps[name]["reverse_edges"] for name in MAP_NAMES)
    assert any(edge["type"] == "atlas.participates-in" for edge in maps["flow-component-map.json"]["edges"])
    assert any(edge["type"] == "atlas.consumes" for edge in maps["repo-dependency-map.json"]["edges"])
    assert any(edge["type"] == "atlas.deployed-by" for edge in maps["infra-dependency-map.json"]["edges"])
    assert all(edge["derived"] is True for edge in maps["repo-dependency-map.json"]["reverse_edges"])


def test_map_generation_is_byte_deterministic(tmp_path: Path):
    root = _map_root(tmp_path)
    first = {name: stable_bytes(value) for name, value in build_maps(root).items()}
    second = {name: stable_bytes(value) for name, value in build_maps(root).items()}
    assert first == second


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

    path = root / "_curated" / "maps" / "repo-dependency-map.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["edges"] = []
    path.write_text(json.dumps(data), encoding="utf-8")
    drift = subprocess.run(
        [sys.executable, str(script), "--root", str(root), "--check"],
        capture_output=True,
        text=True,
    )
    assert drift.returncode != 0
    assert "repo-dependency-map.json" in drift.stdout

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from scripts.atlas_source_snapshot import main
from scripts.lib.source_snapshot import SnapshotError, cleanup_snapshot, prepare_snapshot


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _repository(tmp_path: Path) -> Path:
    repo = tmp_path / "product"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
    _git(repo, "config", "user.email", "atlas@example.invalid")
    _git(repo, "config", "user.name", "Atlas Test")
    (repo / "README.md").write_text("baseline\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "baseline")
    return repo


def test_clean_head_uses_the_existing_checkout(tmp_path: Path):
    repo = _repository(tmp_path)

    manifest = prepare_snapshot(repo, default_ref="main", temp_root=tmp_path / "snapshots")
    payload = json.loads(manifest.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "atlas-source-snapshot/1.0"
    assert payload["mode"] == "in-place"
    assert Path(payload["snapshot_path"]) == repo.resolve()
    assert payload["selected_commit"] == _git(repo, "rev-parse", "HEAD")
    assert payload["default_relationship"] == "on-default"

    cleanup_snapshot(manifest)
    assert repo.exists()
    assert not manifest.exists()


def test_dirty_checkout_requires_an_explicit_revision(tmp_path: Path):
    repo = _repository(tmp_path)
    (repo / "README.md").write_text("unsaved work\n", encoding="utf-8")

    with pytest.raises(SnapshotError, match="dirty"):
        prepare_snapshot(repo, default_ref="main", temp_root=tmp_path / "snapshots")

    assert (repo / "README.md").read_text(encoding="utf-8") == "unsaved work\n"


def test_explicit_commit_uses_a_detached_temporary_worktree_without_touching_dirty_files(tmp_path: Path):
    repo = _repository(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "README.md").write_text("unsaved work\n", encoding="utf-8")

    manifest = prepare_snapshot(
        repo,
        commit=head,
        default_ref="main",
        temp_root=tmp_path / "snapshots",
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    snapshot = Path(payload["snapshot_path"])

    assert payload["mode"] == "temporary-worktree"
    assert snapshot != repo.resolve()
    assert _git(snapshot, "rev-parse", "HEAD") == head
    assert (snapshot / "README.md").read_text(encoding="utf-8") == "baseline\n"
    assert (repo / "README.md").read_text(encoding="utf-8") == "unsaved work\n"

    cleanup_snapshot(manifest)
    assert not snapshot.exists()
    assert (repo / "README.md").read_text(encoding="utf-8") == "unsaved work\n"


def test_unmerged_branch_records_merge_base_and_relationship(tmp_path: Path):
    repo = _repository(tmp_path)
    main_head = _git(repo, "rev-parse", "HEAD")
    _git(repo, "switch", "-c", "feature")
    (repo / "feature.txt").write_text("feature\n", encoding="utf-8")
    _git(repo, "add", "feature.txt")
    _git(repo, "commit", "-m", "feature")

    manifest = prepare_snapshot(repo, default_ref="main", temp_root=tmp_path / "snapshots")
    payload = json.loads(manifest.read_text(encoding="utf-8"))

    assert payload["mode"] == "in-place"
    assert payload["merge_base"] == main_head
    assert payload["default_relationship"] == "ahead-of-default"

    cleanup_snapshot(manifest)


def test_unavailable_default_ref_is_reported_as_unknown(tmp_path: Path):
    repo = _repository(tmp_path)

    manifest = prepare_snapshot(repo, default_ref="origin/main", temp_root=tmp_path / "snapshots")
    payload = json.loads(manifest.read_text(encoding="utf-8"))

    assert payload["default_commit"] is None
    assert payload["merge_base"] is None
    assert payload["default_relationship"] == "unknown"

    cleanup_snapshot(manifest)


def test_cleanup_refuses_a_dirty_temporary_worktree_and_leaves_it_registered(tmp_path: Path):
    repo = _repository(tmp_path)
    first = _git(repo, "rev-parse", "HEAD")
    (repo / "second.txt").write_text("second\n", encoding="utf-8")
    _git(repo, "add", "second.txt")
    _git(repo, "commit", "-m", "second")
    manifest = prepare_snapshot(
        repo,
        commit=first,
        default_ref="main",
        temp_root=tmp_path / "snapshots",
    )
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    snapshot = Path(payload["snapshot_path"])
    (snapshot / "local.txt").write_text("do not delete\n", encoding="utf-8")

    with pytest.raises(SnapshotError, match="dirty"):
        cleanup_snapshot(manifest)

    assert snapshot.exists()
    assert manifest.exists()
    registered = {
        Path(line.removeprefix("worktree ")).resolve()
        for line in _git(repo, "worktree", "list", "--porcelain").splitlines()
        if line.startswith("worktree ")
    }
    assert snapshot.resolve() in registered

    (snapshot / "local.txt").unlink()
    cleanup_snapshot(manifest)


def test_cleanup_rejects_a_tampered_target(tmp_path: Path):
    repo = _repository(tmp_path)
    first = _git(repo, "rev-parse", "HEAD")
    (repo / "second.txt").write_text("second\n", encoding="utf-8")
    _git(repo, "add", "second.txt")
    _git(repo, "commit", "-m", "second")
    manifest = prepare_snapshot(
        repo,
        commit=first,
        default_ref="main",
        temp_root=tmp_path / "snapshots",
    )
    original = json.loads(manifest.read_text(encoding="utf-8"))
    original_snapshot = Path(original["snapshot_path"])
    other = tmp_path / "other"
    other.mkdir()
    original["snapshot_path"] = str(other.resolve())
    manifest.write_text(json.dumps(original), encoding="utf-8")

    with pytest.raises(SnapshotError, match="marker|registered|target"):
        cleanup_snapshot(manifest)

    assert other.exists()
    assert original_snapshot.exists()

    original["snapshot_path"] = str(original_snapshot)
    manifest.write_text(json.dumps(original), encoding="utf-8")
    cleanup_snapshot(manifest)


def test_cli_prepare_and_cleanup_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    repo = _repository(tmp_path)

    assert main(["prepare", "--repository", str(repo), "--default-ref", "main", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    manifest = Path(payload["manifest_path"])
    assert payload["mode"] == "in-place"

    assert main(["cleanup", "--manifest", str(manifest), "--format", "json"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["cleaned"] is True
    assert not manifest.exists()


def test_cleanup_invalidates_an_in_place_snapshot_if_the_checkout_changes(tmp_path: Path):
    repo = _repository(tmp_path)
    manifest = prepare_snapshot(repo, default_ref="main", temp_root=tmp_path / "snapshots")
    (repo / "README.md").write_text("changed during analysis\n", encoding="utf-8")

    with pytest.raises(SnapshotError, match="no longer matches"):
        cleanup_snapshot(manifest)

    assert manifest.exists()
    assert (repo / "README.md").read_text(encoding="utf-8") == "changed during analysis\n"

    (repo / "README.md").write_text("baseline\n", encoding="utf-8")
    cleanup_snapshot(manifest)

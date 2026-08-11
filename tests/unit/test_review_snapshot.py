from pathlib import Path

import pytest

from scripts.lib.review_snapshot import SnapshotError, create_snapshot, remove_snapshot, verify_snapshot


def test_snapshot_tracks_files_missing_paths_and_cleanup(tmp_path: Path):
    source = tmp_path / "source.md"
    source.write_text("one", encoding="utf-8")
    missing = tmp_path / "deleted.md"
    manifest = create_snapshot([source], intended_missing=[missing])
    try:
        assert verify_snapshot(manifest) == []
        source.write_text("two", encoding="utf-8")
        missing.write_text("returned", encoding="utf-8")
        changes = verify_snapshot(manifest)
        assert any("source.md" in item for item in changes)
        assert any("deleted.md" in item for item in changes)
    finally:
        remove_snapshot(manifest)
    assert not manifest.exists()


def test_snapshot_rejects_non_temporary_manifest(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    with pytest.raises(SnapshotError):
        verify_snapshot(manifest)

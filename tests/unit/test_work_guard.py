from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import uuid

import yaml
import pytest

from scripts.lib import work_guard


ROOT = Path(__file__).resolve().parents[2]
CLI = ROOT / "scripts" / "atlas_work_guard.py"


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "atlas"
    root.parent.mkdir(parents=True, exist_ok=True)
    root.mkdir()
    shutil.copytree(ROOT / "taxonomy", root / "taxonomy")
    shutil.copytree(ROOT / "contracts", root / "contracts")
    manifest = {
        "schema_version": "atlas-package/1.0",
        "id": "package.fixture",
        "type": "package",
        "package": "fixture",
        "title": "Fixture",
        "description": "Fixture Atlas.",
        "status": "active",
        "owners": {},
        "aliases": ["fixture"],
        "domains": [],
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
    (root / "atlas-package.json").write_text(json.dumps(manifest), encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    return root


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _handle(result: subprocess.CompletedProcess[str]) -> tuple[str, str]:
    payload = json.loads(result.stdout)
    return payload["state"], payload["key_file"]


def _directory_link(link: Path, target: Path) -> None:
    try:
        os.symlink(target, link, target_is_directory=True)
    except OSError:
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(f"could not create test reparse point: {result.stderr or result.stdout}")


def _write_staging(
    root: Path,
    relative: str,
    *,
    status: str = "new",
    record_id: str = "STG-20260817-example",
) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = {
        "id": record_id,
        "type": "staging.runbook",
        "package": "fixture",
        "timestamp": "2026-08-17",
        "title": "Example",
        "description": "Example evidence.",
        "status": status,
        "captured_by": "Fixture Curator",
        "source_type": "repository",
    }
    path.write_text(
        "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\nEvidence.\n",
        encoding="utf-8",
    )
    return path


def _write_runbook(root: Path, relative: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    frontmatter = {
        "id": "runbook.example",
        "type": "runbook",
        "package": "fixture",
        "schema_version": "atlas/1.0",
        "title": "Example runbook",
        "description": "Example operations.",
        "status": "curated",
        "last_reviewed": "2026-08-17",
        "reviewed_by": ["Fixture Curator"],
        "owners": [],
        "routing": {"aliases": []},
        "evidence": ["fixture://runbook"],
        "coverage": {"level": "partial", "notes": []},
        "last_exercised": "",
        "links": [],
    }
    path.write_text(
        "---\n" + yaml.safe_dump(frontmatter, sort_keys=False) + "---\n\n" + body,
        encoding="utf-8",
    )
    return path


def test_start_records_approved_scope_and_baseline_outside_repository(tmp_path: Path):
    root = _repo(tmp_path)
    missing = "_curated/components/example/new.md"

    result = _run(
        "start",
        "--root",
        str(root),
        "--missing-path",
        missing,
        "--id",
        "comp.example",
        "--format",
        "json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    state_dir = Path(payload["state"])
    key_file = Path(payload["key_file"])
    assert os.path.commonpath([state_dir, root]) != str(root)
    assert os.path.commonpath([state_dir, Path(tempfile.gettempdir()).resolve()]) == str(
        Path(tempfile.gettempdir()).resolve()
    )
    state = json.loads((state_dir / "state.json").read_text(encoding="utf-8"))
    assert state["scope"] == {
        "paths": [],
        "missing_paths": [missing],
        "ids": ["comp.example"],
    }
    assert state["baseline_issues"] == []
    assert state["repo_state"]["head"] is None
    assert (state_dir / "pre").is_dir()
    assert state_dir.name == f"atlas-work-guard-{state['instance_id']}"
    assert key_file.name == f"atlas-work-guard-key-{state['instance_id']}.key"
    assert key_file.parent == state_dir.parent
    assert key_file.is_file()
    assert not key_file.is_relative_to(state_dir)
    assert (state_dir / "state.hmac").is_file()
    assert not (state_dir / "state.sha256").exists()


def test_checkpoint_requires_trusted_root_and_rejects_tampered_state(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_value, key_value = _handle(started)
    state_dir = Path(state_value)

    missing_root = _run(
        "checkpoint", "--state", str(state_dir), "--key-file", key_value, "--format", "json"
    )
    assert missing_root.returncode == 2
    assert "--root" in missing_root.stderr

    state_path = state_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["root"] = str(tmp_path / "different")
    state_path.write_text(json.dumps(state), encoding="utf-8")
    tampered = _run(
        "checkpoint", "--root", str(root), "--state", str(state_dir),
        "--key-file", key_value, "--format", "json"
    )
    assert tampered.returncode == 2
    assert "hmac authentication failed" in tampered.stderr.casefold()


def test_checkpoint_rejects_missing_wrong_and_copied_capability_keys(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    payload = json.loads(started.stdout)
    state_dir = payload["state"]
    key_file = Path(payload["key_file"])

    missing_argument = _run(
        "checkpoint", "--root", str(root), "--state", state_dir, "--format", "json"
    )
    assert missing_argument.returncode == 2
    assert "--key-file" in missing_argument.stderr

    copied_key = tmp_path / "copied.key"
    shutil.copyfile(key_file, copied_key)
    copied = _run(
        "checkpoint",
        "--root",
        str(root),
        "--state",
        state_dir,
        "--key-file",
        str(copied_key),
        "--format",
        "json",
    )
    assert copied.returncode == 2

    key_file.write_bytes(secrets.token_bytes(32))
    wrong = _run(
        "checkpoint",
        "--root",
        str(root),
        "--state",
        state_dir,
        "--key-file",
        str(key_file),
        "--format",
        "json",
    )
    assert wrong.returncode == 2
    assert "key" in wrong.stderr.casefold() or "hmac" in wrong.stderr.casefold()

    key_file.unlink()
    missing_file = _run(
        "checkpoint",
        "--root",
        str(root),
        "--state",
        state_dir,
        "--key-file",
        str(key_file),
        "--format",
        "json",
    )
    assert missing_file.returncode == 2


def test_copied_authenticated_state_cannot_authorize_cleanup_of_another_temp_subtree(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_value, key_value = _handle(started)
    state_dir = Path(state_value)
    key_file = Path(key_value)
    copied_instance = str(uuid.uuid4())
    temp_root = Path(tempfile.gettempdir()).resolve()
    copied_state = temp_root / f"atlas-work-guard-{copied_instance}"
    copied_key = temp_root / f"atlas-work-guard-key-{copied_instance}.key"
    shutil.copytree(state_dir, copied_state)
    shutil.copyfile(key_file, copied_key)
    unrelated = copied_state / "unrelated.keep"
    unrelated.write_text("do not delete", encoding="utf-8")

    result = _run(
        "cleanup", "--root", str(root), "--state", str(copied_state),
        "--key-file", str(copied_key), "--format", "json"
    )

    assert result.returncode == 2
    assert copied_state.is_dir()
    assert unrelated.read_text(encoding="utf-8") == "do not delete"
    assert state_dir.is_dir()
    assert key_file.is_file()
    shutil.rmtree(copied_state)
    copied_key.unlink()
    assert _run(
        "cleanup", "--root", str(root), "--state", str(state_dir),
        "--key-file", str(key_file), "--format", "json"
    ).returncode == 0


def test_recomputed_plain_checksum_cannot_authorize_widened_scope(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_value, key_value = _handle(started)
    state_dir = Path(state_value)
    state_path = state_dir / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["scope"]["paths"].append("atlas-package.json")
    forged = (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8")
    state_path.write_bytes(forged)
    (state_dir / "state.sha256").write_text(hashlib.sha256(forged).hexdigest(), encoding="ascii")

    result = _run(
        "validate", "--root", str(root), "--state", str(state_dir),
        "--key-file", key_value, "--format", "json"
    )

    assert result.returncode == 2
    assert "hmac authentication failed" in result.stderr.casefold()


def test_restore_rejects_snapshot_and_manifest_tampered_together(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_value, key_value = _handle(started)
    state_dir = Path(state_value)
    snapshot_file = state_dir / "pre" / relative
    malicious = b'{"tampered": true}'
    snapshot_file.write_bytes(malicious)
    snapshot_manifest = state_dir / "pre/snapshot.json"
    manifest = json.loads(snapshot_manifest.read_text(encoding="utf-8"))
    manifest["files"][relative] = hashlib.sha256(malicious).hexdigest()
    snapshot_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    original = (root / relative).read_bytes()

    result = _run(
        "restore", "--root", str(root), "--state", str(state_dir), "--key-file", key_value,
        "--to", "pre", "--format", "json"
    )

    assert result.returncode == 2
    assert "tampered" in result.stderr.casefold()
    assert (root / relative).read_bytes() == original


def test_start_rejects_reparse_points_at_governed_roots_and_worktree_ancestors(tmp_path: Path):
    root = _repo(tmp_path / "direct")
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.bin").write_bytes(b"outside")
    _directory_link(root / "_curated", outside)

    governed = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    assert governed.returncode == 2
    assert "reparse" in governed.stderr.casefold()

    actual_parent = tmp_path / "actual"
    actual_root = _repo(actual_parent)
    _write_staging(actual_root, relative)
    alias_parent = tmp_path / "alias"
    _directory_link(alias_parent, actual_parent)
    ancestor = _run(
        "start", "--root", str(alias_parent / "atlas"), "--path", relative, "--format", "json"
    )
    assert ancestor.returncode == 2
    assert "reparse" in ancestor.stderr.casefold()


def test_checkpoint_and_restore_materialized_preserve_new_file_bytes(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_curated/components/example/new.md"
    started = _run("start", "--root", str(root), "--missing-path", relative, "--format", "json")
    state_dir, key_file = _handle(started)
    materialized = root / relative
    materialized.parent.mkdir(parents=True)
    expected = b"---\r\nid: comp.example\r\n---\r\n\r\nExact proposal.\r\n"
    materialized.write_bytes(expected)

    checkpoint = _run(
        "checkpoint", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )
    assert checkpoint.returncode == 0, checkpoint.stderr
    materialized.unlink()

    restored = _run(
        "restore", "--root", str(root), "--state", state_dir, "--key-file", key_file,
        "--to", "materialized", "--format", "json"
    )
    assert restored.returncode == 0, restored.stderr
    assert materialized.read_bytes() == expected


def test_explicit_generated_effect_is_the_only_generated_file_restored(tmp_path: Path):
    root = _repo(tmp_path)
    generated_relative = "_curated/maps/example/generated.json"
    started = _run(
        "start", "--root", str(root), "--generated-path", generated_relative,
        "--format", "json"
    )
    assert started.returncode == 0, started.stderr
    state_dir, key_file = _handle(started)
    generated = root / generated_relative
    generated.parent.mkdir(parents=True)
    expected = b'{"generated": true}\n'
    generated.write_bytes(expected)
    checkpoint = _run(
        "checkpoint", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )
    assert checkpoint.returncode == 0, checkpoint.stderr
    generated.unlink()

    restored = _run(
        "restore", "--root", str(root), "--state", state_dir, "--key-file", key_file,
        "--to", "materialized", "--format", "json"
    )

    assert restored.returncode == 0, restored.stderr
    assert generated.read_bytes() == expected


@pytest.mark.parametrize("target", ["pre", "materialized"])
def test_restore_changes_only_approved_files_and_preserves_unrelated_governed_bytes(
    tmp_path: Path, target: str
):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    approved = _write_staging(root, relative)
    pre_bytes = approved.read_bytes()
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_dir, key_file = _handle(started)
    materialized_bytes = pre_bytes + b"\nMaterialized evidence.\n"
    approved.write_bytes(materialized_bytes)
    checkpoint = _run(
        "checkpoint", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )
    assert checkpoint.returncode == 0, checkpoint.stderr
    approved.write_bytes(b"damaged approved content")
    unrelated = root / "contracts/map-fields.yaml"
    unrelated_bytes = b"unrelated governed change after checkpoint"
    unrelated.write_bytes(unrelated_bytes)

    restored = _run(
        "restore", "--root", str(root), "--state", state_dir, "--key-file", key_file,
        "--to", target, "--format", "json"
    )

    assert restored.returncode == 0, restored.stderr
    assert approved.read_bytes() == (pre_bytes if target == "pre" else materialized_bytes)
    assert unrelated.read_bytes() == unrelated_bytes


def test_restore_pre_removes_new_approved_page_without_touching_unrelated_governed_bytes(
    tmp_path: Path,
):
    root = _repo(tmp_path)
    relative = "_curated/runbooks/new.md"
    manifest = root / "atlas-package.json"
    started = _run("start", "--root", str(root), "--missing-path", relative, "--format", "json")
    state_dir, key_file = _handle(started)
    _write_runbook(root, relative, "Proposal.\n")
    manifest.write_text("{}", encoding="utf-8")

    restored = _run(
        "restore", "--root", str(root), "--state", state_dir, "--key-file", key_file,
        "--to", "pre", "--format", "json"
    )

    assert restored.returncode == 0, restored.stderr
    assert not (root / relative).exists()
    assert manifest.read_bytes() == b"{}"


def test_restore_rolls_back_every_mutation_when_apply_fails(tmp_path: Path, monkeypatch):
    root = _repo(tmp_path)
    first_relative = "_staging/runbooks/STG-20260817-example.md"
    second_relative = "_staging/runbooks/STG-20260817-second.md"
    first = _write_staging(root, first_relative)
    second = _write_staging(
        root, second_relative, record_id="STG-20260817-second"
    )
    handle = work_guard.start_guard(root, paths=[first_relative, second_relative])
    work_guard.checkpoint_guard(root, handle.state_dir, handle.key_file)
    first.write_bytes(b"damaged first approved file")
    second.write_bytes(b"damaged second approved file")
    extra = root / "_intake/extra.bin"
    extra.parent.mkdir(parents=True)
    extra.write_bytes(b"preserve on rollback")
    before = {
        first: first.read_bytes(),
        second: second.read_bytes(),
        extra: extra.read_bytes(),
    }
    real_write_bytes = Path.write_bytes
    root_writes = 0

    def fail_second_root_write(path: Path, data: bytes) -> int:
        nonlocal root_writes
        if root in path.parents:
            root_writes += 1
            if root_writes == 2:
                raise OSError("injected apply failure")
        return real_write_bytes(path, data)

    monkeypatch.setattr(Path, "write_bytes", fail_second_root_write)

    with pytest.raises(work_guard.WorkGuardError, match="rolled back"):
        work_guard.restore_guard(root, handle.state_dir, handle.key_file, "materialized")

    assert {path: path.read_bytes() for path in before} == before


def test_validate_blocks_current_scope_issues_but_advises_unchanged_unrelated_baseline(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative, status="not-a-status")
    (root / "unrelated.md").write_text("[missing](nowhere.md)\n", encoding="utf-8")
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_dir, key_file = _handle(started)

    result = _run(
        "validate", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )

    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert any(
        item["issue"]["code"] == "ATLAS006" and "current-path" in item["reasons"]
        for item in payload["blocking"]
    ), payload
    assert any(
        item["issue"]["code"] == "ATLAS008" and item["reasons"] == ["unchanged-baseline"]
        for item in payload["advisory"]
    )


def test_validate_treats_start_resolved_id_owner_as_approved_current_path(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative, status="not-a-status")
    started = _run(
        "start",
        "--root",
        str(root),
        "--id",
        "STG-20260817-example",
        "--format",
        "json",
    )
    state_dir, key_file = _handle(started)

    result = _run(
        "validate", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )

    payload = json.loads(result.stdout)
    status_issue = next(item for item in payload["blocking"] if item["issue"]["code"] == "ATLAS006")
    assert status_issue["reasons"] == ["current-path"]


def test_restore_resolves_approved_ids_to_exact_owner_pages_at_start(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    owner = _write_staging(root, relative)
    original = owner.read_bytes()
    started = _run(
        "start", "--root", str(root), "--id", "STG-20260817-example", "--format", "json"
    )
    state_dir, key_file = _handle(started)
    owner.write_bytes(b"damaged owner")

    restored = _run(
        "restore", "--root", str(root), "--state", state_dir, "--key-file", key_file,
        "--to", "pre", "--format", "json"
    )

    assert restored.returncode == 0, restored.stderr
    assert owner.read_bytes() == original


def test_validate_blocks_unexpected_out_of_scope_repository_changes(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_dir, key_file = _handle(started)
    contract = root / "contracts/map-fields.yaml"
    contract.write_text(contract.read_text(encoding="utf-8") + "\n# unexpected\n", encoding="utf-8")

    result = _run(
        "validate", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )

    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    scope_issue = next(
        item for item in payload["blocking"] if item["issue"]["code"] == "ATLAS-WORK-GUARD-SCOPE"
    )
    assert scope_issue["issue"]["path"] == "contracts/map-fields.yaml"
    assert scope_issue["reasons"] == ["shared-contract-path", "unexpected-out-of-scope-change"]


def test_validate_inventories_ignored_untracked_governed_bytes(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    (root / ".gitignore").write_text("_intake/ignored.bin\n", encoding="utf-8")
    ignored = root / "_intake/ignored.bin"
    ignored.parent.mkdir(parents=True)
    ignored.write_bytes(b"baseline ignored bytes")
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_dir, key_file = _handle(started)
    ignored.write_bytes(b"changed ignored bytes")

    result = _run(
        "validate", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )

    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    issue = next(
        item
        for item in payload["blocking"]
        if item["issue"]["path"] == "_intake/ignored.bin"
    )
    assert issue["reasons"] == ["unexpected-out-of-scope-change"]


def test_validate_blocks_index_only_git_state_drift(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_dir, key_file = _handle(started)
    subprocess.run(["git", "add", "--", relative], cwd=root, check=True)

    result = _run(
        "validate", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )

    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    issue = next(
        item
        for item in payload["blocking"]
        if item["issue"]["code"] == "ATLAS-WORK-GUARD-GIT"
    )
    assert issue["reasons"] == ["unexpected-index-state"]


def test_cleanup_removes_only_the_guard_temporary_directory(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_value, key_value = _handle(started)
    state_dir = Path(state_value)
    key_file = Path(key_value)
    neighboring_file = state_dir.parent / f"atlas-work-guard-unrelated-{uuid.uuid4()}.keep"
    neighboring_file.write_text("keep", encoding="utf-8")

    result = _run(
        "cleanup", "--root", str(root), "--state", str(state_dir),
        "--key-file", str(key_file), "--format", "json"
    )

    assert result.returncode == 0, result.stderr
    assert not state_dir.exists()
    assert not key_file.exists()
    assert neighboring_file.read_text(encoding="utf-8") == "keep"
    neighboring_file.unlink()
    assert root.is_dir()


def test_cleanup_rejects_reparse_points_inside_guard_state(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, relative)
    started = _run("start", "--root", str(root), "--path", relative, "--format", "json")
    state_value, key_value = _handle(started)
    state_dir = Path(state_value)
    outside = tmp_path / "cleanup-outside"
    outside.mkdir()
    marker = outside / "keep.txt"
    marker.write_text("keep", encoding="utf-8")
    _directory_link(state_dir / "unexpected-link", outside)

    result = _run(
        "cleanup", "--root", str(root), "--state", str(state_dir),
        "--key-file", key_value, "--format", "json"
    )

    assert result.returncode == 2
    assert "reparse" in result.stderr.casefold()
    assert marker.read_text(encoding="utf-8") == "keep"


def test_start_rejects_an_empty_persistence_scope(tmp_path: Path):
    root = _repo(tmp_path)

    result = _run("start", "--root", str(root), "--format", "json")

    assert result.returncode == 2
    assert "at least one approved path, missing path, generated path, or ID is required" in result.stderr


def test_start_captures_structured_generation_preflight_baseline(tmp_path: Path):
    root = _repo(tmp_path)
    unrelated = "_curated/runbooks/unrelated.md"
    _write_runbook(
        root,
        unrelated,
        "## Open questions / coverage limits\n\nMalformed body content.\n",
    )
    approved = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, approved)

    started = _run("start", "--root", str(root), "--path", approved, "--format", "json")

    assert started.returncode == 0, started.stderr
    state_dir, _ = _handle(started)
    state = json.loads((Path(state_dir) / "state.json").read_text(encoding="utf-8"))
    issue = next(
        item for item in state["baseline_generation_issues"] if item["path"] == unrelated
    )
    assert issue["record_id"] == "runbook.example"
    assert isinstance(issue["message"], str) and issue["message"]
    assert set(issue) == {"path", "record_id", "message"}


def test_validate_advises_unchanged_unrelated_generation_preflight_issue(tmp_path: Path):
    root = _repo(tmp_path)
    unrelated = "_curated/runbooks/unrelated.md"
    _write_runbook(
        root,
        unrelated,
        "## Open questions / coverage limits\n\nMalformed body content.\n",
    )
    approved = "_staging/runbooks/STG-20260817-example.md"
    _write_staging(root, approved)
    started = _run("start", "--root", str(root), "--path", approved, "--format", "json")
    state_dir, key_file = _handle(started)

    result = _run(
        "validate", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "advisory"
    issue = next(
        item
        for item in payload["advisory"]
        if item["issue"]["code"] == "ATLAS-WORK-GUARD-REBUILD"
    )
    assert issue["issue"]["path"] == unrelated
    assert issue["issue"]["record_id"] == "runbook.example"
    assert issue["reasons"] == ["unchanged-baseline"]


def test_validate_distinguishes_strict_rebuild_inconsistency_after_clean_lint(tmp_path: Path):
    root = _repo(tmp_path)
    relative = "_curated/runbooks/example.md"
    started = _run("start", "--root", str(root), "--missing-path", relative, "--format", "json")
    state_dir, key_file = _handle(started)
    _write_runbook(
        root,
        relative,
        "## Open questions / coverage limits\n\nThis malformed section is neither empty nor a table.\n",
    )

    result = _run(
        "validate", "--root", str(root), "--state", state_dir,
        "--key-file", key_file, "--format", "json"
    )

    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    inconsistency = next(
        item
        for item in payload["blocking"]
        if item["issue"]["code"] == "ATLAS-WORK-GUARD-REBUILD"
    )
    assert inconsistency["issue"]["record_id"] == "runbook.example"
    assert set(inconsistency["reasons"]) == {
        "current-id",
        "current-path",
        "new-generator-issue",
        "strict-rebuild-inconsistency",
    }

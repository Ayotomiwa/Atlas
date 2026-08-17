from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from dataclasses import dataclass
import hmac
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import tempfile
import uuid

from scripts.atlas_lint import lint_repository
from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.maps import MapBuildError
from scripts.rebuild_atlas import generation_preflight


STATE_VERSION = "atlas-work-guard/1.2"
STATE_PREFIX = "atlas-work-guard-"
KEY_PREFIX = "atlas-work-guard-key-"
INSTANCE_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
GOVERNED_ROOTS = ("_curated", "_staging", "_intake", "taxonomy", "contracts")
GOVERNED_FILES = {"atlas-package.json"}
INVENTORY_EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".venv",
    "node_modules",
    "target",
    "build",
}
INVENTORY_EXCLUDED_FILES = {".git"}


class WorkGuardError(ValueError):
    pass


@dataclass(frozen=True)
class GuardHandle:
    state_dir: Path
    key_file: Path


def _is_reparse_point(path: Path) -> bool:
    try:
        value = path.lstat()
    except OSError:
        return False
    attributes = getattr(value, "st_file_attributes", 0)
    is_junction = getattr(path, "is_junction", lambda: False)
    return bool(
        path.is_symlink()
        or is_junction()
        or attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _assert_no_reparse_ancestors(path: Path, *, label: str) -> None:
    absolute = Path(os.path.abspath(path))
    chain = [absolute, *absolute.parents]
    for candidate in reversed(chain):
        if _is_reparse_point(candidate):
            raise WorkGuardError(f"{label} contains a reparse point: {candidate}")


def _preflight_tree(tree: Path, *, label: str) -> None:
    _assert_no_reparse_ancestors(tree, label=label)
    resolved_tree = tree.resolve(strict=True)
    for current, directories, filenames in os.walk(tree, followlinks=False):
        current_path = Path(current)
        for name in [*directories, *filenames]:
            candidate = current_path / name
            _assert_no_reparse_ancestors(candidate, label=label)
            try:
                candidate.resolve(strict=True).relative_to(resolved_tree)
            except ValueError as exc:
                raise WorkGuardError(f"{label} escapes its root: {candidate}") from exc


def _repository_identity(root: Path) -> dict[str, str]:
    top = _git(root, "rev-parse", "--show-toplevel")
    git_dir = _git(root, "rev-parse", "--path-format=absolute", "--git-dir")
    common_dir = _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if any(result.returncode != 0 for result in (top, git_dir, common_dir)):
        raise WorkGuardError("trusted root must be a Git worktree")
    worktree_root = Path(top.stdout.strip()).resolve()
    if worktree_root != root:
        raise WorkGuardError(f"trusted root must be the Git worktree root: {worktree_root}")
    return {
        "worktree_root": str(worktree_root),
        "git_dir": str(Path(git_dir.stdout.strip()).resolve()),
        "git_common_dir": str(Path(common_dir.stdout.strip()).resolve()),
    }


def _state_bytes(state: dict) -> bytes:
    return (json.dumps(state, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_state(state_dir: Path, state: dict, key: bytes) -> None:
    _assert_no_reparse_ancestors(state_dir, label="guard state path")
    data = _state_bytes(state)
    state_path = state_dir / "state.json"
    seal_path = state_dir / "state.hmac"
    _assert_no_reparse_ancestors(state_path, label="guard state write target")
    _assert_no_reparse_ancestors(seal_path, label="guard state write target")
    state_path.write_bytes(data)
    seal_path.write_text(hmac.new(key, data, sha256).hexdigest() + "\n", encoding="ascii")


def _load_state(
    state_dir: str | Path,
    key_file: str | Path,
    trusted_root: str | Path,
) -> tuple[Path, dict, Path, Path, bytes]:
    raw_state_dir = Path(os.path.abspath(state_dir))
    _assert_no_reparse_ancestors(raw_state_dir, label="guard state path")
    state_dir = raw_state_dir.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if state_dir.parent != temp_root or not state_dir.name.startswith(STATE_PREFIX):
        raise WorkGuardError("guard state path does not use the authenticated temporary layout")
    instance_id = state_dir.name.removeprefix(STATE_PREFIX)
    if not INSTANCE_RE.fullmatch(instance_id):
        raise WorkGuardError("guard state path has an invalid instance identity")
    expected_state_dir = temp_root / f"{STATE_PREFIX}{instance_id}"
    if state_dir != expected_state_dir:
        raise WorkGuardError("guard state path is not the canonical instance directory")
    raw_key_file = Path(os.path.abspath(key_file))
    _assert_no_reparse_ancestors(raw_key_file, label="guard key path")
    key_file = raw_key_file.resolve(strict=False)
    expected_key_file = temp_root / f"{KEY_PREFIX}{instance_id}.key"
    if key_file != expected_key_file:
        raise WorkGuardError("guard key path does not match the authenticated instance layout")
    if not key_file.is_file():
        raise WorkGuardError("guard capability key file is missing")
    state_path = state_dir / "state.json"
    seal_path = state_dir / "state.hmac"
    _assert_no_reparse_ancestors(state_path, label="guard state read target")
    _assert_no_reparse_ancestors(seal_path, label="guard state read target")
    try:
        key = key_file.read_bytes()
        if len(key) != 32:
            raise WorkGuardError("guard capability key has an invalid length")
        data = state_path.read_bytes()
        supplied_tag = seal_path.read_text(encoding="ascii").strip()
        expected_tag = hmac.new(key, data, sha256).hexdigest()
        if not hmac.compare_digest(supplied_tag, expected_tag):
            raise WorkGuardError("guard state HMAC authentication failed")
        state = json.loads(data.decode("utf-8"))
        if _state_bytes(state) != data:
            raise WorkGuardError("guard state bytes are not in canonical form")
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkGuardError(f"invalid guard state: {exc}") from exc
    if state.get("schema_version") != STATE_VERSION:
        raise WorkGuardError("unsupported guard state schema")
    if (
        state.get("instance_id") != instance_id
        or state.get("state_dir") != str(state_dir)
        or state.get("key_fingerprint") != sha256(key).hexdigest()
    ):
        raise WorkGuardError("guard state instance or key identity is tampered")
    raw_root = Path(os.path.abspath(trusted_root))
    _assert_no_reparse_ancestors(raw_root, label="trusted root")
    root = raw_root.resolve()
    if not root.is_dir() or state_dir == root or root in state_dir.parents:
        raise WorkGuardError("trusted repository root is invalid")
    identity = _repository_identity(root)
    if state.get("root") != str(root) or state.get("repository_identity") != identity:
        raise WorkGuardError("guard state is tampered or belongs to a different Git worktree")
    return state_dir, state, root, key_file, key


def _contained_relative(root: Path, value: str, *, must_exist: bool | None = None) -> tuple[str, Path]:
    if not isinstance(value, str) or not value.strip():
        raise WorkGuardError("scope paths must be non-empty repository-relative paths")
    raw = Path(value)
    if raw.is_absolute() or raw.drive or ".." in raw.parts:
        raise WorkGuardError(f"path must stay within the repository: {value}")
    lexical_candidate = root / raw
    _assert_no_reparse_ancestors(lexical_candidate, label="repository path")
    candidate = lexical_candidate.resolve(strict=False)
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise WorkGuardError(f"path must stay within the repository: {value}") from exc
    if candidate.exists() and candidate.is_symlink():
        raise WorkGuardError(f"symbolic-link scope paths are not supported: {value}")
    if must_exist is True and not candidate.is_file():
        raise WorkGuardError(f"approved path does not exist as a file: {value}")
    if must_exist is False and candidate.exists():
        raise WorkGuardError(f"approved missing path already exists: {value}")
    return relative.as_posix(), candidate


def _governed_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    for name in sorted(GOVERNED_FILES):
        path = root / name
        _assert_no_reparse_ancestors(path, label="governed path")
        if path.is_file():
            paths.append(path)
    for name in GOVERNED_ROOTS:
        base = root / name
        _assert_no_reparse_ancestors(base, label="governed root")
        if not base.exists():
            continue
        for current, directories, filenames in os.walk(base, followlinks=False):
            current_path = Path(current)
            _assert_no_reparse_ancestors(current_path, label="governed traversal")
            for name in sorted(directories):
                _assert_no_reparse_ancestors(current_path / name, label="governed traversal")
            for name in sorted(filenames):
                path = current_path / name
                _assert_no_reparse_ancestors(path, label="governed content")
                if path.is_file():
                    try:
                        path.resolve().relative_to(root)
                    except ValueError as exc:
                        raise WorkGuardError(f"governed content escapes repository: {path}") from exc
                    paths.append(path)
    return paths


def _snapshot(root: Path, destination: Path, targets: list[str]) -> str:
    _assert_no_reparse_ancestors(destination.parent, label="snapshot destination")
    files: dict[str, str] = {}
    planned: list[tuple[str, bytes]] = []
    resolved_destination = destination.resolve(strict=False)
    normalized_targets: list[str] = []
    for value in sorted(set(targets)):
        relative, source = _contained_relative(root, value)
        normalized_targets.append(relative)
        if not source.exists():
            continue
        if not source.is_file():
            raise WorkGuardError(f"scope target must be an exact file path: {relative}")
        _assert_no_reparse_ancestors(source, label="snapshot source")
        data = source.read_bytes()
        target = (destination / Path(relative)).resolve(strict=False)
        try:
            target.relative_to(resolved_destination)
        except ValueError as exc:
            raise WorkGuardError(f"snapshot target escapes destination: {relative}") from exc
        planned.append((relative, data))
        files[relative] = sha256(data).hexdigest()
    destination.mkdir(parents=True, exist_ok=False)
    for relative, data in planned:
        target = destination / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        _assert_no_reparse_ancestors(target, label="snapshot target")
        target.write_bytes(data)
    manifest_data = (
        json.dumps(
            {"targets": normalized_targets, "files": files}, indent=2, sort_keys=True
        )
        + "\n"
    ).encode("utf-8")
    manifest_path = destination / "snapshot.json"
    _assert_no_reparse_ancestors(manifest_path, label="snapshot manifest target")
    manifest_path.write_bytes(manifest_data)
    return sha256(manifest_data).hexdigest()


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )


def _file_digest(path: Path) -> str | None:
    if path.is_symlink():
        return "symlink:" + os.readlink(path)
    if not path.is_file():
        return None
    return sha256(path.read_bytes()).hexdigest()


def _repo_inventory(root: Path) -> dict[str, str | None]:
    inventory: dict[str, str | None] = {}
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = sorted(
            name for name in directories if name not in INVENTORY_EXCLUDED_DIRS
        )
        for name in directories:
            _assert_no_reparse_ancestors(current_path / name, label="repository inventory")
        for name in sorted(filenames):
            if name in INVENTORY_EXCLUDED_FILES:
                continue
            path = current_path / name
            _assert_no_reparse_ancestors(path, label="repository inventory")
            relative, contained = _contained_relative(root, path.relative_to(root).as_posix())
            inventory[relative] = _file_digest(contained)
    for path in _governed_paths(root):
        relative = path.relative_to(root).as_posix()
        inventory[relative] = _file_digest(path)
    return inventory


def _repo_state(root: Path) -> dict[str, object]:
    head_result = _git(root, "rev-parse", "--verify", "HEAD")
    status_result = _git(root, "status", "--porcelain=v2", "-z", "--untracked-files=all")
    index_result = _git(root, "ls-files", "--stage", "-z")
    if status_result.returncode != 0 or index_result.returncode != 0:
        raise WorkGuardError("cannot capture Git worktree and index state")
    return {
        "head": head_result.stdout.strip() if head_result.returncode == 0 else None,
        "porcelain_v2_z": status_result.stdout,
        "index_entries_z": index_result.stdout,
        "files": _repo_inventory(root),
    }


def _generation_preflight_issues(root: Path) -> list[dict[str, str | None]]:
    try:
        _, _, errors = generation_preflight(root)
    except (MapBuildError, ValueError) as exc:
        raw_path = getattr(exc, "path", None)
        issues = [
            {
                "path": Path(raw_path).as_posix() if raw_path else ".",
                "record_id": getattr(exc, "record_id", None),
                "message": str(exc),
            }
        ]
    else:
        issues = [
            {
                "path": item.path,
                "record_id": item.record_id,
                "message": item.message,
            }
            for item in errors
        ]
    return sorted(
        issues,
        key=lambda item: (
            str(item["path"]), str(item["record_id"] or ""), str(item["message"])
        ),
    )


def _porcelain_records(raw: object) -> dict[str, str]:
    if not isinstance(raw, str):
        return {}
    tokens = raw.split("\0")
    records: dict[str, str] = {}
    index = 0
    while index < len(tokens):
        record = tokens[index]
        index += 1
        if not record:
            continue
        kind = record[0]
        if kind == "1":
            parts = record.split(" ", 8)
            if len(parts) == 9:
                records[parts[8]] = record
        elif kind == "2":
            parts = record.split(" ", 9)
            original = tokens[index] if index < len(tokens) else ""
            index += 1
            if len(parts) == 10:
                records[parts[9]] = record + "\0" + original
                if original:
                    records[original] = record + "\0" + original
        elif kind == "u":
            parts = record.split(" ", 10)
            if len(parts) == 11:
                records[parts[10]] = record
        elif kind in {"?", "!"} and len(record) > 2:
            records[record[2:]] = record
    return records


def start_guard(
    root: str | Path,
    *,
    paths: list[str] | None = None,
    missing_paths: list[str] | None = None,
    generated_paths: list[str] | None = None,
    ids: list[str] | None = None,
) -> GuardHandle:
    raw_root = Path(os.path.abspath(root))
    _assert_no_reparse_ancestors(raw_root, label="trusted root")
    root = raw_root.resolve()
    if not root.is_dir():
        raise WorkGuardError(f"repository root does not exist: {root}")
    identity = _repository_identity(root)
    approved = sorted({_contained_relative(root, value, must_exist=True)[0] for value in paths or []})
    missing = sorted(
        {_contained_relative(root, value, must_exist=False)[0] for value in missing_paths or []}
    )
    generated: list[str] = []
    for value in generated_paths or []:
        relative, candidate = _contained_relative(root, value)
        if candidate.exists() and not candidate.is_file():
            raise WorkGuardError(f"scope target must be an exact file path: {relative}")
        generated.append(relative)
    generated = sorted(set(generated))
    identifiers = sorted({value.strip() for value in ids or [] if value.strip()})
    if not approved and not missing and not generated and not identifiers:
        raise WorkGuardError(
            "at least one approved path, missing path, generated path, or ID is required"
        )
    owners, _ = _record_owners(root)
    owner_paths = sorted(
        {
            owner_path
            for identifier in identifiers
            for owner_path in owners.get(identifier, set())
        }
    )
    resolved_scope_paths = sorted(
        set(approved) | set(missing) | set(generated) | set(owner_paths)
    )
    instance_id = str(uuid.uuid4())
    temp_root = Path(tempfile.gettempdir()).resolve()
    state_dir = temp_root / f"{STATE_PREFIX}{instance_id}"
    key_file = temp_root / f"{KEY_PREFIX}{instance_id}.key"
    key = secrets.token_bytes(32)
    _assert_no_reparse_ancestors(state_dir, label="guard state path")
    _assert_no_reparse_ancestors(key_file, label="guard key path")
    try:
        if state_dir == root or root in state_dir.parents:
            raise WorkGuardError("operating-system temporary storage resolves inside the repository")
        state_dir.mkdir(mode=0o700)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_BINARY"):
            flags |= os.O_BINARY
        descriptor = os.open(key_file, flags, 0o600)
        try:
            os.write(descriptor, key)
        finally:
            os.close(descriptor)
        pre_manifest_digest = _snapshot(root, state_dir / "pre", resolved_scope_paths)
        state = {
            "schema_version": STATE_VERSION,
            "instance_id": instance_id,
            "state_dir": str(state_dir),
            "key_fingerprint": sha256(key).hexdigest(),
            "root": str(root),
            "repository_identity": identity,
            "scope": {"paths": approved, "missing_paths": missing, "ids": identifiers},
            "generated_paths": generated,
            "record_owner_paths": owner_paths,
            "resolved_scope_paths": resolved_scope_paths,
            "baseline_issues": lint_repository(root),
            "baseline_generation_issues": _generation_preflight_issues(root),
            "repo_state": _repo_state(root),
            "snapshots": {
                "pre": {"directory": "pre", "manifest_sha256": pre_manifest_digest}
            },
        }
        _write_state(state_dir, state, key)
    except Exception:
        shutil.rmtree(state_dir, ignore_errors=True)
        try:
            key_file.unlink()
        except FileNotFoundError:
            pass
        raise
    return GuardHandle(state_dir=state_dir, key_file=key_file)


def checkpoint_guard(root: str | Path, state_dir: str | Path, key_file: str | Path) -> Path:
    state_dir, state, root, _, key = _load_state(state_dir, key_file, root)
    materialized = state_dir / "materialized"
    if materialized.exists():
        raise WorkGuardError("materialized checkpoint already exists")
    manifest_digest = _snapshot(root, materialized, _resolved_scope_paths(root, state))
    state["snapshots"]["materialized"] = {
        "directory": "materialized",
        "manifest_sha256": manifest_digest,
    }
    _write_state(state_dir, state, key)
    return state_dir


def _resolved_scope_paths(root: Path, state: dict) -> list[str]:
    values = state.get("resolved_scope_paths")
    if not isinstance(values, list):
        raise WorkGuardError("guard resolved scope is tampered")
    normalized: list[str] = []
    for value in values:
        relative, _ = _contained_relative(root, value)
        normalized.append(relative)
    if normalized != sorted(set(normalized)):
        raise WorkGuardError("guard resolved scope is not canonical")
    return normalized


def _snapshot_content(
    state_dir: Path, snapshot_spec: dict, root: Path, expected_targets: list[str]
) -> dict[str, bytes]:
    snapshot_name = snapshot_spec.get("directory")
    manifest_digest = snapshot_spec.get("manifest_sha256")
    if not isinstance(snapshot_name, str) or not isinstance(manifest_digest, str):
        raise WorkGuardError("guard snapshot metadata is tampered")
    lexical_snapshot = state_dir / snapshot_name
    _assert_no_reparse_ancestors(lexical_snapshot, label="snapshot path")
    snapshot = lexical_snapshot.resolve()
    try:
        snapshot.relative_to(state_dir)
    except ValueError as exc:
        raise WorkGuardError("snapshot path escapes guard state") from exc
    try:
        manifest_path = snapshot / "snapshot.json"
        _assert_no_reparse_ancestors(manifest_path, label="snapshot manifest")
        manifest_data = manifest_path.read_bytes()
        if sha256(manifest_data).hexdigest() != manifest_digest:
            raise WorkGuardError("guard snapshot manifest is tampered")
        manifest = json.loads(manifest_data.decode("utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkGuardError(f"invalid snapshot: {exc}") from exc
    expected = manifest.get("files")
    if not isinstance(expected, dict):
        raise WorkGuardError("invalid snapshot file inventory")
    targets = manifest.get("targets")
    if targets != expected_targets:
        raise WorkGuardError("guard snapshot target inventory is tampered")
    if not set(expected).issubset(expected_targets):
        raise WorkGuardError("snapshot file inventory exceeds approved scope")
    content: dict[str, bytes] = {}
    for relative, digest in sorted(expected.items()):
        if not isinstance(relative, str) or not isinstance(digest, str):
            raise WorkGuardError("invalid snapshot file inventory entry")
        normalized, target_path = _contained_relative(root, relative)
        del target_path
        source = snapshot / Path(normalized)
        _assert_no_reparse_ancestors(source, label="snapshot content")
        try:
            source.resolve(strict=True).relative_to(snapshot)
        except (FileNotFoundError, ValueError) as exc:
            raise WorkGuardError(f"snapshot content escapes guard state: {relative}") from exc
        if source.is_symlink() or not source.is_file():
            raise WorkGuardError(f"snapshot content is not a regular file: {relative}")
        data = source.read_bytes()
        if sha256(data).hexdigest() != digest:
            raise WorkGuardError(f"snapshot content hash mismatch: {relative}")
        content[normalized] = data
    return content


def _current_scope_content(root: Path, targets: list[str]) -> dict[str, bytes]:
    content: dict[str, bytes] = {}
    for relative in targets:
        _, path = _contained_relative(root, relative)
        if not path.exists():
            continue
        if not path.is_file():
            raise WorkGuardError(f"scope target must be an exact file path: {relative}")
        _assert_no_reparse_ancestors(path, label="governed read target")
        content[relative] = path.read_bytes()
    return content


def _preflight_content_plan(
    root: Path, targets: list[str], content: dict[str, bytes]
) -> None:
    if not set(content).issubset(targets):
        raise WorkGuardError("restore content plan exceeds approved scope")
    for relative in targets:
        _, path = _contained_relative(root, relative)
        if path.exists() and not path.is_file():
            raise WorkGuardError(f"scope target must be an exact file path: {relative}")
        if path.exists() and relative not in content:
            _assert_no_reparse_ancestors(path, label="restore delete target")
    for relative in content:
        _, target = _contained_relative(root, relative)
        _assert_no_reparse_ancestors(target, label="restore write target")


def _apply_content_plan(root: Path, targets: list[str], content: dict[str, bytes]) -> None:
    for relative in sorted(targets, reverse=True):
        _, path = _contained_relative(root, relative)
        if path.exists() and relative not in content:
            if not path.is_file():
                raise WorkGuardError(f"scope target must be an exact file path: {relative}")
            path.unlink()
    for relative, data in sorted(content.items()):
        _, target = _contained_relative(root, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        _assert_no_reparse_ancestors(target, label="restore write target")
        target.write_bytes(data)


def restore_guard(
    root: str | Path,
    state_dir: str | Path,
    key_file: str | Path,
    target: str,
) -> Path:
    state_dir, state, root, _, _ = _load_state(state_dir, key_file, root)
    if target not in {"pre", "materialized"}:
        raise WorkGuardError("restore target must be pre or materialized")
    snapshot_spec = state.get("snapshots", {}).get(target)
    if not isinstance(snapshot_spec, dict):
        raise WorkGuardError(f"no {target} snapshot exists")
    targets = _resolved_scope_paths(root, state)
    desired = _snapshot_content(state_dir, snapshot_spec, root, targets)
    before = _current_scope_content(root, targets)
    _preflight_content_plan(root, targets, desired)
    _preflight_content_plan(root, targets, before)
    try:
        _apply_content_plan(root, targets, desired)
    except Exception as apply_error:
        try:
            _preflight_content_plan(root, targets, before)
            _apply_content_plan(root, targets, before)
        except Exception as rollback_error:
            raise WorkGuardError(
                f"restore failed and rollback also failed: apply={apply_error}; rollback={rollback_error}"
            ) from apply_error
        raise WorkGuardError(f"restore failed and was rolled back: {apply_error}") from apply_error
    return root


def _issue_fingerprint(item: dict) -> str:
    return json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _record_owners(root: Path) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    owners: dict[str, set[str]] = {}
    ids_by_path: dict[str, set[str]] = {}
    for path in _governed_paths(root):
        if path.suffix.lower() != ".md" or not path.parts:
            continue
        relative = path.relative_to(root).as_posix()
        if not relative.startswith(("_curated/", "_staging/")):
            continue
        try:
            frontmatter, _ = parse_frontmatter(path)
        except Exception:
            continue
        identifiers: set[str] = set()
        if isinstance(frontmatter.get("id"), str):
            identifiers.add(frontmatter["id"])
        for field in ("promoted_resources", "assets"):
            for item in frontmatter.get(field) if isinstance(frontmatter.get(field), list) else []:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    identifiers.add(item["id"])
        ids_by_path[relative] = identifiers
        for identifier in identifiers:
            owners.setdefault(identifier, set()).add(relative)
    return owners, ids_by_path


def validate_guard(
    root: str | Path, state_dir: str | Path, key_file: str | Path
) -> dict[str, object]:
    state_dir, state, root, _, _ = _load_state(state_dir, key_file, root)
    del state_dir
    scope = state["scope"]
    approved_paths = set(_resolved_scope_paths(root, state))
    current_ids = set(scope.get("ids") or [])
    owners, ids_by_path = _record_owners(root)
    for path in approved_paths:
        current_ids.update(ids_by_path.get(path, set()))
    owner_paths = {
        path
        for identifier in current_ids
        for path in owners.get(identifier, set())
    } - approved_paths
    for path in owner_paths:
        current_ids.update(ids_by_path.get(path, set()))
    baseline = {
        _issue_fingerprint(item) for item in state.get("baseline_issues") or []
    }
    blocking: list[dict[str, object]] = []
    advisory: list[dict[str, object]] = []
    current_lint = lint_repository(root)
    for item in current_lint:
        reasons: list[str] = []
        path = item.get("path")
        if path in approved_paths:
            reasons.append("current-path")
        elif path in owner_paths:
            reasons.append("direct-owner-path")
        related_paths = set(item.get("related_paths") or [])
        if related_paths & approved_paths:
            reasons.append("current-path")
        elif related_paths & owner_paths:
            reasons.append("direct-owner-path")
        if path == "atlas-package.json" or str(path).startswith(("taxonomy/", "contracts/")):
            reasons.append("shared-contract-path")
        item_ids = {
            value
            for key in ("record_id", "related_ids")
            for value in (
                [item.get(key)] if key == "record_id" else item.get(key, [])
            )
            if isinstance(value, str)
        }
        if item_ids & current_ids:
            reasons.append("current-id")
        if item.get("code") == "ATLAS003" and "duplicate" in str(item.get("message", "")).casefold():
            reasons.append("duplicate-id")
        fingerprint = _issue_fingerprint(item)
        if fingerprint not in baseline:
            reasons.append("new-issue")
        if reasons:
            blocking.append({"issue": item, "reasons": sorted(set(reasons))})
        else:
            advisory.append({"issue": item, "reasons": ["unchanged-baseline"]})

    baseline_files = state.get("repo_state", {}).get("files") or {}
    current_files = _repo_inventory(root)
    changed_paths = sorted(
        relative
        for relative in set(baseline_files) | set(current_files)
        if baseline_files.get(relative) != current_files.get(relative)
    )
    for relative in changed_paths:
        if relative in approved_paths:
            continue
        reasons = ["unexpected-out-of-scope-change"]
        if relative == "atlas-package.json" or relative.startswith(("taxonomy/", "contracts/")):
            reasons.append("shared-contract-path")
        blocking.append(
            {
                "issue": {
                    "code": "ATLAS-WORK-GUARD-SCOPE",
                    "level": "ERROR",
                    "path": relative,
                    "message": "repository content changed outside the approved Atlas work scope",
                },
                "reasons": sorted(reasons),
            }
        )
    baseline_repo_state = state.get("repo_state", {})
    current_repo_state = _repo_state(root)
    if current_repo_state.get("head") != baseline_repo_state.get("head"):
        blocking.append(
            {
                "issue": {
                    "code": "ATLAS-WORK-GUARD-REPO",
                    "level": "ERROR",
                    "path": ".",
                    "message": "repository HEAD changed after the guard started",
                },
                "reasons": ["unexpected-repository-state"],
            }
        )
    if current_repo_state.get("index_entries_z") != baseline_repo_state.get("index_entries_z"):
        blocking.append(
            {
                "issue": {
                    "code": "ATLAS-WORK-GUARD-GIT",
                    "level": "ERROR",
                    "path": ".git/index",
                    "message": "Git staged blob/index identity changed after the guard started",
                },
                "reasons": ["unexpected-index-state"],
            }
        )
    baseline_records = _porcelain_records(baseline_repo_state.get("porcelain_v2_z"))
    current_records = _porcelain_records(current_repo_state.get("porcelain_v2_z"))
    changed_git_paths = sorted(
        path
        for path in set(baseline_records) | set(current_records)
        if baseline_records.get(path) != current_records.get(path) and path not in approved_paths
    )
    for relative in changed_git_paths:
        blocking.append(
            {
                "issue": {
                    "code": "ATLAS-WORK-GUARD-GIT",
                    "level": "ERROR",
                    "path": relative,
                    "message": "Git porcelain-v2 state changed outside the approved Atlas work scope",
                },
                "reasons": ["unexpected-git-state"],
            }
        )
    baseline_generation = state.get("baseline_generation_issues")
    if not isinstance(baseline_generation, list):
        raise WorkGuardError("guard generation baseline is tampered")
    baseline_generation_fingerprints = {
        _issue_fingerprint(item) for item in baseline_generation if isinstance(item, dict)
    }
    baseline_generation_identities = {
        (item.get("path"), item.get("record_id"))
        for item in baseline_generation
        if isinstance(item, dict)
    }
    for generator_item in _generation_preflight_issues(root):
        path = generator_item["path"]
        record_id = generator_item["record_id"]
        reasons: list[str] = []
        if path in approved_paths:
            reasons.append("current-path")
        elif path in owner_paths:
            reasons.append("direct-owner-path")
        if path == "atlas-package.json" or str(path).startswith(("taxonomy/", "contracts/")):
            reasons.append("shared-contract-path")
        if isinstance(record_id, str) and record_id in current_ids:
            reasons.append("current-id")
        fingerprint = _issue_fingerprint(generator_item)
        unchanged = fingerprint in baseline_generation_fingerprints
        if not unchanged:
            identity = (path, record_id)
            reasons.append(
                "changed-generator-issue"
                if identity in baseline_generation_identities
                else "new-generator-issue"
            )
        issue: dict[str, object] = {
            "code": "ATLAS-WORK-GUARD-REBUILD",
            "level": "ERROR",
            "path": path,
            "message": generator_item["message"],
        }
        if record_id:
            issue["record_id"] = record_id
        if unchanged and not reasons:
            advisory.append({"issue": issue, "reasons": ["unchanged-baseline"]})
        else:
            reasons.append("strict-rebuild-inconsistency")
            blocking.append({"issue": issue, "reasons": sorted(set(reasons))})
    return {
        "schema_version": STATE_VERSION,
        "status": "blocked" if blocking else ("advisory" if advisory else "clean"),
        "blocking": blocking,
        "advisory": advisory,
    }


def cleanup_guard(
    root: str | Path, state_dir: str | Path, key_file: str | Path
) -> tuple[Path, Path]:
    state_dir, _, _, key_file, _ = _load_state(state_dir, key_file, root)
    _preflight_tree(state_dir, label="guard cleanup tree")
    _assert_no_reparse_ancestors(key_file, label="guard key cleanup target")
    shutil.rmtree(state_dir)
    key_file.unlink()
    return state_dir, key_file

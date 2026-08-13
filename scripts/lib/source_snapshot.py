from __future__ import annotations

from pathlib import Path
import json
import secrets
import shutil
import subprocess
import tempfile


SCHEMA_VERSION = "atlas-source-snapshot/1.0"
_MARKER_NAME = ".atlas-source-snapshot"


class SnapshotError(ValueError):
    pass


def _run_git(path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SnapshotError(f"Git command failed: {exc}") from exc
    if check and result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
        raise SnapshotError(f"Git {' '.join(args)} failed: {detail}")
    return result


def _git_text(path: Path, *args: str) -> str:
    return _run_git(path, *args).stdout.strip()


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _temporary_root(path: str | Path | None) -> Path:
    operating_system_temp = Path(tempfile.gettempdir()).resolve()
    root = Path(path).resolve() if path is not None else operating_system_temp
    if not _inside(root, operating_system_temp):
        raise SnapshotError("source snapshot state must stay in the operating-system temporary directory")
    root.mkdir(parents=True, exist_ok=True)
    return root


def _resolve_commit(repository: Path, revision: str) -> str:
    result = _run_git(repository, "rev-parse", "--verify", f"{revision}^{{commit}}", check=False)
    if result.returncode:
        raise SnapshotError(f"cannot resolve source revision {revision!r} to a commit")
    return result.stdout.strip()


def _current_branch(repository: Path) -> str | None:
    result = _run_git(repository, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    if result.returncode:
        return None
    return result.stdout.strip() or None


def _detect_default_ref(repository: Path) -> str | None:
    result = _run_git(
        repository,
        "symbolic-ref",
        "--quiet",
        "--short",
        "refs/remotes/origin/HEAD",
        check=False,
    )
    if result.returncode:
        return None
    return result.stdout.strip() or None


def _default_relationship(repository: Path, selected: str, default: str | None) -> tuple[str | None, str]:
    if default is None:
        return None, "unknown"
    merge = _run_git(repository, "merge-base", selected, default, check=False)
    if merge.returncode:
        return None, "unknown"
    merge_base = merge.stdout.strip() or None
    if selected == default:
        return merge_base, "on-default"
    selected_after_default = _run_git(
        repository, "merge-base", "--is-ancestor", default, selected, check=False
    ).returncode == 0
    default_after_selected = _run_git(
        repository, "merge-base", "--is-ancestor", selected, default, check=False
    ).returncode == 0
    if selected_after_default:
        return merge_base, "ahead-of-default"
    if default_after_selected:
        return merge_base, "behind-default"
    return merge_base, "diverged-from-default"


def _write_manifest(container: Path, payload: dict) -> Path:
    manifest = container / "manifest.json"
    payload["manifest_path"] = str(manifest.resolve())
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def prepare_snapshot(
    repository: str | Path,
    *,
    commit: str | None = None,
    default_ref: str | None = None,
    temp_root: str | Path | None = None,
) -> Path:
    requested = Path(repository).resolve()
    root_result = _run_git(requested, "rev-parse", "--show-toplevel", check=False)
    if root_result.returncode:
        raise SnapshotError(f"not inside a Git repository: {requested}")
    physical_root = Path(root_result.stdout.strip()).resolve()
    active_head = _resolve_commit(physical_root, "HEAD")
    active_branch = _current_branch(physical_root)
    dirty = bool(_git_text(physical_root, "status", "--porcelain", "--untracked-files=all"))
    if commit is None and dirty:
        raise SnapshotError(
            "source checkout is dirty; pass an explicit commit to inspect an immutable temporary snapshot"
        )
    selected_ref = commit or "HEAD"
    selected_commit = _resolve_commit(physical_root, selected_ref)
    resolved_default_ref = default_ref or _detect_default_ref(physical_root)
    default_commit: str | None = None
    if resolved_default_ref:
        result = _run_git(
            physical_root,
            "rev-parse",
            "--verify",
            f"{resolved_default_ref}^{{commit}}",
            check=False,
        )
        if result.returncode == 0:
            default_commit = result.stdout.strip()
    merge_base, relationship = _default_relationship(physical_root, selected_commit, default_commit)

    root = _temporary_root(temp_root)
    container = Path(tempfile.mkdtemp(prefix="atlas-source-snapshot-", dir=root)).resolve()
    marker_token = secrets.token_hex(24)
    marker = container / _MARKER_NAME
    marker.write_text(marker_token + "\n", encoding="utf-8")
    mode = "in-place"
    snapshot_path = physical_root
    if dirty or selected_commit != active_head:
        mode = "temporary-worktree"
        snapshot_path = container / "worktree"
        result = _run_git(
            physical_root,
            "worktree",
            "add",
            "--detach",
            str(snapshot_path),
            selected_commit,
            check=False,
        )
        if result.returncode:
            shutil.rmtree(container, ignore_errors=True)
            detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
            raise SnapshotError(f"cannot create temporary source worktree: {detail}")

    payload = {
        "schema_version": SCHEMA_VERSION,
        "physical_git_root": str(physical_root),
        "active_head": active_head,
        "active_branch": active_branch,
        "active_dirty": dirty,
        "selected_ref": selected_ref,
        "selected_commit": selected_commit,
        "default_ref": resolved_default_ref,
        "default_commit": default_commit,
        "merge_base": merge_base,
        "default_relationship": relationship,
        "mode": mode,
        "snapshot_path": str(snapshot_path.resolve()),
        "cleanup_marker": marker_token,
    }
    try:
        return _write_manifest(container, payload)
    except OSError as exc:
        if mode == "temporary-worktree":
            _run_git(physical_root, "worktree", "remove", str(snapshot_path), check=False)
        shutil.rmtree(container, ignore_errors=True)
        raise SnapshotError(f"cannot write temporary source snapshot manifest: {exc}") from exc


def _load_manifest(manifest: str | Path) -> tuple[Path, dict]:
    path = Path(manifest).resolve()
    operating_system_temp = Path(tempfile.gettempdir()).resolve()
    if not _inside(path, operating_system_temp):
        raise SnapshotError("source snapshot manifest must be in the operating-system temporary directory")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"cannot read source snapshot manifest: {exc}") from exc
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise SnapshotError(f"unsupported source snapshot schema: {payload.get('schema_version')!r}")
    if Path(str(payload.get("manifest_path", ""))).resolve() != path:
        raise SnapshotError("source snapshot manifest path does not match its recorded path")
    marker = path.parent / _MARKER_NAME
    try:
        marker_value = marker.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise SnapshotError("source snapshot cleanup marker is missing") from exc
    if not marker_value or marker_value != payload.get("cleanup_marker"):
        raise SnapshotError("source snapshot cleanup marker does not match")
    return path, payload


def _registered_worktrees(repository: Path) -> set[str]:
    result = _git_text(repository, "worktree", "list", "--porcelain")
    paths: set[str] = set()
    for line in result.splitlines():
        if line.startswith("worktree "):
            paths.add(str(Path(line.removeprefix("worktree ")).resolve()).casefold())
    return paths


def cleanup_snapshot(manifest: str | Path) -> None:
    manifest_path, payload = _load_manifest(manifest)
    container = manifest_path.parent.resolve()
    marker = container / _MARKER_NAME
    mode = payload.get("mode")
    physical_root = Path(str(payload.get("physical_git_root", ""))).resolve()
    snapshot = Path(str(payload.get("snapshot_path", ""))).resolve()

    if mode == "temporary-worktree":
        expected = (container / "worktree").resolve()
        if snapshot != expected or not _inside(snapshot, Path(tempfile.gettempdir()).resolve()):
            raise SnapshotError("temporary source snapshot target does not match its protected location")
        if snapshot == physical_root:
            raise SnapshotError("refusing to remove the active source checkout")
        if str(snapshot).casefold() not in _registered_worktrees(physical_root):
            raise SnapshotError("temporary source snapshot is not a registered Git worktree")
        if _resolve_commit(snapshot, "HEAD") != payload.get("selected_commit"):
            raise SnapshotError("temporary source snapshot no longer matches the selected commit")
        if _git_text(snapshot, "status", "--porcelain", "--untracked-files=all"):
            raise SnapshotError("temporary source snapshot is dirty; leaving it in place")
        result = _run_git(physical_root, "worktree", "remove", str(snapshot), check=False)
        if result.returncode:
            detail = result.stderr.strip() or result.stdout.strip() or "unknown Git error"
            raise SnapshotError(f"cannot remove temporary source worktree safely: {detail}")
    elif mode == "in-place":
        if snapshot != physical_root:
            raise SnapshotError("in-place source snapshot target does not match the physical Git root")
        unchanged_head = _resolve_commit(physical_root, "HEAD") == payload.get("selected_commit")
        unchanged_files = not _git_text(
            physical_root, "status", "--porcelain", "--untracked-files=all"
        )
        if not unchanged_head or not unchanged_files:
            raise SnapshotError(
                "in-place source snapshot no longer matches the selected clean commit; invalidate the analysis"
            )
    else:
        raise SnapshotError(f"unsupported source snapshot mode: {mode!r}")

    marker.unlink()
    manifest_path.unlink()
    try:
        container.rmdir()
    except OSError as exc:
        raise SnapshotError(f"source snapshot state directory is not empty: {container}") from exc

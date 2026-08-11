from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import subprocess
import tempfile


SCHEMA_VERSION = "atlas-review-snapshot/1.0"


class SnapshotError(ValueError):
    pass


def _digest(path: Path) -> dict:
    if not path.exists():
        return {"state": "missing", "sha256": None}
    if not path.is_file():
        raise SnapshotError(f"snapshot path is not a file: {path}")
    return {"state": "present", "sha256": sha256(path.read_bytes()).hexdigest()}


def _head(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _inside_temp(path: Path) -> bool:
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        path.resolve().relative_to(temp_root)
        return True
    except ValueError:
        return False


def create_snapshot(
    paths: list[str | Path],
    *,
    checkouts: list[str | Path] | None = None,
    intended_missing: list[str | Path] | None = None,
) -> Path:
    normal_paths = sorted({str(Path(path).resolve()) for path in paths})
    missing_paths = sorted({str(Path(path).resolve()) for path in intended_missing or []})
    overlap = set(normal_paths).intersection(missing_paths)
    if overlap:
        raise SnapshotError(f"paths cannot be both fingerprinted and intended missing: {sorted(overlap)[0]}")
    files = {path: _digest(Path(path)) for path in normal_paths}
    for path in missing_paths:
        state = _digest(Path(path))
        if state["state"] != "missing":
            raise SnapshotError(f"intended missing path exists: {path}")
        files[path] = {**state, "intended_missing": True}
    checkout_heads = {
        str(Path(path).resolve()): _head(Path(path).resolve())
        for path in sorted({str(Path(path).resolve()) for path in checkouts or []})
    }
    payload = {
        "schema_version": SCHEMA_VERSION,
        "files": files,
        "checkouts": checkout_heads,
    }
    handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        prefix="atlas-review-snapshot-",
        suffix=".json",
        delete=False,
    )
    with handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return Path(handle.name)


def verify_snapshot(manifest: str | Path) -> list[str]:
    manifest_path = Path(manifest).resolve()
    if not _inside_temp(manifest_path):
        raise SnapshotError("review snapshot manifest must be in the operating-system temporary directory")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SnapshotError(f"cannot read review snapshot: {exc}") from exc
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise SnapshotError(f"unsupported review snapshot schema: {payload.get('schema_version')!r}")
    changes: list[str] = []
    for raw_path, expected in sorted((payload.get("files") or {}).items()):
        actual = _digest(Path(raw_path))
        if actual != {key: expected.get(key) for key in ("state", "sha256")}:
            changes.append(f"file changed: {raw_path}")
    for raw_path, expected_head in sorted((payload.get("checkouts") or {}).items()):
        actual_head = _head(Path(raw_path))
        if actual_head != expected_head:
            changes.append(f"checkout HEAD changed: {raw_path}")
    return changes


def remove_snapshot(manifest: str | Path) -> None:
    manifest_path = Path(manifest).resolve()
    if not _inside_temp(manifest_path):
        raise SnapshotError("review snapshot manifest must be in the operating-system temporary directory")
    manifest_path.unlink(missing_ok=True)

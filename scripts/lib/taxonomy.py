from __future__ import annotations

from pathlib import Path
import json
import yaml


def load_yaml(path: str | Path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_taxonomy(root: str | Path) -> dict:
    root = Path(root)
    manifest_path = root / "atlas-package.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise TaxonomyError(f"cannot read taxonomy registration: {exc}", path="atlas-package.json") from exc
    registered = manifest.get("taxonomy") or {}
    required = {
        "types": "types",
        "statuses": "statuses",
        "standard_categories": "categories",
        "concept_fields": "concept_fields",
    }
    missing = sorted(set(required) - set(registered))
    if missing:
        raise TaxonomyError(
            "atlas-package.json: missing taxonomy paths for " + ", ".join(missing)
        )
    loaded: dict[str, object] = {}
    for manifest_key, result_key in required.items():
        relative = Path(registered[manifest_key])
        if relative.is_absolute() or ".." in relative.parts:
            raise TaxonomyError(
                f"atlas-package.json: taxonomy path {manifest_key} must be package-relative"
            )
        try:
            loaded[result_key] = load_yaml(root / relative)
        except Exception as exc:
            raise TaxonomyError(f"cannot load registered taxonomy: {exc}", path=relative) from exc
    return loaded


def load_contracts(root: str | Path) -> dict:
    root = Path(root)
    manifest_path = root / "atlas-package.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise TaxonomyError(f"cannot read contract registration: {exc}", path="atlas-package.json") from exc
    registered = manifest.get("contracts") or {}
    required = {"map_fields": "map_fields"}
    missing = sorted(set(required) - set(registered))
    if missing:
        raise TaxonomyError(
            "atlas-package.json: missing contract paths for " + ", ".join(missing)
        )
    loaded: dict[str, object] = {}
    for manifest_key, result_key in required.items():
        relative = Path(registered[manifest_key])
        if relative.is_absolute() or ".." in relative.parts:
            raise TaxonomyError(
                f"atlas-package.json: contract path {manifest_key} must be package-relative"
            )
        try:
            loaded[result_key] = load_yaml(root / relative)
        except Exception as exc:
            raise TaxonomyError(f"cannot load registered contract: {exc}", path=relative) from exc
    return loaded


class TaxonomyError(ValueError):
    """Raised when a taxonomy contract references something it does not define."""

    def __init__(self, message: str, *, path: str | Path | None = None):
        super().__init__(message)
        self.path = Path(path).as_posix() if path is not None else None

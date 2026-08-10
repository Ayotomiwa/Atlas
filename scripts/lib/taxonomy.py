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
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
        loaded[result_key] = load_yaml(root / relative)
    return loaded


def load_contracts(root: str | Path) -> dict:
    root = Path(root)
    manifest_path = root / "atlas-package.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
        loaded[result_key] = load_yaml(root / relative)
    return loaded


class TaxonomyError(ValueError):
    """Raised when a taxonomy contract references something it does not define."""

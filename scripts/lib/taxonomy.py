from __future__ import annotations

from pathlib import Path
import yaml


def load_yaml(path: str | Path):
    with Path(path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_taxonomy(root: str | Path) -> dict:
    root = Path(root)
    return {
        "types": load_yaml(root / "taxonomy" / "types.yaml"),
        "relationships": load_yaml(root / "taxonomy" / "relationships.yaml"),
        "statuses": load_yaml(root / "taxonomy" / "statuses.yaml"),
        "categories": load_yaml(root / "taxonomy" / "standard-categories.yaml"),
    }


def relationship_names(relationships_yaml: dict) -> set[str]:
    """Support both the concise spec examples and enriched real taxonomy entries."""
    names: set[str] = set()
    for item in relationships_yaml.get("relationships") or []:
        if isinstance(item, str):
            names.add(item)
        elif isinstance(item, dict) and isinstance(item.get("name"), str):
            names.add(item["name"])
    return names

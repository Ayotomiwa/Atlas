from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.ids import valid_curated_id
from scripts.lib.taxonomy import load_taxonomy, relationship_names

META = {
    "schema_version": "atlas-map/1.0",
    "generated": True,
    "generator": "scripts/rebuild_maps.py",
    "package": "teama",
    "source_of_truth": ["_curated/**/*.md"],
}
MAP_NAMES = (
    "flow-component-map.json",
    "repo-dependency-map.json",
    "infra-dependency-map.json",
)


class MapBuildError(ValueError):
    pass


@dataclass(frozen=True)
class MapDiagnostic:
    source: str
    relationship: str
    target: str
    reason: str

    def render(self) -> str:
        return f"{self.source}: {self.relationship} -> {self.target or '<missing>'}: {self.reason}"


def stable_bytes(obj: object) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def governed_pages(root: str | Path) -> list[tuple[Path, dict]]:
    """Return non-archived curated concept pages that can contribute to maps."""
    root = Path(root)
    out: list[tuple[Path, dict]] = []
    curated = root / "_curated"
    if not curated.exists():
        return out
    for path in sorted(curated.rglob("*.md")):
        rel = path.relative_to(root)
        if path.name in {"README.md", "index.md", "_template.md"}:
            continue
        if "maps" in rel.parts or "status" in rel.parts:
            continue
        try:
            fm, _ = parse_frontmatter(path)
        except Exception as exc:  # map generation must not silently swallow malformed governed pages
            raise MapBuildError(f"{rel}: invalid frontmatter: {exc}") from exc
        if fm.get("status") == "archived":
            continue
        out.append((path, fm))
    return out


def _projection_names(source_type: str, rel_type: str) -> list[str]:
    names: list[str] = []
    if rel_type == "atlas.participates-in" or (
        source_type == "atlas.flow" and rel_type == "atlas.depends-on"
    ):
        names.append("flow-component-map.json")
    if source_type == "atlas.component" and rel_type in {
        "atlas.consumes",
        "atlas.produces",
        "atlas.depends-on",
    }:
        names.append("repo-dependency-map.json")
    if source_type == "atlas.infra" and rel_type in {
        "atlas.depends-on",
        "atlas.deployed-by",
        "atlas.consumes",
        "atlas.produces",
    }:
        names.append("infra-dependency-map.json")
    if source_type == "atlas.component" and rel_type == "atlas.deployed-by":
        names.append("infra-dependency-map.json")
    return names


def _node(ident: str, page_by_id: dict[str, dict]) -> dict:
    page = page_by_id.get(ident)
    if page:
        return {
            "id": ident,
            "type": page.get("type"),
            "title": page.get("title", ""),
            "status": page.get("status"),
        }
    return {"id": ident, "external_or_unresolved": True}


def build_maps(
    root: str | Path,
    *,
    include_diagnostics: bool = False,
) -> dict[str, dict] | tuple[dict[str, dict], list[MapDiagnostic]]:
    """Build deterministic map projections from curated Markdown relationships.

    Relationship Markdown is authoritative. The generated JSON contains forward and
    derived reverse views; authors never have to duplicate reciprocal edges.
    """
    root = Path(root)
    taxonomy = load_taxonomy(root)
    type_specs = {item["name"]: item for item in taxonomy["types"]["types"]}
    active_types = {name: spec for name, spec in type_specs.items() if spec.get("status") == "active"}
    allowed_relationships = relationship_names(taxonomy["relationships"])
    allowed_confidence = set(taxonomy["statuses"]["relationship_confidence"])

    pages = governed_pages(root)
    page_by_id: dict[str, dict] = {}
    for path, fm in pages:
        rel_path = path.relative_to(root)
        typ = fm.get("type")
        spec = active_types.get(typ)
        if not spec or typ in {"atlas.package", "atlas.index"} or typ.startswith("atlas.staging."):
            raise MapBuildError(f"{rel_path}: inactive or non-concept type {typ!r}")
        ident = fm.get("id")
        if not valid_curated_id(ident, spec.get("id_prefix")):
            raise MapBuildError(f"{rel_path}: invalid id {ident!r} for {typ}")
        if ident in page_by_id:
            raise MapBuildError(f"{rel_path}: duplicate curated id {ident}")
        page_by_id[ident] = fm

    maps = {
        name: {**META, "nodes": [], "edges": [], "reverse_edges": []}
        for name in MAP_NAMES
    }
    nodes: dict[str, set[str]] = {name: set() for name in MAP_NAMES}
    diagnostics: list[MapDiagnostic] = []

    for path, fm in pages:
        source = fm["id"]
        source_type = fm["type"]
        for rel in fm.get("relationships") or []:
            if not isinstance(rel, dict):
                raise MapBuildError(f"{path.relative_to(root)}: relationship must be an object")
            rel_type = rel.get("type")
            target = rel.get("target")
            confidence = rel.get("confidence")
            if rel_type not in allowed_relationships:
                raise MapBuildError(f"{path.relative_to(root)}: unknown relationship {rel_type!r}")
            if not isinstance(target, str) or not target:
                raise MapBuildError(f"{path.relative_to(root)}: relationship target is required")
            if confidence not in allowed_confidence:
                raise MapBuildError(
                    f"{path.relative_to(root)}: invalid relationship confidence {confidence!r}"
                )

            projections = _projection_names(source_type, rel_type)
            if not projections:
                diagnostics.append(
                    MapDiagnostic(
                        source=source,
                        relationship=rel_type,
                        target=target,
                        reason="valid relationship is routing metadata only in V1 and has no dedicated map projection",
                    )
                )
                continue

            edge = {
                "source": source,
                "type": rel_type,
                "target": target,
                "confidence": confidence,
            }
            for key in ("kind", "note", "evidence"):
                if key in rel and rel[key] not in (None, "", []):
                    edge[key] = rel[key]

            for name in projections:
                maps[name]["edges"].append(dict(edge))
                nodes[name].update({source, target})

    for name in MAP_NAMES:
        maps[name]["nodes"] = sorted(
            (_node(ident, page_by_id) for ident in nodes[name]),
            key=lambda item: item["id"],
        )
        maps[name]["edges"] = sorted(
            maps[name]["edges"],
            key=lambda item: (
                item.get("source", ""),
                item.get("type", ""),
                item.get("target", ""),
                item.get("kind", ""),
            ),
        )
        maps[name]["reverse_edges"] = sorted(
            (
                {
                    **edge,
                    "source": edge["target"],
                    "target": edge["source"],
                    "derived": True,
                    "forward_type": edge["type"],
                }
                for edge in maps[name]["edges"]
            ),
            key=lambda item: (
                item.get("source", ""),
                item.get("forward_type", ""),
                item.get("target", ""),
                item.get("kind", ""),
            ),
        )

    if include_diagnostics:
        return maps, sorted(
            diagnostics,
            key=lambda d: (d.source, d.relationship, d.target, d.reason),
        )
    return maps

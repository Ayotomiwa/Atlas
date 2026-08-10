from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
import json
import subprocess

from scripts.lib.maps import governed_pages, load_package_config
from scripts.lib.taxonomy import load_contracts


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    relationship: str
    field: str
    confidence: str
    evidence: tuple[str, ...]
    source_page: str = ""
    target_page: str = ""


CONFIDENCE_RANK = {"reviewed": 0, "possible": 1, "unconfirmed": 2, "conflicting": 3}


class AtlasQuery:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.config = load_package_config(self.root)
        self.map_contract = load_contracts(self.root)["map_fields"]
        self.records: dict[str, dict] = {}
        self.routes: dict[str, dict] = {}
        self.edges: list[Edge] = []
        self.warnings = self._trust_warnings()
        self._load()

    def _trust_warnings(self) -> list[str]:
        governed = self.config.get("governed_branch")
        if not governed:
            return ["The package manifest does not declare a governed branch; local curated status is unverified."]
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            current = result.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return [
                f"Could not determine the current Git branch; check {governed} for governed authority."
            ]
        if not current:
            return [
                f"The checkout is detached or its branch is unknown; check {governed} for governed authority."
            ]
        if current != governed:
            return [
                f"Using local status:curated content on branch {current}; check {governed} for governed authority. "
                "New knowledge may intentionally exist only on this working branch."
            ]
        return []

    def _load(self) -> None:
        for map_key, relative in self.config["maps"].items():
            path = self.root / relative
            if not path.exists():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            for collection, values in payload.items():
                if collection == "metadata" or not isinstance(values, dict):
                    continue
                for ident, record in values.items():
                    value = {
                        "id": ident,
                        "map": map_key,
                        "collection": collection,
                        **record,
                    }
                    self.records[ident] = value
                    self.routes[ident] = {
                        "id": ident,
                        "type": self._record_type(collection),
                        "page": record.get("page", ""),
                        "status": record.get("status"),
                    }
        for path, frontmatter, _ in governed_pages(self.root):
            identifier = frontmatter.get("id")
            if isinstance(identifier, str):
                self.routes.setdefault(
                    identifier,
                    {
                        "id": identifier,
                        "type": frontmatter.get("type"),
                        "title": frontmatter.get("title", ""),
                        "page": path.relative_to(self.root).as_posix(),
                        "status": frontmatter.get("status"),
                    },
                )
        for ident, record in self.records.items():
            self._collect_record_edges(ident, record)
        unique = {edge: edge for edge in self.edges}
        self.edges = sorted(
            unique.values(),
            key=lambda edge: (edge.source, edge.target, edge.relationship, edge.field),
        )

    @staticmethod
    def _record_type(collection: str) -> str:
        return {
            "repositories": "repository",
            "components": "component",
            "flows": "flow",
            "packages": "infra",
            "resources": "infra-resource",
        }.get(collection, collection.rstrip("s"))

    def _target_id(self, item: dict) -> str | None:
        identifier = item.get("id")
        if isinstance(identifier, str):
            return identifier
        name = item.get("name")
        if isinstance(name, str) and name:
            return f"external:{name}"
        return None

    def _remember_target(self, item: dict) -> str | None:
        target = self._target_id(item)
        if target is None:
            return None
        self.routes.setdefault(
            target,
            {
                "id": target,
                "type": "external-system" if item.get("external") else None,
                "name": item.get("name", ""),
                "unresolved": item.get("unresolved", False),
                "external": item.get("external", False),
            },
        )
        return target

    def _add_edge(self, record_id: str, field: str, item: dict, relationship: str) -> None:
        if field in {"used_by", "downstream_flows"}:
            return
        target = self._remember_target(item)
        if target is None:
            return
        source, destination = record_id, target
        if self.map_contract.get("impact_direction", {}).get(relationship) == "dependency":
            source, destination = target, record_id
        source_page = self.routes.get(source, {}).get("page", "")
        target_page = self.routes.get(destination, {}).get("page", "")
        evidence = tuple(str(value) for value in item.get("evidence") or [])
        self.edges.append(
            Edge(
                source=source,
                target=destination,
                relationship=relationship,
                field=field,
                confidence=str(item.get("confidence") or "reviewed"),
                evidence=evidence,
                source_page=source_page,
                target_page=target_page,
            )
        )

    def _collect_record_edges(self, ident: str, record: dict) -> None:
        source_type = {
            "repositories": "repository",
            "components": "component",
            "flows": "flow",
            "packages": "infrastructure",
            "resources": "infrastructure",
        }.get(record.get("collection"))
        if source_type:
            for field, spec in self.map_contract["fields"].get(source_type, {}).items():
                for item in record.get(field) or []:
                    if isinstance(item, dict):
                        self._add_edge(ident, field, item, spec["action"])
            for field, spec in self.map_contract["fields"]["routes"].items():
                for item in record.get(field) or []:
                    if isinstance(item, dict):
                        self._add_edge(ident, field, item, spec["action"])

        if record.get("collection") == "flows":
            for step in record.get("steps") or []:
                participant = step.get("participant") or {}
                participant_id = participant.get("id")
                if isinstance(participant_id, str):
                    self.edges.append(
                        Edge(
                            source=participant_id,
                            target=ident,
                            relationship="participates-in",
                            field="steps",
                            confidence=str(step.get("confidence") or "reviewed"),
                            evidence=tuple(str(value) for value in step.get("evidence") or []),
                            source_page=self.routes.get(participant_id, {}).get("page", ""),
                            target_page=record.get("page", ""),
                        )
                    )
                for field in ("receives", "emits"):
                    for item in step.get(field) or []:
                        if isinstance(item, dict):
                            relationship = "consumes" if field == "receives" else "produces"
                            self._add_edge(ident, f"steps.{field}", item, relationship)
        if record.get("collection") == "repositories":
            parent_id = record.get("parent_repository")
            if isinstance(parent_id, str):
                self.edges.append(
                    Edge(
                        source=parent_id,
                        target=ident,
                        relationship="contains",
                        field="parent_repository",
                        confidence="reviewed",
                        evidence=(),
                        source_page=self.routes.get(parent_id, {}).get("page", ""),
                        target_page=record.get("page", ""),
                    )
                )
        elif record.get("collection") == "components":
            repository_id = record.get("repository")
            if isinstance(repository_id, str):
                self.edges.append(
                    Edge(
                        source=repository_id,
                        target=ident,
                        relationship="contains",
                        field="repository",
                        confidence="reviewed",
                        evidence=(),
                        source_page=self.routes.get(repository_id, {}).get("page", ""),
                        target_page=record.get("page", ""),
                    )
                )
            parent_id = record.get("parent_component")
            if isinstance(parent_id, str):
                self.edges.append(
                    Edge(
                        source=parent_id,
                        target=ident,
                        relationship="contains",
                        field="parent_component",
                        confidence="reviewed",
                        evidence=(),
                        source_page=self.routes.get(parent_id, {}).get("page", ""),
                        target_page=record.get("page", ""),
                    )
                )
        elif record.get("collection") == "resources":
            package_id = record.get("parent_package")
            if isinstance(package_id, str):
                self.edges.append(
                    Edge(
                        source=package_id,
                        target=ident,
                        relationship="contains",
                        field="parent_package",
                        confidence="reviewed",
                        evidence=(),
                        source_page=self.routes.get(package_id, {}).get("page", ""),
                        target_page=record.get("page", ""),
                    )
                )

    def resolve(self, identifier: str) -> dict | None:
        record = self.records.get(identifier)
        if record:
            return record
        routed = self.routes.get(identifier)
        if routed:
            return routed
        for path, frontmatter, _ in governed_pages(self.root):
            if frontmatter.get("id") == identifier:
                route = {
                    "id": identifier,
                    "type": frontmatter.get("type"),
                    "title": frontmatter.get("title", ""),
                    "page": path.relative_to(self.root).as_posix(),
                    "status": frontmatter.get("status"),
                }
                self.routes[identifier] = route
                return route
        return None

    def route(self, query: str) -> list[dict]:
        needle = query.casefold()
        domain_needles = {needle}
        for domain in self.config.get("domains") or []:
            names = [domain.get("id", ""), domain.get("title", ""), *(domain.get("aliases") or [])]
            if any(needle == str(name).casefold() for name in names):
                domain_needles.add(str(domain.get("id", "")).casefold())
        matches: list[dict] = []
        for ident, record in self.records.items():
            searchable = [
                ident,
                record.get("title", ""),
                record.get("description", ""),
                record.get("primary_domain", ""),
                record.get("repository_locator", ""),
                record.get("package_path", ""),
                *(record.get("aliases") or []),
                *(record.get("repository_paths") or []),
            ]
            if any(
                candidate in str(value).casefold()
                for candidate in domain_needles
                for value in searchable
            ):
                matches.append(record)
        return sorted(matches, key=lambda item: item["id"])

    def neighbors(self, identifier: str) -> list[dict]:
        out: list[dict] = []
        for edge in self.edges:
            if edge.source == identifier or edge.target == identifier:
                direction = "outgoing" if edge.source == identifier else "incoming"
                peer = edge.target if direction == "outgoing" else edge.source
                out.append(
                    {
                        "direction": direction,
                        "peer": peer,
                        "peer_route": self.routes.get(peer, {"id": peer}),
                        "edge": asdict(edge),
                    }
                )
        return out

    def impact(self, identifier: str, *, direction: str = "downstream", max_depth: int = 6) -> list[dict]:
        if direction not in {"downstream", "upstream"}:
            raise ValueError("direction must be downstream or upstream")
        adjacency: dict[str, list[Edge]] = {}
        for edge in self.edges:
            source = edge.source if direction == "downstream" else edge.target
            adjacency.setdefault(source, []).append(edge)
        queue = deque([(identifier, [])])
        best_depth = {identifier: 0}
        results: list[dict] = []
        while queue:
            current, path = queue.popleft()
            if len(path) >= max_depth:
                continue
            for edge in adjacency.get(current, []):
                next_id = edge.target if direction == "downstream" else edge.source
                if any(
                    next_id in {existing.source, existing.target}
                    for existing in path
                ):
                    continue
                next_path = [*path, edge]
                depth = len(next_path)
                prior = best_depth.get(next_id)
                if prior is not None and prior < depth:
                    continue
                best_depth[next_id] = depth
                confidence = max(
                    (edge_item.confidence for edge_item in next_path),
                    key=lambda value: CONFIDENCE_RANK.get(value, 99),
                )
                results.append(
                    {
                        "id": next_id,
                        "route": self.routes.get(next_id, {"id": next_id}),
                        "depth": depth,
                        "direct": depth == 1,
                        "confidence": confidence,
                        "via": [asdict(edge_item) for edge_item in next_path],
                    }
                )
                queue.append((next_id, next_path))
        deduped: dict[str, dict] = {}
        for item in sorted(results, key=lambda value: (value["depth"], value["id"])):
            deduped.setdefault(item["id"], item)
        return list(deduped.values())

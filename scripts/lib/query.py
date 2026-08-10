from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
import subprocess
from urllib.parse import urlsplit

from scripts.lib.maps import curated_pages, load_package_config
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


def _normalise_locator(value: str) -> str:
    locator = value.strip().replace("\\", "/")
    if not locator:
        return ""
    if locator.startswith("git@") and ":" in locator:
        host, path = locator[4:].split(":", 1)
        locator = f"{host}/{path}"
    elif "://" in locator:
        parsed = urlsplit(locator)
        locator = f"{parsed.hostname or parsed.netloc}{parsed.path}"
    locator = re.sub(r"/+", "/", locator).rstrip("/")
    if locator.casefold().endswith(".git"):
        locator = locator[:-4]
    return locator.casefold()


def _normalise_relative_path(value: object) -> str:
    if not isinstance(value, str):
        return "."
    path = value.strip().replace("\\", "/").strip("/")
    return path or "."


def _contains_path(parent: str, child: str) -> bool:
    parent = _normalise_relative_path(parent)
    child = _normalise_relative_path(child)
    return parent == "." or child == parent or child.startswith(parent + "/")


def _join_relative(parent: str, child: str) -> str:
    parent = _normalise_relative_path(parent)
    child = _normalise_relative_path(child)
    if parent == ".":
        return child
    if child == ".":
        return parent
    return f"{parent}/{child}"


def _specificity(path: str) -> int:
    path = _normalise_relative_path(path)
    return 0 if path == "." else len(path.split("/"))


class AtlasQuery:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.config = load_package_config(self.root)
        self.map_contract = load_contracts(self.root)["map_fields"]
        self.records: dict[str, dict] = {}
        self.routes: dict[str, dict] = {}
        self.edges: list[Edge] = []
        self.warnings = self._branch_warnings()
        self._load()

    def _branch_warnings(self) -> list[str]:
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
            return ["Could not determine the current Git branch; Atlas routing will continue."]
        if not current:
            return ["The checkout is detached or its branch is unknown; Atlas routing will continue."]
        if current not in {"main", "master"}:
            return [
                f"Current branch {current} is not main or master; results may include unmerged Atlas work. "
                "Routing will continue."
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
        for path, frontmatter, _ in curated_pages(self.root):
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
        for path, frontmatter, _ in curated_pages(self.root):
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
                record.get("repository_root", ""),
                record.get("package_path", ""),
                *(record.get("aliases") or []),
                *(record.get("repository_paths") or []),
                *(root.get("path", "") for root in record.get("source_roots") or [] if isinstance(root, dict)),
            ]
            if any(
                candidate in str(value).casefold()
                for candidate in domain_needles
                for value in searchable
            ):
                matches.append(record)
        return sorted(matches, key=lambda item: item["id"])

    def context(self, path: str | Path = ".") -> dict:
        requested = Path(path).expanduser().resolve()
        start = requested.parent if requested.is_file() else requested
        context_warnings: list[str] = []
        git_root: Path | None = None
        git_remote = ""
        try:
            result = subprocess.run(
                ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            git_root = Path(result.stdout.strip()).resolve()
        except (OSError, subprocess.SubprocessError):
            context_warnings.append("Could not discover a physical Git root for the requested path.")

        if git_root is not None:
            try:
                remote = subprocess.run(
                    ["git", "-C", str(git_root), "remote", "get-url", "origin"],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                git_remote = remote.stdout.strip()
            except (OSError, subprocess.SubprocessError):
                context_warnings.append("The physical Git repository has no readable origin remote.")

        if git_root is None:
            relative_path = "."
        else:
            try:
                relative_path = requested.relative_to(git_root).as_posix() or "."
            except ValueError:
                relative_path = "."
                context_warnings.append("The requested path is outside the discovered physical Git root.")

        normalised_remote = _normalise_locator(git_remote)
        repository_candidates: list[dict] = []
        for identifier, record in self.records.items():
            if record.get("collection") != "repositories":
                continue
            locator = str(record.get("repository_locator") or "")
            normalised_locator = _normalise_locator(locator)
            if normalised_remote and normalised_locator and normalised_remote != normalised_locator:
                continue
            repository_root = _normalise_relative_path(record.get("repository_root"))
            if git_root is not None and not _contains_path(repository_root, relative_path):
                continue
            locator_state = (
                "matched"
                if normalised_remote and normalised_locator and normalised_remote == normalised_locator
                else "not-verified"
            )
            repository_candidates.append(
                {
                    "id": identifier,
                    "page": record.get("page", ""),
                    "status": record.get("status"),
                    "repository_type": record.get("repository_type"),
                    "repository_root": repository_root,
                    "matched_path": repository_root,
                    "match_basis": "repository_root",
                    "locator_match": locator_state,
                    "specificity": _specificity(repository_root),
                }
            )
        repository_candidates.sort(key=lambda item: (-item["specificity"], item["id"]))
        repository_ids = {item["id"]: item for item in repository_candidates}

        component_candidates: list[dict] = []
        for identifier, record in self.records.items():
            if record.get("collection") != "components" or record.get("repository") not in repository_ids:
                continue
            repository_candidate = repository_ids[record["repository"]]
            repository_root = repository_candidate["repository_root"]
            paths = record.get("repository_paths") or []
            matched_paths = [
                _join_relative(repository_root, component_path)
                for component_path in paths
                if _contains_path(_join_relative(repository_root, component_path), relative_path)
            ]
            if matched_paths:
                matched_path = max(matched_paths, key=lambda value: (_specificity(value), value))
                basis = "repository_path"
            else:
                matched_path = repository_root
                basis = "repository_membership"
            component_candidates.append(
                {
                    "id": identifier,
                    "page": record.get("page", ""),
                    "status": record.get("status"),
                    "component_type": record.get("component_type"),
                    "repository": record.get("repository"),
                    "repository_paths": paths,
                    "matched_path": matched_path,
                    "match_basis": basis,
                    "specificity": _specificity(matched_path) if basis == "repository_path" else -1,
                }
            )
        component_candidates.sort(key=lambda item: (-item["specificity"], item["id"]))

        top_repo_specificity = repository_candidates[0]["specificity"] if repository_candidates else None
        top_component_specificity = component_candidates[0]["specificity"] if component_candidates else None
        return {
            "requested_path": str(requested),
            "git_root": str(git_root) if git_root is not None else None,
            "git_remote": git_remote or None,
            "git_relative_path": relative_path,
            "repositories": repository_candidates,
            "components": component_candidates,
            "ambiguous": {
                "repositories": sum(item["specificity"] == top_repo_specificity for item in repository_candidates) > 1,
                "components": sum(item["specificity"] == top_component_specificity for item in component_candidates) > 1,
            },
            "warnings": context_warnings,
        }

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

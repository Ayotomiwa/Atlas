from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
import subprocess
from urllib.parse import urlsplit

from scripts.lib.maps import curated_pages, load_package_config
from scripts.lib.questions import QuestionParseError, parse_open_questions
from scripts.lib.staging import ACTIVE_STAGING_STATUSES, read_staging_pages
from scripts.lib.structured import StructuredFrontmatterError, parse_conflicts, parse_data_assets
from scripts.lib.taxonomy import load_contracts, load_taxonomy


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
SEARCH_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "that",
    "the",
    "this",
    "to",
    "what",
    "which",
    "who",
    "with",
}
SEARCH_INDEXES = {
    "repository": "_curated/repositories/index.md",
    "component": "_curated/components/index.md",
    "flow": "_curated/flows/index.md",
    "infra": "_curated/infra/index.md",
    "infra-resource": "_curated/infra/index.md",
    "data-asset": "_curated/schema-info/index.md",
    "schema-info": "_curated/schema-info/index.md",
    "business-concept": "_curated/business-concepts/index.md",
    "standard": "_curated/standards/index.md",
    "runbook": "_curated/runbooks/index.md",
    "incident-learning": "_curated/incidents/index.md",
}


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
    def __init__(self, root: str | Path, *, compiled_maps: dict[str, dict] | None = None):
        self.root = Path(root).resolve()
        self.config = load_package_config(self.root)
        self.taxonomy = load_taxonomy(self.root)
        self.map_contract = load_contracts(self.root)["map_fields"]
        self.compiled_maps = compiled_maps
        self.records: dict[str, dict] = {}
        self.routes: dict[str, dict] = {}
        self.search_records: dict[str, dict] = {}
        self.edges: list[Edge] = []
        self.open_questions: list[dict] = []
        self.conflicts: dict[str, dict] = {}
        self.question_diagnostics: list[dict] = []
        self.structured_diagnostics: list[dict] = []
        self._branch = self._git_branch()
        self.warnings = self._branch_warnings()
        self._load()

    def _git_branch(self) -> str | None:
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return None

    def _branch_warnings(self) -> list[str]:
        try:
            current = self._branch
        except Exception:
            return ["Atlas branch could not be determined; curated records remain authoritative."]
        if current is None:
            return ["Atlas branch could not be determined; curated records remain authoritative."]
        if not current:
            return ["Atlas is on a detached checkout; curated records remain authoritative."]
        if current not in {"main", "master"}:
            return [
                f"Atlas is on {current}, not main or master; curated records are authoritative, "
                "but this checkout may include unmerged changes."
            ]
        return []

    @staticmethod
    def _page_trust(status: object) -> str:
        if status == "curated":
            return "authoritative"
        if status == "deprecated":
            return "historical"
        return "unknown"

    def _page_checkout_state(self, path: Path, status: object) -> str | None:
        if status != "curated":
            return None
        if self._branch is None:
            return "git-unknown"
        relative = path.relative_to(self.root).as_posix()
        try:
            tracked = subprocess.run(
                ["git", "ls-files", "--error-unmatch", "--", relative],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=5,
            ).returncode == 0
            unchanged = subprocess.run(
                ["git", "diff", "--quiet", "HEAD", "--", relative],
                cwd=self.root,
                timeout=5,
            ).returncode == 0
        except (OSError, subprocess.SubprocessError):
            return "git-unknown"
        if not tracked:
            return "untracked"
        if not unchanged:
            return "modified"
        if not self._branch:
            return "detached"
        if self._branch not in {"main", "master"}:
            return "off-main"
        return "main-clean"

    def _load(self) -> None:
        map_payloads: list[tuple[str, dict]] = []
        if self.compiled_maps is not None:
            map_payloads = sorted(self.compiled_maps.items())
        else:
            for map_key, relative in self.config["maps"].items():
                path = self.root / relative
                if path.exists():
                    map_payloads.append((map_key, json.loads(path.read_text(encoding="utf-8"))))
        for map_key, payload in map_payloads:
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
        pages = curated_pages(self.root)
        for path, frontmatter, _ in pages:
            identifier = frontmatter.get("id")
            if isinstance(identifier, str):
                route = self.routes.setdefault(
                    identifier,
                    {
                        "id": identifier,
                        "type": frontmatter.get("type"),
                        "title": frontmatter.get("title", ""),
                        "page": path.relative_to(self.root).as_posix(),
                        "status": frontmatter.get("status"),
                    },
                )
                route.setdefault("type", frontmatter.get("type"))
                route.setdefault("title", frontmatter.get("title", ""))
                route.setdefault("page", path.relative_to(self.root).as_posix())
                route.setdefault("status", frontmatter.get("status"))
                route.setdefault("primary_domain", frontmatter.get("primary_domain", ""))
                route["trust"] = self._page_trust(frontmatter.get("status"))
                route["checkout_state"] = self._page_checkout_state(path, frontmatter.get("status"))
                if identifier in self.records:
                    self.records[identifier]["trust"] = route["trust"]
                    self.records[identifier]["checkout_state"] = route["checkout_state"]
        self._load_search_records(pages)
        self._load_open_questions(pages)
        for ident, record in self.records.items():
            self._collect_record_edges(ident, record)
        unique = {edge: edge for edge in self.edges}
        self.edges = sorted(
            unique.values(),
            key=lambda edge: (edge.source, edge.target, edge.relationship, edge.field),
        )

    @staticmethod
    def _routing_values(frontmatter: dict, field: str) -> list[str]:
        routing = frontmatter.get("routing")
        if not isinstance(routing, dict):
            return []
        values = routing.get(field)
        return [value for value in values or [] if isinstance(value, str) and value]

    @staticmethod
    def _concise(value: object, limit: int = 240) -> str:
        text = re.sub(r"\s+", " ", str(value or "")).strip()
        return text if len(text) <= limit else text[: limit - 3].rstrip() + "..."

    def _load_search_records(self, pages: list[tuple[Path, dict, str]]) -> None:
        for path, frontmatter, _ in pages:
            identifier = frontmatter.get("id")
            record_type = frontmatter.get("type")
            if not isinstance(identifier, str) or not isinstance(record_type, str):
                continue
            page = path.relative_to(self.root).as_posix()
            record = {
                "id": identifier,
                "type": record_type,
                "title": str(frontmatter.get("title") or ""),
                "description": self._concise(frontmatter.get("description")),
                "status": frontmatter.get("status"),
                "trust": self._page_trust(frontmatter.get("status")),
                "checkout_state": self._page_checkout_state(path, frontmatter.get("status")),
                "primary_domain": frontmatter.get("primary_domain", ""),
                "related_domains": [
                    value for value in frontmatter.get("related_domains") or [] if isinstance(value, str)
                ],
                "page": page,
                "collection_index": SEARCH_INDEXES.get(record_type, "_curated/index.md"),
                "aliases": self._routing_values(frontmatter, "aliases"),
                "keywords": self._routing_values(frontmatter, "keywords"),
                "repository_locator": frontmatter.get("repository_locator", ""),
                "repository_root": frontmatter.get("repository_root", ""),
                "repository_paths": [
                    value for value in frontmatter.get("repository_paths") or [] if isinstance(value, str)
                ],
                "package_path": frontmatter.get("package_path", ""),
                "source_paths": [
                    item.get("path", "")
                    for item in frontmatter.get("source_roots") or []
                    if isinstance(item, dict) and isinstance(item.get("path"), str)
                ],
                "conflicts": [],
            }
            try:
                record["conflicts"] = parse_conflicts(page, frontmatter)
            except StructuredFrontmatterError as exc:
                self.structured_diagnostics.append(
                    {"page": page, "record_id": identifier, "message": str(exc)}
                )
            for conflict in record["conflicts"]:
                conflict_record = {
                    **conflict,
                    "type": "conflict",
                    "owner_id": identifier,
                    "owner_title": record["title"],
                    "page": page,
                    "status": record["status"],
                    "trust": record["trust"],
                    "checkout_state": record["checkout_state"],
                }
                self.conflicts[conflict["id"]] = conflict_record
            self.search_records[identifier] = record
            self.routes.setdefault(
                identifier,
                {
                    "id": identifier,
                    "type": record_type,
                    "title": record["title"],
                    "page": page,
                    "status": record["status"],
                    "trust": record["trust"],
                    "checkout_state": record["checkout_state"],
                    "primary_domain": record["primary_domain"],
                },
            )

            if record_type == "schema-info":
                try:
                    assets = parse_data_assets(page, frontmatter, self.taxonomy)
                except StructuredFrontmatterError as exc:
                    self.structured_diagnostics.append(
                        {"page": page, "record_id": identifier, "message": str(exc)}
                    )
                    assets = []
                for asset in assets:
                    asset_id = asset["id"]
                    asset_record = {
                        **asset,
                        "type": "data-asset",
                        "title": asset["name"],
                        "description": self._concise(asset.get("description")),
                        "status": record["status"],
                        "trust": record["trust"],
                        "checkout_state": record["checkout_state"],
                        "primary_domain": record["primary_domain"],
                        "related_domains": record["related_domains"],
                        "page": page,
                        "collection_index": SEARCH_INDEXES["data-asset"],
                        "aliases": [],
                        "keywords": [],
                        "repository_locator": "",
                        "repository_root": "",
                        "repository_paths": [],
                        "package_path": "",
                        "source_paths": list(asset.get("evidence") or []),
                        "parent_schema": identifier,
                        "collection": "assets",
                    }
                    self.search_records[asset_id] = asset_record
                    self.records[asset_id] = asset_record
                    self.routes[asset_id] = {
                        "id": asset_id,
                        "type": "data-asset",
                        "title": asset["name"],
                        "page": page,
                        "status": record["status"],
                        "trust": record["trust"],
                        "checkout_state": record["checkout_state"],
                        "primary_domain": record["primary_domain"],
                        "parent_schema": identifier,
                    }

            if record_type != "infra":
                continue
            for resource in frontmatter.get("promoted_resources") or []:
                if not isinstance(resource, dict) or not isinstance(resource.get("id"), str):
                    continue
                resource_id = resource["id"]
                resource_record = {
                    "id": resource_id,
                    "type": "infra-resource",
                    "title": str(resource.get("name") or resource_id),
                    "description": self._concise(resource.get("promotion_reason")),
                    "status": frontmatter.get("status"),
                    "trust": record["trust"],
                    "checkout_state": record["checkout_state"],
                    "primary_domain": frontmatter.get("primary_domain", ""),
                    "related_domains": record["related_domains"],
                    "page": page,
                    "collection_index": SEARCH_INDEXES["infra-resource"],
                    "aliases": [],
                    "keywords": [],
                    "repository_locator": "",
                    "repository_root": "",
                    "repository_paths": [],
                    "package_path": frontmatter.get("package_path", ""),
                    "source_paths": [str(resource.get("defined_in_path") or "")],
                    "parent_package": identifier,
                    "resource_type": resource.get("resource_type", ""),
                }
                self.search_records[resource_id] = resource_record
                resource_route = self.routes.setdefault(
                    resource_id,
                    {
                        "id": resource_id,
                        "type": "infra-resource",
                        "title": resource_record["title"],
                        "page": page,
                        "status": resource_record["status"],
                        "trust": resource_record["trust"],
                        "checkout_state": resource_record["checkout_state"],
                        "primary_domain": resource_record["primary_domain"],
                    },
                )
                resource_route.setdefault("type", "infra-resource")
                resource_route.setdefault("title", resource_record["title"])
                resource_route.setdefault("page", page)
                resource_route.setdefault("status", resource_record["status"])
                resource_route.setdefault("trust", resource_record["trust"])
                resource_route.setdefault("checkout_state", resource_record["checkout_state"])
                resource_route.setdefault("primary_domain", resource_record["primary_domain"])

    def _load_open_questions(self, pages: list[tuple[Path, dict, str]]) -> None:
        questions: list[dict] = []
        for path, frontmatter, body in pages:
            identifier = frontmatter.get("id")
            if not isinstance(identifier, str):
                continue
            relative = path.relative_to(self.root)
            try:
                parsed = parse_open_questions(relative, body, identifier)
            except QuestionParseError as exc:
                self.question_diagnostics.append(
                    {
                        "page": relative.as_posix(),
                        "record_id": identifier,
                        "message": exc.message,
                    }
                )
                continue
            owner = {
                **self.routes.get(identifier, {"id": identifier}),
                "id": identifier,
                "type": frontmatter.get("type"),
                "title": frontmatter.get("title", ""),
                "page": relative.as_posix(),
                "status": frontmatter.get("status"),
                "primary_domain": frontmatter.get("primary_domain", ""),
            }
            for question in parsed:
                questions.append(
                    {
                        **question,
                        "owner": owner,
                        "status": frontmatter.get("status"),
                        "primary_domain": frontmatter.get("primary_domain", ""),
                    }
                )

        pending = self._pending_question_evidence({item["id"] for item in questions})
        for question in questions:
            question["affected"] = [
                self.routes.get(identifier, {"id": identifier})
                for identifier in question["affected_ids"]
            ]
            question["pending_staging"] = pending.get(question["id"], [])
        self.open_questions = sorted(questions, key=lambda item: item["id"])

    def _pending_question_evidence(self, question_ids: set[str]) -> dict[str, list[dict]]:
        matches: dict[str, list[dict]] = {}
        if not question_ids:
            return matches
        pages, _ = read_staging_pages(self.root)
        for page in pages:
            status = page.frontmatter.get("status")
            if status not in ACTIVE_STAGING_STATUSES:
                continue
            route = {
                "id": page.frontmatter.get("id", ""),
                "status": status,
                "page": page.page,
            }
            for question_id in question_ids:
                if question_id in page.body:
                    matches.setdefault(question_id, []).append(route)
        return matches

    @staticmethod
    def _record_type(collection: str) -> str:
        return {
            "repositories": "repository",
            "components": "component",
            "flows": "flow",
            "packages": "infra",
            "resources": "infra-resource",
            "assets": "data-asset",
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
        elif record.get("collection") == "assets":
            for item in record.get("inputs") or []:
                if isinstance(item, dict):
                    self._add_edge(ident, "inputs", item, "consumes")
            parent_id = record.get("parent_schema")
            if isinstance(parent_id, str):
                self.edges.append(
                    Edge(
                        source=parent_id,
                        target=ident,
                        relationship="contains",
                        field="assets",
                        confidence=str(record.get("confidence") or "reviewed"),
                        evidence=tuple(str(value) for value in record.get("evidence") or []),
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
        conflict = self.conflicts.get(identifier)
        if conflict:
            return conflict
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
                    "trust": self._page_trust(frontmatter.get("status")),
                    "checkout_state": self._page_checkout_state(path, frontmatter.get("status")),
                }
                self.routes[identifier] = route
                return route
        return None

    def _record_domain(self, record: dict) -> str:
        """Resolve a record's domain, following a promoted resource to its package.

        Promoted resources are embedded in their infrastructure page and carry no
        domain of their own, so a domain route would otherwise silently omit them.
        """
        domain = record.get("primary_domain")
        if domain:
            return str(domain).casefold()
        parent = self.records.get(record.get("parent_package") or record.get("parent_schema") or "")
        return str(parent.get("primary_domain", "")).casefold() if parent else ""

    def route(self, query: str) -> list[dict]:
        needle = query.casefold()
        domain_needles = {needle}
        matched_domains: set[str] = set()
        for domain in self.config.get("domains") or []:
            names = [domain.get("id", ""), domain.get("title", ""), *(domain.get("aliases") or [])]
            if any(needle == str(name).casefold() for name in names):
                domain_id = str(domain.get("id", "")).casefold()
                domain_needles.add(domain_id)
                matched_domains.add(domain_id)
        matches: list[dict] = []
        for ident, record in self.records.items():
            # A registered domain routes by membership, not by name resemblance.
            if matched_domains and self._record_domain(record) in matched_domains:
                matches.append(record)
                continue
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

    @staticmethod
    def _normalised_text(value: object) -> str:
        return re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold()).strip()

    @staticmethod
    def _stem(token: str) -> str:
        if len(token) > 5 and token.endswith("ies"):
            return token[:-3] + "y"
        if len(token) > 5 and token.endswith("ing"):
            stem = token[:-3]
            return stem[:-1] if len(stem) > 2 and stem[-1:] == stem[-2:-1] else stem
        if len(token) > 4 and token.endswith("ed"):
            return token[:-2]
        if len(token) > 4 and token.endswith("es"):
            return token[:-2]
        if len(token) > 3 and token.endswith("s"):
            return token[:-1]
        return token

    @classmethod
    def _tokens(cls, value: object) -> set[str]:
        return {
            cls._stem(token)
            for token in cls._normalised_text(value).split()
            if token not in SEARCH_STOPWORDS and len(token) > 1
        }

    def _domain_filter(self, value: str | None) -> set[str] | None:
        if value is None:
            return None
        matches = self._domain_ids(value)
        if not matches:
            raise ValueError(f"unknown Atlas domain or alias: {value!r}")
        return matches

    @staticmethod
    def _context_lookup(context: dict | None) -> dict[str, dict]:
        if not context:
            return {}
        lookup: dict[str, dict] = {}
        repositories = {
            item.get("id"): item
            for item in context.get("repositories") or []
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        lookup.update(repositories)
        for item in context.get("components") or []:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            repository = repositories.get(item.get("repository"), {})
            lookup[item["id"]] = {
                **item,
                "locator_match": item.get("locator_match")
                or repository.get("locator_match", "not-verified"),
            }
        return lookup

    @classmethod
    def _search_score(cls, record: dict, query: str) -> tuple[int, list[str]]:
        needle = cls._normalised_text(query)
        query_tokens = cls._tokens(query)
        identifier = cls._normalised_text(record.get("id"))
        title = cls._normalised_text(record.get("title"))
        aliases = [cls._normalised_text(value) for value in record.get("aliases") or []]
        keywords = [cls._normalised_text(value) for value in record.get("keywords") or []]
        reasons: list[str] = []
        score = 0

        if needle == identifier:
            return 100_000, ["exact stable ID"]
        if needle and needle in aliases:
            score += 90_000
            reasons.append("exact alias")
        if needle and needle == title:
            score += 80_000
            reasons.append("exact title")

        fields = (
            ("stable ID", [record.get("id", "")], 700),
            ("title", [record.get("title", "")], 600),
            ("alias", record.get("aliases") or [], 550),
            ("keyword", record.get("keywords") or [], 500),
            ("description", [record.get("description", "")], 350),
            (
                "conflict",
                [
                    value
                    for conflict in record.get("conflicts") or []
                    for value in (
                        conflict.get("id", ""),
                        conflict.get("topic", ""),
                        conflict.get("interpretation", ""),
                        *(claim.get("statement", "") for claim in conflict.get("claims") or []),
                    )
                ],
                420,
            ),
            ("domain", [record.get("primary_domain", ""), *(record.get("related_domains") or [])], 260),
            ("type", [record.get("type", ""), record.get("resource_type", "")], 180),
            (
                "source locator",
                [
                    record.get("repository_locator", ""),
                    record.get("repository_root", ""),
                    record.get("package_path", ""),
                    *(record.get("repository_paths") or []),
                    *(record.get("source_paths") or []),
                ],
                80,
            ),
        )
        for label, values, weight in fields:
            normalised_values = [cls._normalised_text(value) for value in values if value]
            phrase = bool(needle and any(needle in value for value in normalised_values))
            field_tokens = set().union(*(cls._tokens(value) for value in values)) if values else set()
            overlap = sorted(query_tokens & field_tokens)
            if phrase:
                score += weight * 4
            if overlap:
                score += weight * len(overlap)
            if phrase or overlap:
                detail = "phrase" if phrase else ", ".join(overlap)
                reasons.append(f"{label}: {detail}")

        # A record must have a lexical/explicit match before path context can help rank it.
        return score, reasons

    @classmethod
    def _matching_conflicts(cls, record: dict, query: str) -> list[dict]:
        needle = cls._normalised_text(query)
        tokens = cls._tokens(query)
        matches: list[dict] = []
        for conflict in record.get("conflicts") or []:
            values = [
                conflict.get("id", ""),
                conflict.get("topic", ""),
                conflict.get("interpretation", ""),
                *(claim.get("statement", "") for claim in conflict.get("claims") or []),
            ]
            normalised = [cls._normalised_text(value) for value in values]
            conflict_tokens = set().union(*(cls._tokens(value) for value in values))
            if (needle and any(needle in value for value in normalised)) or tokens.intersection(conflict_tokens):
                matches.append({"id": conflict["id"], "topic": conflict["topic"]})
        return matches

    def find(
        self,
        query: str,
        *,
        types: list[str] | None = None,
        domain: str | None = None,
        path: str | Path | None = None,
        limit: int = 3,
    ) -> dict:
        query = query.strip()
        if not query:
            raise ValueError("find query must not be empty")
        if limit < 1 or limit > 20:
            raise ValueError("find limit must be between 1 and 20")
        requested_types = {value for value in types or [] if value}
        valid_types = set(SEARCH_INDEXES)
        unknown_types = sorted(requested_types - valid_types)
        if unknown_types:
            raise ValueError("unknown curated search type(s): " + ", ".join(unknown_types))
        domains = self._domain_filter(domain)
        context = self.context(path) if path is not None else None
        context_lookup = self._context_lookup(context)

        # An exact stable ID is resolution, not fuzzy candidate ranking. Filters
        # still apply so callers do not receive a record outside their declared
        # collection or domain boundary.
        exact = self.search_records.get(query)
        if exact is not None:
            exact_domains = {exact.get("primary_domain"), *(exact.get("related_domains") or [])}
            allowed = (not requested_types or exact["type"] in requested_types) and (
                domains is None or bool(domains & exact_domains)
            )
            candidates: list[dict] = []
            if allowed:
                candidate = {
                    key: exact[key]
                    for key in (
                        "id",
                        "type",
                        "title",
                        "description",
                        "status",
                        "trust",
                        "checkout_state",
                        "primary_domain",
                        "page",
                        "collection_index",
                    )
                }
                candidate["match_reasons"] = ["exact stable ID"]
                matched_conflicts = self._matching_conflicts(exact, query)
                if matched_conflicts:
                    candidate["matched_conflicts"] = matched_conflicts
                context_match = context_lookup.get(query)
                if context_match:
                    candidate["context"] = {
                        key: context_match[key]
                        for key in ("match_basis", "matched_path", "locator_match")
                        if context_match.get(key) not in {None, ""}
                    }
                candidates.append(candidate)
            return {
                "query": query,
                "types": sorted(requested_types),
                "domain": sorted(domains) if domains is not None else [],
                "path": str(Path(path).expanduser().resolve()) if path is not None else None,
                "candidates": candidates,
                "total_matches": len(candidates),
                "ambiguous": False,
                "context": context,
            }

        ranked: list[tuple[int, str, dict]] = []
        for identifier, record in self.search_records.items():
            if requested_types and record["type"] not in requested_types:
                continue
            record_domains = {record.get("primary_domain"), *(record.get("related_domains") or [])}
            if domains is not None and not (domains & record_domains):
                continue
            score, reasons = self._search_score(record, query)
            if score <= 0:
                continue
            context_match = context_lookup.get(identifier)
            if context_match:
                locator_match = context_match.get("locator_match", "not-verified")
                score += 250 if locator_match == "matched" else 50
                reasons.append(
                    f"path context: {context_match.get('match_basis', 'candidate')} ({locator_match})"
                )
            candidate = {
                key: record[key]
                for key in (
                    "id",
                    "type",
                    "title",
                    "description",
                    "status",
                    "trust",
                    "checkout_state",
                    "primary_domain",
                    "page",
                    "collection_index",
                )
            }
            candidate["match_reasons"] = reasons
            matched_conflicts = self._matching_conflicts(record, query)
            if matched_conflicts:
                candidate["matched_conflicts"] = matched_conflicts
            if context_match:
                candidate["context"] = {
                    key: context_match[key]
                    for key in ("match_basis", "matched_path", "locator_match")
                    if context_match.get(key) not in {None, ""}
                }
            ranked.append((score, identifier, candidate))

        ranked.sort(key=lambda item: (-item[0], item[1]))
        candidates = [item[2] for item in ranked[:limit]]
        return {
            "query": query,
            "types": sorted(requested_types),
            "domain": sorted(domains) if domains is not None else [],
            "path": str(Path(path).expanduser().resolve()) if path is not None else None,
            "candidates": candidates,
            "total_matches": len(ranked),
            "ambiguous": len(ranked) > 1,
            "context": context,
        }

    def _domain_ids(self, value: str) -> set[str]:
        needle = value.casefold()
        matches: set[str] = set()
        for domain in self.config.get("domains") or []:
            names = [domain.get("id", ""), domain.get("title", ""), *(domain.get("aliases") or [])]
            if any(needle == str(name).casefold() for name in names):
                matches.add(str(domain.get("id", "")))
        return matches

    def _route_view(self, identifier: str) -> dict:
        route = self.routes.get(identifier, {"id": identifier})
        return {
            key: route[key]
            for key in (
                "id", "type", "title", "name", "page", "status", "trust", "checkout_state", "primary_domain"
            )
            if route.get(key) not in {None, ""}
        }

    @staticmethod
    def _related_basis(question: dict, identifiers: set[str], prefix: str) -> str | None:
        if question["owner"]["id"] in identifiers:
            return f"{prefix}-owner"
        if identifiers.intersection(question.get("affected_ids") or []):
            return f"{prefix}-affected"
        return None

    @staticmethod
    def _topic_matches_question(question: dict, query: str) -> bool:
        needle = query.casefold()
        owner = question.get("owner") or {}
        searchable = [
            question.get("id", ""),
            question.get("question", ""),
            question.get("evidence_gap", ""),
            owner.get("id", ""),
            owner.get("title", ""),
            owner.get("primary_domain", ""),
            *(question.get("affected_ids") or []),
        ]
        return any(needle in str(value).casefold() for value in searchable)

    @staticmethod
    def _grounded_context_ids(context: dict) -> set[str]:
        repositories = context.get("repositories") or []
        components = context.get("components") or []
        verified_repositories = {
            item["id"] for item in repositories if item.get("locator_match") == "matched"
        }
        path_components = {
            item["id"] for item in components if item.get("match_basis") == "repository_path"
        }
        identifiers = set(verified_repositories) | set(path_components)
        identifiers.update(
            item["repository"]
            for item in components
            if item["id"] in path_components or item.get("repository") in verified_repositories
        )
        identifiers.update(
            item["id"]
            for item in components
            if item.get("repository") in verified_repositories
        )
        return identifiers

    def questions(
        self,
        query: str | None = None,
        *,
        path: str | Path = ".",
        scope: str = "auto",
        include_pending: bool = False,
    ) -> dict:
        """Return deterministic question candidates without ranking their importance."""

        if scope not in {"auto", "local", "domain", "package"}:
            raise ValueError("question scope must be auto, local, domain, or package")
        query = query.strip() if isinstance(query, str) and query.strip() else None
        effective_scope = ("query" if query else "local") if scope == "auto" else scope
        context: dict | None = None
        target_candidates: list[dict] = []
        domain_candidates: list[str] = []
        context_ids: set[str] = set()
        candidate_only = False
        explicit_lifecycle = False
        matched: list[dict] = []

        if effective_scope == "local":
            context = self.context(path)
            repositories = context.get("repositories") or []
            components = context.get("components") or []
            context_ids = self._grounded_context_ids(context)
            candidate_only = bool(
                not context_ids and (repositories or components)
                or (context.get("ambiguous") or {}).get("repositories")
                or (context.get("ambiguous") or {}).get("components")
            )
            for question in self.open_questions:
                basis = self._related_basis(question, context_ids, "current-path")
                if basis and (not query or self._topic_matches_question(question, query)):
                    matched.append({**question, "match_basis": basis})

        elif effective_scope == "domain":
            domains = self._domain_ids(query) if query else set()
            if not domains:
                context = self.context(path)
                identifiers = self._grounded_context_ids(context)
                context_ids = set(identifiers)
                domains = {
                    str(self.records.get(identifier, {}).get("primary_domain"))
                    for identifier in identifiers
                    if self.records.get(identifier, {}).get("primary_domain")
                }
            domain_candidates = sorted(domains)
            candidate_only = len(domains) != 1
            for question in self.open_questions:
                if question.get("primary_domain") in domains:
                    matched.append({**question, "match_basis": "domain"})

        elif effective_scope == "package":
            for question in self.open_questions:
                if not query or self._topic_matches_question(question, query):
                    matched.append({**question, "match_basis": "package"})

        else:
            assert query is not None
            by_question_id = next(
                (item for item in self.open_questions if item["id"] == query),
                None,
            )
            if by_question_id:
                matched = [{**by_question_id, "match_basis": "exact-question"}]
                explicit_lifecycle = True
            elif query in self.routes:
                identifiers = {query}
                explicit_lifecycle = True
                for question in self.open_questions:
                    basis = self._related_basis(question, identifiers, "exact-target")
                    if basis:
                        matched.append({**question, "match_basis": basis})
            else:
                domains = self._domain_ids(query)
                if domains:
                    domain_candidates = sorted(domains)
                    for question in self.open_questions:
                        if question.get("primary_domain") in domains:
                            matched.append({**question, "match_basis": "domain"})
                else:
                    found = self.find(query, limit=3)
                    target_candidates = found["candidates"]
                    routed_ids = {item["id"] for item in target_candidates}
                    candidate_only = True
                    for question in self.open_questions:
                        basis = self._related_basis(question, routed_ids, "topic-record")
                        if basis:
                            matched.append({**question, "match_basis": basis})
                        elif self._topic_matches_question(question, query):
                            matched.append({**question, "match_basis": "topic-text"})

        if not explicit_lifecycle:
            matched = [item for item in matched if item.get("status") == "curated"]

        suppressed = [item for item in matched if item.get("pending_staging")]
        if not include_pending:
            matched = [item for item in matched if not item.get("pending_staging")]

        return {
            "scope": effective_scope,
            "query": query,
            "path": str(Path(path).expanduser().resolve()),
            "context": context,
            "context_ids": sorted(context_ids),
            "target_candidates": target_candidates,
            "domain_candidates": domain_candidates,
            "candidate_only": candidate_only,
            "results": sorted(matched, key=lambda item: item["id"]),
            "suppressed_pending": [item["id"] for item in sorted(suppressed, key=lambda item: item["id"])],
            "diagnostics": list(self.question_diagnostics),
        }

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
                    "trust": self.routes.get(identifier, {}).get("trust", "unknown"),
                    "checkout_state": self.routes.get(identifier, {}).get("checkout_state"),
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
                    "trust": self.routes.get(identifier, {}).get("trust", "unknown"),
                    "checkout_state": self.routes.get(identifier, {}).get("checkout_state"),
                    "component_type": record.get("component_type"),
                    "repository": record.get("repository"),
                    "locator_match": repository_candidate.get("locator_match", "not-verified"),
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

    def opposite_direction_peers(self, identifier: str, direction: str) -> list[str]:
        """Direct peers the requested direction excludes.

        A deletion question needs both directions: consumers break because they
        read the thing, and producers break because they write to it — but a
        producer sits on an incoming edge. Reporting one direction without
        saying the other is populated lets a partial answer read as complete.
        """
        other = "upstream" if direction == "downstream" else "downstream"
        peers = []
        for edge in self.edges:
            source = edge.source if other == "downstream" else edge.target
            if source == identifier:
                peers.append(edge.target if other == "downstream" else edge.source)
        return sorted(set(peers))

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

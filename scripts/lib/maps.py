from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re

from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.ids import valid_curated_id
from scripts.lib.taxonomy import load_contracts, load_taxonomy


RESOURCE_TYPE = "infra-resource"
MANIFEST_NAME = "atlas-package.json"
MAP_NAMES = (
    "flow-component-map.json",
    "repository-component-map.json",
    "infra-dependency-map.json",
)
MAP_KEYS = {
    "flow-component-map.json": "flow_component",
    "repository-component-map.json": "repository_component",
    "infra-dependency-map.json": "infra_dependency",
}
MAP_DESCRIPTIONS = {
    "flow-component-map.json": "Ordered flow steps, boundary I/O and operational routes.",
    "repository-component-map.json": "Repository topology and component-owned architecture dependencies.",
    "infra-dependency-map.json": "Infrastructure packages, promoted resources and direct users.",
}
QUESTION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
STEP_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ARCHITECTURE_TYPES = {"repository", "component", "flow", "infra"}
ROUTE_FIELDS = ("runbooks", "standards", "incident_learnings")


class MapBuildError(ValueError):
    def __init__(self, message: str, *, path: str | Path | None = None):
        super().__init__(message)
        self.path = Path(path).as_posix() if path is not None else None


@dataclass(frozen=True)
class MapValidationIssue:
    path: str
    record_id: str | None
    message: str


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


def load_package_config(root: str | Path) -> dict:
    root = Path(root)
    path = root / MANIFEST_NAME
    if not path.exists():
        raise MapBuildError(f"{MANIFEST_NAME} is required")
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MapBuildError(f"{MANIFEST_NAME}: invalid JSON: {exc}") from exc
    if config.get("schema_version") != "atlas-package/1.0":
        raise MapBuildError(f"{MANIFEST_NAME}: schema_version must be atlas-package/1.0")
    if config.get("type") != "package" or not valid_curated_id(config.get("id"), "package"):
        raise MapBuildError(f"{MANIFEST_NAME}: type/id must identify a package.* record")
    if not isinstance(config.get("package"), str) or not config["package"]:
        raise MapBuildError(f"{MANIFEST_NAME}: package is required")
    for required in ("status",):
        if not isinstance(config.get(required), str) or not config[required]:
            raise MapBuildError(f"{MANIFEST_NAME}: {required} is required")
    if not isinstance(config.get("owners"), dict):
        raise MapBuildError(f"{MANIFEST_NAME}: owners must be an object")
    if not isinstance(config.get("aliases"), list) or not all(
        isinstance(alias, str) and alias for alias in config["aliases"]
    ):
        raise MapBuildError(f"{MANIFEST_NAME}: aliases must be non-empty strings")
    for section in ("entrypoints", "taxonomy", "contracts"):
        values = config.get(section)
        if not isinstance(values, dict) or not values or not all(
            isinstance(value, str) and value for value in values.values()
        ):
            raise MapBuildError(f"{MANIFEST_NAME}: {section} must declare relative paths")
        for key, value in values.items():
            candidate = Path(value)
            if candidate.is_absolute() or ".." in candidate.parts:
                raise MapBuildError(f"{MANIFEST_NAME}: {section}.{key} must be package-relative")
    maps = config.get("maps")
    if not isinstance(maps, dict) or not all(isinstance(value, str) for value in maps.values()):
        raise MapBuildError(f"{MANIFEST_NAME}: maps must declare generated map paths")
    missing = sorted(set(MAP_KEYS.values()) - set(maps))
    if missing:
        raise MapBuildError(f"{MANIFEST_NAME}: missing map paths for {', '.join(missing)}")
    expected_paths = {
        "flow_component": Path("_curated/maps/flow-component/flow-component-map.json"),
        "repository_component": Path("_curated/maps/repository-component/repository-component-map.json"),
        "infra_dependency": Path("_curated/maps/infra-dependency/infra-dependency-map.json"),
    }
    for key, expected in expected_paths.items():
        declared = Path(maps[key])
        if declared.is_absolute() or declared != expected:
            raise MapBuildError(f"{MANIFEST_NAME}: {key} must be {expected.as_posix()}")
    domains = config.get("domains")
    if not isinstance(domains, list):
        raise MapBuildError(f"{MANIFEST_NAME}: domains must be a list")
    domain_ids: set[str] = set()
    for domain in domains:
        if not isinstance(domain, dict) or not isinstance(domain.get("id"), str):
            raise MapBuildError(f"{MANIFEST_NAME}: each domain requires an id")
        domain_id = domain["id"]
        if not QUESTION_ID_RE.fullmatch(domain_id) or domain_id in domain_ids:
            raise MapBuildError(f"{MANIFEST_NAME}: invalid or duplicate domain id {domain_id!r}")
        if not str(domain.get("title", "")).strip() or not str(domain.get("routing_description", "")).strip():
            raise MapBuildError(f"{MANIFEST_NAME}: domain {domain_id} requires title and routing_description")
        aliases = domain.get("aliases")
        if not isinstance(aliases, list) or not all(isinstance(alias, str) and alias for alias in aliases):
            raise MapBuildError(f"{MANIFEST_NAME}: domain {domain_id} aliases must be strings")
        domain_ids.add(domain_id)
    return config


def map_output_paths(root: str | Path) -> dict[str, Path]:
    root = Path(root)
    config = load_package_config(root)
    return {name: root / config["maps"][key] for name, key in MAP_KEYS.items()}


def curated_pages(
    root: str | Path,
    *,
    collect_errors: list[MapValidationIssue] | None = None,
) -> list[tuple[Path, dict, str]]:
    root = Path(root)
    curated = root / "_curated"
    out: list[tuple[Path, dict, str]] = []
    if not curated.exists():
        return out
    for path in sorted(curated.rglob("*.md")):
        rel = path.relative_to(root)
        if path.name in {"README.md", "index.md", "_template.md"}:
            continue
        if "maps" in rel.parts or "status" in rel.parts:
            continue
        try:
            fm, body = parse_frontmatter(path)
        except Exception as exc:
            error = MapBuildError(f"{rel}: invalid frontmatter: {exc}", path=rel)
            if collect_errors is None:
                raise error from exc
            collect_errors.append(MapValidationIssue(rel.as_posix(), None, f"invalid frontmatter: {exc}"))
            continue
        if fm.get("status") != "archived":
            out.append((path, fm, body))
    return out


def _coverage(value: object) -> str:
    if isinstance(value, dict):
        value = value.get("level")
    return value if isinstance(value, str) and value else "unknown"


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({str(item) for item in value if str(item).strip()})


def _list_field(path: Path, source: dict, field: str) -> list:
    value = source.get(field, [])
    if not isinstance(value, list):
        raise MapBuildError(f"{path}: {field} must be a list")
    return value


def _repository_root(path: Path, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MapBuildError(f"{path}: repository_root is required")
    root = value.strip().rstrip("/") or "."
    if root == ".":
        return root
    if "\\" in root or root.startswith("/") or re.match(r"^[A-Za-z]:", root):
        raise MapBuildError(f"{path}: repository_root must be a POSIX path relative to the physical Git root")
    if any(part in {"", ".", ".."} for part in root.split("/")):
        raise MapBuildError(f"{path}: repository_root contains an invalid path segment")
    return root


def _aliases(fm: dict) -> list[str]:
    routing = fm.get("routing")
    return _string_list(routing.get("aliases")) if isinstance(routing, dict) else []


def _common_record(root: Path, path: Path, fm: dict) -> dict:
    return {
        "title": fm.get("title", ""),
        "description": fm.get("description", ""),
        "page": path.relative_to(root).as_posix(),
        "status": fm.get("status"),
        "coverage": _coverage(fm.get("coverage")),
        "primary_domain": fm.get("primary_domain", ""),
        "related_domains": _string_list(fm.get("related_domains")),
        "aliases": _aliases(fm),
        "last_reviewed": fm.get("last_reviewed", ""),
    }


def _type_specs(taxonomy: dict) -> dict[str, dict]:
    return {
        item["name"]: item
        for item in taxonomy["types"].get("types") or []
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }


def _local_prefixes(taxonomy: dict) -> tuple[str, ...]:
    return tuple(
        f"{item['id_prefix']}."
        for item in taxonomy["types"].get("types") or []
        if isinstance(item, dict) and isinstance(item.get("id_prefix"), str) and item["id_prefix"]
    )


def _lookup_values(taxonomy: dict, source: str, dotted: str) -> set[str]:
    value: object = taxonomy[source]
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise MapBuildError(f"{source} does not define {dotted}")
        value = value[part]
    if not isinstance(value, list):
        raise MapBuildError(f"{source} {dotted} must be a list")
    return set(value)


def _enum_values(taxonomy: dict, dotted: str) -> set[str]:
    return _lookup_values(taxonomy, "concept_fields", dotted)


def domain_hint(typ: object, domain: object, domain_ids: set[str]) -> str:
    """Point an unregistered-domain failure at the file that actually needs editing."""
    if not domain_ids:
        return (
            f"no domains are registered yet, so no {typ} page can be stored; add the first domain to "
            "the atlas-package.json `domains` array before curating architecture records"
        )
    known = ", ".join(sorted(domain_ids))
    return (
        f"grouped {typ} requires a primary_domain registered in atlas-package.json; "
        f"got {domain!r}, registered domains are: {known}"
    )


def _record_error(
    collect: list[MapValidationIssue] | None,
    path: Path,
    exc: MapBuildError,
    record_id: str | None = None,
) -> None:
    """Attribute a per-record failure to its own page, or re-raise for strict callers.

    Strict callers (the generator) must still fail hard, because a skipped record
    would silently produce an incomplete map. Lint passes a collector so an author
    sees every offending page in one run instead of one error per rebuild.
    """
    if collect is None:
        raise exc
    text = str(exc)
    # Messages embed the path via str(Path), which is backslashed on Windows.
    for prefix in (f"{path}: ", f"{path.as_posix()}: "):
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    collect.append(MapValidationIssue(path.as_posix(), record_id, text))


def _resolved_type(identifier: str, page_by_id: dict[str, tuple[Path, dict, str]], resources: dict[str, dict]) -> str | None:
    if identifier in page_by_id:
        return page_by_id[identifier][1].get("type")
    if identifier in resources:
        return RESOURCE_TYPE
    return None


def _validate_confidence(path: Path, owner: str, entry: dict, taxonomy: dict) -> str:
    confidence = entry.get("confidence")
    allowed = set(taxonomy["statuses"]["connection_confidence"])
    if confidence not in allowed:
        raise MapBuildError(f"{path}: {owner} has invalid confidence {confidence!r}")
    if confidence == "reviewed" and not entry.get("evidence"):
        raise MapBuildError(f"{path}: reviewed {owner} requires evidence")
    if confidence != "reviewed" and not str(entry.get("note", "")).strip():
        raise MapBuildError(f"{path}: non-reviewed {owner} requires note")
    return confidence


def _project_entry(
    path: Path,
    owner: str,
    value: object,
    *,
    qualifier: str | None,
    allowed_qualifiers: set[str],
    allowed_target_types: set[str],
    page_by_id: dict[str, tuple[Path, dict, str]],
    resources: dict[str, dict],
    taxonomy: dict,
) -> dict:
    if not isinstance(value, dict):
        raise MapBuildError(f"{path}: {owner} entry must be an object")
    identifier = value.get("id")
    external_name = value.get("name")
    if bool(identifier) == bool(external_name):
        raise MapBuildError(f"{path}: {owner} requires exactly one of id or name")
    confidence = _validate_confidence(path, owner, value, taxonomy)
    projected: dict = {"confidence": confidence}
    if identifier:
        if not isinstance(identifier, str) or not identifier.startswith(_local_prefixes(taxonomy)):
            raise MapBuildError(f"{path}: {owner} id must use a registered local prefix")
        resolved_type = _resolved_type(identifier, page_by_id, resources)
        if resolved_type is None:
            if confidence == "reviewed":
                raise MapBuildError(f"{path}: reviewed local id does not resolve: {identifier}")
            projected.update({"id": identifier, "unresolved": True})
        else:
            if allowed_target_types and resolved_type not in allowed_target_types:
                raise MapBuildError(f"{path}: {owner} id {identifier} has invalid type {resolved_type}")
            projected["id"] = identifier
    else:
        if not isinstance(external_name, str) or not external_name.strip():
            raise MapBuildError(f"{path}: {owner} external name must be non-empty")
        projected.update({"name": external_name.strip(), "external": True})
    if qualifier:
        qualifier_value = value.get(qualifier)
        if qualifier_value not in allowed_qualifiers:
            raise MapBuildError(f"{path}: {owner} requires valid {qualifier}")
        projected[qualifier] = qualifier_value
    for key in ("role", "sequence", "note", "evidence", "condition"):
        if key in value and value[key] not in (None, "", []):
            projected[key] = value[key]
    return projected


def _project_entries(
    path: Path,
    fm: dict,
    source_type: str,
    field: str,
    *,
    page_by_id: dict[str, tuple[Path, dict, str]],
    resources: dict[str, dict],
    taxonomy: dict,
    map_contract: dict,
) -> list[dict]:
    values = _list_field(path, fm, field)
    spec = map_contract["fields"][source_type][field]
    qualifier = spec.get("qualifier")
    allowed_qualifiers = _enum_values(taxonomy, spec["values"]) if qualifier else set()
    return sorted(
        [
            _project_entry(
                path,
                field,
                value,
                qualifier=qualifier,
                allowed_qualifiers=allowed_qualifiers,
                allowed_target_types=set(spec.get("target_types") or []),
                page_by_id=page_by_id,
                resources=resources,
                taxonomy=taxonomy,
            )
            for value in values
        ],
        key=_item_sort_key,
    )


def _route_entries(
    path: Path,
    fm: dict,
    *,
    page_by_id: dict[str, tuple[Path, dict, str]],
    resources: dict[str, dict],
    taxonomy: dict,
    map_contract: dict,
) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for field in ROUTE_FIELDS:
        values = _list_field(path, fm, field)
        spec = map_contract["fields"]["routes"][field]
        out[field] = sorted(
            [
                _project_entry(
                    path,
                    field,
                    value,
                    qualifier=None,
                    allowed_qualifiers=set(),
                    allowed_target_types=set(spec.get("target_types") or []),
                    page_by_id=page_by_id,
                    resources=resources,
                    taxonomy=taxonomy,
                )
                for value in values
            ],
            key=_item_sort_key,
        )
    return out


def _split_table_row(line: str) -> list[str]:
    text = line.strip().strip("|")
    return [cell.replace(r"\|", "|").strip() for cell in re.split(r"(?<!\\)\|", text)]


def _open_questions(path: Path, body: str, record_id: str) -> list[dict]:
    heading = re.search(
        r"^##\s+Open questions / coverage limits\s*$([\s\S]*?)(?=^##\s+|\Z)",
        body,
        re.MULTILINE,
    )
    if not heading:
        return []
    lines = [line for line in heading.group(1).splitlines() if line.strip().startswith("|")]
    expected = ["question id", "question", "affected ids", "evidence gap"]
    header_index = next(
        (index for index, line in enumerate(lines) if [cell.lower() for cell in _split_table_row(line)] == expected),
        None,
    )
    if header_index is None:
        return []
    seen: set[str] = set()
    out: list[dict] = []
    for line in lines[header_index + 2 :]:
        cells = _split_table_row(line)
        if len(cells) != 4 or not any(cells):
            continue
        question_id, question, affected, gap = cells
        question_id = question_id.strip("`")
        if not QUESTION_ID_RE.fullmatch(question_id) or question_id in seen:
            raise MapBuildError(f"{path}: invalid or duplicate open question id {question_id!r}")
        if not question or not gap:
            raise MapBuildError(f"{path}: open question {question_id} requires question and evidence gap")
        seen.add(question_id)
        affected_ids = [] if affected.strip() in {"", "—", "-"} else [
            item.strip().strip("`") for item in affected.split(",") if item.strip()
        ]
        out.append(
            {
                "id": f"{record_id}#{question_id}",
                "affected_ids": affected_ids,
                "page": path.as_posix(),
                "anchor": "open-questions--coverage-limits",
            }
        )
    return sorted(out, key=lambda item: item["id"])


def _entry_points(
    path: Path,
    fm: dict,
    taxonomy: dict,
    page_by_id: dict[str, tuple[Path, dict, str]],
    resources: dict[str, dict],
) -> list[dict]:
    values = _list_field(path, fm, "entry_points")
    allowed = _enum_values(taxonomy, "flow.entry_point_type")
    out: list[dict] = []
    for entry in values:
        if not isinstance(entry, dict) or entry.get("entry_point_type") not in allowed:
            raise MapBuildError(f"{path}: entry point requires valid entry_point_type")
        if not str(entry.get("name", "")).strip():
            raise MapBuildError(f"{path}: entry point name is required")
        confidence = _validate_confidence(path, "entry point", entry, taxonomy)
        projected = {
            key: entry[key]
            for key in ("entry_point_type", "name", "sequence", "confidence", "evidence", "note")
            if key in entry and entry[key] not in (None, "", [])
        }
        identifier = entry.get("id")
        if identifier is not None:
            if not isinstance(identifier, str) or not identifier.startswith(_local_prefixes(taxonomy)):
                raise MapBuildError(f"{path}: entry point id must use a registered local prefix")
            if _resolved_type(identifier, page_by_id, resources) is None and confidence == "reviewed":
                raise MapBuildError(f"{path}: reviewed entry point id does not resolve: {identifier}")
            projected["id"] = identifier
        out.append(projected)
    return sorted(out, key=_item_sort_key)


def _flow_steps(
    path: Path,
    fm: dict,
    taxonomy: dict,
    page_by_id: dict[str, tuple[Path, dict, str]],
    resources: dict[str, dict],
    question_ids: set[str] | None,
) -> list[dict]:
    values = _list_field(path, fm, "steps")
    participant_types = _enum_values(taxonomy, "flow.participant_type")
    transition_types = _enum_values(taxonomy, "flow.transition_type")
    asset_types = _enum_values(taxonomy, "shared.asset_type")
    step_ids: set[str] = set()
    orders: set[int] = set()
    out: list[dict] = []
    raw_transitions: list[tuple[str, list]] = []
    for step in values:
        if not isinstance(step, dict):
            raise MapBuildError(f"{path}: flow step must be an object")
        step_id = step.get("step_id")
        order = step.get("order")
        if not isinstance(step_id, str) or not STEP_ID_RE.fullmatch(step_id) or step_id in step_ids:
            raise MapBuildError(f"{path}: flow step requires a unique kebab-case step_id")
        if not isinstance(order, int) or isinstance(order, bool) or order < 1 or order in orders:
            raise MapBuildError(f"{path}: flow step requires a unique positive order")
        if not str(step.get("name", "")).strip() or not str(step.get("role", "")).strip():
            raise MapBuildError(f"{path}: flow step {step_id} requires name and role")
        confidence = _validate_confidence(path, f"flow step {step_id}", step, taxonomy)
        participant = step.get("participant")
        if not isinstance(participant, dict) or participant.get("type") not in participant_types:
            raise MapBuildError(f"{path}: flow step {step_id} requires a typed participant")
        participant_type = participant["type"]
        participant_name = participant.get("name")
        participant_id = participant.get("id")
        if not str(participant_name or "").strip():
            raise MapBuildError(f"{path}: flow step {step_id} participant requires name")
        projected_participant = {"type": participant_type, "name": participant_name}
        if participant_id is not None:
            if participant_type not in {"component", "infra", "infra-resource"}:
                raise MapBuildError(f"{path}: flow step {step_id} {participant_type} participant cannot have id")
            expected_type = RESOURCE_TYPE if participant_type == "infra-resource" else participant_type
            if _resolved_type(participant_id, page_by_id, resources) != expected_type:
                raise MapBuildError(f"{path}: flow step {step_id} participant id does not resolve as {participant_type}")
            projected_participant["id"] = participant_id
        elif participant_type in {"infra", "infra-resource"}:
            raise MapBuildError(f"{path}: flow step {step_id} onboarded infrastructure requires id")
        elif (
            participant_type == "component"
            and question_ids is not None
            and step.get("onboarding_question_id") not in question_ids
        ):
            raise MapBuildError(f"{path}: unonboarded component step {step_id} requires a valid onboarding_question_id")

        def handoffs(field: str) -> list[dict]:
            handoff_values = _list_field(path, step, field)
            return sorted(
                [
                    _project_entry(
                        path,
                        f"flow step {step_id} {field}",
                        value,
                        qualifier="asset_type",
                        allowed_qualifiers=asset_types,
                        allowed_target_types={"component", "schema-info"},
                        page_by_id=page_by_id,
                        resources=resources,
                        taxonomy=taxonomy,
                    )
                    for value in handoff_values
                ],
                key=_item_sort_key,
            )

        transitions = _list_field(path, step, "transitions")
        raw_transitions.append((step_id, transitions))
        projected = {
            "step_id": step_id,
            "order": order,
            "name": step["name"],
            "participant": projected_participant,
            "role": step["role"],
            "confidence": confidence,
            "receives": handoffs("receives"),
            "emits": handoffs("emits"),
            "transitions": [],
        }
        for key in ("evidence", "note", "onboarding_question_id"):
            if key in step and step[key] not in (None, "", []):
                projected[key] = step[key]
        out.append(projected)
        step_ids.add(step_id)
        orders.add(order)
    by_id = {step["step_id"]: step for step in out}
    for source_id, transitions in raw_transitions:
        for transition in transitions:
            if not isinstance(transition, dict):
                raise MapBuildError(f"{path}: transition from {source_id} must be an object")
            target = transition.get("to")
            transition_type = transition.get("on")
            if target not in step_ids or transition_type not in transition_types:
                raise MapBuildError(f"{path}: transition from {source_id} has invalid to/on")
            item = {"to": target, "on": transition_type}
            for key in ("condition", "note", "evidence"):
                if key in transition and transition[key] not in (None, "", []):
                    item[key] = transition[key]
            by_id[source_id]["transitions"].append(item)
        by_id[source_id]["transitions"].sort(key=_item_sort_key)
    return sorted(out, key=_item_sort_key)


def _parent_id(target: object, expected_type: str, page_by_id: dict[str, tuple[Path, dict, str]]) -> str | None:
    if target in (None, ""):
        return None
    if not isinstance(target, str) or target not in page_by_id or page_by_id[target][1].get("type") != expected_type:
        raise MapBuildError(f"parent target must resolve to {expected_type}: {target!r}")
    return target


def _parent_cycles(records: dict[str, dict], parent_field: str) -> list[tuple[str, ...]]:
    """Return each parent cycle once, normalised to its lowest stable ID."""
    found: set[tuple[str, ...]] = set()
    for start in sorted(records):
        positions: dict[str, int] = {}
        chain: list[str] = []
        current = start
        while current in records and current not in positions:
            positions[current] = len(chain)
            chain.append(current)
            current = records[current].get(parent_field) or ""
        if current not in positions:
            continue
        cycle = chain[positions[current] :]
        lowest = min(range(len(cycle)), key=lambda index: cycle[index])
        found.add(tuple(cycle[lowest:] + cycle[:lowest]))
    return sorted(found)


def _item_sort_key(item: object) -> tuple:
    if not isinstance(item, dict):
        return (str(item),)
    return (
        item.get("order") is None,
        item.get("order") if isinstance(item.get("order"), int) else 0,
        item.get("sequence") is None,
        item.get("sequence") if isinstance(item.get("sequence"), int) else 0,
        str(item.get("id", "")),
        str(item.get("step_id", "")),
        str(item.get("name", "")),
        str(item.get("via", "")),
    )


def _append(items: list, value: object) -> None:
    if value not in items:
        items.append(value)


def _sort_lists(value: object, field: str | None = None) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            _sort_lists(child, key)
    elif isinstance(value, list):
        for child in value:
            _sort_lists(child)
        if field not in {"evidence", "steps", "transitions", "affected_ids"}:
            value.sort(key=_item_sort_key)


def _sparse(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: cleaned
            for key, child in value.items()
            if (cleaned := _sparse(child)) not in (None, "", [], {})
        }
    if isinstance(value, list):
        return [cleaned for child in value if (cleaned := _sparse(child)) not in (None, "", [], {})]
    return value


def _used_by(source_id: str, source_type: str, via: str, item: dict, **extra: object) -> dict:
    out = {
        "id": source_id,
        "type": source_type,
        "via": via,
        "confidence": item.get("confidence", "reviewed"),
        "evidence": item.get("evidence") or [],
    }
    for key in ("note", "role"):
        if item.get(key):
            out[key] = item[key]
    out.update({key: value for key, value in extra.items() if value not in (None, "", [], {})})
    return out


def _metadata(name: str, config: dict, map_contract: dict) -> dict:
    key = MAP_KEYS[name]
    contract = map_contract["maps"][key]
    return {
        "schema_version": "atlas-map/1.0",
        "generated": True,
        "generator": "scripts/rebuild_atlas.py",
        "package": config["package"],
        "map_type": contract["map_type"],
        "description": MAP_DESCRIPTIONS[name],
        "source_of_truth": list(contract["source_of_truth"]),
        "related_maps": {other: path for other, path in config["maps"].items() if other != key},
    }


def build_maps(
    root: str | Path,
    *,
    include_diagnostics: bool = False,
    collect_errors: list[MapValidationIssue] | None = None,
    include_body_questions: bool = True,
) -> dict[str, dict] | tuple[dict[str, dict], list[MapDiagnostic]]:
    """Compile the generated maps from curated pages.

    With `collect_errors`, per-record failures retain their page and stable ID and
    the record is skipped, so a caller can report every bad page at once. Set
    `include_body_questions=False` for frontmatter-only validation. The resulting
    maps are incomplete when errors are collected and must not be written.
    """
    root = Path(root).resolve()
    config = load_package_config(root)
    try:
        taxonomy = load_taxonomy(root)
    except Exception as exc:
        raise MapBuildError(
            f"registered taxonomy cannot be loaded: {exc}",
            path=getattr(exc, "path", None) or "taxonomy",
        ) from exc
    try:
        map_contract = load_contracts(root)["map_fields"]
    except Exception as exc:
        contract_path = getattr(exc, "path", None) or config.get("contracts", {}).get(
            "map_fields", "contracts/map-fields.yaml"
        )
        raise MapBuildError(f"registered map contract cannot be loaded: {exc}", path=contract_path) from exc
    type_specs = _type_specs(taxonomy)
    active_types = {name: spec for name, spec in type_specs.items() if spec.get("status") == "active"}
    domain_ids = {item["id"] for item in config.get("domains") or []}

    pages = curated_pages(root, collect_errors=collect_errors)
    page_by_id: dict[str, tuple[Path, dict, str]] = {}
    for absolute_path, fm, body in pages:
        rel = absolute_path.relative_to(root)
        try:
            typ = fm.get("type")
            spec = active_types.get(typ)
            if not spec or typ == "package" or str(typ).startswith("staging."):
                raise MapBuildError(f"{rel}: inactive or non-concept type {typ!r}")
            ident = fm.get("id")
            if not valid_curated_id(ident, spec.get("id_prefix")):
                raise MapBuildError(f"{rel}: invalid id {ident!r} for {typ}")
            if ident in page_by_id:
                raise MapBuildError(f"{rel}: duplicate curated id {ident}")
            if spec.get("grouped") == "domain":
                domain = fm.get("primary_domain")
                if not isinstance(domain, str) or domain not in domain_ids:
                    raise MapBuildError(f"{rel}: {domain_hint(typ, domain, domain_ids)}")
                folder = Path(spec["folder"])
                inside = rel.relative_to(folder)
                if len(inside.parts) < 2 or inside.parts[0] != domain:
                    raise MapBuildError(f"{rel}: folder must match primary_domain {domain}")
                related_domains = fm.get("related_domains", [])
                if not isinstance(related_domains, list) or any(
                    related not in domain_ids or related == domain for related in related_domains
                ):
                    raise MapBuildError(f"{rel}: related_domains must contain other registered domain IDs")
        except MapBuildError as exc:
            _record_error(collect_errors, rel, exc, fm.get("id") if isinstance(fm.get("id"), str) else None)
            continue
        page_by_id[ident] = (rel, fm, body)

    allowed_coverage = set(taxonomy["statuses"]["map_coverage"])
    allowed_resource_types = _enum_values(taxonomy, "infrastructure.resource_type")
    resource_spec = type_specs[RESOURCE_TYPE]
    resources: dict[str, dict] = {}
    resource_sources: dict[str, tuple[Path, dict]] = {}
    for parent_id, (path, fm, _) in page_by_id.items():
        if fm.get("type") != "infra":
            continue
        promoted = fm.get("promoted_resources", [])
        if not isinstance(promoted, list):
            _record_error(
                collect_errors,
                path,
                MapBuildError(f"{path}: promoted_resources must be a list"),
                parent_id,
            )
            continue
        for resource in promoted:
            try:
                if not isinstance(resource, dict):
                    raise MapBuildError(f"{path}: promoted resource must be an object")
                ident = resource.get("id")
                if not valid_curated_id(ident, resource_spec.get("id_prefix")) or ident in page_by_id or ident in resources:
                    raise MapBuildError(f"{path}: invalid or duplicate promoted resource id {ident!r}")
                if resource.get("resource_type") not in allowed_resource_types:
                    raise MapBuildError(f"{path}: promoted resource {ident} has invalid resource_type")
                if not all(str(resource.get(field, "")).strip() for field in ("name", "defined_in_path", "promotion_reason")):
                    raise MapBuildError(f"{path}: promoted resource {ident} requires name, defined_in_path and promotion_reason")
                if not isinstance(resource.get("environments"), list):
                    raise MapBuildError(f"{path}: promoted resource {ident} environments must be a list")
                _validate_confidence(path, f"promoted resource {ident}", resource, taxonomy)
                if _coverage(resource.get("coverage")) not in allowed_coverage:
                    raise MapBuildError(f"{path}: promoted resource {ident} has invalid coverage")
            except MapBuildError as exc:
                _record_error(collect_errors, path, exc, parent_id)
                continue
            resources[ident] = {
                "name": resource["name"],
                "resource_type": resource["resource_type"],
                "parent_package": parent_id,
                "page": path.as_posix(),
                "status": fm.get("status"),
                "defined_in_path": resource["defined_in_path"],
                "environments": _string_list(resource.get("environments")),
                "promotion_reason": resource["promotion_reason"],
                "confidence": resource["confidence"],
                "coverage": _coverage(resource.get("coverage")),
                "evidence": resource.get("evidence") or [],
                "used_by": [],
            }
            resource_sources[ident] = (path, resource)

    repositories: dict[str, dict] = {}
    components: dict[str, dict] = {}
    flows: dict[str, dict] = {}
    packages: dict[str, dict] = {}
    diagnostics: list[MapDiagnostic] = []

    def project_page(ident: str, path: Path, fm: dict, body: str) -> None:
        typ = fm["type"]
        common = _common_record(root, root / path, fm)
        questions = _open_questions(path, body, ident) if include_body_questions else []
        if typ in ARCHITECTURE_TYPES and "links" in fm:
            raise MapBuildError(f"{path}: architecture pages use runbooks/standards/incident_learnings, not links")
        if typ == "repository":
            repository_type = fm.get("repository_type", "unknown")
            if repository_type not in _enum_values(taxonomy, "repository.repository_type"):
                raise MapBuildError(f"{path}: invalid repository_type {repository_type!r}")
            source_roots = _list_field(path, fm, "source_roots")
            projected_roots = []
            for source_root in source_roots:
                if not isinstance(source_root, dict) or not str(source_root.get("path", "")).strip():
                    raise MapBuildError(f"{path}: source root requires path")
                projected_roots.append(
                    {key: source_root[key] for key in ("path", "purpose", "evidence") if source_root.get(key)}
                )
            repositories[ident] = {
                **common,
                "repository_locator": fm.get("repository_locator", ""),
                "repository_root": _repository_root(path, fm.get("repository_root")),
                "repository_type": repository_type,
                "default_branch": fm.get("default_branch", ""),
                "parent_repository": _parent_id(fm.get("parent_repository"), "repository", page_by_id),
                "source_roots": projected_roots,
                "components": [],
                "depends_on_repositories": _project_entries(
                    path, fm, "repository", "depends_on_repositories",
                    page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract,
                ),
                "used_by": [],
                **_route_entries(path, fm, page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract),
                "open_questions": questions,
            }
        elif typ == "component":
            component_type = fm.get("component_type", "unknown")
            if component_type not in _enum_values(taxonomy, "component.component_type"):
                raise MapBuildError(f"{path}: invalid component_type {component_type!r}")
            repository_id = _parent_id(fm.get("repository"), "repository", page_by_id)
            if not repository_id:
                raise MapBuildError(f"{path}: component requires an onboarded repository ID")
            components[ident] = {
                **common,
                "component_type": component_type,
                "repository": repository_id,
                "repository_paths": _string_list(_list_field(path, fm, "repository_paths")),
                "parent_component": _parent_id(fm.get("parent_component"), "component", page_by_id),
                **{
                    field: _project_entries(
                        path, fm, "component", field,
                        page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract,
                    )
                    for field in map_contract["fields"]["component"]
                },
                "used_by": [],
                **_route_entries(path, fm, page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract),
                "open_questions": questions,
            }
        elif typ == "flow":
            flows[ident] = {
                **common,
                "flow_scope": fm.get("flow_scope", ""),
                "entry_points": _entry_points(path, fm, taxonomy, page_by_id, resources),
                "inputs": _project_entries(
                    path, fm, "flow", "inputs",
                    page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract,
                ),
                "outputs": _project_entries(
                    path, fm, "flow", "outputs",
                    page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract,
                ),
                "upstream_flows": _project_entries(
                    path, fm, "flow", "upstream_flows",
                    page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract,
                ),
                "downstream_flows": [],
                "steps": _flow_steps(
                    path, fm, taxonomy, page_by_id, resources,
                    {question["id"].split("#", 1)[1] for question in questions}
                    if include_body_questions
                    else None,
                ),
                **_route_entries(path, fm, page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract),
                "open_questions": questions,
            }
        elif typ == "infra":
            repository_id = _parent_id(fm.get("repository"), "repository", page_by_id) if fm.get("repository") else None
            if repository_id and not str(fm.get("package_path", "")).strip():
                raise MapBuildError(f"{path}: repository-backed infrastructure requires package_path")
            packages[ident] = {
                **common,
                "infra_package": fm.get("infra_package", ""),
                "repository": repository_id,
                "package_path": fm.get("package_path", ""),
                "template_path": fm.get("template_path", ""),
                "environments": _string_list(_list_field(path, fm, "environments")),
                "resources": sorted(
                    resource_id for resource_id, record in resources.items() if record["parent_package"] == ident
                ),
                **{
                    field: _project_entries(
                        path, fm, "infrastructure", field,
                        page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract,
                    )
                    for field in map_contract["fields"]["infrastructure"]
                },
                "used_by": [],
                **_route_entries(path, fm, page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract),
                "open_questions": questions,
            }
        elif "links" in fm:
            links = fm["links"]
            if not isinstance(links, list):
                raise MapBuildError(f"{path}: links must be a list")
            allowed_links = map_contract.get("page_links") or {}
            for link in links:
                if not isinstance(link, dict):
                    raise MapBuildError(f"{path}: link must be an object")
                link_type = link.get("type")
                target = link.get("target")
                if link_type not in allowed_links or not isinstance(target, str) or not target:
                    raise MapBuildError(f"{path}: invalid page link type/target")
                confidence = _validate_confidence(path, f"link {link_type}", link, taxonomy)
                resolved_type = _resolved_type(target, page_by_id, resources)
                allowed_targets = set(allowed_links[link_type].get("target_types") or [])
                if resolved_type and allowed_targets and resolved_type not in allowed_targets:
                    raise MapBuildError(f"{path}: link {link_type} target {target} has invalid type {resolved_type}")
                if target.startswith(_local_prefixes(taxonomy)) and resolved_type is None and confidence == "reviewed":
                    raise MapBuildError(f"{path}: reviewed page link target does not resolve: {target}")
                diagnostics.append(
                    MapDiagnostic(
                        source=ident,
                        relationship=link_type,
                        target=target,
                        reason="valid cross-cutting page link has no projection in the architecture maps",
                    )
                )

    for ident, (path, fm, body) in page_by_id.items():
        try:
            project_page(ident, path, fm, body)
        except MapBuildError as exc:
            _record_error(collect_errors, path, exc, ident)

    for records, parent_field, label in (
        (repositories, "parent_repository", "repository"),
        (components, "parent_component", "component"),
    ):
        for cycle in _parent_cycles(records, parent_field):
            record_id = cycle[0]
            path = page_by_id[record_id][0]
            error = MapBuildError(f"{path}: {label} hierarchy contains cycle: {' -> '.join((*cycle, cycle[0]))}")
            _record_error(collect_errors, path, error, record_id)

    for repo_id, repo in repositories.items():
        for dependency in repo["depends_on_repositories"]:
            target = dependency.get("id")
            if target in repositories:
                _append(repositories[target]["used_by"], _used_by(repo_id, "repository", "depends_on_repositories", dependency))

    for component_id, component in components.items():
        owning_repository = repositories.get(component["repository"])
        if owning_repository is not None:
            # Absent only in collect mode, where the repository page itself failed.
            owning_repository["components"].append(component_id)
        for dependency in component["depends_on"]:
            target = dependency.get("id")
            if target in components:
                _append(components[target]["used_by"], _used_by(component_id, "component", "depends_on", dependency))

    for flow_id, flow in flows.items():
        for upstream in flow["upstream_flows"]:
            target = upstream.get("id")
            if target in flows:
                _append(
                    flows[target]["downstream_flows"],
                    _used_by(flow_id, "flow", "upstream_flows", upstream),
                )
        for step in flow["steps"]:
            participant = step["participant"]
            participant_id = participant.get("id")
            target_record = components.get(participant_id) or packages.get(participant_id) or resources.get(participant_id)
            if target_record is not None:
                _append(
                    target_record["used_by"],
                    _used_by(
                        flow_id,
                        "flow",
                        "steps",
                        step,
                        step_id=step["step_id"],
                        order=step["order"],
                        role=step["role"],
                    ),
                )

    infra_targets = {**packages, **resources}

    def add_infra_users(source_id: str, source_type: str, record: dict, fields: list[str]) -> None:
        for field in fields:
            for item in record.get(field) or []:
                target = item.get("id")
                if target in infra_targets:
                    _append(infra_targets[target]["used_by"], _used_by(source_id, source_type, field, item))

    component_infra_fields = [
        field
        for field, spec in map_contract["fields"]["component"].items()
        if set(spec.get("target_types") or []) & {"infra", RESOURCE_TYPE}
    ]
    for component_id, component in components.items():
        add_infra_users(component_id, "component", component, component_infra_fields)

    for resource_id, (path, source) in resource_sources.items():
        for field in map_contract["fields"]["infrastructure"]:
            source.setdefault(field, [])
        try:
            projected_actions = {
                field: _project_entries(
                    path, source, "infrastructure", field,
                    page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract,
                )
                for field in map_contract["fields"]["infrastructure"]
            }
            projected_routes = _route_entries(
                path, source, page_by_id=page_by_id, resources=resources, taxonomy=taxonomy, map_contract=map_contract
            )
        except MapBuildError as exc:
            _record_error(collect_errors, path, exc, resource_id)
            continue
        resources[resource_id].update(projected_actions)
        resources[resource_id].update(projected_routes)

    infra_fields = list(map_contract["fields"]["infrastructure"])
    for package_id, package in packages.items():
        add_infra_users(package_id, "infra", package, infra_fields)
    for resource_id, resource in resources.items():
        add_infra_users(resource_id, RESOURCE_TYPE, resource, infra_fields)

    for records in (repositories, components, flows, packages, resources):
        _sort_lists(records)
        for ident, record in list(records.items()):
            records[ident] = _sparse(record)

    maps = {
        "flow-component-map.json": {
            "metadata": _metadata("flow-component-map.json", config, map_contract),
            "flows": dict(sorted(flows.items())),
        },
        "repository-component-map.json": {
            "metadata": _metadata("repository-component-map.json", config, map_contract),
            "repositories": dict(sorted(repositories.items())),
            "components": dict(sorted(components.items())),
        },
        "infra-dependency-map.json": {
            "metadata": _metadata("infra-dependency-map.json", config, map_contract),
            "packages": dict(sorted(packages.items())),
            "resources": dict(sorted(resources.items())),
        },
    }
    if include_diagnostics:
        return maps, diagnostics
    return maps


def validate_map_frontmatter(root: str | Path) -> list[MapValidationIssue]:
    """Validate structured curated frontmatter without inspecting page-body shape."""
    issues: list[MapValidationIssue] = []
    build_maps(root, collect_errors=issues, include_body_questions=False)
    return issues

from __future__ import annotations

from pathlib import Path
import os
import re

from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.maps import curated_pages, iso_date_text, load_package_config
from scripts.lib.query import AtlasQuery
from scripts.lib.taxonomy import load_taxonomy


# Domain-grouped architecture records and flat governance records are catalogued
# the same way; only the middle routing column differs.
GOVERNANCE_COLLECTIONS = {
    "standards": "standard",
    "runbooks": "runbook",
    "incidents": "incident-learning",
    "business-concepts": "business-concept",
}


CATALOGUE_START = "<!-- atlas:generated-catalogue:start -->"
CATALOGUE_END = "<!-- atlas:generated-catalogue:end -->"


def _coverage(value: object) -> str:
    if isinstance(value, dict):
        value = value.get("level")
    return value if isinstance(value, str) and value else "unknown"


def _cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\r", " ").replace("\n", " ").strip()


def _managed(text: str, name: str, content: str) -> str:
    start = f"<!-- atlas:generated-{name}:start -->"
    end = f"<!-- atlas:generated-{name}:end -->"
    block = f"{start}\n{content.rstrip()}\n{end}"
    pattern = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
    if pattern.search(text):
        return pattern.sub(lambda _: block, text)
    return text.rstrip() + "\n\n" + block + "\n"


def _managed_optional(text: str, name: str, content: str | None) -> str:
    start = f"<!-- atlas:generated-{name}:start -->"
    end = f"<!-- atlas:generated-{name}:end -->"
    pattern = re.compile(r"\n*" + re.escape(start) + r"[\s\S]*?" + re.escape(end) + r"\n*")
    if not content:
        return pattern.sub("\n", text).rstrip() + "\n"
    return _managed(text, name, content)


def _relative_link(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(to_path, from_path.parent)).as_posix()


def _curated_records(root: Path, folder: str, typ: str) -> list[tuple[Path, dict]]:
    base = root / "_curated" / folder
    return [
        (path, fm)
        for path, fm, _ in curated_pages(root)
        if fm.get("type") == typ and path.is_relative_to(base)
    ]


def _catalogue(rows: list[tuple[Path, dict]], index_path: Path, *, mode: str = "domain") -> str:
    headers = {
        "domain": "| ID | Title | Description | Status | Primary domain | Coverage | Page |",
        "staging": "| ID | Title | Status | Candidate domain | Source context | Page |",
        "standard": "| ID | Title | Description | Status | Category | Last reviewed | Page |",
        "governance": "| ID | Title | Description | Status | Last reviewed | Page |",
    }
    separators = {
        "domain": "|---|---|---|---|---|---|---|",
        "staging": "|---|---|---|---|---|---|",
        "standard": "|---|---|---|---|---|---|---|",
        "governance": "|---|---|---|---|---|---|",
    }
    lines = [CATALOGUE_START, "## Catalogue", "", headers[mode], separators[mode]]
    for path, fm in sorted(rows, key=lambda item: str(item[1].get("id", ""))):
        link = _relative_link(index_path, path)
        description = _cell(fm.get("description")) or "—"
        if mode == "staging":
            # Candidate domain belongs to the record path, not the catalogue
            # currently rendering it. A per-domain index has the same parent
            # as its records and must not relabel them as `unassigned`.
            domain = path.parent.name if path.parent.name not in {"components", "flows"} else "unassigned"
            lines.append(
                f"| `{fm.get('id', '')}` | {_cell(fm.get('title'))} | `{fm.get('status', '')}` | "
                f"`{domain}` | {_cell(fm.get('source_type'))} | [page]({link}) |"
            )
        elif mode == "standard":
            category = fm.get("standard_category")
            lines.append(
                f"| `{fm.get('id', '')}` | {_cell(fm.get('title'))} | {description} | "
                f"`{fm.get('status', '')}` | {f'`{category}`' if category else '—'} | "
                f"`{iso_date_text(fm.get('last_reviewed'))}` | [page]({link}) |"
            )
        elif mode == "governance":
            lines.append(
                f"| `{fm.get('id', '')}` | {_cell(fm.get('title'))} | {description} | "
                f"`{fm.get('status', '')}` | `{iso_date_text(fm.get('last_reviewed'))}` | [page]({link}) |"
            )
        else:
            lines.append(
                f"| `{fm.get('id', '')}` | {_cell(fm.get('title'))} | {description} | "
                f"`{fm.get('status', '')}` | `{fm.get('primary_domain', '')}` | "
                f"`{_coverage(fm.get('coverage'))}` | [page]({link}) |"
            )
    if not rows:
        empty_cells = 7 if mode in {"domain", "standard"} else 6
        lines.append("| " + " | ".join(["—", "No records", *(["—"] * (empty_cells - 2))]) + " |")
    lines.append(CATALOGUE_END)
    return "\n".join(lines)


def _index_skeleton(title: str, purpose: str, catalogue: str) -> str:
    return (
        f"# {title}\n\n"
        "## Use this index\n\n"
        f"{purpose}\n\n"
        f"{catalogue}\n\n"
        "## Coverage notes\n\n"
        "- Coverage is derived from the listed records; absence is not evidence of no system or impact.\n"
    )


def _replace_catalogue(text: str, catalogue: str) -> str:
    pattern = re.compile(re.escape(CATALOGUE_START) + r"[\s\S]*?" + re.escape(CATALOGUE_END))
    if pattern.search(text):
        return pattern.sub(lambda _: catalogue, text)
    return text.rstrip() + "\n\n" + catalogue + "\n"


def build_index_outputs(root: str | Path) -> dict[Path, bytes]:
    root = Path(root).resolve()
    config = load_package_config(root)
    outputs: dict[Path, bytes] = {}
    collections = {
        "repositories": "repository",
        "components": "component",
        "flows": "flow",
        "infra": "infra",
        "schema-info": "schema-info",
    }
    domain_ids = [item["id"] for item in config.get("domains") or []]
    for folder, typ in collections.items():
        rows = _curated_records(root, folder, typ)
        index_path = root / "_curated" / folder / "index.md"
        catalogue = _catalogue(rows, index_path)
        if index_path.exists():
            rendered = _replace_catalogue(index_path.read_text(encoding="utf-8"), catalogue)
        else:
            rendered = _index_skeleton(
                f"{folder.replace('-', ' ').title()} index",
                f"Use this catalogue to route to reviewed {folder.replace('-', ' ')} records.",
                catalogue,
            )
        outputs[index_path] = rendered.encode("utf-8")
        used_domains = sorted({str(fm.get("primary_domain")) for _, fm in rows if fm.get("primary_domain")})
        for domain in sorted(set(domain_ids) | set(used_domains)):
            domain_rows = [(path, fm) for path, fm in rows if fm.get("primary_domain") == domain]
            domain_index = root / "_curated" / folder / domain / "index.md"
            domain_catalogue = _catalogue(domain_rows, domain_index)
            if domain_index.exists():
                domain_text = _replace_catalogue(domain_index.read_text(encoding="utf-8"), domain_catalogue)
            else:
                domain_text = _index_skeleton(
                    f"{domain} {folder.replace('-', ' ')} index",
                    f"Use this catalogue for the `{domain}` domain.",
                    domain_catalogue,
                )
            outputs[domain_index] = domain_text.encode("utf-8")

    categories = load_taxonomy(root)["categories"].get("categories") or []
    for folder, typ in GOVERNANCE_COLLECTIONS.items():
        rows = _curated_records(root, folder, typ)
        index_path = root / "_curated" / folder / "index.md"
        mode = "standard" if folder == "standards" else "governance"
        catalogue = _catalogue(rows, index_path, mode=mode)
        if index_path.exists():
            rendered = _replace_catalogue(index_path.read_text(encoding="utf-8"), catalogue)
        else:
            rendered = _index_skeleton(
                f"{folder.replace('-', ' ').title()} index",
                f"Use this catalogue to route to reviewed {folder.replace('-', ' ')} records.",
                catalogue,
            )
        outputs[index_path] = rendered.encode("utf-8")
        if folder != "standards":
            continue
        used_categories = {str(fm.get("standard_category")) for _, fm in rows if fm.get("standard_category")}
        for category in sorted(set(categories) | used_categories):
            category_rows = [(path, fm) for path, fm in rows if fm.get("standard_category") == category]
            category_index = root / "_curated" / folder / category / "index.md"
            category_catalogue = _catalogue(category_rows, category_index, mode="standard")
            if category_index.exists():
                category_text = _replace_catalogue(
                    category_index.read_text(encoding="utf-8"), category_catalogue
                )
            else:
                category_text = _index_skeleton(
                    f"{category} standards index",
                    f"Use this catalogue for the `{category}` standard category.",
                    category_catalogue,
                )
            outputs[category_index] = category_text.encode("utf-8")

    for folder, typ in {"components": "staging.component", "flows": "staging.flow"}.items():
        base = root / "_staging" / folder
        rows: list[tuple[Path, dict]] = []
        if base.exists():
            for path in sorted(base.rglob("*.md")):
                if path.name in {"README.md", "index.md", "_template.md"}:
                    continue
                fm, _ = parse_frontmatter(path)
                if fm.get("type") == typ:
                    rows.append((path, fm))
        index_path = base / "index.md"
        catalogue = _catalogue(rows, index_path, mode="staging")
        rendered = (
            _replace_catalogue(index_path.read_text(encoding="utf-8"), catalogue)
            if index_path.exists()
            else _index_skeleton(
                f"Staging {folder} queue",
                "Use this generated catalogue to review evidence by lifecycle state and candidate domain.",
                catalogue,
            )
        )
        outputs[index_path] = rendered.encode("utf-8")
        domains = sorted(
            {path.relative_to(base).parts[0] for path, _ in rows if len(path.relative_to(base).parts) > 1}
            | set(domain_ids)
            | {"unassigned"}
        )
        for domain in domains:
            domain_rows = [
                (path, fm)
                for path, fm in rows
                if len(path.relative_to(base).parts) > 1 and path.relative_to(base).parts[0] == domain
            ]
            domain_index = base / domain / "index.md"
            domain_catalogue = _catalogue(domain_rows, domain_index, mode="staging")
            rendered = (
                _replace_catalogue(domain_index.read_text(encoding="utf-8"), domain_catalogue)
                if domain_index.exists()
                else _index_skeleton(
                    f"{domain} staging {folder} queue",
                    f"Use this queue for staging evidence assigned to `{domain}`.",
                    domain_catalogue,
                )
            )
            outputs[domain_index] = rendered.encode("utf-8")
    return outputs


def generated_index_candidates(root: str | Path) -> set[Path]:
    """Return only Atlas-managed catalogue indexes eligible for stale cleanup."""
    root = Path(root).resolve()
    bases = [
        *(root / "_curated" / folder for folder in ("repositories", "components", "flows", "infra", "schema-info")),
        *(root / "_curated" / folder for folder in GOVERNANCE_COLLECTIONS),
        root / "_staging" / "components",
        root / "_staging" / "flows",
    ]
    candidates: set[Path] = set()
    for base in bases:
        if not base.exists():
            continue
        for path in base.rglob("index.md"):
            if CATALOGUE_START in path.read_text(encoding="utf-8"):
                candidates.add(path.resolve())
    return candidates


def _record_link(root: Path, from_path: Path, identifier: str, routes: dict[str, dict]) -> str:
    route = routes.get(identifier) or {}
    page = route.get("page")
    if not isinstance(page, str) or not page:
        return f"`{identifier}`"
    target = root / page
    return f"[`{identifier}`]({_relative_link(from_path, target)})"


def _target_text(root: Path, page: Path, routes: dict[str, dict], values: object) -> str:
    if not isinstance(values, list) or not values:
        return "—"
    return ", ".join(
        _record_link(root, page, item["id"], routes)
        if isinstance(item, dict) and isinstance(item.get("id"), str)
        else f"`{item.get('name', '')}`"
        for item in values
        if isinstance(item, dict)
    ) or "—"


def _flow_steps_table(root: Path, page: Path, fm: dict, routes: dict[str, dict]) -> str:
    lines = [
        "| Order | Step ID | Step | Participant | Type | Role | Receives | Emits | Transitions | Confidence |",
        "|---:|---|---|---|---|---|---|---|---|---|",
    ]
    steps = sorted(fm.get("steps") or [], key=lambda step: step.get("order", 0) if isinstance(step, dict) else 0)
    for step in steps:
        participant = step.get("participant") or {}
        transitions = step.get("transitions") or []
        transition_text = ", ".join(
            f"`{item.get('on', '')}` → `{item.get('to', '')}`" for item in transitions if isinstance(item, dict)
        ) or "implied by order"
        participant_text = participant.get("name", "")
        if participant.get("id"):
            participant_text += f" ({_record_link(root, page, participant['id'], routes)})"
        lines.append(
            f"| {step.get('order', '')} | `{step.get('step_id', '')}` | {step.get('name', '')} | "
            f"{participant_text} | `{participant.get('type', '')}` | {step.get('role', '')} | "
            f"{_target_text(root, page, routes, step.get('receives'))} | "
            f"{_target_text(root, page, routes, step.get('emits'))} | "
            f"{transition_text} | `{step.get('confidence', '')}` |"
        )
    if not steps:
        lines.append("| — | — | No steps captured | — | — | — | — | — | — | — |")
    return "\n".join(lines)


def _mermaid(fm: dict) -> str:
    if not fm.get("diagram"):
        return "_No generated diagram requested._"
    steps = sorted(fm.get("steps") or [], key=lambda step: step.get("order", 0))
    if not steps:
        return "_No steps are available to diagram._"
    node_names = {step["step_id"]: f"s{index}" for index, step in enumerate(steps)}
    lines = ["```mermaid", "flowchart LR"]
    for step in steps:
        participant = step.get("participant") or {}
        label = f"{step.get('order')}. {step.get('name')}\\n{participant.get('name', '')}".replace('"', "'")
        lines.append(f'    {node_names[step["step_id"]]}["{label}"]')
    for index, step in enumerate(steps):
        transitions = step.get("transitions") or []
        if transitions:
            for transition in transitions:
                label = transition.get("on", "")
                lines.append(
                    f"    {node_names[step['step_id']]} -->|{label}| {node_names[transition['to']]}"
                )
        elif index + 1 < len(steps):
            following = steps[index + 1]
            lines.append(f"    {node_names[step['step_id']]} --> {node_names[following['step_id']]}")
    lines.append("```")
    return "\n".join(lines)


def _repository_table(fm: dict) -> str:
    lines = ["| Source root | Purpose | Evidence |", "|---|---|---|"]
    for item in fm.get("source_roots") or []:
        lines.append(
            f"| `{item.get('path', '')}` | {item.get('purpose', '')} | {', '.join(item.get('evidence') or [])} |"
        )
    if len(lines) == 2:
        lines.append("| — | No source roots captured | — |")
    return "\n".join(lines)


def _component_table(root: Path, page: Path, fm: dict, routes: dict[str, dict]) -> str:
    lines = ["| Field | Target | Qualifier/action | Confidence | Evidence |", "|---|---|---|---|---|"]
    for field, qualifier in (
        ("consumes", "asset_type"),
        ("produces", "asset_type"),
        ("depends_on", "dependency_type"),
        ("uses_resources", None),
        ("reads_from", None),
        ("writes_to", None),
        ("triggers", None),
        ("scheduled_by", None),
        ("deployed_by", None),
        ("monitored_by", None),
    ):
        for item in fm.get(field) or []:
            target = (
                _record_link(root, page, item["id"], routes)
                if isinstance(item.get("id"), str)
                else f"`{item.get('name', '')}`"
            )
            lines.append(
                f"| `{field}` | {target} | "
                f"`{item.get(qualifier, '') if qualifier else field}` | "
                f"`{item.get('confidence', '')}` | {', '.join(item.get('evidence') or [])} |"
            )
    if len(lines) == 2:
        lines.append("| — | No structured routing facts captured | — | — | — |")
    return "\n".join(lines)


def _infra_table(root: Path, page: Path, fm: dict, routes: dict[str, dict]) -> str:
    lines = ["| Record/field | Target or resource | Type/action | Confidence | Evidence |", "|---|---|---|---|---|"]
    for resource in fm.get("promoted_resources") or []:
        resource_id = str(resource.get("id", ""))
        lines.append(
            f"| `promoted_resource` | {_record_link(root, page, resource_id, routes)} | "
            f"`{resource.get('resource_type', '')}` | "
            f"`{resource.get('confidence', '')}` | {', '.join(resource.get('evidence') or [])} |"
        )
    for field in (
        "depends_on",
        "uses_resources",
        "reads_from",
        "writes_to",
        "triggers",
        "scheduled_by",
        "imports_values",
        "exports_values",
        "permissions",
        "monitored_by",
        "deployed_by",
    ):
        for item in fm.get(field) or []:
            action = item.get("dependency_type") or field
            target = (
                _record_link(root, page, item["id"], routes)
                if isinstance(item.get("id"), str)
                else f"`{item.get('name', '')}`"
            )
            lines.append(
                f"| `{field}` | {target} | `{action}` | `{item.get('confidence', '')}` | "
                f"{', '.join(item.get('evidence') or [])} |"
            )
    if len(lines) == 2:
        lines.append("| — | No structured infrastructure facts captured | — | — | — |")
    return "\n".join(lines)


def _related_routes(root: Path, page: Path, fm: dict, query: AtlasQuery) -> str:
    identifier = fm.get("id")
    if not isinstance(identifier, str):
        return "## Related Atlas routes\n\n_No resolved direct Atlas routes._"
    rows: set[tuple[str, str, str, str]] = set()
    for edge in query.edges:
        if edge.source == identifier:
            peer = edge.target
        elif edge.target == identifier:
            peer = edge.source
        else:
            continue
        route = query.routes.get(peer) or {}
        if not route.get("page") or peer.startswith("external:"):
            continue
        rows.add(
            (
                str(route.get("type") or "record"),
                peer,
                edge.field,
                edge.confidence,
            )
        )
    for item in fm.get("links") or []:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        peer = item["id"]
        route = query.routes.get(peer) or {}
        if route.get("page"):
            rows.add((str(route.get("type") or "record"), peer, "links", str(item.get("confidence") or "reviewed")))

    lines = ["## Related Atlas routes", ""]
    if not rows:
        lines.append("_No resolved direct Atlas routes._")
        return "\n".join(lines)
    lines.extend(
        [
            "| Record type | Record | Via | Confidence |",
            "|---|---|---|---|",
        ]
    )
    for record_type, peer, field, confidence in sorted(rows):
        route = query.routes.get(peer) or {}
        title = route.get("title") or route.get("name") or ""
        label = _record_link(root, page, peer, query.routes)
        if title and title != peer:
            label += f" — {_cell(title)}"
        lines.append(f"| `{record_type}` | {label} | `{field}` | `{confidence}` |")
    return "\n".join(lines)


def _asset_table(root: Path, page: Path, fm: dict, routes: dict[str, dict]) -> str | None:
    assets = fm.get("assets") or []
    if not assets:
        return None
    lines = [
        "## Data assets and lineage",
        "",
        "| Asset | Type | Physical name | Inputs | Confidence | Evidence |",
        "|---|---|---|---|---|---|",
    ]
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        inputs: list[str] = []
        for item in asset.get("inputs") or []:
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("id"), str):
                inputs.append(_record_link(root, page, item["id"], routes))
            else:
                inputs.append(f"`{_cell(item.get('name'))}` (external)")
        lines.append(
            f"| {_record_link(root, page, asset.get('id', ''), routes)} — {_cell(asset.get('name'))} | "
            f"`{_cell(asset.get('asset_type'))}` | `{_cell(asset.get('physical_name'))}` | "
            f"{', '.join(inputs) or '—'} | `{_cell(asset.get('confidence'))}` | "
            f"{', '.join(asset.get('evidence') or [])} |"
        )
    return "\n".join(lines)


def _conflict_block(fm: dict) -> str | None:
    conflicts = fm.get("conflicts") or []
    if not conflicts:
        return None
    lines = ["## Structured conflicts", ""]
    owner = fm.get("id", "")
    for conflict in conflicts:
        if not isinstance(conflict, dict):
            continue
        conflict_id = f"{owner}#{conflict.get('conflict_id', '')}"
        lines.extend(
            [
                f"### {_cell(conflict.get('topic'))}",
                "",
                f"Atlas conflict: `{conflict_id}`",
                "",
                "| Evidenced claim | Evidence |",
                "|---|---|",
            ]
        )
        for claim in conflict.get("claims") or []:
            if isinstance(claim, dict):
                lines.append(
                    f"| {_cell(claim.get('statement'))} | {', '.join(claim.get('evidence') or [])} |"
                )
        lines.extend(["", f"Interpretation: {_cell(conflict.get('interpretation'))}", ""])
    return "\n".join(lines).rstrip()


def build_page_view_outputs(root: str | Path, *, compiled_maps: dict[str, dict] | None = None) -> dict[Path, bytes]:
    root = Path(root).resolve()
    outputs: dict[Path, bytes] = {}
    query = AtlasQuery(root, compiled_maps=compiled_maps)
    for path in sorted((root / "_curated").rglob("*.md")):
        if (
            path.name in {"README.md", "index.md", "_template.md"}
            or "maps" in path.parts
            or "status" in path.parts
        ):
            continue
        text = path.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        rendered = text
        if fm.get("type") == "flow":
            rendered = _managed(rendered, "steps-table", _flow_steps_table(root, path, fm, query.routes))
            rendered = _managed(rendered, "flow-diagram", _mermaid(fm))
        elif fm.get("type") == "repository":
            rendered = _managed(rendered, "source-roots", _repository_table(fm))
        elif fm.get("type") == "component":
            rendered = _managed(rendered, "component-routing", _component_table(root, path, fm, query.routes))
        elif fm.get("type") == "infra":
            rendered = _managed(rendered, "infra-routing", _infra_table(root, path, fm, query.routes))
        elif fm.get("type") == "schema-info":
            rendered = _managed_optional(
                rendered,
                "asset-lineage",
                _asset_table(root, path, fm, query.routes),
            )
        rendered = _managed_optional(rendered, "conflicts", _conflict_block(fm))
        rendered = _managed(rendered, "related-routes", _related_routes(root, path, fm, query))
        if rendered != text:
            outputs[path] = rendered.encode("utf-8")
    return outputs

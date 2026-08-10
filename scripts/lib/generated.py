from __future__ import annotations

from pathlib import Path
import os
import re

from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.maps import load_package_config


CATALOGUE_START = "<!-- atlas:generated-catalogue:start -->"
CATALOGUE_END = "<!-- atlas:generated-catalogue:end -->"


def _coverage(value: object) -> str:
    if isinstance(value, dict):
        value = value.get("level")
    return value if isinstance(value, str) and value else "unknown"


def _managed(text: str, name: str, content: str) -> str:
    start = f"<!-- atlas:generated-{name}:start -->"
    end = f"<!-- atlas:generated-{name}:end -->"
    block = f"{start}\n{content.rstrip()}\n{end}"
    pattern = re.compile(re.escape(start) + r"[\s\S]*?" + re.escape(end))
    if pattern.search(text):
        return pattern.sub(lambda _: block, text)
    return text.rstrip() + "\n\n" + block + "\n"


def _relative_link(from_path: Path, to_path: Path) -> str:
    return Path(os.path.relpath(to_path, from_path.parent)).as_posix()


def _curated_records(root: Path, folder: str, typ: str) -> list[tuple[Path, dict]]:
    base = root / "_curated" / folder
    out: list[tuple[Path, dict]] = []
    if not base.exists():
        return out
    for path in sorted(base.rglob("*.md")):
        if path.name in {"README.md", "index.md", "_template.md"}:
            continue
        fm, _ = parse_frontmatter(path)
        if fm.get("type") == typ and fm.get("status") != "archived":
            out.append((path, fm))
    return out


def _catalogue(rows: list[tuple[Path, dict]], index_path: Path, *, staging: bool = False) -> str:
    if staging:
        header = "| ID | Title | Status | Candidate domain | Source context | Page |"
        divider = "|---|---|---|---|---|---|"
    else:
        header = "| ID | Title | Status | Primary domain | Coverage | Page |"
        divider = "|---|---|---|---|---|---|"
    lines = [CATALOGUE_START, "## Catalogue", "", header, divider]
    for path, fm in sorted(rows, key=lambda item: str(item[1].get("id", ""))):
        link = _relative_link(index_path, path)
        if staging:
            source_context = str(fm.get("source_type", ""))
            domain = path.relative_to(index_path.parent).parts[0] if path.parent != index_path.parent else "unassigned"
            lines.append(
                f"| `{fm.get('id', '')}` | {fm.get('title', '')} | `{fm.get('status', '')}` | "
                f"`{domain}` | {source_context} | [page]({link}) |"
            )
        else:
            lines.append(
                f"| `{fm.get('id', '')}` | {fm.get('title', '')} | `{fm.get('status', '')}` | "
                f"`{fm.get('primary_domain', '')}` | `{_coverage(fm.get('coverage'))}` | [page]({link}) |"
            )
    if not rows:
        lines.append("| — | No records | — | — | — | — |")
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
        catalogue = _catalogue(rows, index_path, staging=True)
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
            domain_catalogue = _catalogue(domain_rows, domain_index, staging=True)
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


def _target_text(values: object) -> str:
    if not isinstance(values, list) or not values:
        return "—"
    return ", ".join(
        f"`{item.get('id') or item.get('name', '')}`" for item in values if isinstance(item, dict)
    ) or "—"


def _flow_steps_table(fm: dict) -> str:
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
            participant_text += f" (`{participant['id']}`)"
        lines.append(
            f"| {step.get('order', '')} | `{step.get('step_id', '')}` | {step.get('name', '')} | "
            f"{participant_text} | `{participant.get('type', '')}` | {step.get('role', '')} | "
            f"{_target_text(step.get('receives'))} | {_target_text(step.get('emits'))} | "
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


def _component_table(fm: dict) -> str:
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
            lines.append(
                f"| `{field}` | `{item.get('id') or item.get('name', '')}` | "
                f"`{item.get(qualifier, '') if qualifier else field}` | "
                f"`{item.get('confidence', '')}` | {', '.join(item.get('evidence') or [])} |"
            )
    if len(lines) == 2:
        lines.append("| — | No structured routing facts captured | — | — | — |")
    return "\n".join(lines)


def _infra_table(fm: dict) -> str:
    lines = ["| Record/field | Target or resource | Type/action | Confidence | Evidence |", "|---|---|---|---|---|"]
    for resource in fm.get("promoted_resources") or []:
        lines.append(
            f"| `promoted_resource` | `{resource.get('id', '')}` | `{resource.get('resource_type', '')}` | "
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
            lines.append(
                f"| `{field}` | `{item.get('id') or item.get('name', '')}` | `{action}` | `{item.get('confidence', '')}` | "
                f"{', '.join(item.get('evidence') or [])} |"
            )
    if len(lines) == 2:
        lines.append("| — | No structured infrastructure facts captured | — | — | — |")
    return "\n".join(lines)


def build_page_view_outputs(root: str | Path) -> dict[Path, bytes]:
    root = Path(root).resolve()
    outputs: dict[Path, bytes] = {}
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
            rendered = _managed(rendered, "steps-table", _flow_steps_table(fm))
            rendered = _managed(rendered, "flow-diagram", _mermaid(fm))
        elif fm.get("type") == "repository":
            rendered = _managed(rendered, "source-roots", _repository_table(fm))
        elif fm.get("type") == "component":
            rendered = _managed(rendered, "component-routing", _component_table(fm))
        elif fm.get("type") == "infra":
            rendered = _managed(rendered, "infra-routing", _infra_table(fm))
        if rendered != text:
            outputs[path] = rendered.encode("utf-8")
    return outputs

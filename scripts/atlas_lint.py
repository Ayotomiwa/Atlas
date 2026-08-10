#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import datetime as dt
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.generated import build_index_outputs, build_page_view_outputs, generated_index_candidates
from scripts.lib.ids import valid_curated_id, valid_staging_id
from scripts.lib.links import broken_links
from scripts.lib.maps import MapBuildError, build_maps, load_package_config, map_output_paths, stable_bytes
from scripts.lib.taxonomy import load_taxonomy


SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", ".venv", "node_modules", "target", "build"}
EXEMPT_NAMES = {"README.md", "index.md", "_template.md", "curation-status.md"}
TEXT_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".py", ".toml", ".txt", ".properties"}
SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=\-]{20,}"
    ),
)
QUESTION_HEADER = "| Question ID | Question | Affected IDs | Evidence gap |"

REQUIRED_SECTIONS = {
    "repository": [
        "Summary and boundary",
        "Source topology",
        "Code architecture summary",
        "Architecture routes",
        "Source-owned guidance",
        "Ownership and operational context",
        "Evidence",
        "Open questions / coverage limits",
    ],
    "component": [
        "Summary",
        "Responsibility and boundary",
        "Source location and entrypoints",
        "Code architecture summary",
        "Structured routing",
        "Internal units",
        "Configuration and deployment context",
        "Failure and operational context",
        "Diagram",
        "Evidence",
        "Open questions / coverage limits",
    ],
    "flow": [
        "Summary and boundary",
        "Entry points and boundary I/O",
        "End-to-end steps",
        "Diagram",
        "Failure and conditional paths",
        "Infrastructure and operational routes",
        "Evidence",
        "Open questions / coverage limits",
    ],
    "infra": [
        "Summary and boundary",
        "Package location and environment structure",
        "Structured infrastructure routing",
        "Ordinary resources",
        "Promoted-resource rationale",
        "Permissions, monitoring and operational context",
        "Impact context",
        "Evidence",
        "Open questions / coverage limits",
    ],
    "schema-info": [
        "Summary",
        "Business meaning",
        "Physical identity",
        "Grain",
        "Keys",
        "Temporal model",
        "Compatibility / versioning",
        "Important fields",
        "Producers",
        "Consumers",
        "Approved/known joins",
        "Quality issues",
        "Classification and access notes",
        "Evidence",
        "Open questions / coverage limits",
    ],
}

RETIRED_COMMON = {"relationships", "open_questions"}
STAGING_ENVELOPE = {
    "id",
    "type",
    "package",
    "timestamp",
    "title",
    "description",
    "status",
    "captured_by",
    "source_type",
}
RETIRED_FIELDS = {
    "repository": {"repository_url", "repository_kind", "source_dependencies", "links"},
    "component": {
        "component_scope",
        "domain_group",
        "monorepo_path",
        "deployed_as",
        "contains_internal_units",
        "dependencies",
        "infrastructure_usage",
        "links",
    },
    "flow": {"trigger", "schedule", "entry_component", "exit_component", "infrastructure_usage", "links"},
    "infra": {"resource_names", "dependencies", "links"},
    "schema-info": {"asset_kind"},
    "business-concept": {"approved_definition", "inclusion_criteria", "exclusion_criteria", "approved_variants"},
    "standard": {"applies_to", "mandatory", "scope", "exceptions"},
    "runbook": {"covers", "severity_scope"},
    "incident-learning": {"severity", "resolved"},
}


def issue(code: str, level: str, path: str | Path, message: str) -> dict[str, str]:
    return {"code": code, "level": level, "path": str(path), "message": message}


def _is_skipped(rel: Path) -> bool:
    return any(part in SKIP_DIRS for part in rel.parts) or rel.parts[:3] == ("tests", "fixtures", "invalid")


def _folder_allowed(rel: Path, folder: str) -> bool:
    try:
        rel.relative_to(Path(folder))
        return True
    except ValueError:
        return False


def _parse_iso_date(value: object) -> dt.date | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def _headings(body: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", body, re.MULTILINE))
    out: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        out[match.group(1)] = body[match.end() : end]
    return out


def _atlas_records(root: Path) -> list[Path]:
    out: list[Path] = []
    for base_name in ("_curated", "_staging"):
        base = root / base_name
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            rel = path.relative_to(root)
            if _is_skipped(rel) or path.name in EXEMPT_NAMES:
                continue
            if base_name == "_curated" and ("maps" in rel.parts or "status" in rel.parts):
                continue
            out.append(path)
    return out


def lint_repository(
    root: str | Path,
    *,
    package_name: str | None = None,
    warn_as_error: bool = False,
    git_base: str | None = None,
    check_maps: bool = True,
    today: dt.date | None = None,
) -> list[dict[str, str]]:
    del warn_as_error, git_base  # accepted for CLI/API compatibility; staging immutability is policy-only.
    root = Path(root).resolve()
    today = today or dt.date.today()
    issues: list[dict[str, str]] = []

    try:
        package = load_package_config(root)
    except MapBuildError as exc:
        return [issue("ATLAS001", "ERROR", "atlas-package.json", str(exc))]
    package_name = package_name or package["package"]
    domain_ids = {item["id"] for item in package.get("domains") or []}
    try:
        taxonomy = load_taxonomy(root)
    except Exception as exc:
        return [issue("ATLAS001", "ERROR", "taxonomy", f"registered taxonomy cannot be loaded: {exc}")]
    type_specs = {item["name"]: item for item in taxonomy["types"]["types"]}
    active = {name: spec for name, spec in type_specs.items() if spec.get("status") == "active"}
    curated_status = set(taxonomy["statuses"]["curated_status"])
    staging_status = set(taxonomy["statuses"]["staging_status"])
    concept_fields = taxonomy["concept_fields"]
    seen_ids: dict[str, Path] = {}

    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if _is_skipped(rel):
            continue
        for target in broken_links(path):
            issues.append(issue("ATLAS008", "ERROR", rel, f"broken relative Markdown link: {target}"))

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_EXTENSIONS:
            continue
        rel = path.relative_to(root)
        if _is_skipped(rel):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            issues.append(issue("ATLAS019", "ERROR", rel, "obvious secret pattern detected"))

    for path in _atlas_records(root):
        rel = path.relative_to(root)
        try:
            fm, body = parse_frontmatter(path)
        except Exception as exc:
            issues.append(issue("ATLAS001", "ERROR", rel, str(exc)))
            continue
        typ = fm.get("type")
        spec = active.get(typ)
        if not spec or typ in {"package", "index"}:
            issues.append(issue("ATLAS002", "ERROR", rel, f"inactive or unknown type: {typ!r}"))
            continue
        if not _folder_allowed(rel, spec["folder"]):
            issues.append(issue("ATLAS002", "ERROR", rel, f"type {typ} is not allowed under {rel.parent}"))
        if fm.get("package") != package_name:
            issues.append(issue("ATLAS004", "ERROR", rel, f"package must equal {package_name}"))

        if str(typ).startswith("staging."):
            ident = fm.get("id")
            if not valid_staging_id(ident):
                issues.append(issue("ATLAS003", "ERROR", rel, "invalid staging id"))
            elif rel.name != f"{ident}.md":
                issues.append(issue("ATLAS026", "ERROR", rel, "staging filename must be <staging-id>.md"))
            if fm.get("status") not in staging_status:
                issues.append(issue("ATLAS006", "ERROR", rel, f"invalid staging status {fm.get('status')!r}"))
            for field in sorted(set(fm) - STAGING_ENVELOPE):
                issues.append(
                    issue("ATLAS025", "ERROR", rel, f"staging frontmatter must use the common envelope; remove {field}")
                )
            if spec.get("grouped") == "domain":
                inside = rel.relative_to(Path(spec["folder"]))
                group = inside.parts[0] if len(inside.parts) > 1 else ""
                if group not in domain_ids | {"unassigned"}:
                    issues.append(
                        issue("ATLAS027", "ERROR", rel, "staging component/flow must be under a registered domain or unassigned")
                    )
            continue

        ident = fm.get("id")
        if not valid_curated_id(ident, spec.get("id_prefix")):
            issues.append(issue("ATLAS003", "ERROR", rel, "invalid curated id prefix/grammar"))
        elif ident in seen_ids:
            issues.append(issue("ATLAS003", "ERROR", rel, f"duplicate id also in {seen_ids[ident]}"))
        else:
            seen_ids[ident] = rel

        status = fm.get("status")
        if status not in curated_status:
            issues.append(issue("ATLAS006", "ERROR", rel, f"invalid curated status {status!r}"))
        if status == "curated":
            reviewed = _parse_iso_date(fm.get("last_reviewed"))
            if not fm.get("reviewed_by") or reviewed is None or not (fm.get("evidence") or fm.get("evidence_exemption")):
                issues.append(
                    issue(
                        "ATLAS007",
                        "ERROR",
                        rel,
                        "status curated requires reviewed_by, ISO last_reviewed, and evidence or exemption",
                    )
                )
        if spec.get("grouped") == "domain":
            domain = fm.get("primary_domain")
            inside = rel.relative_to(Path(spec["folder"]))
            if domain not in domain_ids:
                issues.append(issue("ATLAS027", "ERROR", rel, f"primary_domain is not registered: {domain!r}"))
            elif len(inside.parts) < 2 or inside.parts[0] != domain:
                issues.append(issue("ATLAS027", "ERROR", rel, "folder must match primary_domain"))
        elif spec.get("grouped") == "category":
            category = fm.get("standard_category")
            categories = set(taxonomy["categories"].get("categories") or [])
            inside = rel.relative_to(Path(spec["folder"]))
            if category not in categories:
                issues.append(issue("ATLAS027", "ERROR", rel, f"standard_category is not registered: {category!r}"))
            elif len(inside.parts) < 2 or inside.parts[0] != category:
                issues.append(issue("ATLAS027", "ERROR", rel, "folder must match standard_category"))

        retired = RETIRED_COMMON | RETIRED_FIELDS.get(typ, set())
        for field in sorted(retired):
            if field in fm:
                issues.append(issue("ATLAS025", "ERROR", rel, f"retired field is not allowed: {field}"))

        controlled = {
            "repository": (("repository_type", "repository", "repository_type"),),
            "component": (("component_type", "component", "component_type"),),
            "schema-info": (
                ("asset_type", "shared", "asset_type"),
                ("temporal_model", "schema", "temporal_model"),
            ),
            "standard": (("requirement_level", "standard", "requirement_level"),),
        }
        for field, group, vocabulary in controlled.get(typ, ()):
            if fm.get(field) not in set(concept_fields[group][vocabulary]):
                issues.append(issue("ATLAS025", "ERROR", rel, f"{field} has invalid value {fm.get(field)!r}"))
        if typ == "standard" and status == "curated" and fm.get("requirement_level") == "unknown":
            issues.append(issue("ATLAS025", "ERROR", rel, "curated standards cannot use requirement_level: unknown"))

        headings = _headings(body)
        for heading in REQUIRED_SECTIONS.get(typ, []):
            if heading not in headings:
                issues.append(issue("ATLAS016", "ERROR", rel, f"missing required section: {heading}"))
        question_section = headings.get("Open questions / coverage limits")
        if question_section is not None and "|" in question_section and QUESTION_HEADER not in question_section:
            issues.append(issue("ATLAS023", "ERROR", rel, "open-question table must use the fixed four-column header"))
        reviewed = _parse_iso_date(fm.get("last_reviewed"))
        if status in {"proposed", "curated"} and reviewed and (today - reviewed).days > 180:
            issues.append(issue("ATLAS020", "WARN", rel, "review older than 180 days"))

    try:
        generated_maps = build_maps(root)
    except MapBuildError as exc:
        issues.append(issue("ATLAS018", "ERROR", "_curated/maps", f"maps cannot be generated: {exc}"))
        generated_maps = None

    if check_maps and generated_maps is not None:
        outputs = {map_output_paths(root)[name]: stable_bytes(value) for name, value in generated_maps.items()}
        outputs.update(build_index_outputs(root))
        outputs.update(build_page_view_outputs(root))
        for path, expected in outputs.items():
            if not path.exists() or path.read_bytes() != expected:
                issues.append(issue("ATLAS018", "ERROR", path.relative_to(root), "generated Atlas surface drift"))
        for path in sorted(
            generated_index_candidates(root) - {candidate.resolve() for candidate in outputs},
            key=lambda candidate: candidate.as_posix(),
        ):
            issues.append(issue("ATLAS018", "ERROR", path.relative_to(root), "stale generated domain index"))

    issues.sort(key=lambda item: (item["path"], item["code"], item["level"], item["message"]))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--warn-as-error", action="store_true")
    parser.add_argument("--package", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--git-base", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--skip-map-check", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    issues = lint_repository(
        args.path,
        package_name=args.package,
        warn_as_error=args.warn_as_error,
        git_base=args.git_base,
        check_maps=not args.skip_map_check,
    )
    if args.format == "json":
        print(json.dumps(issues, indent=2))
    else:
        for item in issues:
            print(f"{item['level']} {item['code']} {item['path']}: {item['message']}")
        errors = sum(item["level"] == "ERROR" for item in issues)
        warnings = sum(item["level"] == "WARN" for item in issues)
        print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if any(
        item["level"] == "ERROR" or (args.warn_as_error and item["level"] == "WARN")
        for item in issues
    ) else 0


if __name__ == "__main__":
    raise SystemExit(main())

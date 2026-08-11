#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import datetime as dt
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.ids import valid_curated_id, valid_staging_id
from scripts.lib.links import broken_links
from scripts.lib.maps import (
    MapBuildError,
    domain_hint,
    load_package_config,
    validate_map_frontmatter,
)
from scripts.lib.taxonomy import load_taxonomy


SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", ".venv", "node_modules", "target", "build"}
EXEMPT_NAMES = {"README.md", "index.md", "_template.md", "curation-status.md"}

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
# Fields an author might still write that nothing reads. Structured metadata earns
# its place by being machine-consumed; anything that only restates a required body
# section is authored twice and reconciled nowhere.
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
    "schema-info": {
        "asset_kind",
        "grain",
        "primary_keys",
        "business_keys",
        "latest_record_rule",
    },
    "business-concept": {"approved_definition", "inclusion_criteria", "exclusion_criteria", "approved_variants"},
    "standard": {"applies_to", "mandatory", "scope", "exceptions"},
    "runbook": {"covers", "severity_scope"},
    "incident-learning": {"severity", "resolved"},
}


# Identity and placement rules the map compiler repeats; reporting both would
# describe one mistake twice, once with a less specific message.
IDENTITY_CODES = {"ATLAS002", "ATLAS003", "ATLAS005", "ATLAS027"}


def issue(code: str, level: str, path: str | Path, message: str) -> dict[str, str]:
    return {"code": code, "level": level, "path": Path(path).as_posix(), "message": message}


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
) -> list[dict[str, str]]:
    root = Path(root).resolve()
    issues: list[dict[str, str]] = []

    try:
        package = load_package_config(root)
    except MapBuildError as exc:
        return [issue("ATLAS001", "ERROR", "atlas-package.json", str(exc))]
    package_name = package["package"]
    domain_ids = {item["id"] for item in package.get("domains") or []}
    try:
        taxonomy = load_taxonomy(root)
    except Exception as exc:
        return [
            issue(
                "ATLAS001",
                "ERROR",
                getattr(exc, "path", None) or "taxonomy",
                f"registered taxonomy cannot be loaded: {exc}",
            )
        ]
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

    for path in _atlas_records(root):
        rel = path.relative_to(root)
        try:
            fm, _ = parse_frontmatter(path)
        except Exception as exc:
            issues.append(issue("ATLAS001", "ERROR", rel, str(exc)))
            continue
        typ = fm.get("type")
        spec = active.get(typ) if isinstance(typ, str) else None
        if not spec or typ == "package":
            declared = type_specs.get(typ) if isinstance(typ, str) else None
            if declared and declared.get("status") == "reserved":
                issues.append(
                    issue("ATLAS005", "ERROR", rel, f"type {typ!r} is reserved and cannot have pages yet")
                )
            else:
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
            if not fm.get("reviewed_by") or reviewed is None or not fm.get("evidence"):
                issues.append(
                    issue(
                        "ATLAS007",
                        "ERROR",
                        rel,
                        "status curated requires reviewed_by, ISO last_reviewed and evidence",
                    )
                )
        if spec.get("grouped") == "domain":
            domain = fm.get("primary_domain")
            inside = rel.relative_to(Path(spec["folder"]))
            if domain not in domain_ids:
                issues.append(issue("ATLAS027", "ERROR", rel, domain_hint(typ, domain, domain_ids)))
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
        routing = fm.get("routing")
        if isinstance(routing, dict) and "domains" in routing:
            issues.append(
                issue("ATLAS025", "ERROR", rel, "retired field is not allowed: routing.domains")
            )
        if typ == "runbook":
            exercised = fm.get("last_exercised")
            if exercised not in (None, "") and _parse_iso_date(exercised) is None:
                issues.append(
                        issue("ATLAS025", "ERROR", rel, "last_exercised must be an ISO YYYY-MM-DD date or empty")
                )
        if typ == "schema-info":
            for field in ("physical_name", "platform", "classification"):
                if field not in fm or not isinstance(fm.get(field), str):
                    issues.append(issue("ATLAS025", "ERROR", rel, f"{field} must be a string"))
        if typ == "incident-learning":
            incident_date = fm.get("incident_date")
            if incident_date not in (None, "") and _parse_iso_date(incident_date) is None:
                issues.append(issue("ATLAS025", "ERROR", rel, "incident_date must be an ISO YYYY-MM-DD date or empty"))
            elif "incident_date" not in fm:
                issues.append(issue("ATLAS025", "ERROR", rel, "incident_date is required and may be empty"))
            if "source_severity" not in fm or not isinstance(fm.get("source_severity"), str):
                issues.append(issue("ATLAS025", "ERROR", rel, "source_severity must be a string"))

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

    # Structured map inputs are frontmatter. Validate them without reading body
    # headings/tables and without comparing or writing generated artifacts.
    try:
        record_errors = validate_map_frontmatter(root)
    except MapBuildError as exc:
        issues.append(issue("ATLAS001", "ERROR", exc.path or "_curated/maps", str(exc)))
        record_errors = []
    already_reported = {
        item["path"] for item in issues if item["code"] in IDENTITY_CODES | {"ATLAS001"}
    }
    for record_error in record_errors:
        if record_error.path in already_reported:
            continue
        prefix = f"{record_error.record_id}: " if record_error.record_id else ""
        issues.append(issue("ATLAS009", "ERROR", record_error.path, prefix + record_error.message))

    issues.sort(key=lambda item: (item["path"], item["code"], item["level"], item["message"]))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)
    issues = lint_repository(args.path)
    if args.format == "json":
        print(json.dumps(issues, indent=2))
    else:
        for item in issues:
            print(f"{item['level']} {item['code']} {item['path']}: {item['message']}")
        errors = sum(item["level"] == "ERROR" for item in issues)
        warnings = sum(item["level"] == "WARN" for item in issues)
        print(f"{errors} error(s), {warnings} warning(s)")
    return 1 if any(item["level"] == "ERROR" for item in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())

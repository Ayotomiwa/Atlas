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
from scripts.lib.ids import valid_curated_id, valid_staging_id
from scripts.lib.intake import checkpoint_references, validate_change_source, validate_checkpoint
from scripts.lib.links import broken_links
from scripts.lib.maps import (
    MapBuildError,
    domain_hint,
    load_package_config,
    validate_map_frontmatter,
)
from scripts.lib.onboarding_campaign import (
    CAMPAIGN_DIR,
    CampaignError,
    load_campaign,
    validate_onboarding_source,
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
    "onboarding_source",
}
STAGING_TYPE_FIELDS = {"staging.change": {"change_source"}}
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
GROUP_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def issue(
    code: str,
    level: str,
    path: str | Path,
    message: str,
    *,
    record_id: str | None = None,
    related_paths: list[str | Path] | None = None,
    related_ids: list[str] | None = None,
) -> dict[str, object]:
    item: dict[str, object] = {
        "code": code,
        "level": level,
        "path": Path(path).as_posix(),
        "message": message,
    }
    if record_id is not None:
        item["record_id"] = record_id
    if related_paths:
        item["related_paths"] = sorted({Path(value).as_posix() for value in related_paths})
    if related_ids:
        item["related_ids"] = sorted(set(related_ids))
    return item


def _is_skipped(rel: Path) -> bool:
    return any(part in SKIP_DIRS for part in rel.parts) or rel.parts[:3] == ("tests", "fixtures", "invalid")


def _folder_allowed(rel: Path, folder: str) -> bool:
    try:
        rel.relative_to(Path(folder))
        return True
    except ValueError:
        return False


def _parse_iso_date(value: object) -> dt.date | None:
    # YAML turns an unquoted YYYY-MM-DD into a date, so accept both forms.
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
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


def _boolean_key_paths(value: object, prefix: str = "frontmatter") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        if True in value:
            found.append(prefix)
        for key, child in value.items():
            found.extend(_boolean_key_paths(child, f"{prefix}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_boolean_key_paths(child, f"{prefix}[{index}]"))
    return found


def _load_onboarding_campaigns(
    root: Path, issues: list[dict[str, object]]
) -> dict[str, list[tuple[Path, dict]]]:
    """Load direct campaign files so lint can check staging/controller joins."""

    campaign_root = root / CAMPAIGN_DIR
    campaigns: dict[str, list[tuple[Path, dict]]] = {}
    if not campaign_root.exists():
        return campaigns
    for path in sorted(campaign_root.rglob("*.json")):
        rel = path.relative_to(root)
        if path.parent != campaign_root:
            issues.append(
                issue(
                    "ATLAS029",
                    "ERROR",
                    rel,
                    "onboarding campaigns must be direct children of _intake/onboarding",
                )
            )
            continue
        try:
            campaign = load_campaign(path)
        except CampaignError as exc:
            issues.append(issue("ATLAS029", "ERROR", rel, str(exc)))
            continue
        campaign_id = campaign["campaign_id"]
        campaigns.setdefault(campaign_id, []).append((rel, campaign))

    for campaign_id, candidates in sorted(campaigns.items()):
        if len(candidates) < 2:
            continue
        paths = [path for path, _ in candidates]
        for path in paths:
            issues.append(
                issue(
                    "ATLAS029",
                    "ERROR",
                    path,
                    f"duplicate onboarding campaign_id {campaign_id}",
                    related_paths=paths,
                )
            )
    return campaigns


def _lint_onboarding_joins(
    campaigns: dict[str, list[tuple[Path, dict]]],
    staging_records: dict[str, list[tuple[Path, dict]]],
    staging_pages: list[tuple[Path, dict]],
    issues: list[dict[str, object]],
) -> None:
    """Validate bidirectional portfolio controller references without prose rules."""

    for staging_path, staging in staging_pages:
        provenance = staging.get("onboarding_source")
        if provenance is None:
            continue
        errors = validate_onboarding_source(provenance)
        for message in errors:
            issues.append(issue("ATLAS025", "ERROR", staging_path, message))
        if errors:
            continue
        assert isinstance(provenance, dict)
        campaign_id = provenance["campaign_id"]
        item_id = provenance["item_id"]
        campaign_candidates = campaigns.get(campaign_id) or []
        if not campaign_candidates:
            issues.append(
                issue(
                    "ATLAS029",
                    "ERROR",
                    staging_path,
                    f"onboarding_source references missing campaign {campaign_id}",
                )
            )
            continue
        if len(campaign_candidates) != 1:
            campaign_paths = ", ".join(path.as_posix() for path, _ in campaign_candidates)
            issues.append(
                issue(
                    "ATLAS029",
                    "ERROR",
                    staging_path,
                    f"onboarding_source references ambiguous campaign {campaign_id}: {campaign_paths}",
                )
            )
            continue
        _, campaign = campaign_candidates[0]
        campaign_items = {
            item.get("item_id"): item
            for item in campaign.get("items", [])
            if isinstance(item, dict) and isinstance(item.get("item_id"), str)
        }
        campaign_item = campaign_items.get(item_id)
        if campaign_item is None:
            issues.append(
                issue(
                    "ATLAS029",
                    "ERROR",
                    staging_path,
                    f"onboarding_source references missing item {item_id} in campaign {campaign_id}",
                )
            )
            continue
        staging_id = staging.get("id")
        state = campaign_item.get("state")
        listed_ids = campaign_item.get("staging_ids")
        if (
            state == "staged"
            and isinstance(staging_id, str)
            and isinstance(listed_ids, list)
            and staging_id not in listed_ids
        ):
            issues.append(
                issue(
                    "ATLAS029",
                    "ERROR",
                    staging_path,
                    f"onboarding_source points to staged campaign item {item_id}, but "
                    f"staging ID {staging_id} is not listed in that item's staging_ids",
                )
            )
        elif state in {"already-covered", "skipped"}:
            issues.append(
                issue(
                    "ATLAS029",
                    "ERROR",
                    staging_path,
                    f"onboarding_source contradicts terminal campaign item {item_id} "
                    f"with state {state}; that outcome must not have newly staged evidence",
                )
            )

    for campaign_id, campaign_candidates in sorted(campaigns.items()):
        if len(campaign_candidates) != 1:
            continue
        campaign_path, campaign = campaign_candidates[0]
        for item_index, item in enumerate(campaign.get("items", [])):
            if not isinstance(item, dict) or item.get("state") != "staged":
                continue
            item_id = item.get("item_id")
            staging_ids = item.get("staging_ids")
            if not isinstance(item_id, str) or not isinstance(staging_ids, list):
                continue
            for staging_index, staging_id in enumerate(staging_ids):
                if not isinstance(staging_id, str):
                    continue
                location = f"items[{item_index}].staging_ids[{staging_index}]"
                candidates = staging_records.get(staging_id) or []
                if not candidates:
                    issues.append(
                        issue(
                            "ATLAS029",
                            "ERROR",
                            campaign_path,
                            f"{location} references missing staging ID {staging_id}",
                        )
                    )
                    continue
                if len(candidates) != 1:
                    paths = ", ".join(path.as_posix() for path, _ in candidates)
                    issues.append(
                        issue(
                            "ATLAS029",
                            "ERROR",
                            campaign_path,
                            f"{location} references ambiguous staging ID {staging_id}: {paths}",
                        )
                    )
                    continue
                staging_path, staging = candidates[0]
                if staging.get("onboarding_source") != {
                    "campaign_id": campaign_id,
                    "item_id": item_id,
                }:
                    issues.append(
                        issue(
                            "ATLAS029",
                            "ERROR",
                            campaign_path,
                            f"{location} does not match onboarding_source on {staging_path.as_posix()}",
                        )
                    )


def lint_repository(
    root: str | Path,
) -> list[dict[str, object]]:
    root = Path(root).resolve()
    issues: list[dict[str, object]] = []

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
    staging_records: dict[str, list[tuple[Path, dict]]] = {}
    staging_pages: list[tuple[Path, dict]] = []

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
        for owner in _boolean_key_paths(fm):
            issues.append(
                issue(
                    "ATLAS025",
                    "ERROR",
                    rel,
                    f"{owner} contains a boolean key; quote the reserved YAML key \"on\" in transitions",
                )
            )
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
            staging_pages.append((rel, fm))
            ident = fm.get("id")
            if not valid_staging_id(ident):
                issues.append(issue("ATLAS003", "ERROR", rel, "invalid staging id"))
            elif rel.name != f"{ident}.md":
                issues.append(issue("ATLAS026", "ERROR", rel, "staging filename must be <staging-id>.md"))
            else:
                staging_records.setdefault(ident, []).append((rel, fm))
            if fm.get("status") not in staging_status:
                issues.append(issue("ATLAS006", "ERROR", rel, f"invalid staging status {fm.get('status')!r}"))
            allowed_fields = STAGING_ENVELOPE | STAGING_TYPE_FIELDS.get(typ, set())
            for field in sorted(set(fm) - allowed_fields):
                issues.append(
                    issue("ATLAS025", "ERROR", rel, f"staging frontmatter must use the common envelope; remove {field}")
                )
            if typ == "staging.change":
                for message in validate_change_source(
                    fm.get("change_source"),
                    required=fm.get("source_type") == "merged-change",
                ):
                    issues.append(issue("ATLAS025", "ERROR", rel, message))
            if spec.get("grouped") == "domain":
                inside = rel.relative_to(Path(spec["folder"]))
                group = inside.parts[0] if len(inside.parts) > 1 else ""
                exact_grouped_path = len(inside.parts) == 2 and GROUP_SLUG_RE.fullmatch(group)
                if not exact_grouped_path:
                    issues.append(
                        issue(
                            "ATLAS027",
                            "ERROR",
                            rel,
                            f"{typ} must be under exactly <candidate-domain>/<staging-id>.md "
                            "using a valid candidate-domain slug",
                        )
                    )
            continue

        ident = fm.get("id")
        if not valid_curated_id(ident, spec.get("id_prefix")):
            issues.append(issue("ATLAS003", "ERROR", rel, "invalid curated id prefix/grammar"))
        elif ident in seen_ids:
            issues.append(
                issue(
                    "ATLAS003",
                    "ERROR",
                    rel,
                    f"duplicate id also in {seen_ids[ident]}",
                    record_id=ident,
                    related_paths=[seen_ids[ident]],
                    related_ids=[ident],
                )
            )
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
        if routing is not None and not isinstance(routing, dict):
            issues.append(issue("ATLAS025", "ERROR", rel, "routing must be an object"))
        elif isinstance(routing, dict):
            if "domains" in routing:
                issues.append(
                    issue("ATLAS025", "ERROR", rel, "retired field is not allowed: routing.domains")
                )
            if "keywords" in routing:
                keywords = routing.get("keywords")
                if not isinstance(keywords, list) or not all(
                    isinstance(value, str) and value.strip() for value in keywords
                ):
                    issues.append(
                        issue("ATLAS025", "ERROR", rel, "routing.keywords must contain non-empty strings")
                    )
                elif len({value.strip().casefold() for value in keywords}) != len(keywords):
                    issues.append(
                        issue("ATLAS025", "ERROR", rel, "routing.keywords must be unique")
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

    campaigns = _load_onboarding_campaigns(root, issues)

    for staging_id, candidates in sorted(staging_records.items()):
        if len(candidates) < 2:
            continue
        candidate_paths = [path for path, _ in candidates]
        issues.append(
            issue(
                "ATLAS003",
                "ERROR",
                candidate_paths[-1],
                f"duplicate staging id appears in {len(candidate_paths)} records",
                record_id=staging_id,
                related_paths=candidate_paths,
                related_ids=[staging_id],
            )
        )

    _lint_onboarding_joins(campaigns, staging_records, staging_pages, issues)

    checkpoint_root = root / "_intake" / "checkpoints"
    if checkpoint_root.exists():
        for path in sorted(checkpoint_root.rglob("*.json")):
            rel = path.relative_to(root)
            if path.parent != checkpoint_root:
                issues.append(
                    issue("ATLAS028", "ERROR", rel, "intake checkpoints must be direct children of _intake/checkpoints")
                )
            try:
                checkpoint = json.loads(path.read_text(encoding="utf-8"))
            except OSError as exc:
                issues.append(issue("ATLAS028", "ERROR", rel, f"cannot read intake checkpoint: {exc}"))
                continue
            except json.JSONDecodeError as exc:
                issues.append(issue("ATLAS028", "ERROR", rel, f"invalid intake checkpoint JSON: {exc}"))
                continue
            checkpoint_errors = validate_checkpoint(checkpoint)
            for message in checkpoint_errors:
                issues.append(issue("ATLAS028", "ERROR", rel, message))
            source = checkpoint.get("source") if isinstance(checkpoint, dict) else None
            source_key = source.get("key") if isinstance(source, dict) else None
            if isinstance(source_key, str) and path.name != f"{source_key}.json":
                issues.append(
                    issue("ATLAS028", "ERROR", rel, "checkpoint filename must be <source.key>.json")
                )
            if checkpoint_errors or not isinstance(checkpoint, dict):
                continue
            source_branch = source.get("default_branch") if isinstance(source, dict) else None
            checked_references: set[tuple[str, str, str | None]] = set()
            for reference in checkpoint_references(checkpoint):
                reference_key = (
                    reference.staging_id,
                    reference.commit,
                    reference.merge_request,
                )
                if reference_key in checked_references:
                    continue
                checked_references.add(reference_key)
                candidates = staging_records.get(reference.staging_id) or []
                if not candidates:
                    issues.append(
                        issue(
                            "ATLAS028",
                            "ERROR",
                            rel,
                            f"{reference.location} references missing staging ID {reference.staging_id}",
                        )
                    )
                    continue
                if len(candidates) != 1:
                    candidate_paths = ", ".join(path.as_posix() for path, _ in candidates)
                    issues.append(
                        issue(
                            "ATLAS028",
                            "ERROR",
                            rel,
                            f"{reference.location} references ambiguous staging ID {reference.staging_id}: {candidate_paths}",
                        )
                    )
                    continue
                staging_path, staging = candidates[0]
                if staging.get("type") != "staging.change":
                    issues.append(
                        issue(
                            "ATLAS028",
                            "ERROR",
                            rel,
                            f"{reference.location} must reference staging.change, found {staging_path.as_posix()}",
                        )
                    )
                    continue
                change_source = staging.get("change_source")
                if not isinstance(change_source, dict) or change_source.get("source_key") != reference.source_key:
                    issues.append(
                        issue(
                            "ATLAS028",
                            "ERROR",
                            rel,
                            f"{reference.location} source key does not match {staging_path.as_posix()}",
                        )
                    )
                elif change_source.get("branch") != source_branch:
                    issues.append(
                        issue(
                            "ATLAS028",
                            "ERROR",
                            rel,
                            f"{reference.location} branch does not match {staging_path.as_posix()}",
                        )
                    )
                else:
                    commit_range = change_source.get("commit_range")
                    through = (
                        commit_range.get("through_inclusive")
                        if isinstance(commit_range, dict)
                        else None
                    )
                    if through != reference.commit:
                        issues.append(
                            issue(
                                "ATLAS028",
                                "ERROR",
                                rel,
                                f"{reference.location} commit does not match {staging_path.as_posix()} change_source range",
                            )
                        )
                    if reference.merge_request is not None:
                        merge_requests = change_source.get("merge_requests")
                        matched = [
                            item
                            for item in (merge_requests if isinstance(merge_requests, list) else [])
                            if isinstance(item, dict)
                            and item.get("id") == reference.merge_request
                        ]
                        if len(matched) != 1 or matched[0].get("merged_commit") != reference.commit:
                            issues.append(
                                issue(
                                    "ATLAS028",
                                    "ERROR",
                                    rel,
                                    f"{reference.location} merge request does not match {staging_path.as_posix()} change_source provenance",
                                )
                            )

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
        issues.append(
            issue(
                "ATLAS009",
                "ERROR",
                record_error.path,
                prefix + record_error.message,
                record_id=record_error.record_id,
            )
        )

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

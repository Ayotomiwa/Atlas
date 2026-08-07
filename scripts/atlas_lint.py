#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.lib.frontmatter import parse_frontmatter
from scripts.lib.ids import valid_curated_id, valid_staging_id
from scripts.lib.links import broken_links, links_to
from scripts.lib.maps import MapBuildError, build_maps, stable_bytes
from scripts.lib.taxonomy import load_taxonomy, relationship_names

NOT_COVERED = "*Not covered — no evidence in current staging material.*"
KINDS = {
    "event",
    "api",
    "table",
    "file",
    "component",
    "shared-library",
    "schema-library",
    "config",
    "job-output",
    "infra",
    "other",
}
EXEMPT_NAMES = {
    "README.md",
    "index.md",
    "_template.md",
    "CLAUDE.md",
    "log.md",
    "service-questionnaire.md",
    "standards-questionnaire.md",
    "local-CLAUDE.template.md",
    "curation-status.md",
}
SKIP_DIRS = {".git", ".pytest_cache", "__pycache__", ".venv", "node_modules", "target", "build"}
SECRET_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(
        r"(?i)(?:api[_-]?key|client[_-]?secret|access[_-]?token|password)\s*[:=]\s*[\"']?[A-Za-z0-9_./+=\-]{20,}"
    ),
)
TEXT_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".py", ".toml", ".txt", ".properties"}

REQUIRED_SECTIONS = {
    "atlas.component": [
        "Summary",
        "Responsibility",
        "Location",
        "Internal units",
        "Consumes",
        "Produces",
        "Flows",
        "Infrastructure",
        "Local repository references",
        "Operational notes",
        "Runbooks",
        "Standards",
        "Incident learnings",
        "Evidence",
        "Possible relationships",
        "Open questions / coverage limits",
    ],
    "atlas.flow": [
        "Summary",
        "Purpose and boundary",
        "Entry point",
        "End-to-end steps",
        "Participating components",
        "Inputs and outputs",
        "Upstream dependencies",
        "Downstream consumers",
        "Jobs and schedules",
        "Infrastructure",
        "Failure modes",
        "Runbooks",
        "Incident learnings",
        "Standards",
        "Evidence",
        "Possible relationships",
        "Open questions / coverage limits",
    ],
    "atlas.infra": [
        "Summary",
        "Package location and structure",
        "Environment notes",
        "Internal resources",
        "Promoted resources and promotion reason",
        "Resource relationships",
        "Components using resources",
        "Flows using resources",
        "Parameters/imports/exports",
        "Schedules/triggers/events",
        "Permissions and roles",
        "Monitoring",
        "Impact if changed or deleted",
        "Evidence",
        "Possible relationships",
        "Open questions / coverage limits",
    ],
    "atlas.schema-info": [
        "Summary",
        "Business meaning",
        "Physical identity",
        "Grain",
        "Keys",
        "Temporal model",
        "Important fields",
        "Producers",
        "Consumers",
        "Approved/known joins",
        "Quality issues",
        "Classification and access notes",
        "Evidence",
        "Open questions / coverage limits",
    ],
    "atlas.business-concept": [
        "Definition",
        "Boundaries",
        "Examples",
        "Non-examples",
        "Related data assets",
        "Standards",
        "Evidence",
        "Open questions / coverage limits",
    ],
    "atlas.standard": [
        "Standard",
        "Scope",
        "Rationale",
        "Required behaviour",
        "Recommended behaviour",
        "Examples",
        "Anti-patterns",
        "Exceptions",
        "Related standards",
        "Evidence",
        "Open questions / coverage limits",
    ],
    "atlas.runbook": [
        "Purpose",
        "Trigger / symptom",
        "Prerequisites",
        "Safety",
        "Investigation",
        "Recovery",
        "Validation",
        "Rollback",
        "Escalation",
        "Monitoring",
        "Evidence",
        "Open questions / coverage limits",
    ],
    "atlas.incident-learning": [
        "Sanitised summary",
        "Impact",
        "Cause",
        "Detection",
        "Recovery",
        "Reusable learning",
        "Runbook / standard gaps",
        "Evidence",
        "Sensitive-data note",
        "Open questions / coverage limits",
    ],
}


def issue(code: str, level: str, path: str | Path, message: str) -> dict[str, str]:
    return {"code": code, "level": level, "path": str(path), "message": message}


def _is_skipped(rel: Path) -> bool:
    return any(part in SKIP_DIRS for part in rel.parts) or rel.parts[:3] == ("tests", "fixtures", "invalid")


def _is_governed(rel: Path) -> bool:
    if rel == Path("package.md"):
        return True
    if rel.name in EXEMPT_NAMES:
        return False
    if rel.parts and rel.parts[0] == "_curated":
        return "maps" not in rel.parts and "status" not in rel.parts
    if rel.parts and rel.parts[0] == "_staging":
        return True
    return False


def _folder_allowed(rel: Path, spec: dict) -> bool:
    folder = spec.get("folder")
    if folder == "**":
        return True
    if folder == ".":
        file_name = spec.get("file")
        return rel.parent == Path(".") and (not file_name or rel.name == file_name)
    try:
        rel.relative_to(Path(folder))
        return True
    except ValueError:
        return False


def _headings(body: str) -> dict[str, str]:
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", body, re.MULTILINE))
    out: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        out[match.group(1).strip()] = body[start:end].strip()
    return out


def _local_evidence_paths(fm: dict) -> Iterable[str]:
    values: list[object] = list(fm.get("evidence") or [])
    for rel in fm.get("relationships") or []:
        if isinstance(rel, dict):
            values.extend(rel.get("evidence") or [])
    local_prefixes = ("_staging/", "_curated/", "reviews/", "onboarding/", "taxonomy/")
    for value in values:
        if isinstance(value, str) and value.startswith(local_prefixes):
            yield value.split("#", 1)[0]


def _parse_iso_date(value: object) -> dt.date | None:
    if isinstance(value, dt.date):
        return value
    if not isinstance(value, str) or not value:
        return None
    try:
        return dt.date.fromisoformat(value)
    except ValueError:
        return None


def _collect_consumed_staging(root: Path, parsed_pages: list[tuple[Path, dict, str]]) -> set[str]:
    consumed: set[str] = set()
    for _, fm, _ in parsed_pages:
        for value in _local_evidence_paths(fm):
            if value.startswith("_staging/"):
                consumed.add(value)
    reviews = root / "reviews"
    if reviews.exists():
        pattern = re.compile(r"_staging/[A-Za-z0-9_./-]+\.md")
        for path in reviews.rglob("*.md"):
            if path.name == "_template.md":
                continue
            consumed.update(pattern.findall(path.read_text(encoding="utf-8")))
    return consumed


def _git_base(root: Path, explicit: str | None) -> str | None:
    if explicit:
        return explicit
    github_base = os.environ.get("GITHUB_BASE_REF")
    candidates = []
    if github_base:
        candidates.append(f"origin/{github_base}")
    candidates.extend(["origin/main", "origin/master", "HEAD^1"])
    for candidate in candidates:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", candidate],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            if candidate.startswith("origin/"):
                merge = subprocess.run(
                    ["git", "-C", str(root), "merge-base", "HEAD", candidate],
                    capture_output=True,
                    text=True,
                )
                if merge.returncode == 0:
                    return merge.stdout.strip()
            return candidate
    return None


def _check_consumed_staging_immutability(
    root: Path, consumed: set[str], explicit_base: str | None
) -> list[dict[str, str]]:
    if not consumed or not (root / ".git").exists():
        return []
    base = _git_base(root, explicit_base)
    if not base:
        return []
    proc = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-status", "-M", base, "HEAD"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    issues: list[dict[str, str]] = []
    for line in proc.stdout.splitlines():
        fields = line.split("\t")
        status = fields[0]
        paths = fields[1:]
        if status.startswith("A"):
            continue
        staging_paths = [p for p in paths if p.startswith("_staging/")]
        if any(p in consumed for p in staging_paths):
            issues.append(
                issue(
                    "ATLAS021",
                    "ERROR",
                    staging_paths[-1],
                    f"consumed staging evidence is immutable within a curation proposal (git status {status})",
                )
            )
    return issues


def lint_repository(
    root: str | Path,
    *,
    package_name: str = "teama",
    warn_as_error: bool = False,
    git_base: str | None = None,
    check_maps: bool = True,
    today: dt.date | None = None,
) -> list[dict[str, str]]:
    root = Path(root).resolve()
    today = today or dt.date.today()
    taxonomy = load_taxonomy(root)
    type_specs = {item["name"]: item for item in taxonomy["types"]["types"]}
    active = {name: spec for name, spec in type_specs.items() if spec.get("status") == "active"}
    reserved = {name for name, spec in type_specs.items() if spec.get("status") == "reserved"}
    allowed_rels = relationship_names(taxonomy["relationships"])
    curated_status = set(taxonomy["statuses"]["curated_status"])
    staging_status = set(taxonomy["statuses"]["staging_status"])
    confidence = set(taxonomy["statuses"]["relationship_confidence"])
    categories = set(taxonomy["categories"]["categories"])

    issues: list[dict[str, str]] = []
    parsed_pages: list[tuple[Path, dict, str]] = []
    curated_ids: dict[str, Path] = {}

    # Link resolution applies to repository Markdown, not intentionally-invalid fixtures.
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if _is_skipped(rel):
            continue
        for target in broken_links(path):
            issues.append(issue("ATLAS008", "ERROR", rel, f"broken relative Markdown link: {target}"))

    # Obvious secret checks apply to repository text artefacts, excluding deliberately
    # invalid test fixtures. Test fixtures must use synthetic placeholders.
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
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                issues.append(issue("ATLAS019", "ERROR", rel, "obvious secret pattern detected"))
                break

    governed = [
        path
        for path in sorted(root.rglob("*.md"))
        if not _is_skipped(path.relative_to(root)) and _is_governed(path.relative_to(root))
    ]

    for path in governed:
        rel = path.relative_to(root)
        try:
            fm, body = parse_frontmatter(path)
        except Exception as exc:
            issues.append(issue("ATLAS001", "ERROR", rel, str(exc)))
            continue
        parsed_pages.append((path, fm, body))

        typ = fm.get("type")
        if typ in reserved:
            issues.append(issue("ATLAS005", "ERROR", rel, f"reserved type cannot have pages: {typ}"))
            continue
        spec = active.get(typ)
        if not spec:
            issues.append(issue("ATLAS002", "ERROR", rel, f"inactive or unknown type: {typ!r}"))
            continue
        if not _folder_allowed(rel, spec):
            issues.append(issue("ATLAS002", "ERROR", rel, f"type {typ} is not allowed under {rel.parent}"))

        if fm.get("package") != package_name:
            issues.append(issue("ATLAS004", "ERROR", rel, f"package must equal {package_name}"))

        if typ == "atlas.package":
            ident = fm.get("id")
            if not valid_curated_id(ident, spec.get("id_prefix")):
                issues.append(issue("ATLAS003", "ERROR", rel, "invalid package id prefix/grammar"))
            elif ident in curated_ids:
                issues.append(issue("ATLAS003", "ERROR", rel, f"duplicate id also in {curated_ids[ident]}"))
            else:
                curated_ids[ident] = rel
            continue

        if typ.startswith("atlas.staging."):
            if not valid_staging_id(fm.get("id")):
                issues.append(issue("ATLAS003", "ERROR", rel, "invalid staging id"))
            if fm.get("status") not in staging_status:
                issues.append(issue("ATLAS006", "ERROR", rel, f"invalid staging status {fm.get('status')!r}"))
            continue

        ident = fm.get("id")
        if not valid_curated_id(ident, spec.get("id_prefix")):
            issues.append(issue("ATLAS003", "ERROR", rel, "invalid curated id prefix/grammar"))
        elif ident in curated_ids:
            issues.append(issue("ATLAS003", "ERROR", rel, f"duplicate id also in {curated_ids[ident]}"))
        else:
            curated_ids[ident] = rel

        status = fm.get("status")
        if status not in curated_status:
            issues.append(issue("ATLAS006", "ERROR", rel, f"invalid curated status {status!r}"))
        if status == "curated":
            reviewed_date = _parse_iso_date(fm.get("last_reviewed"))
            exemption = fm.get("evidence_exemption")
            if not fm.get("reviewed_by") or reviewed_date is None or (not fm.get("evidence") and not exemption):
                issues.append(
                    issue(
                        "ATLAS007",
                        "ERROR",
                        rel,
                        "status curated requires non-empty reviewed_by, valid last_reviewed, and evidence or a documented exemption",
                    )
                )

        if typ == "atlas.standard":
            category = fm.get("standard_category")
            storage_category = rel.parts[2] if len(rel.parts) >= 4 else None
            if category not in categories or storage_category != category:
                issues.append(
                    issue(
                        "ATLAS017",
                        "ERROR",
                        rel,
                        "standard_category is invalid or does not match the standards category folder",
                    )
                )

        relationships = fm.get("relationships") or []
        if not isinstance(relationships, list):
            relationships = []
            issues.append(issue("ATLAS009", "ERROR", rel, "relationships must be a list"))
        for relationship in relationships:
            if not isinstance(relationship, dict):
                issues.append(issue("ATLAS009", "ERROR", rel, "relationship must be an object"))
                continue
            rel_type = relationship.get("type")
            if rel_type not in allowed_rels:
                issues.append(issue("ATLAS009", "ERROR", rel, f"unknown relationship {rel_type!r}"))
            if rel_type in {"atlas.consumes", "atlas.produces", "atlas.depends-on"} and relationship.get("kind") not in KINDS:
                issues.append(issue("ATLAS011", "ERROR", rel, "relationship kind is missing or invalid"))
            edge_confidence = relationship.get("confidence")
            if edge_confidence not in confidence:
                issues.append(issue("ATLAS012", "ERROR", rel, "relationship confidence is invalid"))
            elif edge_confidence != "reviewed" and not str(relationship.get("note", "")).strip():
                issues.append(issue("ATLAS012", "ERROR", rel, "non-reviewed relationship requires an explanatory note"))

        if status == "archived":
            index_path = root / spec["folder"] / "index.md"
            if typ == "atlas.standard" and len(rel.parts) >= 4:
                index_path = root / "_curated" / "standards" / rel.parts[2] / "index.md"
            if index_path.exists() and links_to(index_path, path):
                issues.append(issue("ATLAS014", "ERROR", rel, "archived page appears in normal index/catalogue"))
        elif status in curated_status:
            index_path = root / spec["folder"] / "index.md"
            if typ == "atlas.standard" and len(rel.parts) >= 4:
                index_path = root / "_curated" / "standards" / rel.parts[2] / "index.md"
            if not index_path.exists() or not links_to(index_path, path):
                issues.append(issue("ATLAS013", "ERROR", rel, f"non-archived page missing from {index_path.relative_to(root)}"))

        for evidence_path in _local_evidence_paths(fm):
            if not (root / evidence_path).exists():
                issues.append(issue("ATLAS015", "ERROR", rel, f"local evidence path does not resolve: {evidence_path}"))

        headings = _headings(body)
        for heading in REQUIRED_SECTIONS.get(typ, []):
            content = headings.get(heading)
            if content is None:
                issues.append(issue("ATLAS016", "ERROR", rel, f"missing required section: {heading}"))
            elif not content.strip():
                issues.append(issue("ATLAS016", "ERROR", rel, f"required section is empty: {heading}"))

        reviewed_date = _parse_iso_date(fm.get("last_reviewed"))
        if status in {"proposed", "curated"} and reviewed_date and (today - reviewed_date).days > 180:
            issues.append(issue("ATLAS020", "WARN", rel, "review older than 180 days"))

        if typ == "atlas.component" and fm.get("deployed_as"):
            infra_root = root / "_curated" / "infra"
            infra_text = "\n".join(
                p.read_text(encoding="utf-8")
                for p in infra_root.rglob("*.md")
                if p.name not in {"README.md", "index.md", "_template.md"}
            ) if infra_root.exists() else ""
            for deployed in fm.get("deployed_as") or []:
                if str(deployed) not in infra_text:
                    issues.append(issue("ATLAS022", "WARN", rel, f"deployed_as has no corresponding infra evidence/resource name: {deployed}"))

    # Resolve reviewed local relationships after the full curated ID set is known.
    for path, fm, _ in parsed_pages:
        rel = path.relative_to(root)
        typ = fm.get("type")
        if not isinstance(typ, str) or typ.startswith("atlas.staging.") or typ == "atlas.package":
            continue
        for relationship in fm.get("relationships") or []:
            if not isinstance(relationship, dict):
                continue
            target = relationship.get("target")
            if relationship.get("confidence") == "reviewed" and isinstance(target, str) and target.startswith("atlas-") and target not in curated_ids:
                issues.append(issue("ATLAS010", "ERROR", rel, f"reviewed local relationship target does not resolve: {target}"))

    consumed = _collect_consumed_staging(root, parsed_pages)
    issues.extend(_check_consumed_staging_immutability(root, consumed, git_base))

    if check_maps:
        try:
            generated = build_maps(root)
            for name, obj in generated.items():
                path = root / "_curated" / "maps" / name
                if not path.exists() or path.read_bytes() != stable_bytes(obj):
                    issues.append(issue("ATLAS018", "ERROR", path.relative_to(root), "generated map drift"))
        except MapBuildError as exc:
            issues.append(issue("ATLAS018", "ERROR", "_curated/maps", f"maps cannot be generated: {exc}"))

    # Keep deterministic output ordering.
    issues.sort(key=lambda item: (item["path"], item["code"], item["level"], item["message"]))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--warn-as-error", action="store_true")
    parser.add_argument("--package", default="teama", help=argparse.SUPPRESS)
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

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re
from typing import Iterable

from scripts.lib.frontmatter import parse_frontmatter


ACTIVE_STAGING_STATUSES = frozenset({"new", "curating"})
TERMINAL_STAGING_STATUSES = frozenset(
    {"consumed", "no-change", "deferred", "rejected"}
)
STAGING_STATUSES = ACTIVE_STAGING_STATUSES | TERMINAL_STAGING_STATUSES
STAGING_BUCKETS = frozenset(
    {
        "business-concepts",
        "changes",
        "components",
        "flows",
        "incidents",
        "infra",
        "runbooks",
        "schema-info",
        "standards",
    }
)

_IGNORED_FILENAMES = frozenset({"README.md", "index.md", "_template.md"})
_TARGET_HEADING_RE = re.compile(
    r"^## Suggested curated targets[ \t]*$", re.MULTILINE
)
_NEXT_LEVEL_TWO_HEADING_RE = re.compile(r"^##\s+", re.MULTILINE)
_HTML_COMMENT_RE = re.compile(r"<!--[\s\S]*?(?:-->|\Z)")
_FENCE_OPEN_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_CURATED_PATH_RE = re.compile(r"(?:\.\.?/)*_curated/[A-Za-z0-9_./-]+")
_STABLE_ID_PREFIXES = (
    "asset|comp|concept|decision|flow|incident|infra|join|package|query|repo|"
    "resource|runbook|schema|standard"
)
_STABLE_ID_RE = re.compile(
    rf"(?<![A-Za-z0-9_-])(({_STABLE_ID_PREFIXES})\.[a-z0-9][a-z0-9.-]*)(?![A-Za-z0-9_-])"
)
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+] |\d+[.)] )(.*)$")
_EMPTY_TARGET_TEXT = {
    "none",
    "none recorded",
    "no suggested targets",
    "no targets",
    "not yet known",
    "unknown",
}


@dataclass(frozen=True)
class StagingDiagnostic:
    page: str
    record_id: str | None
    message: str
    kind: str

    def as_dict(self) -> dict:
        return {
            "page": self.page,
            "record_id": self.record_id,
            "message": self.message,
            "kind": self.kind,
        }


@dataclass(frozen=True)
class StagingPage:
    path: Path
    page: str
    frontmatter: dict
    body: str
    bucket: str
    candidate_domain: str


def _json_value(value: object) -> object:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _candidate_domain(relative_to_staging: Path) -> str:
    parts = relative_to_staging.parts
    if len(parts) >= 3 and parts[0] in {"components", "flows"}:
        return parts[1]
    return ""


def _mask_text(value: str) -> str:
    return "".join("\n" if character == "\n" else " " for character in value)


def _mask_ignored_markdown(body: str) -> str:
    """Mask comments and fenced examples while preserving all character offsets."""

    masked = _HTML_COMMENT_RE.sub(lambda match: _mask_text(match.group(0)), body)
    lines = masked.splitlines(keepends=True)
    fence_character = ""
    fence_length = 0
    for index, line in enumerate(lines):
        if not fence_character:
            opened = _FENCE_OPEN_RE.match(line)
            if opened:
                marker = opened.group(1)
                fence_character = marker[0]
                fence_length = len(marker)
                lines[index] = _mask_text(line)
            continue
        lines[index] = _mask_text(line)
        closing = re.match(
            rf"^[ \t]{{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*(?:\n|\Z)",
            line,
        )
        if closing:
            fence_character = ""
            fence_length = 0
    return "".join(lines)


def read_staging_pages(
    root: str | Path,
) -> tuple[list[StagingPage], list[StagingDiagnostic]]:
    """Read staging evidence without loading curated pages, maps, or compilers."""

    root = Path(root).resolve()
    staging_root = root / "_staging"
    pages: list[StagingPage] = []
    diagnostics: list[StagingDiagnostic] = []
    if not staging_root.exists():
        return pages, diagnostics

    for path in sorted(staging_root.rglob("*.md")):
        if path.name in _IGNORED_FILENAMES:
            continue
        relative = path.relative_to(root).as_posix()
        relative_to_staging = path.relative_to(staging_root)
        bucket = relative_to_staging.parts[0]
        try:
            frontmatter, body = parse_frontmatter(path)
        except Exception as exc:
            diagnostics.append(
                StagingDiagnostic(
                    page=relative,
                    record_id=None,
                    message=f"invalid frontmatter: {exc}",
                    kind="frontmatter",
                )
            )
            continue
        if not isinstance(frontmatter, dict):
            diagnostics.append(
                StagingDiagnostic(
                    page=relative,
                    record_id=None,
                    message="YAML frontmatter must be a mapping",
                    kind="frontmatter",
                )
            )
            continue
        record_id = frontmatter.get("id")
        if bucket not in STAGING_BUCKETS:
            diagnostics.append(
                StagingDiagnostic(
                    page=relative,
                    record_id=record_id if isinstance(record_id, str) else None,
                    message=f"unknown staging bucket {bucket!r}; record excluded",
                    kind="unknown-bucket",
                )
            )
            continue
        pages.append(
            StagingPage(
                path=path,
                page=relative,
                frontmatter=frontmatter,
                body=body,
                bucket=bucket,
                candidate_domain=_candidate_domain(relative_to_staging),
            )
        )
    return pages, diagnostics


def _normalise_target(value: str) -> str:
    target = value.strip().strip("<>").replace("\\", "/")
    target = target.split("#", 1)[0].split("?", 1)[0]
    curated_at = target.find("_curated/")
    if curated_at >= 0:
        target = target[curated_at:]
    return target.rstrip("/.,;:")


def _target_tokens(text: str) -> list[str]:
    values: list[str] = []
    candidates = [match.group(1) for match in _MARKDOWN_LINK_RE.finditer(text)]
    candidates.extend(match.group(1) for match in _INLINE_CODE_RE.finditer(text))
    candidates.extend(match.group(0) for match in _CURATED_PATH_RE.finditer(text))
    candidates.extend(match.group(1) for match in _STABLE_ID_RE.finditer(text))
    for candidate in candidates:
        target = _normalise_target(candidate)
        if target.startswith("_curated/") or _STABLE_ID_RE.fullmatch(target):
            values.append(target)
    return list(dict.fromkeys(values))


def parse_suggested_targets(
    page: StagingPage,
) -> tuple[list[str], list[StagingDiagnostic]]:
    searchable_body = _mask_ignored_markdown(page.body)
    matches = list(_TARGET_HEADING_RE.finditer(searchable_body))
    if not matches:
        return [], [
            StagingDiagnostic(
                page=page.page,
                record_id=str(page.frontmatter.get("id") or "") or None,
                message="missing exact '## Suggested curated targets' section",
                kind="suggested-targets",
            )
        ]
    if len(matches) > 1:
        return [], [
            StagingDiagnostic(
                page=page.page,
                record_id=str(page.frontmatter.get("id") or "") or None,
                message="multiple '## Suggested curated targets' sections",
                kind="suggested-targets",
            )
        ]

    start = matches[0].end()
    next_heading = _NEXT_LEVEL_TWO_HEADING_RE.search(searchable_body, start)
    section = searchable_body[
        start : next_heading.start() if next_heading else len(searchable_body)
    ]
    targets: list[str] = []
    diagnostics: list[StagingDiagnostic] = []
    meaningful_text: list[str] = []
    for line_number, line in enumerate(section.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--") or stripped.startswith(">"):
            continue
        list_item = _LIST_ITEM_RE.match(line)
        if not list_item:
            meaningful_text.append(stripped)
            continue
        item = list_item.group(1).strip()
        if item.rstrip(".").casefold() in _EMPTY_TARGET_TEXT:
            continue
        found = _target_tokens(item)
        if not found:
            diagnostics.append(
                StagingDiagnostic(
                    page=page.page,
                    record_id=str(page.frontmatter.get("id") or "") or None,
                    message=(
                        "suggested target list item does not contain a stable ID or "
                        f"_curated path: {item!r}"
                    ),
                    kind="suggested-targets",
                )
            )
            continue
        targets.extend(found)

    if not targets and meaningful_text:
        normalised = " ".join(meaningful_text).rstrip(".").casefold()
        if normalised not in _EMPTY_TARGET_TEXT:
            diagnostics.append(
                StagingDiagnostic(
                    page=page.page,
                    record_id=str(page.frontmatter.get("id") or "") or None,
                    message=(
                        "suggested targets must be Markdown list items containing a stable ID "
                        "or _curated path"
                    ),
                    kind="suggested-targets",
                )
            )
    return sorted(set(targets)), diagnostics


def load_staging_records(root: str | Path) -> tuple[list[dict], list[dict]]:
    pages, page_diagnostics = read_staging_pages(root)
    records: list[dict] = []
    diagnostics = list(page_diagnostics)
    id_pages: dict[str, list[str]] = {}

    for page in pages:
        frontmatter = page.frontmatter
        record_id = str(frontmatter.get("id") or "")
        targets, target_diagnostics = parse_suggested_targets(page)
        diagnostics.extend(target_diagnostics)
        if record_id:
            id_pages.setdefault(record_id, []).append(page.page)
        records.append(
            {
                "id": record_id,
                "type": str(frontmatter.get("type") or ""),
                "bucket": page.bucket,
                "title": str(frontmatter.get("title") or ""),
                "description": str(frontmatter.get("description") or ""),
                "status": str(frontmatter.get("status") or ""),
                "timestamp": str(_json_value(frontmatter.get("timestamp") or "")),
                "captured_by": str(frontmatter.get("captured_by") or ""),
                "source_type": str(frontmatter.get("source_type") or ""),
                "candidate_domain": page.candidate_domain,
                "suggested_targets": targets,
                "change_source": _json_value(frontmatter.get("change_source")),
                "page": page.page,
            }
        )

    for record_id, paths in sorted(id_pages.items()):
        if len(paths) < 2:
            continue
        diagnostics.append(
            StagingDiagnostic(
                page=paths[0],
                record_id=record_id,
                message=f"duplicate staging ID appears in: {', '.join(paths)}",
                kind="duplicate-id",
            )
        )

    return (
        sorted(records, key=lambda item: (item["id"], item["page"])),
        [item.as_dict() for item in sorted(diagnostics, key=lambda item: (item.page, item.kind, item.message))],
    )


def _curated_target_registry(
    root: str | Path,
) -> tuple[dict[str, str], dict[str, frozenset[str]]]:
    """Resolve ID/page aliases directly from curated frontmatter, without maps."""

    root = Path(root).resolve()
    curated_root = root / "_curated"
    id_pages: dict[str, set[str]] = {}
    if not curated_root.exists():
        return {}, {}
    for path in sorted(curated_root.rglob("*.md")):
        relative_to_curated = path.relative_to(curated_root)
        if path.name in _IGNORED_FILENAMES:
            continue
        if relative_to_curated.parts[0] in {"maps", "status"}:
            continue
        try:
            frontmatter, _ = parse_frontmatter(path)
        except Exception:
            continue
        if not isinstance(frontmatter, dict) or frontmatter.get("status") == "archived":
            continue
        record_id = frontmatter.get("id")
        if not isinstance(record_id, str) or not record_id:
            continue
        page = path.relative_to(root).as_posix()
        page_ids = [record_id]
        for field in ("promoted_resources", "assets"):
            embedded = frontmatter.get(field)
            if not isinstance(embedded, list):
                continue
            page_ids.extend(
                item["id"]
                for item in embedded
                if isinstance(item, dict)
                and isinstance(item.get("id"), str)
                and item["id"]
            )
        for page_id in page_ids:
            id_pages.setdefault(page_id, set()).add(page)

    id_to_page = {
        record_id: next(iter(paths))
        for record_id, paths in id_pages.items()
        if len(paths) == 1
    }
    page_to_ids: dict[str, set[str]] = {}
    for record_id, page in id_to_page.items():
        page_to_ids.setdefault(page, set()).add(record_id)
    return id_to_page, {
        page: frozenset(record_ids) for page, record_ids in page_to_ids.items()
    }


def _target_aliases(
    target: str,
    id_to_page: dict[str, str],
    page_to_ids: dict[str, frozenset[str]],
) -> set[str]:
    normalised = _normalise_target(target)
    aliases = {normalised}
    if normalised in id_to_page:
        aliases.add(id_to_page[normalised])
    aliases.update(page_to_ids.get(normalised, ()))
    return aliases


def _targets_match(
    selected_targets: set[str],
    record_targets: list[str],
    id_to_page: dict[str, str],
    page_to_ids: dict[str, frozenset[str]],
) -> bool:
    """Match ID/page aliases without treating sibling embedded IDs as equal."""

    for selected in selected_targets:
        selected_aliases = _target_aliases(selected, id_to_page, page_to_ids)
        for record_target in record_targets:
            if record_target in selected_aliases:
                return True
            record_aliases = _target_aliases(
                record_target, id_to_page, page_to_ids
            )
            if selected in record_aliases:
                return True
    return False


def _calendar_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None


def _require_known_values(values: Iterable[str], allowed: frozenset[str], label: str) -> set[str]:
    selected = {value.strip() for value in values if value.strip()}
    unknown = sorted(selected - allowed)
    if unknown:
        raise ValueError(f"unknown staging {label}: {', '.join(unknown)}")
    return selected


def query_staging(
    root: str | Path,
    *,
    statuses: Iterable[str] = (),
    buckets: Iterable[str] = (),
    domain: str | None = None,
    timestamp: str | None = None,
    targets: Iterable[str] = (),
    include_terminal: bool = False,
) -> dict:
    records, diagnostics = load_staging_records(root)
    selected_statuses = _require_known_values(statuses, STAGING_STATUSES, "status")
    selected_buckets = _require_known_values(buckets, STAGING_BUCKETS, "bucket")
    if not selected_statuses:
        selected_statuses = set(STAGING_STATUSES if include_terminal else ACTIVE_STAGING_STATUSES)

    selected_domain = (domain or "").strip()
    selected_targets = {
        _normalise_target(value) for value in targets if _normalise_target(value)
    }
    id_to_page, page_to_ids = _curated_target_registry(root)
    if timestamp is not None:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", timestamp):
            raise ValueError("--date must use ISO YYYY-MM-DD")
        try:
            date.fromisoformat(timestamp)
        except ValueError as exc:
            raise ValueError("--date must be a valid ISO YYYY-MM-DD date") from exc

    results = []
    for record in records:
        if record["status"] not in selected_statuses:
            continue
        if selected_buckets and record["bucket"] not in selected_buckets:
            continue
        if selected_domain and record["candidate_domain"] != selected_domain:
            continue
        if timestamp and _calendar_date(record["timestamp"]) != date.fromisoformat(timestamp):
            continue
        if selected_targets and not _targets_match(
            selected_targets,
            record["suggested_targets"],
            id_to_page,
            page_to_ids,
        ):
            continue
        results.append(record)

    return {
        "results": results,
        "diagnostics": diagnostics,
        "filters": {
            "statuses": sorted(selected_statuses),
            "buckets": sorted(selected_buckets),
            "domain": selected_domain or None,
            "date": timestamp,
            "targets": sorted(selected_targets),
            "include_terminal": bool(include_terminal),
        },
    }

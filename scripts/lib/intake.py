from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
import datetime as dt
import hashlib
import json
import os
import re
import tempfile
from urllib.parse import urlsplit

from scripts.lib.ids import valid_staging_id


SCHEMA_VERSION = "atlas-intake/1.0"
CHECKPOINT_DIR = Path("_intake/checkpoints")
SOURCE_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
OUTCOMES = {
    "staged",
    "no-stage",
    "already-represented",
    "deferred",
    "unassessed",
}
RESOLVED_OUTCOMES = {"staged", "no-stage", "already-represented"}
SCP_LOCATOR_RE = re.compile(
    r"^(?:[A-Za-z0-9._-]+@)?[A-Za-z0-9.-]+:[^\s@?#]+$"
)


class IntakeError(ValueError):
    """Base error for checkpoint parsing, validation and updates."""


class CheckpointConflictError(IntakeError):
    """Raised when a compare-and-swap checkpoint write loses a race."""


@dataclass(frozen=True)
class CheckpointReference:
    staging_id: str
    location: str
    source_key: str
    commit: str
    merge_request: str | None
    change_key: str


def validate_change_source(value: object, *, required: bool = False) -> list[str]:
    """Validate the optional Git provenance block on ``staging.change``."""

    if value is None:
        return ["change_source is required when source_type is merged-change"] if required else []
    if not isinstance(value, dict):
        return ["change_source must be an object"]
    errors = _validate_exact_keys(
        value,
        required={"source_key", "branch", "commit_range", "merge_requests"},
        location="change_source",
    )
    source_key = value.get("source_key")
    if not isinstance(source_key, str) or SOURCE_KEY_RE.fullmatch(source_key) is None:
        errors.append("change_source.source_key must be a lowercase slug")
    if not _is_nonempty_string(value.get("branch")):
        errors.append("change_source.branch must be a non-empty string")

    commit_range = value.get("commit_range")
    if not isinstance(commit_range, dict):
        errors.append("change_source.commit_range must be an object")
    else:
        errors.extend(
            _validate_exact_keys(
                commit_range,
                required={"from_exclusive", "through_inclusive"},
                location="change_source.commit_range",
            )
        )
        from_exclusive = commit_range.get("from_exclusive")
        if from_exclusive is not None and not _is_sha(from_exclusive):
            errors.append(
                "change_source.commit_range.from_exclusive must be a 40- or 64-character "
                "lowercase hexadecimal commit or null"
            )
        if not _is_sha(commit_range.get("through_inclusive")):
            errors.append(
                "change_source.commit_range.through_inclusive must be a 40- or 64-character "
                "lowercase hexadecimal commit"
            )

    merge_requests = value.get("merge_requests")
    if not isinstance(merge_requests, list):
        errors.append("change_source.merge_requests must be a list")
    else:
        seen_ids: set[str] = set()
        for index, merge_request in enumerate(merge_requests):
            location = f"change_source.merge_requests[{index}]"
            if not isinstance(merge_request, dict):
                errors.append(f"{location} must be an object")
                continue
            errors.extend(
                _validate_exact_keys(
                    merge_request,
                    required={"id", "merged_commit"},
                    location=location,
                )
            )
            ident = merge_request.get("id")
            if not _is_nonempty_string(ident):
                errors.append(f"{location}.id must be a non-empty string")
            elif ident in seen_ids:
                errors.append(f"change_source.merge_requests contains duplicate id {ident}")
            else:
                seen_ids.add(ident)
            if not _is_sha(merge_request.get("merged_commit")):
                errors.append(
                    f"{location}.merged_commit must be a 40- or 64-character lowercase hexadecimal commit"
                )
    return errors


def stable_checkpoint_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _validate_filename(path: Path, value: dict) -> None:
    source = value.get("source")
    source_key = source.get("key") if isinstance(source, dict) else None
    if isinstance(source_key, str) and path.name != f"{source_key}.json":
        raise IntakeError("checkpoint filename must be <source.key>.json")


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and COMMIT_RE.fullmatch(value) is not None


def _is_nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _locator_error(value: object) -> str | None:
    if not _is_nonempty_string(value):
        return "source.locator must be a non-empty credential-free Git locator"
    locator = value.strip()
    if PureWindowsPath(locator).is_absolute() or PurePosixPath(locator).is_absolute():
        return "source.locator must not be a machine-local absolute path"
    if any(character.isspace() for character in locator):
        return "source.locator must not contain whitespace"
    if "://" not in locator and SCP_LOCATOR_RE.fullmatch(locator):
        return None

    try:
        parsed = urlsplit(locator)
        hostname = parsed.hostname
        username = parsed.username
        password = parsed.password
    except ValueError:
        return "source.locator must be a valid credential-free Git locator"
    if parsed.scheme:
        if parsed.scheme not in {"https", "ssh"}:
            return "source.locator must use credential-free HTTPS, SSH or scp-style Git syntax"
        if parsed.query or parsed.fragment:
            return "source.locator must not contain query parameters or fragments"
        if not hostname or not parsed.path.strip("/"):
            return "source.locator must identify a Git host and repository path"
        if password is not None:
            return "source.locator must not contain credentials"
        if parsed.scheme == "https" and username is not None:
            return "HTTPS source.locator must not contain user information"
        return None

    return "source.locator must use credential-free HTTPS, SSH or scp-style Git syntax"


def _validate_exact_keys(
    value: dict,
    *,
    required: set[str],
    optional: set[str] | None = None,
    location: str,
) -> list[str]:
    optional = optional or set()
    errors: list[str] = []
    missing = sorted(required - set(value))
    unexpected = sorted(set(value) - required - optional)
    if missing:
        errors.append(f"{location} is missing: {', '.join(missing)}")
    if unexpected:
        errors.append(f"{location} has unsupported fields: {', '.join(unexpected)}")
    return errors


def _validate_cursor(
    value: object,
    location: str,
    *,
    allow_null_commit: bool = False,
) -> list[str]:
    if not isinstance(value, dict):
        return [f"{location} must be an object"]
    errors = _validate_exact_keys(
        value,
        required={"commit", "merge_request"},
        location=location,
    )
    commit = value.get("commit")
    if commit is None and allow_null_commit:
        pass
    elif not _is_sha(commit):
        suffix = " or null" if allow_null_commit else ""
        errors.append(
            f"{location}.commit must be a 40- or 64-character lowercase hexadecimal commit{suffix}"
        )
    merge_request = value.get("merge_request")
    if merge_request is not None and not _is_nonempty_string(merge_request):
        errors.append(f"{location}.merge_request must be a non-empty string or null")
    if commit is None and merge_request is not None:
        errors.append(f"{location}.merge_request must be null when commit is null")
    return errors


def _validate_staging_ids(value: object, location: str) -> list[str]:
    if not isinstance(value, list):
        return [f"{location} must be a list"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, staging_id in enumerate(value):
        item_location = f"{location}[{index}]"
        if not valid_staging_id(staging_id):
            errors.append(f"{item_location} must be a valid staging ID")
        elif staging_id in seen:
            errors.append(f"{location} contains duplicate staging ID {staging_id}")
        else:
            seen.add(staging_id)
    return errors


def _validate_disposition(value: object, location: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{location} must be an object"]
    errors = _validate_exact_keys(
        value,
        required={"change_key", "commit", "merge_request", "outcome", "staging_ids"},
        optional={"reason"},
        location=location,
    )
    if not _is_nonempty_string(value.get("change_key")):
        errors.append(f"{location}.change_key must be a non-empty string")
    if not _is_sha(value.get("commit")):
        errors.append(f"{location}.commit must be a 40- or 64-character lowercase hexadecimal commit")
    merge_request = value.get("merge_request")
    if merge_request is not None and not _is_nonempty_string(merge_request):
        errors.append(f"{location}.merge_request must be a non-empty string or null")
    outcome = value.get("outcome")
    if outcome not in OUTCOMES:
        errors.append(f"{location}.outcome must be one of {', '.join(sorted(OUTCOMES))}")
    errors.extend(_validate_staging_ids(value.get("staging_ids"), f"{location}.staging_ids"))
    staging_ids = value.get("staging_ids") if isinstance(value.get("staging_ids"), list) else []
    if outcome in {"staged", "already-represented"} and not staging_ids:
        errors.append(f"{location}.staging_ids is required for outcome {outcome}")
    if outcome in {"no-stage", "unassessed"} and staging_ids:
        errors.append(f"{location}.staging_ids must be empty for outcome {outcome}")
    reason = value.get("reason")
    if outcome in {"no-stage", "deferred", "unassessed"} and not _is_nonempty_string(reason):
        errors.append(f"{location}.reason is required for outcome {outcome}")
    elif reason is not None and not _is_nonempty_string(reason):
        errors.append(f"{location}.reason must be a non-empty string when supplied")
    return errors


def _validate_unresolved(value: object, location: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{location} must be an object"]
    errors = _validate_exact_keys(
        value,
        required={"change_key", "commit", "merge_request", "reason", "staging_ids"},
        location=location,
    )
    if not _is_nonempty_string(value.get("change_key")):
        errors.append(f"{location}.change_key must be a non-empty string")
    if not _is_sha(value.get("commit")):
        errors.append(f"{location}.commit must be a 40- or 64-character lowercase hexadecimal commit")
    merge_request = value.get("merge_request")
    if merge_request is not None and not _is_nonempty_string(merge_request):
        errors.append(f"{location}.merge_request must be a non-empty string or null")
    if not _is_nonempty_string(value.get("reason")):
        errors.append(f"{location}.reason must be a non-empty string")
    errors.extend(_validate_staging_ids(value.get("staging_ids"), f"{location}.staging_ids"))
    return errors


def _valid_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def validate_checkpoint(value: object) -> list[str]:
    """Return deterministic semantic errors for one checkpoint document."""

    if not isinstance(value, dict):
        return ["checkpoint must be a JSON object"]
    errors = _validate_exact_keys(
        value,
        required={
            "schema_version",
            "source",
            "observed_through",
            "considered_through",
            "last_run",
            "unresolved",
            "updated_at",
            "updated_by",
        },
        location="checkpoint",
    )
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    source = value.get("source")
    source_key = ""
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        errors.extend(
            _validate_exact_keys(
                source,
                required={"key", "locator", "default_branch"},
                location="source",
            )
        )
        source_key = source.get("key") if isinstance(source.get("key"), str) else ""
        if SOURCE_KEY_RE.fullmatch(source_key) is None:
            errors.append("source.key must be a lowercase slug")
        locator_error = _locator_error(source.get("locator"))
        if locator_error:
            errors.append(locator_error)
        if not _is_nonempty_string(source.get("default_branch")):
            errors.append("source.default_branch must be a non-empty string")

    errors.extend(_validate_cursor(value.get("observed_through"), "observed_through"))
    errors.extend(
        _validate_cursor(
            value.get("considered_through"),
            "considered_through",
            allow_null_commit=True,
        )
    )

    last_run = value.get("last_run")
    dispositions: list[dict] = []
    if not isinstance(last_run, dict):
        errors.append("last_run must be an object")
    else:
        errors.extend(
            _validate_exact_keys(
                last_run,
                required={"from_exclusive", "through_inclusive", "dispositions"},
                location="last_run",
            )
        )
        from_exclusive = last_run.get("from_exclusive")
        if from_exclusive is not None and not _is_sha(from_exclusive):
            errors.append(
                "last_run.from_exclusive must be a 40- or 64-character lowercase hexadecimal commit or null"
            )
        if not _is_sha(last_run.get("through_inclusive")):
            errors.append(
                "last_run.through_inclusive must be a 40- or 64-character lowercase hexadecimal commit"
            )
        raw_dispositions = last_run.get("dispositions")
        if not isinstance(raw_dispositions, list):
            errors.append("last_run.dispositions must be a list")
        else:
            seen_keys: set[str] = set()
            dispositions = [item for item in raw_dispositions if isinstance(item, dict)]
            for index, item in enumerate(raw_dispositions):
                location = f"last_run.dispositions[{index}]"
                errors.extend(_validate_disposition(item, location))
                if isinstance(item, dict) and _is_nonempty_string(item.get("change_key")):
                    if item["change_key"] in seen_keys:
                        errors.append(f"last_run.dispositions contains duplicate change_key {item['change_key']}")
                    seen_keys.add(item["change_key"])
            through = last_run.get("through_inclusive")
            if _is_sha(through) and from_exclusive != through and not raw_dispositions:
                errors.append("a non-empty last_run range must contain at least one disposition")

    unresolved = value.get("unresolved")
    unresolved_items: list[dict] = []
    if not isinstance(unresolved, list):
        errors.append("unresolved must be a list")
    else:
        seen_keys: set[str] = set()
        unresolved_items = [item for item in unresolved if isinstance(item, dict)]
        for index, item in enumerate(unresolved):
            location = f"unresolved[{index}]"
            errors.extend(_validate_unresolved(item, location))
            if isinstance(item, dict) and _is_nonempty_string(item.get("change_key")):
                if item["change_key"] in seen_keys:
                    errors.append(f"unresolved contains duplicate change_key {item['change_key']}")
                seen_keys.add(item["change_key"])

    def unresolved_identity(item: dict) -> tuple[object, object, object, tuple[object, ...]]:
        staging_ids = item.get("staging_ids")
        return (
            item.get("change_key"),
            item.get("commit"),
            item.get("merge_request"),
            tuple(staging_ids) if isinstance(staging_ids, list) else (),
        )

    unresolved_identities = {unresolved_identity(item) for item in unresolved_items}
    for item in dispositions:
        if item.get("outcome") in {"deferred", "unassessed"} and unresolved_identity(item) not in unresolved_identities:
            errors.append(
                f"last_run disposition {item.get('change_key')} with outcome {item.get('outcome')} "
                "must have an unresolved entry with matching commit, merge request and staging IDs"
            )

    observed = value.get("observed_through")
    considered = value.get("considered_through")
    if isinstance(last_run, dict) and isinstance(observed, dict):
        through = last_run.get("through_inclusive")
        if _is_sha(through) and observed.get("commit") != through:
            errors.append("observed_through.commit must equal last_run.through_inclusive")
        endpoint_dispositions = [item for item in dispositions if item.get("commit") == through]
        if _is_sha(through) and last_run.get("from_exclusive") != through and not endpoint_dispositions:
            errors.append("a non-empty last_run range must end with a disposition for through_inclusive")
        if endpoint_dispositions:
            endpoint_merge_requests = {item.get("merge_request") for item in endpoint_dispositions}
            if observed.get("merge_request") not in endpoint_merge_requests:
                errors.append(
                    "observed_through.merge_request must match an endpoint disposition"
                )
    if isinstance(last_run, dict) and isinstance(considered, dict):
        through = last_run.get("through_inclusive")
        has_unassessed = any(item.get("outcome") == "unassessed" for item in dispositions)
        if _is_sha(through) and has_unassessed and considered.get("commit") != last_run.get("from_exclusive"):
            errors.append(
                "considered_through.commit must equal last_run.from_exclusive while unassessed changes remain"
            )
        if _is_sha(through) and not has_unassessed and considered.get("commit") != through:
            errors.append("considered_through.commit must equal last_run.through_inclusive when no changes are unassessed")
        if _is_sha(through) and not has_unassessed:
            endpoint_merge_requests = {
                item.get("merge_request")
                for item in dispositions
                if item.get("commit") == through
            }
            if endpoint_merge_requests and considered.get("merge_request") not in endpoint_merge_requests:
                errors.append(
                    "considered_through.merge_request must match an endpoint disposition"
                )

    if not _valid_timestamp(value.get("updated_at")):
        errors.append("updated_at must be an ISO 8601 timestamp with a timezone")
    if not _is_nonempty_string(value.get("updated_by")):
        errors.append("updated_by must be a non-empty string")
    return errors


def validate_checkpoint_transition(previous: dict, current: dict) -> list[str]:
    """Validate invariants that require the preceding committed checkpoint."""

    errors: list[str] = []
    if previous.get("source") != current.get("source"):
        errors.append("checkpoint source key, locator and default branch are immutable")

    previous_considered = previous.get("considered_through")
    previous_commit = (
        previous_considered.get("commit") if isinstance(previous_considered, dict) else None
    )
    current_run = current.get("last_run")
    current_from = current_run.get("from_exclusive") if isinstance(current_run, dict) else None
    if current_from != previous_commit:
        errors.append("last_run.from_exclusive must equal the previous considered_through.commit")

    current_considered = current.get("considered_through")
    if (
        isinstance(previous_considered, dict)
        and isinstance(current_considered, dict)
        and current_considered.get("commit") == previous_commit
        and current_considered != previous_considered
    ):
        errors.append(
            "considered_through must preserve the complete previous cursor when consideration does not advance"
        )

    def change_identity(item: object) -> tuple[object, object, object] | None:
        if not isinstance(item, dict):
            return None
        return (item.get("change_key"), item.get("commit"), item.get("merge_request"))

    current_unresolved = current.get("unresolved")
    unresolved_identities = {
        identity
        for item in (current_unresolved if isinstance(current_unresolved, list) else [])
        if (identity := change_identity(item)) is not None
    }
    dispositions = current_run.get("dispositions") if isinstance(current_run, dict) else None
    resolved_identities = {
        identity
        for item in (dispositions if isinstance(dispositions, list) else [])
        if isinstance(item, dict)
        and item.get("outcome") in RESOLVED_OUTCOMES
        and (identity := change_identity(item)) is not None
    }
    previous_unresolved = previous.get("unresolved")
    if isinstance(previous_unresolved, list):
        for item in previous_unresolved:
            identity = change_identity(item)
            if identity is None or identity in unresolved_identities or identity in resolved_identities:
                continue
            errors.append(
                f"previous unresolved change {identity[0]} cannot disappear without an explicit resolving disposition"
            )
    return errors


def checkpoint_references(value: dict) -> list[CheckpointReference]:
    source = value.get("source") if isinstance(value, dict) else None
    source_key = source.get("key", "") if isinstance(source, dict) else ""
    references: list[CheckpointReference] = []
    last_run = value.get("last_run") if isinstance(value, dict) else None
    if isinstance(last_run, dict) and isinstance(last_run.get("dispositions"), list):
        for index, disposition in enumerate(last_run["dispositions"]):
            if not isinstance(disposition, dict) or not isinstance(disposition.get("staging_ids"), list):
                continue
            for staging_id in disposition["staging_ids"]:
                if isinstance(staging_id, str):
                    references.append(
                        CheckpointReference(
                            staging_id,
                            f"last_run.dispositions[{index}].staging_ids",
                            source_key,
                            str(disposition.get("commit") or ""),
                            disposition.get("merge_request") if isinstance(disposition.get("merge_request"), str) else None,
                            str(disposition.get("change_key") or ""),
                        )
                    )
    unresolved = value.get("unresolved") if isinstance(value, dict) else None
    if isinstance(unresolved, list):
        for index, item in enumerate(unresolved):
            if not isinstance(item, dict) or not isinstance(item.get("staging_ids"), list):
                continue
            for staging_id in item["staging_ids"]:
                if isinstance(staging_id, str):
                    references.append(
                        CheckpointReference(
                            staging_id,
                            f"unresolved[{index}].staging_ids",
                            source_key,
                            str(item.get("commit") or ""),
                            item.get("merge_request") if isinstance(item.get("merge_request"), str) else None,
                            str(item.get("change_key") or ""),
                        )
                    )
    return references


def load_checkpoint(path: str | Path) -> dict:
    path = Path(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise IntakeError(f"cannot read checkpoint: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise IntakeError(f"invalid checkpoint JSON: {exc}") from exc
    errors = validate_checkpoint(value)
    if errors:
        raise IntakeError("; ".join(errors))
    _validate_filename(path, value)
    return value


def checkpoint_digest(path: str | Path) -> str | None:
    path = Path(path)
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise IntakeError(f"cannot read checkpoint for digest: {exc}") from exc
    return hashlib.sha256(data).hexdigest()


def write_checkpoint_atomic(
    path: str | Path,
    value: dict,
    *,
    expected_digest: str | None,
) -> str:
    """Validate and atomically replace a checkpoint if its prior digest matches.

    Pass ``expected_digest=None`` to assert that the checkpoint does not exist.
    The returned digest identifies the canonical bytes written.
    """

    path = Path(path)
    errors = validate_checkpoint(value)
    if errors:
        raise IntakeError("; ".join(errors))
    _validate_filename(path, value)
    if expected_digest is not None and re.fullmatch(r"[0-9a-f]{64}", expected_digest) is None:
        raise IntakeError("expected digest must be a lowercase SHA-256 digest or explicit missing state")
    data = stable_checkpoint_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(f".{path.name}.lock")
    try:
        lock_handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise CheckpointConflictError(
            f"checkpoint update is already locked by another writer: {lock.name}"
        ) from exc
    except OSError as exc:
        raise IntakeError(f"cannot acquire checkpoint update lock: {exc}") from exc
    try:
        with os.fdopen(lock_handle, "w", encoding="utf-8") as handle:
            handle.write(f"pid={os.getpid()}\n")
    except Exception:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
        raise

    temporary: Path | None = None
    try:
        try:
            current_bytes = path.read_bytes()
        except FileNotFoundError:
            current_bytes = None
        except OSError as exc:
            raise IntakeError(f"cannot read existing checkpoint: {exc}") from exc
        current_digest = hashlib.sha256(current_bytes).hexdigest() if current_bytes is not None else None
        if current_digest != expected_digest:
            expected = expected_digest or "missing"
            actual = current_digest or "missing"
            raise CheckpointConflictError(
                f"checkpoint changed concurrently: expected {expected}, found {actual}"
            )
        if current_bytes is not None:
            try:
                previous = json.loads(current_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise IntakeError(f"existing checkpoint is invalid JSON: {exc}") from exc
            previous_errors = validate_checkpoint(previous)
            if previous_errors:
                raise IntakeError("existing checkpoint is invalid: " + "; ".join(previous_errors))
            _validate_filename(path, previous)
            transition_errors = validate_checkpoint_transition(previous, value)
            if transition_errors:
                raise IntakeError("invalid checkpoint transition: " + "; ".join(transition_errors))
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass
        try:
            lock.unlink()
        except FileNotFoundError:
            pass
    return hashlib.sha256(data).hexdigest()

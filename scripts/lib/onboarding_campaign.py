from __future__ import annotations

from copy import deepcopy
import datetime as dt
import hashlib
import json
import os
import posixpath
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import tempfile

from scripts.lib.ids import ID_RE, valid_staging_id
from scripts.lib.intake import _locator_error


SCHEMA_VERSION = "atlas-onboarding-campaign/1.0"
CAMPAIGN_DIR = Path("_intake/onboarding")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
PHASES = {"pilot", "rollout", "paused", "complete"}
ITEM_STATES = {"queued", "blocked", "staged", "already-covered", "skipped"}
TERMINAL_STATES = {"staged", "already-covered", "skipped"}
REASON_MAX_LENGTH = 280
ONBOARDING_SOURCE_FIELDS = frozenset({"campaign_id", "item_id"})


class CampaignError(ValueError):
    """Base error for onboarding campaign parsing, validation and updates."""


class CampaignConflictError(CampaignError):
    """Raised when a campaign compare-and-swap write loses a race."""


def _exact_keys(value: dict, *, required: set[str], location: str) -> list[str]:
    missing = sorted(required - set(value))
    unexpected = sorted(set(value) - required)
    errors: list[str] = []
    if missing:
        errors.append(f"{location} is missing: {', '.join(missing)}")
    if unexpected:
        errors.append(f"{location} has unsupported fields: {', '.join(unexpected)}")
    return errors


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha_or_null(value: object, location: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, str) or COMMIT_RE.fullmatch(value) is None:
        return [
            f"{location} must be a 40- or 64-character lowercase hexadecimal commit or null"
        ]
    return []


def _canonical_repository_root(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return posixpath.normpath(value.replace("\\", "/"))


def _repository_root_errors(value: object, location: str) -> tuple[list[str], str | None]:
    if not _nonempty_string(value):
        return [f"{location} must be a non-empty repository-relative path"], None
    path = str(value)
    canonical = _canonical_repository_root(path)
    assert canonical is not None
    if path == ".":
        return [], canonical
    if (
        "\\" in path
        or PureWindowsPath(path).is_absolute()
        or PurePosixPath(path).is_absolute()
        or ":" in path
    ):
        return [f"{location} must not be a machine-local or absolute path"], canonical
    if canonical != path or any(part == ".." for part in PurePosixPath(path).parts):
        return [
            f"{location} must be a canonical repository-relative path without parent traversal"
        ], canonical
    return [], canonical


def _slug_list(value: object, location: str) -> list[str]:
    if not isinstance(value, list):
        return [f"{location} must be a list"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str) or SLUG_RE.fullmatch(item) is None:
            errors.append(f"{location}[{index}] must be a lowercase slug")
        elif item in seen:
            errors.append(f"{location} contains duplicate value {item}")
        else:
            seen.add(item)
    return errors


def validate_onboarding_source(
    value: object, *, location: str = "onboarding_source"
) -> list[str]:
    """Validate the optional staging provenance written by portfolio onboarding."""

    if not isinstance(value, dict):
        return [f"{location} must be an object"]
    errors = _exact_keys(value, required=set(ONBOARDING_SOURCE_FIELDS), location=location)
    for field in sorted(ONBOARDING_SOURCE_FIELDS):
        if not isinstance(value.get(field), str) or SLUG_RE.fullmatch(value[field]) is None:
            errors.append(f"{location}.{field} must be a lowercase slug")
    return errors


def _routing_hints(value: object, location: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"{location} must be an object"]
    errors = _exact_keys(value, required={"atlas_ids", "product_roots"}, location=location)
    atlas_ids = value.get("atlas_ids")
    if not isinstance(atlas_ids, list):
        errors.append(f"{location}.atlas_ids must be a list")
    else:
        seen_ids: set[str] = set()
        for index, atlas_id in enumerate(atlas_ids):
            if not isinstance(atlas_id, str) or ID_RE.fullmatch(atlas_id) is None:
                errors.append(f"{location}.atlas_ids[{index}] must be an Atlas stable ID")
            elif atlas_id in seen_ids:
                errors.append(f"{location}.atlas_ids contains duplicate value {atlas_id}")
            else:
                seen_ids.add(atlas_id)
    product_roots = value.get("product_roots")
    if not isinstance(product_roots, list):
        errors.append(f"{location}.product_roots must be a list")
    else:
        seen_roots: set[str] = set()
        for index, product_root in enumerate(product_roots):
            root_location = f"{location}.product_roots[{index}]"
            root_errors, canonical = _repository_root_errors(product_root, root_location)
            errors.extend(root_errors)
            if canonical is not None:
                if canonical in seen_roots:
                    errors.append(f"{location}.product_roots contains duplicate canonical path {canonical}")
                else:
                    seen_roots.add(canonical)
    return errors


def _valid_timestamp(value: object) -> bool:
    if not _nonempty_string(value):
        return False
    candidate = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = dt.datetime.fromisoformat(candidate)
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _reason_errors(value: object, location: str) -> list[str]:
    if value is None:
        return []
    if (
        not _nonempty_string(value)
        or "\r" in value
        or "\n" in value
        or len(value) > REASON_MAX_LENGTH
    ):
        return [
            f"{location} must be a compact single-line operational reason of at most {REASON_MAX_LENGTH} characters or null"
        ]
    return []


def _staging_ids(value: object, location: str) -> list[str]:
    if not isinstance(value, list):
        return [f"{location} must be a list"]
    errors: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not valid_staging_id(item):
            errors.append(f"{location}[{index}] must be a valid staging ID")
        elif item in seen:
            errors.append(f"{location} contains duplicate staging ID {item}")
        else:
            seen.add(item)
    return errors


def validate_campaign(value: object) -> list[str]:
    """Return deterministic structural and state errors for a campaign document."""

    if not isinstance(value, dict):
        return ["campaign must be a JSON object"]
    errors = _exact_keys(
        value,
        required={
            "schema_version",
            "campaign_id",
            "title",
            "phase",
            "updated_at",
            "updated_by",
            "pilot",
            "active_trial",
            "sources",
            "items",
        },
        location="campaign",
    )
    if value.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(value.get("campaign_id"), str) or SLUG_RE.fullmatch(value["campaign_id"]) is None:
        errors.append("campaign_id must be a lowercase slug")
    if not _nonempty_string(value.get("title")):
        errors.append("title must be a non-empty string")
    if value.get("phase") not in PHASES:
        errors.append(f"phase must be one of {', '.join(sorted(PHASES))}")
    if not _valid_timestamp(value.get("updated_at")):
        errors.append("updated_at must be an ISO 8601 timestamp with a timezone")
    if not _nonempty_string(value.get("updated_by")):
        errors.append("updated_by must be a non-empty string")

    source_keys: set[str] = set()
    sources = value.get("sources")
    if not isinstance(sources, list):
        errors.append("sources must be a list")
    else:
        for index, source in enumerate(sources):
            location = f"sources[{index}]"
            if not isinstance(source, dict):
                errors.append(f"{location} must be an object")
                continue
            errors.extend(
                _exact_keys(
                    source,
                    required={"source_key", "locator", "default_branch"},
                    location=location,
                )
            )
            source_key = source.get("source_key")
            if not isinstance(source_key, str) or SLUG_RE.fullmatch(source_key) is None:
                errors.append(f"{location}.source_key must be a lowercase slug")
            elif source_key in source_keys:
                errors.append(f"sources contains duplicate source_key {source_key}")
            else:
                source_keys.add(source_key)
            locator_error = _locator_error(source.get("locator"))
            if locator_error:
                errors.append(locator_error.replace("source.locator", f"{location}.locator"))
            if not _nonempty_string(source.get("default_branch")):
                errors.append(f"{location}.default_branch must be a non-empty string")

    item_ids: set[str] = set()
    item_roots: set[tuple[str, str]] = set()
    item_states: dict[str, str] = {}
    items = value.get("items")
    if not isinstance(items, list):
        errors.append("items must be a list")
    else:
        for index, item in enumerate(items):
            location = f"items[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{location} must be an object")
                continue
            errors.extend(
                _exact_keys(
                    item,
                    required={
                        "item_id", "source_key", "repository_root", "archetype", "traits",
                        "routing_hints", "state", "selected_commit", "staging_ids",
                        "atlas_commit", "reason",
                    },
                    location=location,
                )
            )
            item_id = item.get("item_id")
            if not isinstance(item_id, str) or SLUG_RE.fullmatch(item_id) is None:
                errors.append(f"{location}.item_id must be a lowercase slug")
            elif item_id in item_ids:
                errors.append(f"items contains duplicate item_id {item_id}")
            else:
                item_ids.add(item_id)
                if isinstance(item.get("state"), str):
                    item_states[item_id] = item["state"]
            source_key = item.get("source_key")
            if not isinstance(source_key, str) or SLUG_RE.fullmatch(source_key) is None:
                errors.append(f"{location}.source_key must be a lowercase slug")
            elif source_key not in source_keys:
                errors.append(f"{location}.source_key must reference a campaign source")
            root = item.get("repository_root")
            root_errors, canonical_root = _repository_root_errors(
                root, f"{location}.repository_root"
            )
            errors.extend(root_errors)
            if isinstance(source_key, str) and canonical_root is not None:
                identity = (source_key, canonical_root)
                if identity in item_roots:
                    errors.append(
                        "items contains duplicate (source_key, repository_root) "
                        f"{source_key}, {canonical_root}"
                    )
                else:
                    item_roots.add(identity)
            if not isinstance(item.get("archetype"), str) or SLUG_RE.fullmatch(item["archetype"]) is None:
                errors.append(f"{location}.archetype must be a lowercase slug")
            errors.extend(_slug_list(item.get("traits"), f"{location}.traits"))
            errors.extend(_routing_hints(item.get("routing_hints"), f"{location}.routing_hints"))
            state = item.get("state")
            if state not in ITEM_STATES:
                errors.append(f"{location}.state must be one of {', '.join(sorted(ITEM_STATES))}")
            errors.extend(_sha_or_null(item.get("selected_commit"), f"{location}.selected_commit"))
            errors.extend(_staging_ids(item.get("staging_ids"), f"{location}.staging_ids"))
            errors.extend(_sha_or_null(item.get("atlas_commit"), f"{location}.atlas_commit"))
            reason = item.get("reason")
            errors.extend(_reason_errors(reason, f"{location}.reason"))
            if state in {"blocked", "skipped"} and not _nonempty_string(reason):
                errors.append(f"{location}.reason is required for state {state}")
            if state == "staged":
                if item.get("selected_commit") is None:
                    errors.append(f"{location}.selected_commit is required for state staged")
                if not isinstance(item.get("staging_ids"), list) or not item["staging_ids"]:
                    errors.append(f"{location}.staging_ids is required for state staged")
                if item.get("atlas_commit") is None:
                    errors.append(f"{location}.atlas_commit is required for state staged")

    pilot = value.get("pilot")
    if not isinstance(pilot, dict):
        errors.append("pilot must be an object")
    else:
        errors.extend(_exact_keys(pilot, required={"item_ids", "confirmed"}, location="pilot"))
        raw_pilot_ids = pilot.get("item_ids")
        if not isinstance(raw_pilot_ids, list):
            errors.append("pilot.item_ids must be a list")
            pilot_ids: list[object] = []
        else:
            pilot_ids = raw_pilot_ids
        seen_pilot: set[str] = set()
        for index, item_id in enumerate(pilot_ids):
            if not isinstance(item_id, str) or SLUG_RE.fullmatch(item_id) is None:
                errors.append(f"pilot.item_ids[{index}] must be a lowercase slug")
            elif item_id in seen_pilot:
                errors.append(f"pilot.item_ids contains duplicate item_id {item_id}")
            else:
                seen_pilot.add(item_id)
                if item_id not in item_ids:
                    errors.append(f"pilot.item_ids must reference a campaign item: {item_id}")
        if not isinstance(pilot.get("confirmed"), bool):
            errors.append("pilot.confirmed must be a boolean")
        elif pilot["confirmed"]:
            if not pilot_ids:
                errors.append("a confirmed pilot must contain at least one item")
            for item_id in pilot_ids:
                if isinstance(item_id, str) and item_states.get(item_id) not in TERMINAL_STATES:
                    errors.append(f"confirmed pilot item {item_id} must be terminal")

    active_trial = value.get("active_trial")
    if active_trial is not None:
        if not isinstance(active_trial, dict):
            errors.append("active_trial must be an object or null")
        else:
            errors.extend(
                _exact_keys(
                    active_trial,
                    required={"archetype", "item_ids"},
                    location="active_trial",
                )
            )
            archetype = active_trial.get("archetype")
            if not isinstance(archetype, str) or SLUG_RE.fullmatch(archetype) is None:
                errors.append("active_trial.archetype must be a lowercase slug")
            raw_trial_ids = active_trial.get("item_ids")
            if not isinstance(raw_trial_ids, list):
                errors.append("active_trial.item_ids must be a list")
                trial_ids: list[object] = []
            else:
                trial_ids = raw_trial_ids
                if not trial_ids:
                    errors.append("active_trial.item_ids must contain at least one item")
            seen_trial: set[str] = set()
            for index, item_id in enumerate(trial_ids):
                if not isinstance(item_id, str) or SLUG_RE.fullmatch(item_id) is None:
                    errors.append(f"active_trial.item_ids[{index}] must be a lowercase slug")
                elif item_id in seen_trial:
                    errors.append(
                        f"active_trial.item_ids contains duplicate item_id {item_id}"
                    )
                else:
                    seen_trial.add(item_id)
                    if item_id not in item_ids:
                        errors.append(
                            "active_trial.item_ids must reference a campaign item: "
                            f"{item_id}"
                        )
            if value.get("phase") != "paused":
                errors.append("active_trial is allowed only while phase is paused")
            if not isinstance(pilot, dict) or pilot.get("confirmed") is not True:
                errors.append("active_trial requires a confirmed pilot")

    if value.get("phase") == "rollout" and not isinstance(pilot, dict) or (
        value.get("phase") == "rollout" and pilot.get("confirmed") is not True
    ):
        errors.append("rollout requires a confirmed pilot")
    if value.get("phase") == "complete":
        nonterminal = sorted(
            item_id for item_id, state in item_states.items() if state not in TERMINAL_STATES
        )
        if nonterminal:
            errors.append("complete requires every item to be staged, already-covered or skipped")
    return errors


def _canonical(value: dict) -> dict:
    campaign = deepcopy(value)
    if isinstance(campaign.get("sources"), list):
        campaign["sources"] = sorted(
            campaign["sources"], key=lambda item: item.get("source_key", "") if isinstance(item, dict) else ""
        )
    if isinstance(campaign.get("items"), list):
        for item in campaign["items"]:
            if isinstance(item, dict):
                for field in ("traits", "staging_ids"):
                    if isinstance(item.get(field), list):
                        item[field] = sorted(item[field])
                routing_hints = item.get("routing_hints")
                if isinstance(routing_hints, dict):
                    for field in ("atlas_ids", "product_roots"):
                        if isinstance(routing_hints.get(field), list):
                            routing_hints[field] = sorted(routing_hints[field])
        campaign["items"] = sorted(
            campaign["items"], key=lambda item: item.get("item_id", "") if isinstance(item, dict) else ""
        )
    pilot = campaign.get("pilot")
    if isinstance(pilot, dict) and isinstance(pilot.get("item_ids"), list):
        pilot["item_ids"] = sorted(pilot["item_ids"])
    active_trial = campaign.get("active_trial")
    if isinstance(active_trial, dict) and isinstance(active_trial.get("item_ids"), list):
        active_trial["item_ids"] = sorted(active_trial["item_ids"])
    return campaign


def stable_campaign_bytes(value: object) -> bytes:
    """Return the canonical, deterministic on-disk representation."""

    canonical = _canonical(value) if isinstance(value, dict) else value
    return (json.dumps(canonical, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _validate_filename(path: Path, value: dict) -> None:
    campaign_id = value.get("campaign_id")
    if isinstance(campaign_id, str) and path.name != f"{campaign_id}.json":
        raise CampaignError("campaign filename must be <campaign_id>.json")


def load_campaign(path: str | Path) -> dict:
    path = Path(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise CampaignError(f"cannot read campaign: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise CampaignError(f"invalid campaign JSON: {exc}") from exc
    errors = validate_campaign(value)
    if errors:
        raise CampaignError("; ".join(errors))
    _validate_filename(path, value)
    return value


def campaign_digest(path: str | Path) -> str | None:
    path = Path(path)
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise CampaignError(f"cannot read campaign for digest: {exc}") from exc
    return hashlib.sha256(data).hexdigest()


def _identity_map(items: object) -> dict[str, tuple[object, object]]:
    if not isinstance(items, list):
        return {}
    return {
        item["item_id"]: (
            item.get("source_key"),
            _canonical_repository_root(item.get("repository_root")),
        )
        for item in items
        if isinstance(item, dict) and isinstance(item.get("item_id"), str)
    }


def validate_campaign_transition(previous: dict, current: dict) -> list[str]:
    """Validate the immutable identity and safe-state rules of an update."""

    previous = _canonical(previous)
    current = _canonical(current)
    errors: list[str] = []
    if previous.get("campaign_id") != current.get("campaign_id"):
        errors.append("campaign identity is immutable")
    if previous.get("phase") == "complete" and previous != current:
        errors.append("a complete campaign cannot change")

    previous_phase = previous.get("phase")
    current_phase = current.get("phase")
    previous_pilot = previous.get("pilot")
    current_pilot = current.get("pilot")
    previous_trial = previous.get("active_trial")
    current_trial = current.get("active_trial")
    current_confirmed = (
        current_pilot.get("confirmed") is True if isinstance(current_pilot, dict) else False
    )
    if previous_phase == "pilot" and current_phase not in {"pilot", "paused", "rollout"}:
        errors.append("pilot campaign may only transition to pilot, paused or rollout")
    elif previous_phase == "rollout" and current_phase not in {"rollout", "paused", "complete"}:
        errors.append("rollout campaign may only transition to rollout, paused or complete")
    elif previous_phase == "paused":
        allowed = {"paused", "rollout", "complete"} if current_confirmed else {"paused", "pilot"}
        if current_phase not in allowed:
            confirmation = "confirmed" if current_confirmed else "unconfirmed"
            article = "a" if current_confirmed else "an"
            destinations = (
                "paused, rollout or complete" if current_confirmed else "paused or pilot"
            )
            errors.append(
                f"paused campaign with {article} {confirmation} pilot may only transition to {destinations}"
            )

    if isinstance(previous_trial, dict):
        if isinstance(current_trial, dict) and previous_trial != current_trial:
            errors.append("active trial selection and archetype are immutable while active")
        elif current_trial is None:
            current_states = {
                item.get("item_id"): item.get("state")
                for item in current.get("items", [])
                if isinstance(item, dict) and isinstance(item.get("item_id"), str)
            }
            selected = previous_trial.get("item_ids")
            if not isinstance(selected, list) or any(
                current_states.get(item_id) not in TERMINAL_STATES for item_id in selected
            ):
                errors.append(
                    "active trial cannot be cleared until every selected item is terminal"
                )
            elif current_phase not in {"rollout", "complete"}:
                errors.append(
                    "active trial must be cleared in the same update that resumes rollout "
                    "or completes the campaign"
                )
            elif current_phase == "complete" and any(
                state not in TERMINAL_STATES for state in current_states.values()
            ):
                errors.append(
                    "active trial may enter complete only when every campaign item is terminal"
                )
    elif isinstance(current_trial, dict):
        if (
            previous_phase != "rollout"
            or not isinstance(previous_pilot, dict)
            or previous_pilot.get("confirmed") is not True
        ):
            errors.append(
                "a new active trial requires the previous campaign to be in rollout "
                "with a confirmed pilot"
            )
        previous_states = {
            item.get("item_id"): item.get("state")
            for item in previous.get("items", [])
            if isinstance(item, dict) and isinstance(item.get("item_id"), str)
        }
        selected = current_trial.get("item_ids")
        if not isinstance(selected, list) or any(
            previous_states.get(item_id) != "queued" for item_id in selected
        ):
            errors.append("a new active trial may select only previously queued items")

    previous_sources = {
        source.get("source_key"): source
        for source in previous.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("source_key"), str)
    }
    current_sources = {
        source.get("source_key"): source
        for source in current.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("source_key"), str)
    }
    if set(previous_sources) != set(current_sources):
        errors.append("campaign source-key set is immutable")
    for source_key, source in previous_sources.items():
        if current_sources.get(source_key) != source:
            errors.append(f"source identity {source_key} is immutable")

    previous_items = {
        item.get("item_id"): item
        for item in previous.get("items", [])
        if isinstance(item, dict) and isinstance(item.get("item_id"), str)
    }
    current_items = {
        item.get("item_id"): item
        for item in current.get("items", [])
        if isinstance(item, dict) and isinstance(item.get("item_id"), str)
    }
    if set(previous_items) != set(current_items):
        errors.append("campaign item-ID set is immutable")
    previous_identities = _identity_map(previous.get("items"))
    current_identities = _identity_map(current.get("items"))
    for item_id, identity in previous_identities.items():
        if current_identities.get(item_id) != identity:
            errors.append(f"item identity {item_id} is immutable")
            continue
        old_item = previous_items[item_id]
        new_item = current_items[item_id]
        old_state = old_item.get("state")
        new_state = new_item.get("state")
        if old_state in TERMINAL_STATES and old_item != new_item:
            errors.append(f"terminal item {item_id} cannot change")
        elif old_state == "queued" and new_state not in {"queued", "blocked", *TERMINAL_STATES}:
            errors.append(f"queued item {item_id} may only become blocked or terminal")
        elif old_state == "blocked" and new_state not in {"blocked", "queued", *TERMINAL_STATES}:
            errors.append(f"blocked item {item_id} may only return to queued or become terminal")

    if isinstance(previous_pilot, dict) and isinstance(current_pilot, dict):
        if previous_pilot.get("confirmed") is True and current_pilot.get("confirmed") is not True:
            errors.append("a confirmed pilot cannot be unconfirmed")
        if (
            previous_pilot.get("confirmed") is True
            and previous_pilot.get("item_ids") != current_pilot.get("item_ids")
        ):
            errors.append("confirmed pilot item_ids are immutable")
    return errors


def write_campaign_atomic(path: str | Path, value: dict, *, expected_digest: str | None) -> str:
    """Validate and atomically replace a campaign only if its digest still matches."""

    path = Path(path)
    errors = validate_campaign(value)
    if errors:
        raise CampaignError("; ".join(errors))
    _validate_filename(path, value)
    if expected_digest is not None and re.fullmatch(r"[0-9a-f]{64}", expected_digest) is None:
        raise CampaignError("expected digest must be a lowercase SHA-256 digest or explicit missing state")
    data = stable_campaign_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(f".{path.name}.lock")
    try:
        lock_handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise CampaignConflictError(f"campaign update is already locked by another writer: {lock.name}") from exc
    except OSError as exc:
        raise CampaignError(f"cannot acquire campaign update lock: {exc}") from exc
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
            raise CampaignError(f"cannot read existing campaign: {exc}") from exc
        current_digest = hashlib.sha256(current_bytes).hexdigest() if current_bytes is not None else None
        if current_digest != expected_digest:
            expected = expected_digest or "missing"
            actual = current_digest or "missing"
            raise CampaignConflictError(f"campaign changed concurrently: expected {expected}, found {actual}")
        if current_bytes is not None:
            try:
                previous = json.loads(current_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise CampaignError(f"existing campaign is invalid JSON: {exc}") from exc
            previous_errors = validate_campaign(previous)
            if previous_errors:
                raise CampaignError("existing campaign is invalid: " + "; ".join(previous_errors))
            _validate_filename(path, previous)
            transition_errors = validate_campaign_transition(previous, value)
            if transition_errors:
                raise CampaignError("invalid campaign transition: " + "; ".join(transition_errors))
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
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

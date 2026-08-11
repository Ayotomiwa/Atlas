from __future__ import annotations

from pathlib import Path
from copy import deepcopy
import json

import pytest

from scripts.atlas_intake import main
from scripts.lib.intake import (
    CheckpointConflictError,
    IntakeError,
    checkpoint_digest,
    load_checkpoint,
    validate_change_source,
    validate_checkpoint,
    write_checkpoint_atomic,
)


FROM_COMMIT = "1" * 40
THROUGH_COMMIT = "a" * 40
NEXT_COMMIT = "b" * 40
STAGING_ID = "STG-20260811-merged-change"


def _checkpoint() -> dict:
    return {
        "schema_version": "atlas-intake/1.0",
        "source": {
            "key": "datalens-monorepo",
            "locator": "https://example.invalid/datalens.git",
            "default_branch": "main",
        },
        "observed_through": {"commit": THROUGH_COMMIT, "merge_request": "1420"},
        "considered_through": {"commit": THROUGH_COMMIT, "merge_request": "1420"},
        "last_run": {
            "from_exclusive": FROM_COMMIT,
            "through_inclusive": THROUGH_COMMIT,
            "dispositions": [
                {
                    "change_key": "mr:1420",
                    "commit": THROUGH_COMMIT,
                    "merge_request": "1420",
                    "outcome": "staged",
                    "staging_ids": [STAGING_ID],
                }
            ],
        },
        "unresolved": [],
        "updated_at": "2026-08-11T12:30:00+01:00",
        "updated_by": "Fixture Curator",
    }


def _next_checkpoint() -> dict:
    checkpoint = _checkpoint()
    checkpoint["observed_through"] = {"commit": NEXT_COMMIT, "merge_request": None}
    checkpoint["considered_through"] = {"commit": NEXT_COMMIT, "merge_request": None}
    checkpoint["last_run"] = {
        "from_exclusive": THROUGH_COMMIT,
        "through_inclusive": NEXT_COMMIT,
        "dispositions": [
            {
                "change_key": f"commit:{NEXT_COMMIT}",
                "commit": NEXT_COMMIT,
                "merge_request": None,
                "outcome": "no-stage",
                "staging_ids": [],
                "reason": "The change contains no reusable Atlas context.",
            }
        ],
    }
    checkpoint["updated_at"] = "2026-08-11T13:00:00+01:00"
    return checkpoint


def test_checkpoint_and_change_source_contracts():
    assert validate_checkpoint(_checkpoint()) == []
    change_source = {
        "source_key": "datalens-monorepo",
        "branch": "main",
        "commit_range": {
            "from_exclusive": FROM_COMMIT,
            "through_inclusive": THROUGH_COMMIT,
        },
        "merge_requests": [{"id": "1420", "merged_commit": THROUGH_COMMIT}],
    }
    assert validate_change_source(change_source, required=True) == []

    direct_commit = {
        **change_source,
        "commit_range": {"from_exclusive": None, "through_inclusive": "b" * 64},
        "merge_requests": [],
    }
    assert validate_change_source(direct_commit, required=True) == []

    change_source["merge_requests"].append(
        {"id": "1420", "merged_commit": THROUGH_COMMIT.upper()}
    )
    errors = validate_change_source(change_source, required=True)
    assert any("duplicate id 1420" in item for item in errors)
    assert any("lowercase hexadecimal commit" in item for item in errors)


def test_unassessed_blocks_considered_cursor_and_requires_unresolved_reason():
    checkpoint = _checkpoint()
    checkpoint["observed_through"]["merge_request"] = None
    checkpoint["last_run"]["dispositions"] = [
        {
            "change_key": "commit:pending",
            "commit": THROUGH_COMMIT,
            "merge_request": None,
            "outcome": "unassessed",
            "staging_ids": [],
            "reason": "The changed source boundary is ambiguous.",
        }
    ]
    checkpoint["considered_through"] = {"commit": FROM_COMMIT, "merge_request": None}
    checkpoint["unresolved"] = [
        {
            "change_key": "commit:pending",
            "commit": THROUGH_COMMIT,
            "merge_request": None,
            "reason": "The changed source boundary is ambiguous.",
            "staging_ids": [],
        }
    ]
    assert validate_checkpoint(checkpoint) == []

    checkpoint["unresolved"][0]["commit"] = NEXT_COMMIT
    errors = validate_checkpoint(checkpoint)
    assert any("matching commit, merge request and staging IDs" in item for item in errors)

    initial = deepcopy(checkpoint)
    initial["last_run"]["from_exclusive"] = None
    initial["considered_through"] = {"commit": None, "merge_request": None}
    initial["unresolved"][0]["commit"] = THROUGH_COMMIT
    assert validate_checkpoint(initial) == []


def test_non_empty_checkpoint_range_requires_a_disposition():
    checkpoint = _checkpoint()
    checkpoint["last_run"]["dispositions"] = []
    errors = validate_checkpoint(checkpoint)
    assert any("non-empty last_run range" in item for item in errors)


def test_checkpoint_cursor_merge_request_matches_endpoint_disposition():
    checkpoint = _checkpoint()
    checkpoint["observed_through"]["merge_request"] = "9999"
    checkpoint["considered_through"]["merge_request"] = "9999"

    errors = validate_checkpoint(checkpoint)

    assert any("observed_through.merge_request" in item for item in errors)
    assert any("considered_through.merge_request" in item for item in errors)


def test_non_empty_checkpoint_range_has_endpoint_disposition():
    checkpoint = _checkpoint()
    checkpoint["last_run"]["dispositions"][0]["commit"] = FROM_COMMIT

    errors = validate_checkpoint(checkpoint)

    assert any("must end with a disposition" in item for item in errors)


def test_deferred_disposition_requires_exact_unresolved_provenance_and_staging_ids():
    checkpoint = _checkpoint()
    checkpoint["last_run"]["dispositions"][0].update(
        {
            "outcome": "deferred",
            "reason": "Consumer verification is incomplete.",
        }
    )
    checkpoint["unresolved"] = [
        {
            "change_key": "mr:1420",
            "commit": THROUGH_COMMIT,
            "merge_request": "1420",
            "reason": "Consumer verification is incomplete.",
            "staging_ids": [],
        }
    ]
    errors = validate_checkpoint(checkpoint)
    assert any("matching commit, merge request and staging IDs" in item for item in errors)


@pytest.mark.parametrize(
    "locator",
    [
        "https://example.invalid/group/repository.git",
        "ssh://git@example.invalid/group/repository.git",
        "git@example.invalid:group/repository.git",
        "example.invalid:group/repository.git",
    ],
)
def test_checkpoint_accepts_credential_free_git_locators(locator: str):
    checkpoint = _checkpoint()
    checkpoint["source"]["locator"] = locator
    assert validate_checkpoint(checkpoint) == []


@pytest.mark.parametrize(
    "locator",
    [
        "https://user:token@example.invalid/repository.git",
        "https://token@example.invalid/repository.git",
        "https://example.invalid/repository.git?access_token=value",
        "https://example.invalid/repository.git#credential",
        "ssh://git:password@example.invalid/group/repository.git",
        "https://[invalid/repository.git",
        "user:password@example.invalid/repository.git",
        "file:///srv/repository",
        "/srv/repository",
        r"C:\Users\engineer\repository",
    ],
)
def test_checkpoint_rejects_credentials_and_machine_local_locators(locator: str):
    checkpoint = _checkpoint()
    checkpoint["source"]["locator"] = locator
    assert any("source.locator" in item for item in validate_checkpoint(checkpoint))


def test_atomic_checkpoint_write_uses_digest_and_exclusive_lock(tmp_path: Path):
    path = tmp_path / "_intake/checkpoints/datalens-monorepo.json"
    first_digest = write_checkpoint_atomic(path, _checkpoint(), expected_digest=None)
    assert first_digest == checkpoint_digest(path)
    assert load_checkpoint(path) == _checkpoint()

    changed = _next_checkpoint()
    lock = path.with_name(f".{path.name}.lock")
    lock.write_text("other writer", encoding="utf-8")
    with pytest.raises(CheckpointConflictError, match="already locked"):
        write_checkpoint_atomic(path, changed, expected_digest=first_digest)
    assert load_checkpoint(path) == _checkpoint()
    lock.unlink()

    with pytest.raises(CheckpointConflictError, match="expected 0{64}"):
        write_checkpoint_atomic(path, changed, expected_digest="0" * 64)
    assert not lock.exists()

    second_digest = write_checkpoint_atomic(path, changed, expected_digest=first_digest)
    assert second_digest != first_digest
    assert load_checkpoint(path)["updated_at"] == changed["updated_at"]


def test_checkpoint_transition_preserves_source_cursor_and_unresolved_work(tmp_path: Path):
    path = tmp_path / "_intake/checkpoints/datalens-monorepo.json"
    previous = _checkpoint()
    previous["last_run"]["dispositions"][0].update(
        {
            "outcome": "deferred",
            "reason": "Consumer verification is incomplete.",
        }
    )
    previous["unresolved"] = [
        {
            "change_key": "mr:1420",
            "commit": THROUGH_COMMIT,
            "merge_request": "1420",
            "reason": "Consumer verification is incomplete.",
            "staging_ids": [STAGING_ID],
        }
    ]
    digest = write_checkpoint_atomic(path, previous, expected_digest=None)

    changed_source = _next_checkpoint()
    changed_source["source"]["default_branch"] = "master"
    with pytest.raises(IntakeError, match="source key, locator and default branch are immutable"):
        write_checkpoint_atomic(path, changed_source, expected_digest=digest)

    wrong_base = _next_checkpoint()
    wrong_base["last_run"]["from_exclusive"] = FROM_COMMIT
    with pytest.raises(IntakeError, match="previous considered_through"):
        write_checkpoint_atomic(path, wrong_base, expected_digest=digest)

    changed_cursor_identity = _next_checkpoint()
    changed_cursor_identity["observed_through"] = {
        "commit": NEXT_COMMIT,
        "merge_request": "1421",
    }
    changed_cursor_identity["considered_through"] = {
        "commit": THROUGH_COMMIT,
        "merge_request": "different-mr",
    }
    changed_cursor_identity["last_run"]["dispositions"] = [
        {
            "change_key": "mr:1421",
            "commit": NEXT_COMMIT,
            "merge_request": "1421",
            "outcome": "unassessed",
            "staging_ids": [],
            "reason": "The changed source boundary is ambiguous.",
        }
    ]
    changed_cursor_identity["unresolved"] = [
        *previous["unresolved"],
        {
            "change_key": "mr:1421",
            "commit": NEXT_COMMIT,
            "merge_request": "1421",
            "reason": "The changed source boundary is ambiguous.",
            "staging_ids": [],
        },
    ]
    with pytest.raises(IntakeError, match="complete previous cursor"):
        write_checkpoint_atomic(path, changed_cursor_identity, expected_digest=digest)

    dropped = _next_checkpoint()
    with pytest.raises(IntakeError, match="cannot disappear"):
        write_checkpoint_atomic(path, dropped, expected_digest=digest)

    resolved = _next_checkpoint()
    resolved["last_run"]["dispositions"].insert(
        0,
        {
            "change_key": "mr:1420",
            "commit": THROUGH_COMMIT,
            "merge_request": "1420",
            "outcome": "already-represented",
            "staging_ids": [STAGING_ID],
        },
    )
    assert write_checkpoint_atomic(path, resolved, expected_digest=digest)


def test_intake_cli_show_and_compare_and_swap_write(tmp_path: Path, capsys):
    input_path = tmp_path / "next.json"
    input_path.write_text(json.dumps(_checkpoint()), encoding="utf-8")

    assert main(["--root", str(tmp_path), "--format", "json", "show", "datalens-monorepo"]) == 0
    missing = json.loads(capsys.readouterr().out)
    assert missing["exists"] is False
    assert missing["digest"] is None

    assert main([
        "--root",
        str(tmp_path),
        "--format",
        "json",
        "write",
        "--checkpoint",
        "datalens-monorepo",
        "--input",
        str(input_path),
        "--expected-digest",
        "missing",
    ]) == 0
    written = json.loads(capsys.readouterr().out)
    assert written["written"] is True

    assert main(["--root", str(tmp_path), "--format", "json", "show", "datalens-monorepo"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["exists"] is True
    assert shown["digest"] == written["digest"]
    assert shown["data"] == _checkpoint()

    assert main([
        "--root",
        str(tmp_path),
        "write",
        "--checkpoint",
        "datalens-monorepo",
        "--input",
        str(input_path),
        "--expected-digest",
        "missing",
    ]) == 2
    assert "changed concurrently" in capsys.readouterr().err

    assert main([
        "--root",
        str(tmp_path),
        "show",
        "_intake/checkpoints/nested/datalens-monorepo.json",
    ]) == 1
    assert "direct child" in capsys.readouterr().err

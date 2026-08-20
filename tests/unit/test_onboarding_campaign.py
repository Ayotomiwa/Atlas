from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts.atlas_onboarding_campaign import main
from scripts.lib.onboarding_campaign import (
    CampaignConflictError,
    CampaignError,
    campaign_digest,
    load_campaign,
    stable_campaign_bytes,
    validate_campaign,
    validate_campaign_transition,
    write_campaign_atomic,
)


SELECTED_COMMIT = "a" * 40
ATLAS_COMMIT = "b" * 40
STAGING_ID = "STG-20260820-infrastructure-pilot"


def _campaign() -> dict:
    return {
        "schema_version": "atlas-onboarding-campaign/1.0",
        "campaign_id": "infrastructure-portfolio",
        "title": "Infrastructure portfolio onboarding",
        "phase": "pilot",
        "updated_at": "2026-08-20T12:30:00+01:00",
        "updated_by": "Atlas Curator",
        "pilot": {"item_ids": ["networking"], "confirmed": False},
        "active_trial": None,
        "sources": [
            {
                "source_key": "infrastructure-monorepo",
                "locator": "https://example.invalid/platform/infrastructure.git",
                "default_branch": "main",
            }
        ],
        "items": [
            {
                "item_id": "networking",
                "source_key": "infrastructure-monorepo",
                "repository_root": "terraform/networking",
                "archetype": "terraform-module",
                "traits": ["networking", "terraform"],
                "routing_hints": {
                    "atlas_ids": ["infrastructure.networking"],
                    "product_roots": ["platform/networking"],
                },
                "state": "queued",
                "selected_commit": None,
                "staging_ids": [],
                "atlas_commit": None,
                "reason": None,
            },
            {
                "item_id": "service-mesh",
                "source_key": "infrastructure-monorepo",
                "repository_root": "kubernetes/service-mesh",
                "archetype": "kubernetes-platform",
                "traits": ["kubernetes"],
                "routing_hints": {
                    "atlas_ids": ["infrastructure.platform"],
                    "product_roots": ["platform/service-mesh"],
                },
                "state": "blocked",
                "selected_commit": None,
                "staging_ids": [],
                "atlas_commit": None,
                "reason": "The owner has not confirmed the source boundary.",
            },
        ],
    }


def _staged_campaign() -> dict:
    campaign = _campaign()
    campaign["items"][0].update(
        {
            "state": "staged",
            "selected_commit": SELECTED_COMMIT,
            "staging_ids": [STAGING_ID],
            "atlas_commit": ATLAS_COMMIT,
            "reason": "Pilot evidence was captured.",
        }
    )
    campaign["pilot"]["confirmed"] = True
    return campaign


def test_campaign_contract_accepts_credential_free_sources_and_canonicalizes_bytes():
    campaign = _campaign()

    assert validate_campaign(campaign) == []
    reordered = deepcopy(campaign)
    reordered["sources"] = list(reversed(reordered["sources"]))
    reordered["items"] = list(reversed(reordered["items"]))
    reordered["items"][0]["traits"] = list(reversed(reordered["items"][0]["traits"]))
    reordered["items"][0]["routing_hints"]["atlas_ids"] = list(
        reversed(reordered["items"][0]["routing_hints"]["atlas_ids"])
    )
    assert stable_campaign_bytes(reordered) == stable_campaign_bytes(campaign)


def test_campaign_contract_rejects_disallowed_operational_and_local_fields():
    campaign = _campaign()
    campaign["items"][0]["worker"] = "session-123"
    campaign["items"][0]["repository_root"] = r"C:\\Users\\engineer\\checkout"
    campaign["sources"][0]["locator"] = "https://user:token@example.invalid/repository.git"

    errors = validate_campaign(campaign)

    assert any("unsupported fields: worker" in error for error in errors)
    assert any("repository_root" in error for error in errors)
    assert any("locator" in error for error in errors)


def test_campaign_requires_compact_auditable_metadata_and_operational_routing_hints():
    campaign = _campaign()
    del campaign["title"]
    campaign["updated_at"] = "2026-08-20T12:30:00"
    campaign["updated_by"] = ""
    campaign["items"][0]["archetype"] = "Terraform module"
    campaign["items"][0]["traits"] = ["terraform", "Networking"]
    campaign["items"][0]["routing_hints"] = {
        "atlas_ids": ["not-a-stable-id"],
        "product_roots": ["platform/./networking"],
    }
    campaign["items"][1]["reason"] = "x" * 281 + "\nnot operational"

    errors = validate_campaign(campaign)

    assert any("campaign is missing: title" in error for error in errors)
    assert any("updated_at" in error for error in errors)
    assert any("updated_by" in error for error in errors)
    assert any("archetype must be a lowercase slug" in error for error in errors)
    assert any("traits[1] must be a lowercase slug" in error for error in errors)
    assert any("routing_hints.atlas_ids[0]" in error for error in errors)
    assert any("routing_hints.product_roots[0]" in error for error in errors)
    assert any("reason must be a compact single-line" in error for error in errors)


@pytest.mark.parametrize(
    ("root", "canonical_root"),
    [
        ("terraform/./networking", "terraform/networking"),
        ("terraform//networking", "terraform/networking"),
        ("terraform/networking/", "terraform/networking"),
        (r"terraform\\networking", "terraform/networking"),
        ("terraform/../networking", "networking"),
        ("/terraform/networking", "/terraform/networking"),
    ],
)
def test_campaign_rejects_noncanonical_repository_roots_and_uses_canonical_identity(
    root: str, canonical_root: str
):
    campaign = _campaign()
    campaign["items"][0]["repository_root"] = root
    campaign["items"][1]["repository_root"] = canonical_root
    campaign["items"][1]["source_key"] = "infrastructure-monorepo"

    errors = validate_campaign(campaign)

    assert any("items[0].repository_root" in error for error in errors)
    assert any("duplicate (source_key, repository_root)" in error for error in errors)


def test_campaign_accepts_only_dot_as_repository_root_and_checks_product_roots():
    campaign = _campaign()
    campaign["items"][0]["repository_root"] = "."
    campaign["items"][0]["routing_hints"]["product_roots"] = ["."]
    assert validate_campaign(campaign) == []

    campaign["items"][0]["routing_hints"]["product_roots"] = ["platform//networking"]
    assert any("routing_hints.product_roots[0]" in error for error in validate_campaign(campaign))


def test_campaign_contract_validates_ids_references_and_terminal_data():
    campaign = _campaign()
    campaign["items"][0]["item_id"] = "Not a slug"
    campaign["items"][1]["source_key"] = "missing-source"
    campaign["pilot"]["item_ids"] = ["missing-item", "missing-item"]
    campaign["items"][1].update(
        {
            "state": "staged",
            "selected_commit": "A" * 40,
            "staging_ids": ["bad-id"],
            "atlas_commit": "invalid",
        }
    )

    errors = validate_campaign(campaign)

    assert any("item_id must be a lowercase slug" in error for error in errors)
    assert any("source_key must reference a campaign source" in error for error in errors)
    assert any("pilot.item_ids contains duplicate" in error for error in errors)
    assert any("pilot.item_ids must reference" in error for error in errors)
    assert any("lowercase hexadecimal commit" in error for error in errors)
    assert any("valid staging ID" in error for error in errors)


def test_staged_item_requires_selected_commit_staging_ids_and_atlas_commit():
    campaign = _campaign()
    campaign["items"][0].update(
        {
            "state": "staged",
            "selected_commit": SELECTED_COMMIT,
            "staging_ids": [STAGING_ID],
            "atlas_commit": None,
        }
    )

    errors = validate_campaign(campaign)

    assert any("items[0].atlas_commit is required for state staged" in error for error in errors)


def test_phase_rules_require_terminal_confirmed_pilot_and_terminal_completion():
    campaign = _campaign()
    campaign["phase"] = "rollout"
    assert any("rollout requires a confirmed pilot" in error for error in validate_campaign(campaign))

    campaign = _staged_campaign()
    campaign["phase"] = "rollout"
    assert validate_campaign(campaign) == []
    campaign["phase"] = "complete"
    assert any("complete requires every item" in error for error in validate_campaign(campaign))
    campaign["items"][1]["state"] = "skipped"
    assert validate_campaign(campaign) == []


def test_active_trial_is_a_paused_nonempty_referenced_selection():
    campaign = _staged_campaign()
    campaign["phase"] = "paused"
    campaign["active_trial"] = {
        "archetype": "shared-control-plane",
        "item_ids": ["service-mesh"],
    }

    assert validate_campaign(campaign) == []

    campaign["phase"] = "rollout"
    assert any(
        "active_trial is allowed only while phase is paused" in error
        for error in validate_campaign(campaign)
    )

    campaign["phase"] = "paused"
    campaign["active_trial"]["item_ids"] = []
    assert any(
        "active_trial.item_ids must contain at least one item" in error
        for error in validate_campaign(campaign)
    )

    campaign["active_trial"]["item_ids"] = ["missing", "missing"]
    errors = validate_campaign(campaign)
    assert any("active_trial.item_ids contains duplicate" in error for error in errors)
    assert any("active_trial.item_ids must reference" in error for error in errors)

    campaign["active_trial"] = {"archetype": "Shared shape", "item_ids": ["service-mesh"]}
    assert any(
        "active_trial.archetype must be a lowercase slug" in error
        for error in validate_campaign(campaign)
    )

    missing = _campaign()
    del missing["active_trial"]
    assert any("campaign is missing: active_trial" in error for error in validate_campaign(missing))

    unconfirmed = _campaign()
    unconfirmed["phase"] = "paused"
    unconfirmed["active_trial"] = {
        "archetype": "shared-control-plane",
        "item_ids": ["service-mesh"],
    }
    assert any(
        "active_trial requires a confirmed pilot" in error
        for error in validate_campaign(unconfirmed)
    )


def test_active_trial_transition_is_immutable_until_selected_items_are_terminal():
    rollout = _staged_campaign()
    rollout["phase"] = "rollout"
    rollout["items"][1].update({"state": "queued", "reason": None})
    trial = deepcopy(rollout)
    trial["phase"] = "paused"
    trial["active_trial"] = {
        "archetype": "shared-control-plane",
        "item_ids": ["service-mesh"],
    }
    assert validate_campaign_transition(rollout, trial) == []

    changed = deepcopy(trial)
    changed["active_trial"]["archetype"] = "different-shape"
    assert any(
        "active trial selection and archetype are immutable" in error
        for error in validate_campaign_transition(trial, changed)
    )

    premature = deepcopy(trial)
    premature["phase"] = "rollout"
    premature["active_trial"] = None
    assert any(
        "active trial cannot be cleared until every selected item is terminal" in error
        for error in validate_campaign_transition(trial, premature)
    )

    terminal_trial = deepcopy(trial)
    terminal_trial["items"][1].update(
        {
            "state": "skipped",
            "reason": "The user explicitly excluded this product boundary.",
        }
    )
    cleared_but_paused = deepcopy(terminal_trial)
    cleared_but_paused["active_trial"] = None
    assert any(
        "same update that resumes rollout" in error
        for error in validate_campaign_transition(terminal_trial, cleared_but_paused)
    )

    completed = deepcopy(terminal_trial)
    completed["phase"] = "rollout"
    completed["active_trial"] = None
    assert validate_campaign(completed) == []
    assert validate_campaign_transition(terminal_trial, completed) == []

    campaign_complete = deepcopy(terminal_trial)
    campaign_complete["phase"] = "complete"
    campaign_complete["active_trial"] = None
    assert validate_campaign(campaign_complete) == []
    assert validate_campaign_transition(terminal_trial, campaign_complete) == []


def test_active_trial_creation_selects_only_previously_queued_items():
    rollout = _staged_campaign()
    rollout["phase"] = "rollout"
    trial = deepcopy(rollout)
    trial["phase"] = "paused"
    trial["active_trial"] = {
        "archetype": "shared-control-plane",
        "item_ids": ["service-mesh"],
    }

    assert any(
        "new active trial may select only previously queued items" in error
        for error in validate_campaign_transition(rollout, trial)
    )

    rollout["items"][1].update({"state": "queued", "reason": None})
    trial["items"][1].update({"state": "queued", "reason": None})
    assert validate_campaign_transition(rollout, trial) == []

    paused = deepcopy(rollout)
    paused["phase"] = "paused"
    paused_trial = deepcopy(paused)
    paused_trial["active_trial"] = deepcopy(trial["active_trial"])
    assert any(
        "previous campaign to be in rollout with a confirmed pilot" in error
        for error in validate_campaign_transition(paused, paused_trial)
    )


def test_campaign_transition_phase_machine_and_confirmed_pilot_membership():
    pilot = _campaign()
    blocked_phase = deepcopy(pilot)
    blocked_phase["phase"] = "complete"
    assert any("pilot campaign may only transition" in error for error in validate_campaign_transition(pilot, blocked_phase))

    paused_unconfirmed = deepcopy(pilot)
    paused_unconfirmed["phase"] = "paused"
    assert validate_campaign_transition(pilot, paused_unconfirmed) == []
    assert validate_campaign_transition(paused_unconfirmed, pilot) == []
    rollout_from_unconfirmed_pause = deepcopy(paused_unconfirmed)
    rollout_from_unconfirmed_pause["phase"] = "rollout"
    assert any("paused campaign with an unconfirmed pilot" in error for error in validate_campaign_transition(paused_unconfirmed, rollout_from_unconfirmed_pause))

    confirmed_pause = _staged_campaign()
    confirmed_pause["phase"] = "paused"
    confirmed_rollout = deepcopy(confirmed_pause)
    confirmed_rollout["phase"] = "rollout"
    assert validate_campaign_transition(confirmed_pause, confirmed_rollout) == []
    confirmed_pilot = deepcopy(confirmed_pause)
    confirmed_pilot["phase"] = "pilot"
    assert any("paused campaign with a confirmed pilot" in error for error in validate_campaign_transition(confirmed_pause, confirmed_pilot))

    changed_membership = deepcopy(confirmed_pause)
    changed_membership["items"][1]["state"] = "skipped"
    changed_membership["pilot"]["item_ids"] = ["service-mesh"]
    assert any("confirmed pilot item_ids are immutable" in error for error in validate_campaign_transition(confirmed_pause, changed_membership))


def test_campaign_transition_rejects_inventory_expansion_after_first_write():
    previous = _campaign()

    added_source = deepcopy(previous)
    added_source["sources"].append(
        {
            "source_key": "second-source",
            "locator": "https://example.invalid/platform/second.git",
            "default_branch": "main",
        }
    )
    assert validate_campaign(added_source) == []
    assert any(
        "source-key set is immutable" in error
        for error in validate_campaign_transition(previous, added_source)
    )

    added_item = deepcopy(previous)
    extra = deepcopy(added_item["items"][0])
    extra.update(
        {
            "item_id": "observability",
            "repository_root": "terraform/observability",
            "routing_hints": {"atlas_ids": [], "product_roots": []},
        }
    )
    added_item["items"].append(extra)
    assert validate_campaign(added_item) == []
    assert any(
        "item-ID set is immutable" in error
        for error in validate_campaign_transition(previous, added_item)
    )


def test_atomic_write_requires_digest_and_preserves_identities_and_transitions(tmp_path: Path):
    path = tmp_path / "_intake/onboarding/infrastructure-portfolio.json"
    original = _campaign()
    first_digest = write_campaign_atomic(path, original, expected_digest=None)
    assert first_digest == campaign_digest(path)
    assert load_campaign(path) == original

    lock = path.with_name(f".{path.name}.lock")
    lock.write_text("other writer", encoding="utf-8")
    with pytest.raises(CampaignConflictError, match="already locked"):
        write_campaign_atomic(path, _staged_campaign(), expected_digest=first_digest)
    lock.unlink()

    with pytest.raises(CampaignConflictError, match="expected 0{64}"):
        write_campaign_atomic(path, _staged_campaign(), expected_digest="0" * 64)

    moved_item = _staged_campaign()
    moved_item["items"][0]["repository_root"] = "terraform/other"
    with pytest.raises(CampaignError, match="item identity"):
        write_campaign_atomic(path, moved_item, expected_digest=first_digest)

    staged_digest = write_campaign_atomic(path, _staged_campaign(), expected_digest=first_digest)
    wrong_transition = _staged_campaign()
    wrong_transition["items"][0].update(
        {
            "state": "queued",
            "selected_commit": None,
            "staging_ids": [],
            "atlas_commit": None,
            "reason": None,
        }
    )
    wrong_transition["pilot"]["confirmed"] = False
    with pytest.raises(CampaignError, match="terminal item networking cannot change"):
        write_campaign_atomic(path, wrong_transition, expected_digest=staged_digest)

    changed_terminal = _staged_campaign()
    changed_terminal["items"][0]["reason"] = "A different reason"
    with pytest.raises(CampaignError, match="terminal item networking cannot change"):
        write_campaign_atomic(path, changed_terminal, expected_digest=staged_digest)


def test_campaign_cli_shows_deterministic_filtered_items_and_writes(tmp_path: Path, capsys):
    input_path = tmp_path / "campaign.json"
    input_path.write_text(json.dumps(_campaign()), encoding="utf-8")

    assert main(["--root", str(tmp_path), "--format", "json", "show", "infrastructure-portfolio"]) == 0
    missing = json.loads(capsys.readouterr().out)
    assert missing["exists"] is False

    assert main([
        "--root", str(tmp_path), "write", "--campaign", "infrastructure-portfolio",
        "--input", str(input_path), "--expected-digest", "missing",
    ]) == 0
    written = capsys.readouterr().out
    assert "Wrote campaign" in written
    assert "Previous digest" not in written

    assert main([
        "--root", str(tmp_path), "show", "infrastructure-portfolio", "--status", "blocked",
        "--limit", "1",
    ]) == 0
    shown = capsys.readouterr().out
    assert "Phase: pilot" in shown
    assert "Counts: blocked=1, queued=1" in shown
    assert "service-mesh" in shown
    assert "networking" not in shown

    assert main([
        "--root", str(tmp_path), "show", "_intake/onboarding/nested/infrastructure-portfolio.json",
    ]) == 1
    assert "direct child" in capsys.readouterr().err

# `_intake/` — shared operational progress

`_intake/` holds shared, mutable progress for source processing. Change checkpoints record how far Atlas has **observed and considered** a default branch. Infrastructure onboarding campaigns record which confirmed product boundaries have reached committed staging evidence. Both prevent repeated work and expose unresolved items; neither is staging evidence, curated knowledge, or semantic authority.

## Infrastructure onboarding campaigns

Store one campaign at `_intake/onboarding/<campaign-id>.json`. A campaign coordinates a confirmed infrastructure inventory through a representative pilot and bounded rollout batches. It does not contain source findings and does not replace repository onboarding: every item is still analysed and staged through `atlas-onboard-repository` and `atlas-repo-analyst`.

Use the controller through a natural request such as “Onboard this infrastructure portfolio” or the explicit `atlas-onboard-infra-portfolio` skill. Inspect and update state only through the helper:

```text
python scripts/atlas_onboarding_campaign.py --format json show <campaign-id>
python scripts/atlas_onboarding_campaign.py --format json show <campaign-id> --status blocked --limit 10
python scripts/atlas_onboarding_campaign.py --format json write --campaign <campaign-id> --input <assembled-json> --expected-digest <sha256-or-missing>
```

The `atlas-onboarding-campaign/1.0` document stores credential-free sources, confirmed logical roots, campaign-local sampling traits, pilot membership, active-trial state, item state, selected source commits, resulting staging IDs and Atlas commits, and compact blocker/reason metadata. The required `active_trial` field is normally `null`; while `phase: paused` it may identify one evidenced archetype and a non-empty immutable selection of campaign item IDs. It can be cleared only after every selected item is terminal, in the same compare-and-swap update that resumes rollout or completes an otherwise terminal campaign. The field is operational routing state, not an engineering claim. The document never stores local checkout paths, source content, engineering findings, worker leases, session IDs, or `in-progress` state.

Items are `queued`, `blocked`, `staged`, `already-covered`, or `skipped`; phases are `pilot`, `rollout`, `paused`, or `complete`. A stopped session does not continue in the background. Resume reconciles committed staging provenance before retrying, and compare-and-swap protects every update from silent concurrent overwrite. Completion means each item is `staged` with committed evidence recorded, `already-covered` by adequate existing evidence, or explicitly `skipped` with a reason. The controller never curates, clones, pushes, merges, or publishes; authority remains the separate curation and human-review path.

Campaign writes hold a sibling lock across digest comparison and atomic replacement. A campaign lock left by an interrupted process may be removed only after verifying that no writer is active; never delete it merely to bypass a live conflict. Reload the campaign and reconcile its digest after stale-lock recovery.

## Checkpoints

Store one checkpoint per source at `checkpoints/<source-key>.json`; nested checkpoint folders are not allowed. The source key is a stable lowercase slug chosen for the physical Git repository, not a URL or a repository path. The locator must use credential-free HTTPS, SSH or scp-style Git syntax. It must not contain URL user credentials, query parameters, fragments, or a machine-local absolute path. Checkpoints use `schema_version: atlas-intake/1.0` and contain:

- a credential-free source locator and default branch;
- the latest default-branch commit observed;
- the latest contiguous commit considered;
- a compact summary of the last inspected range and its dispositions;
- unresolved deferred or unassessed changes;
- updater and timezone-qualified update time.

Example shape:

```json
{
  "schema_version": "atlas-intake/1.0",
  "source": {
    "key": "datalens-monorepo",
    "locator": "https://example.invalid/datalens.git",
    "default_branch": "main"
  },
  "observed_through": {
    "commit": "89abcdef0123456789abcdef0123456789abcdef",
    "merge_request": "1420"
  },
  "considered_through": {
    "commit": "89abcdef0123456789abcdef0123456789abcdef",
    "merge_request": "1420"
  },
  "last_run": {
    "from_exclusive": "0123456789abcdef0123456789abcdef01234567",
    "through_inclusive": "89abcdef0123456789abcdef0123456789abcdef",
    "dispositions": [
      {
        "change_key": "mr:1420",
        "commit": "89abcdef0123456789abcdef0123456789abcdef",
        "merge_request": "1420",
        "outcome": "staged",
        "staging_ids": ["STG-20260811-example-change"]
      }
    ]
  },
  "unresolved": [],
  "updated_at": "2026-08-11T12:30:00+01:00",
  "updated_by": "Engineer name"
}
```

Allowed dispositions are `staged`, `no-stage`, `already-represented`, `deferred`, and `unassessed`. Every non-empty inspected range has at least one disposition. A `no-stage`, `deferred`, or `unassessed` disposition must explain why. Deferred and unassessed changes remain in `unresolved` with exactly matching change key, commit, merge request and staging IDs. An `unassessed` outcome leaves `considered_through.commit` equal to `last_run.from_exclusive`; both may be `null` only for an uncompleted first range. `consumed` is not an intake disposition: it is derived later from the referenced staging record's lifecycle.

## Cursor rules

- The first scan requires an explicit base commit, a locally provable merged-MR commit, or the exact future-intake anchor recorded by approved full repository onboarding evidence. Verify the anchor against this source's history; never guess a historical cursor. Onboarding itself does not create or advance the checkpoint.
- `observed_through` records what the fetch exposed, even if assessment could not finish.
- Advance `considered_through` only across a contiguous range whose relevant changes have a recorded disposition. `deferred` may advance it while retaining an unresolved item; `unassessed` may not.
- Stop and request a rebaseline when the stored cursor is no longer an ancestor, history was rewritten, or the source/range is ambiguous. Git ancestry is checked by the change-staging workflow, not Atlas lint.
- A checkpoint may reference only one unambiguous existing `staging.change` ID with the same source key, branch, inclusive commit and matching MR/merge-commit provenance. The staging files remain immutable; later `consumed` state is read from their frontmatter.

## Safe updates and recovery

Inspect a checkpoint and obtain its digest:

```text
python scripts/atlas_intake.py --root . --format json show datalens-monorepo
```

Write a fully assembled checkpoint using the returned digest, or `missing` for the first write:

```text
python scripts/atlas_intake.py --root . --format json write --checkpoint datalens-monorepo --input checkpoint.json --expected-digest <sha256-or-missing>
```

The helper validates the document, holds an exclusive sibling lock across the digest comparison and atomic replace, and rejects concurrent changes. On updates it also keeps source identity and the default branch immutable, requires the next range to start at the previous considered cursor, and prevents unresolved work from disappearing unless a current `staged`, `no-stage`, or `already-represented` disposition explicitly resolves the same change. A lock left by an interrupted process must be removed only after confirming no writer is active. If staging succeeded but the checkpoint update failed, the next run must detect the existing staging evidence and classify the change as `already-represented` rather than duplicating it.

Checkpoint recovery and history come from Git. Do not store credentials, tokens, private URL user-info, source contents, or semantic engineering claims here.

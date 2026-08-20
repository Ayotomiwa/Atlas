# Infrastructure portfolio campaign workflow

Use this reference for every campaign mode. Campaign data is resumable operational state, not engineering evidence.

## State access

Read the current document and compare-and-swap digest before making a decision:

```text
python <ATLAS_ROOT>/scripts/atlas_onboarding_campaign.py --root <ATLAS_ROOT> --format json show <campaign-id>
```

Assemble the complete next JSON document in an operating-system temporary file, then write it only through:

```text
python <ATLAS_ROOT>/scripts/atlas_onboarding_campaign.py --root <ATLAS_ROOT> --format json write --campaign <campaign-id> --input <temporary-json> --expected-digest <sha256-or-missing>
```

The helper validates structure, canonical ordering and state transitions. It does not choose product boundaries, archetypes, evidence meaning, or pilot membership. A CAS conflict means another state won: stop, reload, reconcile, and present any changed scope before asking for another write approval.

Do not persist local checkout paths, source contents, semantic findings, leases, worker/session IDs, or an `in-progress` state. The only item states are `queued`, `blocked`, `staged`, `already-covered`, and `skipped`.

## Prepare

Accept either:

- an explicit CSV or JSON inventory; or
- direct children of one explicitly named directory level.

Directory enumeration is not recursive. A child name is only a candidate boundary until the user confirms it. Do not infer nested products from Terraform modules, folders, application links, or naming patterns.

Normalize the inventory into credential-free sources plus confirmed items. Each source has a lowercase `source_key`, locator and default branch. Each item has a stable campaign-local ID, source key, repository-relative `repository_root`, campaign-local archetype/traits, optional routing hints, and `state: queued`. Reject duplicate `(source_key, repository_root)` boundaries. Keep application repository/component hints non-authoritative.

Show one persistence preview with the full normalized inventory, excluded candidates, source assumptions, campaign path, proposed pilot, selected feature branch, and exact path/scope planned for the local commit. Do not predict a commit SHA. Only after approval write `_intake/onboarding/<campaign-id>.json` with `phase: pilot` and commit that exact path on the selected feature branch.

## Choose and complete the pilot

Choose three pilot items by default; use fewer only when the inventory is smaller. Expand above three, up to six, only when three cannot represent the materially distinct shapes. Prefer a small set that spans materially different:

- source topology, such as standalone roots and monorepo projects;
- IaC families and deployment shapes;
- application relationship shapes, such as one app, several apps, shared infrastructure, or no known app.

Include one shared, ambiguous, or high-risk item when the inventory contains one. These are campaign-local sampling traits, not Atlas taxonomy or architectural claims.

Process pilot items with the same item workflow used in rollout. Once every pilot item is terminal, show what the pilot established, what remains uncertain, and whether the proposed rollout assumptions still hold. Set `pilot.confirmed: true` and enter `phase: rollout` only after the user confirms proceeding. This is a new operational-state decision, not a repeated approval for the already committed pilot evidence.

If rollout later exposes a genuinely new archetype, pause normal batch selection. State the repository evidence and analyst finding that show which material shape the confirmed pilot did not cover. Keep the original confirmed pilot membership unchanged, select a small queued trial that represents the new shape, and store only its operational identity as `active_trial: {archetype, item_ids}` while `phase: paused`. Process that immutable selection while the campaign remains paused. After every selected item is terminal and the user accepts the result, clear `active_trial` in the same CAS update that resumes rollout (or completes an otherwise terminal campaign).

## Run one batch

Rollout selects up to five eligible queued items in stable campaign order. A pilot batch uses its confirmed proposed members. Before source inspection, disclose the exact items and boundaries selected.

For each item, apply the existing `atlas-onboard-repository` contract:

1. Freeze the immutable source commit and exact logical boundary.
2. Delegate evidence inspection to `atlas-repo-analyst`. At most three read-only analyses may run concurrently; give each only its item boundary and permitted explicit references.
3. Reconcile the returned packets without inventing cross-item meaning. Missing application coverage becomes a candidate/open question and is never recursively queued.
4. Ask one consolidated clarification round for the batch.

Prepare one combined staging preview. It must identify each item, selected commit, proposed records/paths and provenance, evidence limits, unresolved decisions, exclusions, planned staging commits, and campaign updates. Obtain one approval for that exact batch. Pass the campaign ID, item ID, campaign digest, exact boundary/commit, verified analyst packet, approved item slice and approval into `atlas-onboard-repository`.

After approval, serialize every mutation:

1. Run one item handoff. Repository onboarding reverifies the boundary, commit and files; semantically stages the unchanged item slice; tags every record with `onboarding_source: {campaign_id, item_id}`; validates; and creates its exact local staging commit.
2. Receive the selected commit, staging IDs and Atlas staging commit. Reload the campaign and its digest, reconcile the returned provenance, update the item to `staged`, and use one CAS write. Validate and commit the exact campaign path.
3. Continue with the next approved item only after the prior staging and campaign commits succeed.

An evidence-backed existing baseline may produce `already-covered`. Use `blocked` with a compact reason when a safe decision needs information; it can return to `queued`. Use `skipped` only for an explicitly excluded boundary with a reason. Do not change a terminal item.

## Resume, status and pause

`status` is read-only. Show phase, counts, pilot state, any active trial's archetype and selected item IDs, blocked reasons, next eligible items and the latest digest without claiming that queued work is being processed.

Before `run` or `resume`, search staging for `onboarding_source` matching this campaign. If committed records exist while the item is still `queued` or `blocked`, verify their item boundary, source commit and local Atlas commit. Reconcile a complete match to `staged` before retrying. Preserve ambiguity and stop on conflicting or partial matches. Interrupted analysis has no durable worker state and leaves the item `queued`.

`pause` previews and approves only the campaign phase/update metadata, writes through CAS, validates, and commits the exact campaign path. It does not cancel a process in the background because no background process exists. Resume reloads the committed queue in a later session.

Set `phase: complete` only when every item is terminal. Completion means the item is `staged` with curation-ready evidence committed and recorded, `already-covered` by adequate existing evidence, or explicitly `skipped` with a reason. The controller never curates, clones, pushes, merges, approves, or publishes Atlas knowledge.

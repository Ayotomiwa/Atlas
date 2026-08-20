# Infrastructure portfolio campaign workflow

Campaign state is resumable operational data, not engineering evidence. Read it with `python <ATLAS_ROOT>/scripts/atlas_onboarding_campaign.py --root <ATLAS_ROOT> --format json show <campaign-id>`. Assemble the next complete document in an operating-system temporary file and write it with `write --campaign <campaign-id> --input <file> --expected-digest <sha256-or-missing>`. A CAS conflict stops the write and requires reload/reconciliation.

## Prepare

Accept CSV or JSON, or enumerate direct children of one explicitly named directory level. Never recurse or treat a directory name as proof of a product boundary. Normalize credential-free sources and confirmed logical roots, reject duplicate `(source_key, repository_root)` identities, and keep local checkout paths and source content out of campaign state. Campaign-local archetype/traits and application routing hints aid sampling only; they are not Atlas claims.

Preview the full inventory, exclusions, proposed pilot, campaign path, selected feature branch, and exact path/scope planned for the local commit. Do not predict a commit SHA. After approval, create the `pilot` campaign through CAS and commit the exact path.

## Pilot and rollout

Choose three pilot items by default. Expand above three, up to six, only when three cannot represent the materially distinct source-topology, IaC-family and application-relationship shapes; include one shared, ambiguous or high-risk item where present. Once pilot items are terminal, show their outcome and require confirmation before `rollout`.

A genuinely new archetype pauses normal rollout for a small queued trial. State the repository evidence and analyst finding that show which material shape the confirmed pilot did not cover. Do not mutate the original confirmed pilot membership. Store only the trial's operational identity as `active_trial: {archetype, item_ids}` while paused; its selection stays immutable until all selected items are terminal. After the user accepts the trial outcome, clear it in the same CAS update that resumes rollout (or completes an otherwise terminal campaign).

Rollout selects a batch of five queued items in stable order. Freeze each exact source commit and have `atlas-repo-analyst` inspect only that boundary; at most three read-only inspections run concurrently. Reconcile packets, ask one consolidated clarification round, and show one combined staging preview. One approval covers the unchanged item slices and planned campaign updates.

Serialize mutations. Pass campaign/item IDs, digest, boundary/commit, verified analyst packet, approved slice and approval into `atlas-onboard-repository`. It reverifies, stages semantically, adds `onboarding_source`, validates and commits. Then reload the campaign, reconcile the returned selected commit/staging IDs/Atlas commit, CAS-update that item to `staged`, validate and commit the campaign path before the next item.

Use `already-covered` only with adequate existing evidence, `blocked` for a resolvable stop, and `skipped` for an explicit exclusion. Missing application coverage remains an open question or routing candidate; never recursively enqueue an application repository.

## Resume, status and pause

`status` is read-only and includes any active trial's archetype and selected item IDs. `pause` previews/approves and commits only the phase update. Before `run` or `resume`, reconcile staging records whose `onboarding_source` matches a queued or blocked item; a complete committed match becomes `staged`, while conflicting/partial matches stop. Interrupted analysis leaves the item `queued`; no worker or `in-progress` state is persisted.

Set `complete` only when every item is `staged` with committed evidence recorded, `already-covered` by adequate existing evidence, or explicitly `skipped` with a reason. A stopped session does not continue in the background. The controller never clones, curates, pushes, merges, approves or publishes; staged evidence becomes authority only through separate curation and human-controlled publication.

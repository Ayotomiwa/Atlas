---
name: atlas-stage-changes
description: Inspect merged default-branch changes since a shared Atlas intake checkpoint, determine which changes contain reusable Datalens engineering context, and stage approved evidence without curating it. Use when asked to process new monorepo MRs or commits, catch Atlas up with main, or determine what merged changes have already been considered.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-stage-changes

Read `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `../_shared/agent-handoffs.md`, `_intake/README.md`, `_staging/README.md`, `_staging/changes/README.md`, `_staging/changes/_template.md`, and `references/workflow.md`.

1. Resolve `ATLAS_ROOT`, the physical product Git root, the most-specific available Atlas repository context, source key, remote and default branch. Preserve missing, ambiguous and `not-verified` routing; no context match does not prove the source is irrelevant.
2. Load the shared checkpoint and its digest through `scripts/atlas_intake.py`. Fetch the remote default branch. If refresh fails, disclose that remote completeness is unknown and do not advance the shared checkpoint.
3. On first use, require an explicit `--base <commit>` or a locally provable merged-MR commit. Never guess the initial cursor. Verify ancestry before assessing a range.
4. Inspect first-parent merges and direct commits from the exclusive cursor through the fetched tip. Use MR identity from local Git metadata or explicit user confirmation tied to the relevant default-branch commit; label the latter `user-confirmed`. Never require an external MR API.
5. Compare the range with all staging change provenance, route changed paths through resolved or explicitly ambiguous repository context and relevant Atlas records, then delegate substantial interpretation to `atlas-change-analyst`.
6. Reconcile every logical change as `staged`, `no-stage`, `already-represented`, `deferred`, or `unassessed`. Ask one consolidated material clarification round and show the proposed staging/checkpoint changes before writing.
7. Only after explicit approval, create one immutable-by-policy `staging.change` record per coherent reusable change, splitting only independent boundaries. Include required `change_source` provenance; flag sensitive paths without opening their contents or copying values.
8. Run Atlas lint. Record the fetched tip as observed and advance the considered cursor only when every change has an advancing outcome (`staged`, `no-stage`, `already-represented`, or `deferred`). Perform one compare-and-swap through `scripts/atlas_intake.py`, then lint again. A concurrent checkpoint change, rewritten history, or source ambiguity stops the checkpoint update; unreadable evidence or `unassessed` preserves the observed/considered distinction without deleting staged evidence.
9. Report dispositions, created records, unresolved items, checkpoint movement, validation, evidence references and material file hops. If staging succeeded but checkpoint update failed, say that the next run must detect the records as `already-represented`.

Never curate, edit existing committed staging evidence beyond lifecycle status, hand-edit generated files or checkpoint JSON, commit, push, merge, approve, or claim that an unrefreshed local ref is the remote default-branch tip.

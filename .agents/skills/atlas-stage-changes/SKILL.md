---
name: atlas-stage-changes
description: Inspect merged default-branch changes since a shared Atlas intake checkpoint, determine which changes contain reusable Datalens engineering context, and stage approved evidence without curating it. Use when asked to process new monorepo MRs or commits, catch Atlas up with main, or determine what merged changes have already been considered.
---

# atlas-stage-changes

Read the shared runtime/provenance/handoff references, `_intake/README.md`, staging root/change policy and `references/workflow.md`.

1. Resolve Atlas, product Git root, most-specific available repository context, source key, remote and default branch; preserve missing, ambiguous and `not-verified` routing.
2. Read the checkpoint and digest through `scripts/atlas_intake.py`, fetch the remote default branch, and verify ancestry. On first use require an explicit base or locally provable merged-MR commit. Never guess a cursor or advance from an unrefreshed ref.
3. Inspect first-parent merges and direct commits, using MR identity from local Git metadata or explicit user confirmation tied to the relevant default-branch commit. Label user-supplied identity `user-confirmed`, compare structured provenance across all staging changes, route changed paths through Atlas, and delegate substantial interpretation to `atlas-change-analyst`.
4. Reconcile every logical change as `staged`, `no-stage`, `already-represented`, `deferred` or `unassessed`. Ask one consolidated clarification round and preview staging plus checkpoint effects.
5. After explicit approval, write coherent `staging.change` records with required `change_source`; lint, compare-and-swap the observed tip and eligible considered cursor through the helper, then lint again. Deferred items remain unresolved and any unassessed/concurrent/ambiguous/re-written range blocks considered advancement.
6. Report dispositions, evidence, staged pages, unresolved items, cursor movement, validation and material file hops.

Never curate, hand-edit generated files/checkpoints, revise committed staging evidence, use an external MR API, commit, push, merge, approve or claim remote completeness after refresh failure.

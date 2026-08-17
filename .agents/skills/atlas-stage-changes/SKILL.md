---
name: atlas-stage-changes
description: Inspect merged default-branch changes since a shared Atlas intake checkpoint, determine which changes contain reusable Datalens engineering context, and stage approved evidence without curating it. Use when asked to process new monorepo MRs or commits, catch Atlas up with main, or determine what merged changes have already been considered.
---

# atlas-stage-changes

Read shared human-intent/persistence/runtime/provenance/handoff, curation-safety and clear-writing references, `_intake/README.md`, staging root/change policy/index and `references/workflow.md`. This is incremental **Sync Atlas**.

1. Resolve Atlas, product Git root and repository context. If adequate full-baseline coverage does not exist, route to repository onboarding instead of asking the user to choose. Preserve missing, ambiguous and `not-verified` routing.
2. Read the checkpoint/digest, fetch the default branch and verify ancestry. On first use accept an explicit base, locally provable merged-MR commit or exact future-intake anchor from approved onboarding evidence. Never guess or advance from an unrefreshed ref.
3. Inspect first-parent merges and direct commits, using MR identity from local Git metadata or explicit user confirmation tied to the relevant default-branch commit. Label user-supplied identity `user-confirmed`, compare structured provenance across all staging changes, route changed paths through Atlas, and delegate substantial interpretation to `atlas-change-analyst`.
4. Reconcile internal dispositions, but present plain-language groups: new evidence, already covered, no durable impact, needs human information and could not safely assess. Ask one consolidated clarification round.
5. Show one persistence preview covering exact staging files and checkpoint compare-and-swap. After approval, complete the shared taxonomy/contract and destination-contract reads, write coherent `staging.change` records with the clear-writing contract, lint, update the eligible cursor through the helper, lint again, and commit the exact evidence plus checkpoint atomically. Deferred items remain unresolved and unassessed/concurrent/ambiguous/rewritten ranges block advancement.
6. Report branch/commit, dispositions, evidence, staged pages, unresolved items, cursor movement, validation and material file hops.

Never curate, hand-edit generated files/checkpoints, revise committed staging evidence, use an external MR API, push, merge, force-update, approve or claim remote completeness after refresh failure.

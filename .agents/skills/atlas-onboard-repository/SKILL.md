---
name: atlas-onboard-repository
description: Establish a full curation-ready Datalens Atlas baseline for one logical repository boundary from an immutable selected source snapshot, without curating it.
---

# atlas-onboard-repository

Read shared human-intent/persistence/runtime/provenance/handoff and curation-safety references, `references/full-baseline.md`, the clarification checklist, staging root policy/index and every potentially relevant bucket contract. This is full-baseline **Sync Atlas**.

1. Establish one logical boundary and check existing coverage. Route adequate existing coverage plus an incremental request to `atlas-stage-changes`; preserve ambiguity and `not-verified` context.
2. Prepare the exact immutable source snapshot. No explicit revision permits only clean current `HEAD`; otherwise require the exact commit. Never alter the active checkout. Preserve selected/default commits, merge base and relationship.
3. Delegate coordination to `atlas-repo-analyst`. Assess every full-baseline lens; use one analyst for a small boundary or split material lenses behind a coordinator for a large boundary. Reconcile before preview.
4. Follow explicit shared/infra references only; report sibling products as follow-ups. Exclude irrelevant VCS/dependency/generated/build/vendor/large-data content. Give every lens an evidence state and stopping reason.
5. Ask one consolidated blocking clarification round and offer other gaps as confirm-or-correct; skipped non-blocking gaps remain unknown.
6. Prepare one repository/component discovery record plus independent curation-ready flow/infra/schema/operations/governance records when justified. Include exact anchors and a causal walkthrough per component; never placeholders or folder-shaped components.
7. Immediately before preview, clean up through the snapshot helper so it verifies the selected commit and clean state. A mismatch invalidates the analysis; never force cleanup.
8. Show one batch preview including exclusions, unresolved lenses, source snapshot and future intake anchor. After one approval, complete the shared taxonomy/contract and destination-contract reads, then write the unchanged batch without repeated handoff approval. Do not advance `_intake/`.
9. Validate and report plain-language outcomes plus the full evidence matrix/scan manifest as audit detail.

An infra-only folder normally produces infra evidence; a component needs an independently addressable behavior boundary.

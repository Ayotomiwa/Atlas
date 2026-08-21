---
name: atlas-onboard-repository
description: Establish a full curation-ready Datalens Atlas baseline for one logical repository boundary from an immutable selected source snapshot, without curating it.
---

# atlas-onboard-repository

Read shared human-intent/persistence/runtime/provenance/handoff, curation-safety and clear-writing references, `references/full-baseline.md`, the clarification checklist, staging root policy/index and every potentially relevant bucket contract. This is full-baseline **Sync Atlas**.

1. Establish one logical boundary and check existing coverage. Route adequate existing coverage plus an incremental request to `atlas-stage-changes`; preserve ambiguity and `not-verified` context.
2. Prepare the exact immutable source snapshot. No explicit revision permits only clean current `HEAD`; otherwise require the exact commit. Never alter the active checkout. Preserve selected/default commits, merge base and relationship.
3. Delegate coordination to `atlas-repo-analyst`. Require breadth discovery followed by targeted architecture depth over the same immutable snapshot. The breadth packet identifies candidate and rejected boundaries, coverage and a depth plan. The depth phase inspects only material sources and returns one reconciled analyst packet. Use one analyst for a small boundary or split material lenses behind a coordinator for a large boundary.
4. Follow explicit shared/infra references only; report sibling products as follow-ups. Exclude irrelevant VCS/dependency/generated/build/vendor/large-data content. Give every lens an evidence state and stopping reason.
5. Apply the curation-readiness gate. Every proposed component needs an architecture capsule covering purpose and independent boundary, entrypoint or trigger, causal path, dependencies and state, infrastructure interactions, durable outputs or effects, failure or partial-completion behavior, completion signals, exact source anchors, coverage limits and stopping reason. If a known source route could materially change the proposal, return the exact gap for targeted depth on the same snapshot. Do not accept a file inventory as a component explanation.
6. Ask one consolidated blocking clarification round for gaps that the available source cannot resolve and offer other gaps as confirm-or-correct; skipped non-blocking gaps remain unknown.
7. Assess every lens and prepare only independently justified records. An infra-only boundary may use `staging.infra` as its primary record; create repository/component discovery only when independently justified. Draft flow/infra/schema/operations/governance records with the clear-writing contract. Lead with per-component architecture capsules and use topology tables as supporting evidence; never create placeholders, folder-shaped components or a new onboarding type.
8. Immediately before preview, clean up through the snapshot helper so it verifies the selected commit and clean state. A mismatch invalidates the analysis; never force cleanup.
9. Show one batch preview including exclusions, unresolved lenses, source snapshot and future intake anchor. After one approval, complete the shared taxonomy/contract and destination-contract reads, then write the unchanged batch without repeated handoff approval. Do not advance `_intake/`.
10. Validate, create one exact-path local commit for the approved staging batch, and report branch/commit plus the evidence matrix, targeted depth plan, architecture capsules and full scan manifest as audit detail.

## Portfolio-controller handoff

Accept a handoff only with campaign/item IDs plus digest, exact logical boundary and selected source commit, verified analyst packet and exact approved item slice. Reverify commit, boundary and files before reuse; any change returns to the controller for reanalysis/re-preview. For an unchanged packet, do not repeat analysis, clarification or approval. This skill still stages semantically, validates and commits; tag every produced record with `onboarding_source`, then return staging IDs and commit so the controller can CAS-update campaign state. Flag missing app coverage; never recursively queue it. Standalone onboarding is unchanged.

An infra-only folder normally produces infra evidence; a component needs an independently addressable behavior boundary.

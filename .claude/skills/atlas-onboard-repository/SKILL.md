---
name: atlas-onboard-repository
description: Establish a full curation-ready Datalens Atlas baseline for one logical repository boundary from an immutable selected source snapshot, without curating it.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-onboard-repository

Read `../_shared/human-intents.md`, `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `../_shared/agent-handoffs.md`, `references/full-baseline.md`, `references/clarification-checklist.md`, `_staging/README.md`, and all potentially relevant staging bucket contracts. This is the full-baseline **Sync Atlas** workflow and stages evidence only.

1. Establish one logical source boundary, its physical Git root/remote, candidate `repository_root`, enclosing boundary, included paths, exclusions and user-supplied references. Use typed repository/component `find` plus `context` to identify existing coverage; preserve ambiguity and `not-verified` status. If adequate baseline coverage exists and the request is incremental, route internally to `atlas-stage-changes`.
2. Freeze the exact source state with `python <ATLAS_ROOT>/scripts/atlas_source_snapshot.py prepare`. With no explicit revision, accept only a clean current `HEAD`; otherwise require the user to identify the commit. Never alter the active checkout. Preserve selected/default commits, merge base and branch relationship for evidence and future intake anchoring.
3. Always delegate coordination to `atlas-repo-analyst`. Assess every full-baseline lens in `references/full-baseline.md`; one analyst may handle a small boundary, while a large boundary may split independent material lenses among read-only specialists. Reconcile their evidence before previewing it.
4. Follow only explicit references into shared or infrastructure paths. Do not recursively onboard sibling products. Exclude VCS internals, environments, dependencies, generated output, large data, samples, binaries and vendor trees unless directly relevant. Every lens receives an evidence state and stopping reason.
5. Ask one consolidated clarification round for material boundary/domain/component identity/ownership/publication/safety gaps. Present other uncertainties as an optional confirm-or-correct list; skipped non-blocking gaps remain unknown.
6. Build a curation-ready batch: one `staging.component` repository/component discovery record plus separate flow, infrastructure, schema, runbook, incident, standard or concept records whenever each has an independently evidenced reusable boundary. Include a per-component causal walkthrough and precise source anchors. Never create placeholders or folder-shaped components.
7. Immediately before preview, clean up through the snapshot helper so it verifies the selected commit and clean state. A mismatch invalidates the analysis and requires a new snapshot; never force cleanup.
8. Show one batch preview under the shared approval contract, including exclusions, unresolved lenses, selected source snapshot and future intake anchor. Only after approval write the unchanged batch; internal staging handoffs do not re-request approval. Do not create or advance an `_intake/` checkpoint during onboarding.
9. Run permitted validation.
10. Use the shared completion summary and include staged records, evidence matrix, full scan manifest, exclusions, inaccessible references, stopping reasons and validation as audit detail.

An infrastructure-only folder normally becomes infrastructure evidence, not a redundant repository candidate. A component requires an independently addressable runtime/reusable boundary; a folder or job group alone is insufficient.

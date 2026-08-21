# Full repository baseline

Onboarding must make later curation possible without another broad product-repository scan. It does not need to prove that every lens contains a reusable record.

## Immutable source selection

Use `python <ATLAS_ROOT>/scripts/atlas_source_snapshot.py prepare --repository <path> [--commit <revision>] [--default-ref <ref>] --format json` before analysis.

- Without a revision, only the exact clean current `HEAD` is acceptable.
- If the checkout is dirty or the requested state is ambiguous, ask for the exact commit. Never stash, reset, clean, switch or otherwise disturb the active checkout.
- The helper creates a detached temporary worktree when the selected commit cannot safely be read in place.
- Record the selected commit, default-ref commit, merge base and relationship in staging evidence.
- An unmerged branch is valid evidence when explicitly selected. Its branch commit is the knowledge snapshot; its merge base is the future change-intake anchor. Do not call the branch merged.
- Immediately before presenting the staging preview, cleanup through the helper. Cleanup verifies that the selected commit and cleanliness still match. A mismatch invalidates the analysis; reselect and reinspect rather than staging. If cleanup reports a dirty temporary worktree, leave it and report its path.
- The temporary manifest is operational state, not evidence. Do not advance `_intake/` during onboarding.

## Required lenses

Assess every lens and assign `confirmed`, `partial`, `unknown`, `inaccessible`, or `not-applicable` with source routes and a stopping reason:

1. logical repository boundary, enclosing source boundary, locator and ownership;
2. primary/related domain evidence;
3. build, test, release and artifact/publication topology;
4. source roots and their responsibilities;
5. independently addressable components and rejected folder/module candidates;
6. per-component entrypoints, causal control flow, inputs, outputs, dependencies, infrastructure, configuration, deployment and failure behavior;
7. end-to-end flows and material handoffs;
8. infrastructure packages/resources and operational actions;
9. schemas/contracts, grain, compatibility and lineage;
10. operations, runbooks, incidents and standards relevance.

Unknown is an honest result. Do not create a component, flow, resource, schema or runbook merely to fill a lens.

## Phase 1: breadth discovery

Inspect the logical boundary broadly enough to identify the important source, configuration, test, deployment and documentation roots; candidate records; rejected folder or module candidates; exclusions; and material gaps. Produce a breadth evidence matrix and a targeted depth plan.

Breadth stops when every required lens has a state and stopping reason, every material root is inspected, excluded with a reason or selected for depth, and the candidate list identifies which source paths can still change a record decision.

## Phase 2: targeted architecture depth

Use the breadth findings to inspect only material candidates and blocking gaps. Reuse the same source snapshot, evidence matrix and claim ledger. Do not begin another broad scan.

For every material component candidate, write an architecture capsule that covers its purpose and independent boundary, entrypoint or trigger, causal processing path, dependencies and state, infrastructure interactions, durable outputs or effects, failure or partial-completion behavior, completion signals, exact source anchors, coverage limits and stopping reason.

Continue only while a known source route could materially change a proposed record, connection, confidence level, coverage statement or deferral decision. When the available source cannot resolve a material gap, ask in the consolidated clarification round or keep the candidate partial, unknown or deferred.

## Adaptive analysis

- Small boundary: one repository analyst may cover all lenses.
- Larger boundary: use a coordinating repository analyst and split material lenses among read-only specialists where parallel inspection reduces delay.
- Reconcile overlaps and contradictions before the user preview. One fact has one narrowest staging home; other records reference it rather than duplicating prose.

## Curation-ready output

Assess every lens, then stage only independently justified evidence. An infra-only boundary may make `staging.infra` the primary record; create a repository/component discovery record only when it has its own independently evidenced reusable boundary. Do not add an onboarding-specific staging type. Add separate flow, schema, runbook, incident, standard or concept records only when each has an independently useful evidenced boundary.

Every staged record must include a readable explanation, precise source paths/anchors, causality rather than file adjacency, coverage limits and unresolved decisions. For every material component candidate, lead with its architecture capsule and use tables as supporting evidence. A component passes the readiness gate only when its capsule supports curation without another broad source scan, or the record explicitly keeps the candidate partial or deferred with a stopping reason. A file inventory is not a component explanation.

The final preview covers the whole coherent staging batch and the future maintenance anchor after snapshot validation/cleanup succeeds. One approval authorises that unchanged batch; downstream staging writes do not ask again.

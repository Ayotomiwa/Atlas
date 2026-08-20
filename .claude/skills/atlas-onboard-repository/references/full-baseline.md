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

## Adaptive analysis

- Small boundary: one repository analyst may cover all lenses.
- Larger boundary: use a coordinating repository analyst and split material lenses among read-only specialists where parallel inspection reduces delay.
- Reconcile overlaps and contradictions before the user preview. One fact has one narrowest staging home; other records reference it rather than duplicating prose.

## Curation-ready output

Assess every lens, then stage only independently justified evidence. An infra-only boundary may make `staging.infra` the primary record; create a repository/component discovery record only when it has its own independently evidenced reusable boundary. Do not add an onboarding-specific staging type. Add separate flow, schema, runbook, incident, standard or concept records only when each has an independently useful evidenced boundary.

Every staged record must include a readable explanation, precise source paths/anchors, causality rather than file adjacency, coverage limits and unresolved decisions. For every candidate component include its own causal walkthrough from entrypoint through material work to output/failure behavior. A file inventory is not a component explanation.

The final preview covers the whole coherent staging batch and the future maintenance anchor after snapshot validation/cleanup succeeds. One approval authorises that unchanged batch; downstream staging writes do not ask again.

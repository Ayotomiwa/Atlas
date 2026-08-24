# Specialist-agent handoffs

The parent skill owns eligibility, routing, selected IDs, source scope, approvals, and final presentation. An analyst works from the supplied objective, selected records, supplied source state—immutable when the owning workflow requires it—and authorised boundary. It does not restart discovery or widen scope merely to make its packet feel complete.

A small direct lookup may stay with the parent only when it concerns one selected record and requires no ambiguity resolution, traversal, source fallback, impact analysis, or history. Delegate when any of those conditions applies.

Give an analyst:

- objective and requested output;
- when source or risk analysis applies, the selected method—`source-analysis`, `change-risk-analysis`, or both—and the exact question each method must answer;
- when source analysis applies, the concrete behavior target, claims needing proof and required stop condition; include entrypoint candidates only when already known and keep them explicitly provisional;
- when change-risk analysis applies, the exact change or failure boundary; include the behavioral delta, safety facts and downstream boundaries only when already known and keep them explicitly provisional;
- absolute Atlas root, product Git root and current path;
- typed find/path-context candidates or exact stable IDs, including `not-verified` state;
- reusable session state: selected stable IDs, curated pages already opened, requested revision or range, resolved full commit or range, product-source paths and their revisions, coverage endpoint, route class, and whether the checkout advisory was disclosed;
- authorised scan boundary, exclusions and fallback limits;
- known user-confirmed facts and unresolved ambiguity;
- validation deferrals and write prohibition where applicable.

Carry the **ephemeral Atlas session** across a handoff. **Reuse** still-valid retained context, selected IDs and opened pages only when repository, revision, question type and required confidence remain compatible. Batch independent Atlas reads of selected records and batch Atlas-located source verification when the missing claims share the same authorised boundary. The analyst uses the handoff-selected records and range rather than re-resolving them. **Re-enter** routing through the parent only when the handoff is incomplete, source state changed, or the work crosses its authorised boundary or recorded coverage endpoint; never restart the whole route by default. Full ordered access events belong only in routing evaluation artifacts.

Every analyst returns:

1. findings in the clearest presentation for the question;
2. a claim ledger with claim, source classification, supporting references, confidence, lifecycle status, direct/inferred state and all premises for inference;
3. material route hops with source, target, natural field/step, confidence and reference;
4. materially consulted paths;
5. checked-but-not-found paths when negative findings depend on them;
6. coverage limits, conflicts, inaccessible context and remaining questions;
7. when selected, the complete result required by `source-analysis.md` or `change-risk-analysis.md`;
8. recommended next routes only when they add value.

The parent skill verifies that references and method artifacts support the exact claims, not only that the summary sounds plausible. A cleared concern requires the traced path or executable evidence that cleared it. The parent preserves the analyst's chosen presentation, adds no unsupported synthesis, and exposes material file hops at the adaptive depth required by the answer. The complete ledger stays internal unless requested or required for an audit artifact.

For a write-capable specialist, also pass the exact persistence preview, the user's approval, permitted files/claims/status effects, required contract reads and exact Git path scope. A staging handoff additionally carries one ephemeral duplicate snapshot: searched staging statuses/buckets, curated types/indexes, relevant file-content fingerprints, qualified question IDs, duplicate records, candidate targets and unresolved ambiguity. Refresh the whole snapshot when any searched surface changed; otherwise recheck exact output-path and selected-target identity immediately before writing. Never persist this snapshot. A curator receives no Git, generation, validation, repair, review or lifecycle ownership: it returns materialized paths and a claim ledger for the parent checkpoint commit and scoped validation. The specialist must not expand scope or ask for approval again; it returns a material change to the parent for a revised preview.

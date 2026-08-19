# Specialist-agent handoffs

Give an analyst:

- objective and requested output;
- absolute Atlas root, product Git root and current path;
- typed find/path-context candidates or exact stable IDs, including `not-verified` state;
- reusable session state: selected stable IDs, curated pages already opened, requested revision or range, resolved full commit or range, product-source paths and their revisions, coverage endpoint, route class, and whether the checkout advisory was disclosed;
- authorised scan boundary, exclusions and fallback limits;
- known user-confirmed facts and unresolved ambiguity;
- validation deferrals and write prohibition where applicable.

Carry the **ephemeral Atlas session** across a handoff. **Reuse** still-valid retained context, selected IDs and opened pages only when repository, revision, question type and required confidence remain compatible. Batch independent Atlas reads of selected records and batch Atlas-located source verification when the missing claims share the same authorised boundary. **Re-enter** routing only for the changed repository, requested revision, record, question type, suspected source state or crossed coverage endpoint; never restart the whole route by default. Full ordered access events belong only in routing evaluation artifacts.

Every analyst returns:

1. findings in the clearest presentation for the question;
2. a claim ledger with claim, source classification, supporting references, confidence, lifecycle status, direct/inferred state and all premises for inference;
3. material route hops with source, target, natural field/step, confidence and reference;
4. materially consulted paths;
5. checked-but-not-found paths when negative findings depend on them;
6. coverage limits, conflicts, inaccessible context and remaining questions;
7. recommended next routes only when they add value.

The parent skill verifies that references support the exact claims, preserves the analyst's chosen presentation, adds no unsupported synthesis, and exposes material file hops at the adaptive depth required by the answer. The complete ledger stays internal unless requested or required for an audit artifact.

For a write-capable specialist, also pass the exact persistence preview, the user's approval, permitted files/claims/status effects, required contract reads and exact Git path scope. A staging handoff additionally carries one ephemeral duplicate snapshot: searched staging statuses/buckets, curated types/indexes, relevant file-content fingerprints, qualified question IDs, duplicate records, candidate targets and unresolved ambiguity. Refresh the whole snapshot when any searched surface changed; otherwise recheck exact output-path and selected-target identity immediately before writing. Never persist this snapshot. A curator receives no Git, generation, validation, repair, review or lifecycle ownership: it returns materialized paths and a claim ledger for the parent checkpoint commit and scoped validation. The specialist must not expand scope or ask for approval again; it returns a material change to the parent for a revised preview.

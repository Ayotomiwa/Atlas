# Specialist-agent handoffs

Give an analyst:

- objective and requested output;
- absolute Atlas root, product Git root and current path;
- typed find/path-context candidates or exact stable IDs, including `not-verified` state;
- authorised scan boundary, exclusions and fallback limits;
- known user-confirmed facts and unresolved ambiguity;
- validation deferrals and write prohibition where applicable.

Every analyst returns:

1. findings in the clearest presentation for the question;
2. a claim ledger with claim, source classification, supporting references, confidence, lifecycle status, direct/inferred state and all premises for inference;
3. material route hops with source, target, natural field/step, confidence and reference;
4. materially consulted paths;
5. checked-but-not-found paths when negative findings depend on them;
6. coverage limits, conflicts, inaccessible context and remaining questions;
7. recommended next routes only when they add value.

The parent skill verifies that references support the exact claims, preserves the analyst's chosen presentation, adds no unsupported synthesis, and exposes material file hops at the adaptive depth required by the answer. The complete ledger stays internal unless requested or required for an audit artifact.

For a write-capable specialist, also pass the exact persistence preview, the user's approval and the permitted files/claims/status effects. The specialist must not expand that scope or ask for the same approval again; it returns a material change to the parent for a revised preview.

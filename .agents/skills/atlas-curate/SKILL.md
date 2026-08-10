---
name: atlas-curate
description: Reconcile a coherent batch of eligible Atlas staging evidence into a human-reviewable proposal, with independent review and no self-approval or publication.
---

# atlas-curate

Read shared runtime/provenance/handoff contracts. Curation proposes knowledge; human-reviewed merge creates authority.

1. Process coherent related `status: new` batches after checking merged queue state/active work and source/target contracts.
2. Search existing IDs, aliases, locators and semantic matches. Build a per-record/target `CREATE`, `UPDATE`, `DEFER`, `REJECT` or `CONFLICT` matrix. Ask about unresolved boundaries/domains/identities/contradictions.
3. Pass the resolved matrix and source ledger to `atlas-curator`; it materialises only supported changes.
4. Run generation/permitted validation, then invoke `atlas-reviewer` independently with original evidence and changes. Fix safe blocker/major findings and re-review; stop on recurrence or human judgment.
5. Update only permitted lifecycle/checkpoint data. Report claim-to-evidence traceability, non-promoted claims, questions and validation.

Never commit, push, merge, approve or hand-edit generated artifacts.

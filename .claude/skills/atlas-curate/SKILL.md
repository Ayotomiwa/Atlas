---
name: atlas-curate
description: Reconcile a coherent batch of eligible Atlas staging evidence into a human-reviewable proposal, with independent review and no self-approval or publication.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-curate

Read `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md`. Curation proposes knowledge; a human-reviewed merge creates authority.

1. Read staging policy, taxonomy/statuses and each source record. Process coherent related `status: new` batches; check merged queue status and active work. Never mutate committed staging beyond top-level `status`.
2. Read every source bucket contract and target curated README/template/index. Search stable IDs, aliases, locators and semantic duplicates.
3. Build a decision matrix per staging record and target: `CREATE`, `UPDATE`, `DEFER`, `REJECT` or `CONFLICT`. Ask the user about unresolved boundaries, domains, identities or contradictions before materialisation.
4. Pass the resolved decision matrix, original evidence routes and source ledger to `atlas-curator`. The curator materialises only supported changes and does not redefine scope or ask the user.
5. Run `python scripts/rebuild_atlas.py` plus currently permitted validation. Never hand-edit generated artifacts.
6. Invoke `atlas-reviewer` independently with the original staging evidence, decision matrix and complete changes. Fix safe blocker/major findings and re-review. Stop when a material finding recurs or requires human judgment.
7. Update the compact checkpoint and proposed staging outcomes only. The proposal report traces every curated claim to staging and source evidence, lists non-promoted claims/relationships/questions and validation state, and requires human review.

Never commit, push, merge, approve, or treat local `status: curated` as proof of review.

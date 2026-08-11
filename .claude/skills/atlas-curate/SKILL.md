---
name: atlas-curate
description: Reconcile a coherent batch of eligible Atlas staging evidence into authoritative curated knowledge with independent review and no publication.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-curate

Read `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `../_shared/agent-handoffs.md`. Successful evidence reconciliation and independent review produce authoritative `status: curated` knowledge; merge only distributes and audits it.

1. Read staging policy, taxonomy/statuses, `references/semantic-preflight.md`, and each source record. Process coherent related `status: new` batches; check merged queue status and active work, then mark the selected records `curating` while reconciliation and review are active. Never mutate committed staging beyond top-level `status`.
2. Read every source bucket contract and target curated README/template/index. Use exact IDs and typed `find` across aliases, descriptions, keywords and locators to identify semantic duplicate/target candidates; never silently select ambiguity.
3. Build a decision matrix per staging record and target: `CREATE`, `UPDATE`, `DEFER`, `REJECT` or `CONFLICT`. Ask one clarification round: required identity, scope, ownership, domain, promotion, conflict and safety decisions first, followed by one optional confirm-or-correct gap list. Skipped non-blocking gaps remain unknown.
4. Resolve the curating identity for `reviewed_by` from `git config user.name`, asking the user if Git has no usable identity. It records who curated the page, never the agent and never a later merger or publisher.
5. Pass the resolved decision matrix, curating identity, original evidence routes and source ledger to `atlas-curator`. The curator materialises only supported changes and does not redefine scope or ask the user.
6. Run `python scripts/rebuild_atlas.py` plus currently permitted validation. Never hand-edit generated artifacts.
7. Create a temporary review fingerprint with `scripts/atlas_review_snapshot.py create`, passing the exact staging inputs, changed curated pages, affected generated projections, relevant local evidence, intended missing/deleted paths and source checkout roots. Verify it immediately before invoking `atlas-reviewer`; a mismatch restarts review and does not count as a substantive failure.
8. Invoke `atlas-reviewer` independently with the original evidence, decision matrix, complete changes and fingerprint path. Apply fixes only after review ends. Every re-review gets a new fingerprint; stop when a material finding recurs or requires human judgment.
9. Mark successfully processed staging evidence `consumed`; use the other terminal staging outcomes when applicable. Update the compact checkpoint only. The curation report traces every curated claim to staging and source evidence, lists non-promoted claims/relationships/questions and validation state, and records that later merge/publication does not change lifecycle authority.

Never commit, push, merge, publish, bypass independent review, or hand-edit generated artifacts.

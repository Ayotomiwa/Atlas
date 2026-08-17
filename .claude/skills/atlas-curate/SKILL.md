---
name: atlas-curate
description: Reconcile a coherent batch of eligible Atlas staging evidence into authoritative curated knowledge with independent review and no publication.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-curate

Read `../_shared/human-intents.md`, `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `../_shared/agent-handoffs.md`, and `../_shared/curation-safety.md`. This is **Curate Atlas**. Successful evidence reconciliation and independent review produce authoritative `status: curated` knowledge; merge only distributes and audits it.

1. Read staging policy, the authoring prerequisites in the shared safety contract, and `references/semantic-preflight.md`. Default the queue scope to the user's current repository, domain, stable ID or named topic; show the package-wide queue only when requested. Use `python scripts/atlas_query.py staging --format json` and process coherent related `status: new` records. Do not mark them `curating` before the persistence preview is approved.
2. Read every source bucket contract and target curated README/template/index. Use exact IDs and typed `find` across aliases, descriptions, keywords and locators to identify semantic duplicate/target candidates; never silently select ambiguity.
3. Build a decision matrix per staging record and target: `CREATE`, `UPDATE`, `DEFER`, `REJECT` or `CONFLICT`. Staging must normally supply enough explanation and exact evidence for curation without broad product-source rediscovery. Curation may inspect precisely cited product evidence and browse Atlas broadly for duplicates, links and target context. If materially new product facts are needed, stage them first and issue a revised curation preview.
4. Ask one clarification round: required identity, scope, ownership, domain, promotion, conflict and safety decisions first, followed by one optional confirm-or-correct gap list. Skipped non-blocking gaps remain unknown. Present proposed outcomes in plain language before internal decision codes.
5. Show one concrete preview covering selected staging status changes, curated files/claims, generated effects, unknowns, exclusions and independent review. Obtain one approval for that unchanged scope, re-check merged queue state and active work, then start the shared work guard and mark selected records `curating`. A newly claimed/changed record invalidates the preview and stops the batch.
6. Resolve the curating identity for `reviewed_by` from `git config user.name`, asking the user if Git has no usable identity. It records who curated the page, never the agent and never a later merger or publisher.
7. Pass the approved decision matrix, preview scope, curating identity, original evidence routes and source ledger to `atlas-curator`. The curator materialises only supported changes and never requests the same approval. Create the automatic materialized checkpoint after it returns.
8. Own the shared aggregate lint classification, at-most-two mechanical repair passes, scope-clean check, generation and freshness check. Never hand-edit generated artifacts. An unrelated baseline issue may defer generation/freshness but cannot block semantic curation. A current-cause failure or unexplained lint/compiler inconsistency leaves only active/new records that entered this batch in `curating`; repair-only recovery leaves already-consumed evidence `consumed`.
9. Create and verify a temporary review fingerprint over exact inputs, materialized changes, projections, cited local evidence and source checkout heads, then invoke `atlas-reviewer` independently. Apply only shared-contract meaning-preserving fixes after review; every re-review gets a new fingerprint. A semantic scope change requires a revised user preview; a recurring material finding stops for human judgment.
10. Mark successfully processed evidence `consumed`; use other terminal outcomes when applicable. Update the compact checkpoint only. Report **Current work**, **Scope validation**, **Generated freshness**, and **Package health**, then trace claims, non-promoted material and questions in audit detail. Later merge/publication does not change lifecycle authority.

Never commit, push, merge, publish, bypass independent review, or hand-edit generated artifacts.

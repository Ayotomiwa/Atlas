---
name: atlas-curate
description: Reconcile a coherent batch of eligible Atlas staging evidence into authoritative curated knowledge with independent review and no publication.
---

# atlas-curate

Read shared runtime/provenance/handoff contracts. Successful evidence reconciliation and independent review produce authoritative `status: curated` knowledge; merge only distributes and audits it.

1. Process coherent related `status: new` batches after checking merged queue state/active work, source/target contracts and `references/semantic-preflight.md`; mark the selected records `curating` while reconciliation and review are active.
2. Use exact IDs and typed `find` to identify existing semantic candidates. Build a per-record/target `CREATE`, `UPDATE`, `DEFER`, `REJECT` or `CONFLICT` matrix. Ask one round with blocking identity/scope/ownership/domain/promotion/conflict/safety decisions first and other gaps as optional confirm-or-correct items.
3. Pass the resolved matrix and source ledger to `atlas-curator`; it materialises only supported changes.
4. Run generation/permitted validation. Create and verify a temporary `atlas_review_snapshot.py` fingerprint of exact inputs, changes, projections, evidence and checkout HEADs before independent review. The reviewer verifies again before returning. State mutation invalidates and restarts review without counting as a finding.
5. Apply fixes only after review completes and create a fresh fingerprint for every re-review. Mark successful staging outcomes `consumed`; report claim-to-evidence traceability, non-promoted claims, questions and validation.

Never commit, push, merge, publish, bypass independent review or hand-edit generated artifacts.

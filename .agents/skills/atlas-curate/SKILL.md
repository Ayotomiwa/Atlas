---
name: atlas-curate
description: Reconcile a coherent batch of eligible Atlas staging evidence into authoritative curated knowledge with independent review and no publication.
---

# atlas-curate

Read shared human-intent/persistence/runtime/provenance/handoff contracts. This is **Curate Atlas**. Successful reconciliation and independent review produce authoritative `status: curated` knowledge; merge only distributes and audits it.

1. Default the active queue to the current repository/domain/ID/topic; show the package-wide queue only when requested. Read source/target contracts and semantic preflight, but do not mark records `curating` before approval.
2. Build internal decisions with exact IDs/find. Staging should allow curation without broad product rediscovery: inspect exact cited product evidence only, while browsing Atlas broadly for targets/links. Newly required product facts must be staged first and cause a revised preview.
3. Ask one consolidated blocking/confirm-or-correct round and present outcomes in plain language. Show one preview covering staging statuses, curated files/claims, generation, unknowns and review. After approval re-check merged queue/active work, then mark records `curating`; a newly claimed/changed record invalidates the preview. Pass the approved scope/matrix to `atlas-curator`; it never asks again.
4. Run generation/permitted validation. Create and verify a temporary `atlas_review_snapshot.py` fingerprint of exact inputs, changes, projections, evidence and checkout HEADs before independent review. The reviewer verifies again before returning. State mutation invalidates and restarts review without counting as a finding.
5. Apply meaning-preserving fixes only after review and use a fresh fingerprint for every re-review. Semantic scope changes require a revised preview. Mark successful outcomes `consumed`; use the shared completion summary before audit traceability.

Never commit, push, merge, publish, bypass independent review or hand-edit generated artifacts.

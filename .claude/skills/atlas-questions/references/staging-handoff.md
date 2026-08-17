# Staging handoff

Propose staging only for durable, reusable, attributable evidence. The preview must appear before any write:

```text
Proposed staging evidence
- Bucket: <primary-fact bucket>
- Working title: <title>
- Atlas questions addressed: <qualified question IDs>
- User-confirmed claims: <bounded claims>
- Provenance: <user role/source, timeframe and scope>
- Remaining uncertainty: <unresolved limits>
- Duplicate or pending evidence: <routes or none found>
- Excluded: <sensitive, speculative, transient or unrelated claims>
```

Group answers into one staging record only when they form one coherent reusable evidence unit. Split independent facts and let `atlas-stage` choose the final bucket using the applicable staging README/template.

Pass a duplicate-search ledger with the approved handoff:

- staging statuses and buckets searched;
- curated record types and indexes searched;
- ephemeral search-surface freshness fingerprints for the file set and content state of every searched staging and curated surface;
- qualified question IDs;
- matching staging IDs, paths and statuses;
- curated candidate IDs, pages and any ambiguity;
- selected target IDs, pages and baseline statuses;
- unresolved candidates.

Compute freshness fingerprints in memory for this handoff only; do not persist a cache or generated artifact. `atlas-stage` first compares every fingerprint before treating the handoff as unchanged. A missing or changed fingerprint invalidates the narrow path: repeat full duplicate discovery and return a revised preview. Only when the ledger is complete, every fingerprint still matches, and the evidence, targets and scope are unchanged does `atlas-stage` recheck only output-path uniqueness, exact qualified-question references, the current states of known duplicates, and the selected target ID/page/status against its baseline. A new match, target change, ambiguity or material scope change also invalidates the narrow path. A direct staging request or incomplete ledger always uses the full duplicate search.

An approval must clearly authorize persistence. A request to continue answering questions is not staging approval. After approval, invoke `atlas-stage` with the exact preview and approval; do not reproduce its write procedure or request the same approval again. If the final bucket, claims, files or exclusions materially change during handoff, return a revised preview first.

The staging record must cite each originating `<record-id>#<question-id>` in its body so later question discovery can suppress active duplicate evidence. Staging does not resolve the curated question. Only normal curation with independent review may update or remove it.

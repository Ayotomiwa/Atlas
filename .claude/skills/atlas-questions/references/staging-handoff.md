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

An approval must clearly authorize persistence. A request to continue answering questions is not staging approval. After approval, invoke `atlas-stage` with the exact preview and approval; do not reproduce its write procedure or request the same approval again. If the final bucket, claims, files or exclusions materially change during handoff, return a revised preview first.

The staging record must cite each originating `<record-id>#<question-id>` in its body so later question discovery can suppress active duplicate evidence. Staging does not resolve the curated question. Only normal curation with independent review may update or remove it.

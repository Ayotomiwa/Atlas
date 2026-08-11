# Staging index

- [changes](changes/README.md) — Reusable evidence discovered because of an engineering change
- [components](components/README.md) / [queue](components/index.md) — Raw repository/component discovery grouped by evidenced domain or `unassigned`
- [flows](flows/README.md) / [queue](flows/index.md) — Raw end-to-end flow evidence grouped by evidenced domain or `unassigned`
- [infra](infra/README.md) — Raw IaC/package/resource evidence
- [schema-info](schema-info/README.md) — Raw table/event/file/API/data-contract evidence
- [business-concepts](business-concepts/README.md) — Raw supplied business definitions and meaning
- [incidents](incidents/README.md) — Sanitised reusable incident/near-miss learning
- [runbooks](runbooks/README.md) — Draft operational procedures
- [standards](standards/README.md) — Candidate reusable engineering standards

New findings not caused by a change go directly to the appropriate semantic bucket. Staging remains evidence-only and never authoritative.

Use `python scripts/atlas_query.py staging` for one read-only view across every bucket. It defaults to active `new` and `curating` records; use its filters or `--include-terminal` for narrower or historical inspection.

Merged-source observation and consideration state is separate from evidence. See [change intake](../_intake/README.md) or use `/atlas-stage-changes`; `_intake/` is not another staging bucket.

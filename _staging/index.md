# Staging index

- [changes](changes/README.md) — Reusable context discovered because of a logical engineering change; code-derived capture normally follows the merged/default-branch state
- [components](components/README.md) — Raw repo/service/component discovery
- [flows](flows/README.md) — Raw end-to-end flow evidence
- [infra](infra/README.md) — Raw IaC/package/resource evidence
- [schema-info](schema-info/README.md) — Raw table/event/file/API/data-contract evidence
- [business-concepts](business-concepts/README.md) — Raw supplied business definitions/meaning
- [incidents](incidents/README.md) — Sanitised reusable incident/near-miss learning
- [runbooks](runbooks/README.md) — Draft operational procedures
- [standards](standards/README.md) — Candidate reusable team standards/conventions

New findings that are not caused by an engineering change should go directly to the most appropriate semantic bucket rather than being forced through `changes/`.

# Runbooks staging

## Purpose

`_staging/runbooks/` captures **draft or discovered operational procedure evidence** before it is reviewed as a trusted runbook.

Use it to preserve candidate investigation/recovery guidance, gaps in existing procedures, or operational steps learned from code, documentation, incidents or experienced engineers.

## Belongs here

Capture:

- draft trigger/symptom definitions;
- prerequisites/access requirements;
- candidate safety/stop conditions;
- investigation sequences;
- recovery/replay/restart observations;
- validation checks;
- rollback and escalation guidance;
- monitoring references;
- gaps in existing runbooks;
- evidence showing where a procedure came from or when it worked.

## Does not belong here

Do not use this bucket for:

- an incident record — use `_staging/incidents/`;
- live operational commands with embedded secrets;
- untested destructive actions presented as safe;
- local development setup owned by a product repo;
- general architecture/component descriptions;
- a procedure already curated unless the entry is evidence for a proposed update.

## Safety rule

Staging runbook content is **not trusted operational instruction**. It must never be presented as an approved recovery procedure merely because it is written clearly.

Clearly distinguish:

- steps actually observed/performed;
- steps explicitly user/operator-confirmed;
- proposed or possible steps requiring review.

## Granularity

Capture one coherent operational scenario/procedure per staging entry. Split unrelated failure modes when their trigger, safety, recovery or validation differs.

## Curation outcomes

A staged procedure may update/create `_curated/runbooks/`, or reveal related component/flow/infra/incident/standard updates. Curators should not promote destructive or security-sensitive steps without appropriate evidence/review.

## Immutability

After a staging entry is referenced by curation, do not edit/move it. Record corrections or later exercise results as follow-up evidence.

## Security and sensitivity

Never include passwords, tokens, privileged credentials, customer data, sensitive production values or bypass instructions. Describe required access and link to authorised operational systems.

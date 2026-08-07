---
name: atlas-onboard-service
description: Onboard a service by bounded repository scanning and stage only supported evidence.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-onboard-service

Read `onboarding/README.md`, `onboarding/service-questionnaire.md`, `_staging/components/README.md` and its template. Delegate broad read-only scanning to `atlas-repo-analyst` in `service-onboarding` mode. Build an evidence matrix covering responsibility, inputs, outputs, interfaces, runtime/deployment, infra, flows, schedules/triggers, schemas/data assets, runbooks/docs, operational signals and owners. Inspect README/CONTRIBUTING/docs, CLAUDE.md, build files, package metadata, Docker/CI/CODEOWNERS, source/config, IaC, APIs/schemas, SQL/migrations, scheduler/workflow config and runbooks when present; skip generated/vendor directories. Ask one consolidated clarification round for material gaps and a second only if blocking. Follow accessible user-supplied infra/context paths. Distinguish observed, user-confirmed, possible and not covered. Always stage a component when identified; stage infra/flow/schema/runbook/incident evidence only when supported. Never create empty placeholder evidence, curate, or invent authoritative relationships. Finish with staged files, missing evidence, likely curation targets, and optional next skills.

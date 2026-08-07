---
name: atlas-onboard-service
description: Use to onboard a service/repository into TeamA Atlas by performing a bounded evidence scan and staging only supported findings.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-onboard-service

1. Identify the active service/repository and Atlas root.
2. Read `onboarding/README.md`, `onboarding/service-questionnaire.md`, `_staging/components/README.md` and its template.
3. Delegate/read-only scan via `atlas-repo-analyst` where available. Inspect README/CONTRIBUTING/docs, CLAUDE.md, build metadata, package files, Docker, CI, CODEOWNERS, src/config, application config, IaC, service metadata, API/schema/event definitions, migrations/DDL/SQL, scheduler/workflow config, and runbooks when present. Ignore `.git`, `node_modules`, `target`, `build`, `.venv`, binaries and generated outputs unless relevant.
4. Build an evidence matrix: Question | Finding | Source | State (`observed|user-confirmed|possible|not-covered`) | Candidate Atlas target | Blocking?.
5. Identify material gaps and ask one consolidated clarification round, especially infra location, upstream/downstream systems, flow boundary/name, ownership and inaccessible references.
6. Follow only accessible user-supplied locations; ask a second targeted clarification only when a missing answer blocks correct staging.
7. Stage only supported evidence: always component when identified; infra only with infra evidence; flow only with evidenced/user-confirmed boundary; schema-info when durable assets/interfaces are material; runbook/incident only when present.
8. Do not create empty placeholder staging files and do not curate or author authoritative relationships.
9. Run staging lint and report files staged, missing evidence, likely curation targets, plus optional `atlas-onboard-standards`/`atlas-setup-repo` next steps.

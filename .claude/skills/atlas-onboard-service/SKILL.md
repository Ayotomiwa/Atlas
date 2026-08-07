---
name: atlas-onboard-service
description: Onboard a service by bounded repository scanning, targeted clarification and staging only supported evidence into the correct Atlas buckets.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-onboard-service

This is the primary V1 service-onboarding workflow. It stages evidence only; it never curates.

## Preparation

1. Identify the active service/repository and the TeamA Atlas root.
2. Read `onboarding/README.md`, `onboarding/service-questionnaire.md`, `_staging/components/README.md`, and `_staging/components/_template.md`.
3. Delegate deep read-only repository inspection to `atlas-repo-analyst` in `service-onboarding` mode when useful.

## Bounded scan

Inspect the following when present: README/CONTRIBUTING/docs, local `CLAUDE.md`, Maven/Gradle/Python/npm build metadata, Docker files, `.gitlab-ci.yml`, `.github/workflows/`, CODEOWNERS, source and obvious configuration directories, `application*.yml`/properties, Terraform/CloudFormation/CDK/SAM/Serverless, service metadata, API/OpenAPI/schema/event definitions, migrations/DDL/SQL, schedulers/cron/EventBridge/Step Functions/workflow configuration, and runbooks/operational docs.

Do not recursively dump `.git`, `node_modules`, `target`, `build`, `.venv`, binaries, generated output, or vendor trees unless explicitly relevant. Bash is for bounded read-only inspection; do not run destructive commands.

## Evidence matrix

Build a matrix with: Question, Finding, Source path/reference, State (`observed`, `user-confirmed`, `possible`, `not-covered`), Candidate Atlas target, and Blocking for staging (`yes`/`no`). Cover component responsibility, inputs, outputs, interfaces, runtime/deployment, infrastructure, flows, schedules/triggers, schema/data assets, runbooks/docs, operational signals, and known owners.

## Clarification

1. Ask one consolidated clarification round for material gaps, prioritising ambiguous responsibility, authoritative external infra location, known upstream/downstream systems, flow boundary/name, owner/SME, and inaccessible referenced docs/repos.
2. If the user supplies an accessible path or added directory, inspect it and update the evidence matrix.
3. Ask a second targeted clarification only if a missing answer blocks correct staging. Do not interrogate for optional details.
4. If a supplied location is inaccessible, say exactly what must be exposed or provided; do not infer its contents.

## Staging rules

- Always stage a component record when a service is successfully identified.
- Stage infra only when infra evidence exists.
- Stage flow only when an end-to-end boundary is observed or user-confirmed.
- Stage schema-info when durable interfaces/data assets are material.
- Stage runbook or incident evidence only when present.
- Do not create empty placeholder staging files merely because a category is missing.
- Distinguish observed, user-confirmed, possible, and not-covered claims.
- Do not write curated pages or authoritative relationships.

Finish by running lint and reporting files staged, missing evidence, likely next curation targets, and whether `atlas-onboard-standards` or `atlas-setup-repo` would be useful next.

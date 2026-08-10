---
name: atlas-onboard-service
description: Onboard a service by bounded repository scanning, targeted clarification and staging only supported evidence into the correct Atlas buckets.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-onboard-service

This workflow stages evidence only; it never curates.

## Preparation

1. Identify the active service/repository and the TeamA Atlas root.
2. Read `onboarding/README.md`, `onboarding/service-questionnaire.md`, `_staging/components/README.md`, and `_staging/components/_template.md`.
3. Delegate deep read-only repository inspection to `atlas-repo-analyst` in `service-onboarding` mode when useful.
4. Treat the component staging contract as the primary raw capture surface for both repository topology and candidate architectural components. Do not assume one repository equals one component or the whole surrounding flow/infrastructure boundary.

## Bounded scan

Inspect relevant README/CONTRIBUTING/docs, local agent guidance, build metadata, containers/CI, CODEOWNERS, source/configuration roots, service metadata, interface/schema definitions, migrations, infrastructure/workflow configuration, and operational documentation.

Do not recursively dump VCS metadata, dependency caches, build output, virtual environments, binaries, generated output, or vendor trees unless explicitly relevant. Use bounded read-only inspection and do not change the product repository.

## Evidence matrix

Build a matrix with: Question, Finding, Source path/reference, State (`observed`, `user-confirmed`, `possible`, `not-covered`), Candidate Atlas record/field, and Blocking for staging (`yes`/`no`).

Cover in one repository discovery record, tagging component-specific evidence to its candidate:

- repository identity and mutable locator, repository/monorepo topology, important source roots and explicit source/build dependencies;
- candidate primary domain, candidate component splits/parents, independently addressable responsibilities, important entrypoints and implementation control flow;
- durable consumes/produces, runtime/deployment, infrastructure actions, flow boundaries/steps/handoffs, schedules/triggers, and schema assets;
- source-owned setup/build/test/deploy documentation, runbooks, incidents, operational signals, standards hints and owners.

Do not stop at a single component-shaped summary. Capture a candidate-component matrix plus per-candidate entrypoints, I/O, dependencies, infrastructure actions, deployment, failure and operational evidence so curation can split the repository without inference.

A component may participate in cross-repository flows or infrastructure defined elsewhere. Preserve missing surrounding context as possible or not covered.

## Clarification

1. Ask one consolidated clarification round for material gaps, prioritising ambiguous repository/component boundaries, uncertain primary domain, authoritative external infrastructure, upstream/downstream systems, flow boundary/name, ownership and inaccessible references.
2. Inspect any newly supplied accessible path and update the evidence matrix.
3. Ask a second targeted question only when an answer blocks safe staging.
4. If a source is inaccessible, state what must be exposed; never infer its contents.

## Staging rules

- Always stage a component record when a service/repository is successfully identified. Curation may later split it into one `repo.*` page and multiple `comp.*` pages.
- Store staging components/flows under a registered candidate-domain folder only when supported; otherwise use `unassigned`.
- Preserve bucket-specific structure and uncertainty; do not collapse evidence into a generic findings list.
- Stage infrastructure only when infrastructure evidence exists, after reading its staging README/template.
- Stage a flow only when an end-to-end boundary is observed or user-confirmed, after reading its staging README/template. Do not manufacture a flow from one local call chain.
- Stage schema, runbook or incident evidence only when material evidence exists and after reading the bucket contract.
- Do not create empty placeholders.
- Do not write curated pages, authoritative typed connections/links, or generated artifacts.

Finish with the staged files, inspected evidence, missing/inaccessible context, possible findings, likely repository/component/flow/domain curation targets, and useful follow-on workflows. Run validation only when it has not been explicitly deferred by the user.

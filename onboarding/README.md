# Onboarding

Onboarding is a bounded evidence-capture workflow. It operates only on repositories/directories already available to the active session or explicitly supplied by the user; inaccessible context is never treated as absent.

## Service onboarding

1. Identify the active service repository and Atlas root.
2. Read this guide, `service-questionnaire.md`, and the component staging contract.
3. Perform a broad but bounded repository scan and build the evidence matrix.
4. Ask one consolidated clarification round for material gaps.
5. Follow any user-supplied accessible infrastructure/context path and update the matrix.
6. Ask a second clarification only if a remaining gap blocks correct staging.
7. Stage component evidence and only those linked buckets for which evidence exists.
8. Run lint and report staged files, missing evidence, and likely next curation targets.

The evidence matrix records: Question; Finding; Source path/reference; State (`observed`, `user-confirmed`, `possible`, `not-covered`); Candidate Atlas target; and whether the gap blocks staging.

## Standards discovery

Use `atlas-onboard-standards` separately. It classifies findings as `team-standard-candidate`, `repo-local-convention`, `tool-default`, or `unknown-scope`; it does not curate standards.

## Safety

Do not crawl unrelated enterprise systems, bypass permissions, persist secrets/customer data, invent missing infrastructure or flows, or write curated knowledge during onboarding.

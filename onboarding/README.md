# Onboarding

## Purpose

Onboarding is a **bounded evidence-capture workflow** that turns an unfamiliar service/repository into structured staging evidence without pretending that a repository scan can prove everything about the surrounding platform.

It is deliberately broader than `atlas-stage` but stops before curation. The primary V1 workflow is `atlas-onboard-service`; standards discovery is a separate workflow because evidence of implementation is not automatically evidence of policy.

## Trust and access boundary

Onboarding may inspect only repositories/directories already available to the active session or explicitly supplied by the user. It must not:

- crawl unrelated enterprise systems;
- bypass repository or filesystem permissions;
- autonomously follow inaccessible/private references;
- treat inaccessible context as absent context;
- write curated knowledge;
- invent missing repositories, infrastructure, owners, dependencies or flows.

If reusable knowledge comes from a private conversation or external source, explicit user approval is required before persisting it to staging.

## Service onboarding workflow

### 1. Establish scope

Identify:

- active service/repository;
- Atlas root/package;
- repository boundary (including monorepo subpath when relevant);
- any user-supplied additional infra/context locations.

Read this guide, `service-questionnaire.md`, `_staging/components/README.md` and its template before staging.

### 2. Broad but bounded scan

Inspect relevant signals when present, including:

- README and local `CLAUDE.md`;
- build/dependency files;
- source entry points and package/module structure;
- configuration;
- API/event/schema/data-contract definitions;
- deployment/runtime descriptors;
- infrastructure references;
- schedules/triggers/orchestration;
- runbooks/docs;
- monitoring/operational references;
- ownership hints.

The scan should be deep enough to build reusable evidence but should not read unrelated areas merely to make the report look complete.

### 3. Build the evidence matrix

For each important question record:

| Question | Finding | Source path/reference | State | Candidate Atlas target | Blocks correct staging? |
|---|---|---|---|---|---|
| | | | observed / user-confirmed / possible / not-covered | | yes/no |

The matrix should cover, where material:

- component responsibility/boundary;
- inputs/consumes;
- outputs/produces;
- interfaces/contracts;
- runtime/deployment;
- infrastructure;
- flow participation/boundary;
- schedules/triggers;
- schema/data assets;
- runbooks/docs;
- operational signals;
- known owner/SME.

### 4. Clarify only meaningful gaps

Ask **one consolidated first clarification round** for high-value gaps the repository cannot establish, especially:

- authoritative infra location;
- known upstream/downstream systems;
- plausible-but-ambiguous flow boundary/name;
- ownership/SME;
- explicitly referenced but inaccessible docs/repos.

If the user supplies an accessible path, inspect it and update the matrix. Ask a second targeted round only when a remaining answer blocks correct staging. Optional unknowns should stay `possible` or `not-covered` rather than triggering an interrogation.

### 5. Stage only supported buckets

A successfully identified service always produces component staging evidence. Additional buckets are conditional:

| Bucket | Stage when |
|---|---|
| `_staging/components/` | the service/component identity and evidence are established |
| `_staging/infra/` | actual infra/IaC/resource evidence exists |
| `_staging/flows/` | an end-to-end boundary is evidenced or user-confirmed |
| `_staging/schema-info/` | durable APIs/events/tables/files/contracts are material |
| `_staging/runbooks/` | operational procedure evidence exists |
| `_staging/incidents/` | reusable incident/near-miss evidence exists |

Do **not** create empty flow/infra/etc. placeholder files merely because onboarding could not discover them.

### 6. Validate and report

Run staging validation and finish with an onboarding report containing:

- files staged;
- evidence sources inspected;
- important missing/inaccessible context;
- possible/unconfirmed findings;
- likely curation targets;
- recommendation to run `atlas-onboard-standards` and/or `atlas-setup-repo` when useful.

## Standards discovery

Use `atlas-onboard-standards` separately. It scans repository evidence for candidate rules but classifies findings carefully:

- `team-standard-candidate`;
- `repo-local-convention`;
- `tool-default`;
- `unknown-scope`.

Repeated implementation is evidence of practice, not proof of mandate. Use `standards-questionnaire.md` only for ambiguous high-value candidates whose scope/authority matters.

## Local Atlas setup

`atlas-setup-repo` manages only the marked Atlas block in a product repo's `CLAUDE.md`. The product repository continues to own exact build/test/lint/local-development instructions. On rerun, preserve all user content outside the managed markers.

The template intentionally stays short: it routes to Atlas; it does not copy Atlas knowledge into every product repository.

## Safety and quality rules

- distinguish `observed`, `user-confirmed`, `possible` and `not-covered`;
- do not treat missing evidence as evidence of absence;
- do not fabricate TeamA facts to complete a questionnaire;
- do not persist secrets, customer data or raw sensitive logs;
- do not curate during onboarding;
- do not create empty evidence files for categories with no evidence;
- keep source paths/references precise enough that a future curator can reproduce the finding.

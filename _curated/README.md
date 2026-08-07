# Curated knowledge

`_curated/` is TeamA Atlas's reviewed knowledge layer. It contains durable engineering context that humans and AI agents can route to repeatedly without rediscovering the same facts from source systems.

## Trust model

A file being under `_curated/` does **not** make every claim automatically authoritative.

- `status: curated` — reviewed and authoritative within the page's stated coverage when present on the governed/default branch.
- `status: proposed` / `draft` — reviewable knowledge, not yet authoritative.
- `status: deprecated` — still useful for historical/transition context but no longer preferred.
- `status: archived` — retained in place/history and excluded from normal routing.

Claude may propose curated changes. Humans approve/merge them.

## What lives here

Each concept folder has a distinct responsibility:

| Area | Represents |
|---|---|
| `components/` | Meaningful repositories, services, deployable units, job groups and reusable libraries |
| `flows/` | End-to-end operational/data paths across meaningful steps/components |
| `infra/` | Infrastructure packages/templates and selectively promoted resources |
| `schema-info/` | Durable table/event/file/API/data-contract structure and reviewed semantics |
| `business-concepts/` | Reviewed business definitions, boundaries and approved variants |
| `standards/` | Reusable TeamA engineering rules grouped by category |
| `runbooks/` | Reviewed operational procedures |
| `incidents/` | Sanitised reusable incident/near-miss learning |
| `maps/` | Generated machine-readable relationship projections |
| `status/` | Latest curation checkpoint only, not engineering truth or the staging queue |

## How folder files divide responsibility

Within a curated concept folder:

- `README.md` defines **meaning, scope, granularity, evidence and reviewer rules**;
- `_template.md` defines the **shape of a new page**;
- `index.md` is the **routing/catalogue surface for existing pages**.

Do not move semantic policy into `index.md`, and do not treat the template alone as sufficient curation guidance.

## Relationship model

Relationships are authored on curated Markdown pages in frontmatter `relationships:` using `taxonomy/relationships.yaml`.

The JSON files under `_curated/maps/` are generated projections of those relationships. **Pages are the authoring source of truth; maps are never hand-authored relationship truth.**

Relationship certainty is per edge (`reviewed`, `possible`, `unconfirmed`, `conflicting`), not a blanket page-level confidence.

## Evidence and coverage

Material claims should trace to staging evidence, repository paths, external references or reviewer-confirmed sources. Missing evidence should remain visible through explicit coverage notes or the required marker:

```markdown
*Not covered — no evidence in current staging material.*
```

An absent relationship or missing section does not mean "not affected" or "does not exist".

## Editing workflow

Before changing a concept page:

1. read that folder's `README.md`, `_template.md` and `index.md`;
2. search for an existing concept by ID, alias, path and semantic match;
3. preserve source evidence and uncertainty;
4. write/update as `proposed`, never let Claude self-promote to `curated`;
5. update the relevant index;
6. rebuild generated maps after relationship changes;
7. update the consumed staging record's lifecycle `status` only — never rewrite its evidence;
8. update the compact curation checkpoint when useful;
9. run lint, map freshness checks and relevant tests;
10. use the Atlas PR/MR itself as the human review/audit record.

A human reviewer decides whether accepted curated pages become `status: curated` before the approved change lands on the governed/default branch.

## What not to put here

Do not curate raw evidence, transient delivery status, full incident records, secrets, customer data, raw sensitive logs, unsupported guesses or implementation detail that belongs in the owning product repository and can be reliably derived there.

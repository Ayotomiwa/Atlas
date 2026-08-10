# Curated knowledge

`_curated/` is TeamA Atlas's reviewed knowledge layer. It stores durable engineering context that humans and agents should not need to rediscover repeatedly.

## Trust

- `curated` — reviewed content usable for routing; it is authoritative only after human review and merge.
- `draft` / `proposed` — reviewable but not authoritative.
- `deprecated` — retained for transition/history but no longer preferred.
- `archived` — excluded from normal routing and generated maps.

Agents may prepare `status: curated` proposals but never self-approve or merge them. Query tooling reports lifecycle status but does not infer human approval or merge state; its warning outside `main` or `master` is advisory and never blocks routing.

## Concept responsibilities

| Area | Represents |
|---|---|
| `repositories/` | Source repository identity, topology and code-orientation routes |
| `components/` | Independently addressable runtime or reusable architectural units |
| `flows/` | End-to-end ordered paths, branches and handoffs |
| `infra/` | Infrastructure packages and selectively promoted resources |
| `schema-info/` | Durable table/event/file/API/data-contract structure and semantics |
| `business-concepts/` | Reviewed business definitions and boundaries |
| `standards/` | Reusable engineering rules grouped by category |
| `runbooks/` | Reviewed operational procedures |
| `incidents/` | Sanitised reusable incident learning |
| `maps/` | Generated machine-readable routing projections |
| `status/` | Latest compact curation checkpoint |

READMEs own semantic and reviewer policy. Templates own authoring shape. Indexes only route and catalogue.

## Stable IDs and domains

Use `<type-prefix>.<stable-name>`, such as `repo.orders-platform`, `comp.sds-client` or `flow.order-fulfilment`. Add semantic segments only when required to remove ambiguity. A semantic name may coincide with a repository name, but identity never depends on that mutable locator.

Repositories, components, flows, infrastructure and schema-info pages live under a controlled primary-domain folder. `primary_domain` must match the folder and be declared in `atlas-package.json`; `related_domains` records secondary involvement. Paths may move without changing identity.

## Structured connections

Curated pages author readable, domain-specific blocks rather than a generic `relationships` array. Natural field names such as `depends_on`, `consumes`, `produces`, `reads_from` and `writes_to` carry the meaning. Compiler-only endpoint and impact-direction rules live in `contracts/map-fields.yaml`; authors use the applicable README/template.

Confidence is per entry (`reviewed`, `possible`, `unconfirmed`, `conflicting`). Possible facts remain in their normal collection with evidence and an explanatory note. Maps keep only high-value reverse views; comprehensive reverse and transitive traversal is computed on demand.

Open questions use the fixed body table `Question ID | Question | Affected IDs | Evidence gap`. Maps compile compact routes, not full narrative context.

## Editing workflow

1. Read the target README, template and index.
2. Search by stable ID, alias, repository locator and semantic match.
3. Preserve evidence, confidence and coverage boundaries.
4. Author each structured fact once on its narrowest true record.
5. Run `python scripts/rebuild_atlas.py` to regenerate maps, catalogues and managed page views.
6. Update only the staging lifecycle status after committed evidence is consumed; corrections are new evidence.
7. Use the PR/MR and Git history as the review record.

Never curate secrets, customer data, unsupported guesses, transient delivery status or source detail that is more reliably owned by the product repository.

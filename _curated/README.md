# Curated knowledge

`_curated/` is Datalens Atlas's reviewed knowledge layer. It stores durable engineering context that humans and agents should not need to rediscover repeatedly.

## Trust

- `curated` — active, authoritative knowledge.
- `deprecated` — retained for transition/history but no longer preferred.
- `archived` — excluded from normal routing, generated catalogues and maps.

Curation authors `status: curated` directly after evidence reconciliation and independent review. There is no later approval status to mutate: PR/MR and Git history distribute and audit the change, but do not create its semantic authority.

A `status: curated` page must carry `reviewed_by`, an ISO `last_reviewed` and evidence; there is no exemption.

`reviewed_by` names **the person who curated the page**, not a later merger or publisher. When an agent curates, it takes that identity from the session's `git config user.name`, or asks the user when Git has no usable identity. It is never left empty on a curated page, and never filled with the agent's own name. `last_reviewed` is the date that curation established the content against its evidence; write it as a plain ISO date.

Query tooling derives trust from lifecycle: every active `status: curated` page is `authoritative`, and deprecated content is `historical`. Checkout state is a separate advisory (`main-clean`, `off-main`, `modified`, `untracked`, `detached` or `git-unknown`). It is shown briefly when relevant and never blocks routing or downgrades authority; after merge and checkout on `main`/`master`, it becomes `main-clean` automatically without editing the page.

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

READMEs own semantic and reviewer policy, and every one of them carries a review checklist. Templates own authoring shape; compact routing/filter fields may remain structured while explanations and attribution belong in the body. Indexes only route: their generated catalogues include concise descriptions and page links, while surrounding routing prose and coverage notes remain hand-maintained.

## Stable IDs and domains

Use `<type-prefix>.<stable-name>`, such as `repo.orders-platform`, `comp.sds-client` or `flow.order-fulfilment`. Add semantic segments only when required to remove ambiguity. A semantic name may coincide with a repository name, but identity never depends on that mutable locator.

Repositories, components, flows, infrastructure and schema-info pages live under a controlled primary-domain folder. `primary_domain` must match the folder and be declared in `atlas-package.json`; `related_domains` records secondary involvement. Paths may move without changing identity.

## Structured connections

Curated pages author readable, domain-specific blocks rather than a generic `relationships` array. Natural field names such as `depends_on`, `consumes`, `produces`, `reads_from` and `writes_to` carry the meaning. Compiler-only endpoint and impact-direction rules live in `contracts/map-fields.yaml`; authors use the applicable README/template.

Confidence is per entry (`reviewed`, `possible`, `unconfirmed`, `conflicting`). Possible facts remain in their normal collection with evidence and an explanatory note. Maps keep only high-value reverse views; comprehensive reverse and transitive traversal is computed on demand.

Open questions use the fixed body table `Question ID | Question | Affected IDs | Evidence gap`. Maps compile compact routes, not full narrative context.

Schema pages may own embedded `asset.*` data assets and author lineage only through each asset's `inputs`; consumers are derived at query time. Common `conflicts` preserve at least two evidenced claims plus a bounded interpretation. Assets inherit their schema page's lifecycle/trust and conflicts remain page-local rather than becoming map records.

```yaml
conflicts:
  - conflict_id: native-push-automation
    topic: Native push publication
    claims:
      - statement: Documentation says pushes publish changes.
        evidence: [path/to/README.md]
      - statement: Checked-in workflows ignore pushes.
        evidence: [path/to/workflow.yml]
    interpretation: Checked-in native automation is disabled; external automation is unknown.
```

`routing.aliases` contains equivalent lookup names. Optional `routing.keywords` contains a small set of other phrases engineers may search for; keywords are routing hints rather than taxonomy or evidence. Generated page tables link resolved local IDs, and the generated `Related Atlas routes` block shows direct forward and derived reverse routes without reciprocal authorship.

## Editing workflow

1. Read the target README, template and index.
2. Resolve exact IDs directly or use typed `atlas_query.py find`; use the relevant index when candidates are weak or ambiguous.
3. Preserve evidence, confidence and coverage boundaries.
4. Author each structured fact once on its narrowest true record.
5. Run `python scripts/rebuild_atlas.py` to regenerate maps, catalogues and managed page views.
6. Update only the staging lifecycle status after committed evidence is consumed; corrections are new evidence.
7. Use the PR/MR and Git history as the review record.

Never curate secrets, customer data, unsupported guesses, transient delivery status or source detail that is more reliably owned by the product repository.

# Curated components

Use a component page to answer: **what does this independently addressable runtime or reusable unit do, what does it use, what does it produce, and what does it not own?**

For example, a scheduled worker can be a component when it has an independently meaningful runtime responsibility. The folder containing several workers is not automatically another component. Component pages explain architectural behavior without becoming function-by-function source walkthroughs.

## Boundary and granularity

A component can be a service, job, Lambda, API, consumer/producer, batch unit, shared library or infrastructure module. A repository, folder, domain or job group alone is not a component. Use `parent_component` only when the child is independently addressable and the parent is a real architectural boundary.

`component_type` is controlled by `taxonomy/concept-fields.yaml`. `component_scope` is retired. Repository identity and paths, component hierarchy and infrastructure links now carry the facts that field previously mixed together.

## Domain and source placement

Store each page at `_curated/components/<primary-domain>/<record>.md`. The domain must be registered in `atlas-package.json` and match `primary_domain`. `repository` must use the most specific useful `repo.*` source boundary. `repository_paths` are relative to that repository's `repository_root`; they are mutable locators and never identity.

## Structured authoring

- `consumes` and `produces` describe durable contracts using `asset_type`.
- `depends_on` describes component, library, configuration and build requirements using `dependency_type`.
- `uses_resources`, `reads_from`, `writes_to`, `triggers`, `scheduled_by`, `deployed_by` and `monitored_by` state the natural infrastructure action directly.
- `runbooks`, `standards` and `incident_learnings` route governed operational context directly.
- Possible, unconfirmed and conflicting facts stay in their normal collection with confidence, evidence and an explanatory note.

Each connection entry uses `id` for a stable Atlas target or `name` for an external target. The containing field already explains the connection, so entries never repeat a generic relationship name. Do not author flow participation on component pages: ordered flow steps are the sole participation source. The map keeps only one derived `used_by` view; the query tool derives other reverse and transitive paths.

## Documentation depth

Document purpose, responsibility, source entrypoints, concise control flow, durable interfaces, dependencies, configuration concepts, deployment context, failures and operational routes. Exact setup/build/run commands remain owned by the source repository. Add reviewed Mermaid only when one view of roughly three to eight meaningful nodes materially clarifies an internal boundary or control path. Follow the shared diagram-writing rules: preserve evidence and uncertainty, avoid color-only meaning, and keep the prose or structured table as a fallback. Use `atlas-diagram` for focused review.

Run `python scripts/rebuild_atlas.py` after structured changes. Never edit generated maps or managed tables.

## Review

Before approving a component page, confirm that:

- the unit is independently addressable, and `parent_component` reflects real architectural composition rather than folder nesting;
- `component_type` and the responsibility statement agree, and explicit non-responsibilities are recorded;
- `repository` names the most specific useful source boundary and `repository_paths` resolve within it;
- `consumes`/`produces` describe durable contracts, not incidental internal calls, and each carries a correct `asset_type`;
- `depends_on` separates component, library, configuration and build requirements through `dependency_type`;
- infrastructure actions use the field that matches what the code actually does — reading is not writing, and triggering is not scheduling;
- every non-reviewed entry keeps its confidence and an explanatory note instead of being quietly upgraded;
- no flow participation is authored here;
- failure and operational context routes to runbooks and monitoring without copying sensitive logs;
- coverage limits and open questions name what is unknown rather than leaving it blank.
- any diagram answers one engineering question and introduces no node, edge or causal claim beyond the reviewed page evidence.

This README defines the component page model and review rules. Repository onboarding and curation workflows own discovery, approvals, persistence, validation, and independent review.

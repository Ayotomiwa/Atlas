# Curated components

Component pages describe independently addressable runtime or reusable engineering units. They explain architectural behavior without becoming source-code walkthroughs.

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

Document purpose, responsibility, source entrypoints, concise control flow, durable interfaces, dependencies, configuration concepts, deployment context, failures and operational routes. Exact setup/build/run commands remain owned by the source repository. Add reviewed Mermaid only when it materially clarifies structure.

Run `python scripts/rebuild_atlas.py` after structured changes. Never edit generated maps or managed tables.

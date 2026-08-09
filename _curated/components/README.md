# Components policy

## Purpose

`_curated/components/` stores reviewed knowledge about meaningful TeamA implementation components: repositories, services, deployable units, scheduled job groups and reusable libraries.

A component page should help a human or agent answer: **what is this component, where does it live, what does it do, what does it consume or produce, and which flows/infrastructure/operations are connected to it?**

## Trust level

Only pages with `status: curated` are authoritative TeamA knowledge. `draft` pages are reviewable proposals, not facts. Claude may create or update proposals but never self-approve them.

## When to use this area

Use a component page for stable, reusable context about one meaningful implementation unit, including:

- responsibility and boundaries;
- repository and monorepo location;
- component type/scope;
- important internal units;
- inputs and outputs;
- related flows and infrastructure;
- local repository references;
- operational notes, runbooks, standards and incident learnings.

## When not to use it

Do not use a component page for:

- a full end-to-end process — use `_curated/flows/`;
- raw discovery notes — use `_staging/components/`;
- a one-off change summary — use `_staging/changes/`;
- detailed infrastructure package modelling — use `_curated/infra/`;
- every handler, Lambda, SQL file, script or config file by default;
- unsupported ownership, dependency or runtime claims.

## Granularity rule

Create one page per meaningful repo, service, deployable unit, scheduled job group or reusable library. Lower-level artefacts normally belong under **Internal units** on the parent page.

Split an internal unit into its own component page only when it is independently deployable/scheduled/operated, reused across multiple flows/components, attached to its own runbook, or has meaningful blast-radius impact.

## Storage/filename convention

Use descriptive kebab-case filenames beneath `_curated/components/`. Grouping folders may mirror useful TeamA/domain structure, but the stable page `id` is a logical identity and is **not derived from the path**.

Example:

```text
_curated/components/sds/sds-generic-client.md
id: atlas-comp.sds.sds-generic-client
```

Moving the file does not require changing its ID.

## Required frontmatter/type-specific fields

Start from `_template.md`. Use `type: atlas.component`, `package: teama`, the common curated envelope and these component fields:

```yaml
component_type: unknown
component_scope: unknown
repository: ""
monorepo_path: ""
deployed_as: []
contains_internal_units: false
```

Relationships are authored in frontmatter `relationships:`; generated maps are projections and must not be hand-edited.

## Relationship guidance

Use only relationships defined in `taxonomy/relationships.yaml`.

Typical component relationships include:

- `atlas.consumes` for APIs/events/tables/files/config/job outputs/libraries;
- `atlas.produces` for outputs exposed or published by the component;
- `atlas.depends-on` for meaningful component or external dependencies;
- `atlas.participates-in` for flow participation;
- `atlas.deployed-by` for deployment/infrastructure relationships;
- `atlas.must-follow` for applicable standards.

For `atlas.consumes`, `atlas.produces` and `atlas.depends-on`, include a valid `kind`. Preserve relationship-level confidence and evidence. Never infer "not affected" from an absent edge.

## Evidence expectations

Material claims should be traceable to one or more of:

- staging evidence;
- repository/monorepo paths;
- README or local `CLAUDE.md`;
- build/dependency metadata;
- source/config/schema paths;
- infrastructure definitions;
- runbooks or incident learnings;
- external Jira/Confluence/SharePoint references;
- reviewer-confirmed statements.

If evidence is incomplete, keep the claim possible/unconfirmed or record the gap under coverage limits.

## `not covered` rule

When a required section genuinely has no evidence, use exactly:

```markdown
*Not covered — no evidence in current staging material.*
```

Do not add plausible filler merely to make the page look complete.

## Agent curation instructions

Before proposing a component change, read this README, `_template.md` and `index.md`. Search existing pages by stable ID, aliases, repository path and semantic match before creating a new page. Preserve staging evidence and uncertainty, update the relevant index, rebuild maps, update curation status/review records, and run validation.

## Reviewer checklist

Before approval, verify:

- component identity and granularity are appropriate;
- responsibility/location are evidenced;
- internal units are not over-split;
- consumes/produces/flow/infra relationships are supported;
- local relationship targets resolve where required;
- uncertainty and coverage limits are explicit;
- the page is indexed and generated maps remain consistent;
- no secrets or sensitive data were introduced.

## Index maintenance rule

Every non-archived component page must appear in `index.md`. Archived pages remain in Git/history but are excluded from normal routing.

## Security/sensitivity reminder

Never capture credentials, tokens, customer data, raw sensitive logs, connection strings or unnecessary personal data. Link to authorised sources rather than copying sensitive material into Atlas.

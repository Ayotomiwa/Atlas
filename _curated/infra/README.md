# Infrastructure policy

## Purpose

`_curated/infra/` stores reviewed knowledge about meaningful infrastructure packages/templates and selectively promoted resources that matter for routing, operations or impact analysis.

An infra page should help answer: **what does this package define or configure, what resources matter, who/what uses them, and what could be affected if they change or are deleted?**

## Trust level

Only `status: curated` pages are authoritative. `draft` pages remain subject to human review. Claude may propose infrastructure knowledge but never self-approve it.

## When to use this area

Use an infra page for stable knowledge about:

- an IaC/service-catalogue package or template;
- environment configuration that changes behaviour/risk;
- important shared or operationally significant resources;
- schedules, triggers, roles, permissions and monitoring;
- component/flow use of infrastructure;
- package/resource deletion or change impact.

## When not to use it

Do not create an infra page for every low-level resource, environment file, helper script, log group or IAM statement. Do not store application implementation detail, raw template dumps, full incident records or unsupported blast-radius claims here.

## Granularity rule

Normally use one page per meaningful infra package/template. Keep lower-level resources as internal resources unless they are shared, independently operated, incident-relevant, security-sensitive, deletion-sensitive, flow-critical, monitored, or a significant blast-radius node.

A promoted resource should have an explicit reason for promotion; promotion is for impact analysis, not completeness theatre.

## Storage/filename convention

Use stable kebab-case filenames in `_curated/infra/`. The logical page ID is not path-derived and remains stable across file moves.

## Required frontmatter/type-specific fields

Start from `_template.md` and include:

```yaml
infra_package: ""
template_path: ""
resource_names: []
environments: []
promoted_resources: []
```

## Relationship guidance

Author relationships on curated Markdown only using the approved taxonomy. Infra `atlas.depends-on`, `atlas.deployed-by` and resource-usage relationships feed the infra dependency projection. Flow participation/usage may also surface in routing maps where appropriate.

Do not move ordinary component/API/data relationships into the infra map merely because AWS or IaC is involved. Keep the semantic owner of the relationship clear.

## Evidence expectations

Evidence may include:

- staging infra evidence;
- IaC package paths;
- Terraform/CloudFormation/CDK/SAM/service-catalogue definitions;
- metadata and environment configuration;
- parameters/imports/exports;
- schedule/trigger definitions;
- IAM/permission references;
- component/flow pages;
- runbooks and incident learnings;
- reviewer-confirmed statements.

Promoted resources require evidence plus a defensible promotion reason.

## `not covered` rule

Use exactly `*Not covered — no evidence in current staging material.*` where a required section lacks evidence. Do not infer hidden resources, permissions or consumers.

## Agent curation instructions

Before proposing an infra change, read this README, `_template.md` and `index.md`. Identify the package boundary first, distinguish internal from promoted resources, preserve evidence/uncertainty, update curated relationships rather than maps directly, rebuild maps, update status/review records and run validation.

## Reviewer checklist

Verify:

- package/template identity and path;
- environment differences that matter;
- resource modelling is not over-split;
- every promoted resource has a reason;
- component/flow/resource relationships are evidenced;
- permissions/triggers/monitoring are represented accurately;
- impact language separates known, possible and unknown;
- indexes/maps are consistent;
- no sensitive material is embedded.

## Index maintenance rule

Every non-archived infra page must appear in `index.md`. Archived pages remain in history but are excluded from normal routing.

## Security/sensitivity reminder

Never store credentials, secret values, tokens, customer data or raw sensitive production logs. For security-sensitive resources, record identifiers/relationships only when appropriate and link to authorised systems for sensitive detail.

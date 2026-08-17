---
id: STG-YYYYMMDD-<slug>
type: staging.infra
package: datalens
timestamp: YYYY-MM-DD
title: ""
description: ""
status: new
captured_by: ""
source_type: ""
---

# Infrastructure evidence: <package or topic>

> Store this record at `_staging/infra/<candidate-domain-or-unassigned>/<STG-ID>.md`. Use exactly one grouping folder. Choose a candidate domain only when evidence or a user confirmation supports it; otherwise use `unassigned`. Do not encode repository or package paths in the grouping, and remember that the committed path remains immutable.

> Capture the package/resource context deeply enough to preserve structure, relationships and operational significance. This is raw evidence, not a trusted infrastructure model. Do not promote every resource or infer consumers/blast radius from names alone.

## Summary

State what package or infrastructure context was inspected, what question triggered the work, and why the result is reusable. Use plain technical language before Atlas terms.

### Candidate package identity and scope

- Package/module/template name:
- Repository:
- Package path within repository:
- Primary IaC/service-catalogue template:
- Metadata/deployment descriptor:
- Helper/preconfiguration script:
- Environment/config locations:
- Related deployment/source location:
- Scope state: `observed` / `user-confirmed` / `possible` / `not-covered`

## Evidence

Capture exact attributable infrastructure/config references where available.

- Package/module path:
- Template/IaC file:
- Metadata/deployment descriptor:
- Environment config/overlay:
- Resource/logical ID definition:
- Parameter/import/export:
- Schedule/trigger/event definition:
- IAM/permission reference:
- Monitoring/alarm/log definition:
- Component/flow reference:
- Runbook/incident reference:
- Engineer/user-confirmed statement:
- Other:

## What is known

Record only **observed** or **user-confirmed** findings below.

### Package location and structure

Capture only files/paths that matter to understanding deployment, configuration, resources or operation.

| Path | Type | Purpose | Evidence | State |
|---|---|---|---|---|
| | template/metadata/script/environment-config/source/module/other | | | observed/user-confirmed |

### Package and resource behavior

Explain causally how deployment or execution introduces the important resources and how evidenced reads, writes, triggers, schedules, permissions, monitoring, or deployment actions connect them to components and flows. Distinguish declared configuration from observed runtime behavior.

- Deployment/execution path:
- Resource responsibilities and causal interactions:
- Component/flow use:
- Operational and change significance:
- Coverage limits:

### Environment differences

Record differences only where they affect behaviour, deployment, permissions, routing, operation or risk.

| Environment/context | Path/source | Difference / effect | Evidence | State |
|---|---|---|---|---|
| | | | | observed/user-confirmed |

### Internal resources

Do not create separate Atlas concepts merely because a resource exists.

| Resource/logical ID | Type | Defined/referenced in | Purpose | Why operationally significant, if known | Evidence |
|---|---|---|---|---|---|
| | function/job/queue/topic/bucket/database/role/policy/scheduler/alarm/cluster/network/other | | | | |

### Observed resource relationships

Preserve source semantics. Final curated facts use the natural field that matches the observed action, such as `reads_from`, `writes_to`, `triggers` or `scheduled_by`; relationship verbs are not an author taxonomy.

| From resource | Observed relationship/behaviour | To resource/value | Source | State |
|---|---|---|---|---|
| | triggers/reads/writes/imports/exports/depends/permission/alarms-on/other | | | observed/user-confirmed |

### Components using resources

| Component | Resource | Observed use/relationship | Evidence | State |
|---|---|---|---|---|
| | | | | observed/user-confirmed |

Only include component usage when it is supported; a resource definition does not prove a consumer.

### Flows using resources

| Flow/candidate flow | Resource/package | Role in path | Evidence | State |
|---|---|---|---|---|
| | | | | observed/user-confirmed |

### Parameters, imports and exports

| Name | Kind | Defined/produced by | Consumed/referenced by | Evidence |
|---|---|---|---|---|
| | parameter/import/export/output/shared-value/other | | | |

### Schedules, triggers and events

| Trigger/schedule/event | Target | Definition/frequency/event | Evidence |
|---|---|---|---|
| | | | |

### Permissions and roles

Describe material access relationships without copying secret values or unnecessary security-sensitive detail.

| Role/policy/permission | Allows/controls | Used by / applies to | Evidence |
|---|---|---|---|
| | | | |

### Monitoring and operational relevance

| Alarm/log/dashboard/monitor | Watches | Operational meaning / signal | Evidence |
|---|---|---|---|
| | | | |

### Change/deletion impact evidence

Record only impact directly observed or explicitly user-confirmed here. Put plausible blast radius in the next section.

| Item/scenario | Known observed/confirmed impact | Evidence | Coverage limit |
|---|---|---|---|
| | | | |

### Resource promotion evidence

Use the canonical [curated resource-promotion criteria](../../_curated/infra/README.md#resource-promotion). Record evidence for later review; do not decide promotion in staging.

| Resource | Applicable criterion/observation | Evidenced users or operational route | Confidence/gap | Evidence |
|---|---|---|---|---|
| | | | observed / user-confirmed / possible / not covered | |

## What is possible / unconfirmed

Capture relationships, consumers, significance and blast-radius implications that remain plausible but unsupported.

| Possible relationship/resource significance/impact | Why plausible | Evidence needed to confirm |
|---|---|---|
| | | |

Examples include an assumed consumer of an export, a likely cross-package dependency, an inferred permission path, or possible downstream impact. Do not promote these because resource names, stacks or timestamps happen to align.

## Suggested curated targets

List only evidence-supported durable targets, for example:

- `_curated/infra/...`
- related `_curated/components/...`
- related `_curated/flows/...`
- related `_curated/runbooks/...`
- related `_curated/incidents/...`
- curated connection fields that will regenerate `infra-dependency-map.json` or other relevant projections

Do not propose direct edits to generated map JSON as connection truth.

## Open questions

- Is the package/module/template boundary correct?
- Which package files or referenced locations remain inaccessible?
- Which environment differences materially affect behaviour or risk?
- Which resources are confirmed versus only referenced by name?
- Which resource-to-resource relationships are explicit?
- Which components actually use each important resource?
- Which flows depend on these resources?
- Are parameters/imports/exports crossing package boundaries?
- Which schedules/triggers/events control execution?
- Which permissions/roles matter operationally and remain unverified?
- Which alarms/logs/dashboards are meaningful during support?
- Which resources, if any, show evidence strong enough to consider promotion?
- What change/deletion impact is known, possible or simply not covered?

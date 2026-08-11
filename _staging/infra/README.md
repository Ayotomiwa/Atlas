# Infrastructure staging

## Purpose

`_staging/infra/` captures raw, attributable evidence about TeamA infrastructure packages, IaC definitions, environment configuration and resource relationships **before any infrastructure claim is trusted**.

Use this bucket when the important knowledge is primarily about infrastructure rather than application/component behaviour.

A useful infra entry should help an investigator answer:

> **What infrastructure package or resource context exists, how is it structured, what does it create/connect, who uses it, and what evidence exists about operational or blast-radius significance?**

## Belongs here

Capture evidence about:

- an IaC/service-catalogue package, module or template and its location;
- CloudFormation/SAM/Terraform/CDK or equivalent infrastructure definitions;
- service/deployment metadata and helper/preconfiguration scripts;
- environment overlays or configuration that materially change behaviour/risk;
- queues, topics, buckets, functions/jobs, databases, clusters, roles, policies, parameters, schedulers or alarms when relevant to the package context;
- resources created, referenced, imported or exported;
- resource-to-resource relationships;
- schedules, triggers and events;
- permissions/roles and access relationships;
- alarms, dashboards, logs and operational monitors;
- components or flows using infrastructure when evidenced;
- change/deletion impact evidence or operational significance discovered during investigation.

Generic examples of useful discoveries include:

```text
an IaC package whose environment overlays alter deployment behaviour
a queue triggering a worker/function
a bucket read by a processing job
a scheduler starting a pipeline step
a role granting a component access to a resource
an alarm exposing a failure condition used during support
an exported value consumed by another package
```

These are examples of **shapes**, not TeamA production facts.

## Does not belong here

Do not use this bucket for:

- ordinary component implementation detail — use `_staging/components/`;
- a one-off logical MR/change summary — use `_staging/changes/`;
- a complete end-to-end flow narrative — use `_staging/flows/`;
- standalone schema/business semantics — use the relevant staging bucket;
- full incident records or raw sensitive operational data;
- entire IaC/template dumps when targeted evidence is sufficient;
- unsupported resource relationships inferred solely from similar names.

If infrastructure knowledge was discovered during a change, it may first appear in `_staging/changes/`; create dedicated infra evidence when the package/resource context is reusable enough to deserve focused capture.

## Granularity

Stage the **meaningful infrastructure package/context first**. An entry may describe the package layout and multiple internal resources without creating one staging file per cloud resource.

Lower-level resources normally remain internal evidence. When a resource looks operationally significant, capture evidence against the canonical [curated resource-promotion criteria](../../_curated/infra/README.md#resource-promotion). This is **input to a later promotion decision, never the decision itself**.

## Discovery lenses

A focused infra investigation should look for the following when available:

| Lens | Useful questions |
|---|---|
| Package identity | What package/module/template is this and where does it live? |
| Structure | Which templates, metadata, scripts, environment folders or source/config files matter? |
| Environments | What actually differs across environments and why does it matter? |
| Internal resources | What resources are defined/referenced and where? |
| Resource links | What triggers, reads, writes, imports, exports or depends on what? |
| Component usage | Which components use which resources, and how? |
| Flow usage | Which flows rely on these resources for execution/routing? |
| Parameters/exports | Which values cross package/deployment boundaries? |
| Scheduling/events | What starts or coordinates resource activity? |
| Permissions | Which roles/policies grant material access, without copying secrets? |
| Monitoring | Which alarms/logs/dashboards expose meaningful operational state? |
| Impact | What evidence exists about change/deletion consequences, and what remains unknown? |

These are capture prompts, not a requirement to fabricate completeness.

## Resource relationship discipline

Do not turn every provider-specific property into an Atlas relationship. Preserve relationships that matter for understanding routing, operation or impact.

Useful evidence may show that one resource triggers, reads from, writes to, imports from, exports to, is deployed by or otherwise depends on another. Curation chooses the matching natural field; staging may preserve source wording while keeping unsupported mapping decisions open.

Keep ordinary application/API/data relationships with their semantic owner rather than forcing them into infrastructure merely because a cloud resource is involved.

## Resource promotion evidence

Curation decides promotion against the canonical [resource-promotion criteria](../../_curated/infra/README.md#resource-promotion). Staging must give that decision enough attributable evidence to work with:

1. the resource identity/logical ID;
2. where it is defined;
3. which canonical criterion or criteria may apply and what was observed;
4. the source supporting each observation;
5. which components, flows, packages or runbooks use it, when evidenced;
6. confidence and what remains possible/unconfirmed.

Do not assume every resource should become a promoted impact-analysis node.

## Evidence expectations

Prefer concrete references such as:

- package/template/module paths;
- service/deployment metadata;
- environment configuration;
- logical/resource IDs;
- parameters, imports and exports;
- scheduler/event/trigger definitions;
- IAM/permission references;
- monitoring definitions;
- linked component/flow evidence;
- runbook/incident references;
- explicit engineer/user-confirmed explanations.

Evidence of a resource definition does **not** automatically prove who uses it or what breaks if it changes.

## Evidence and uncertainty states

Keep these states distinct:

- **observed** — directly supported by accessible source/config/documentation;
- **user-confirmed** — explicitly supplied/confirmed by the user or engineer;
- **possible / unconfirmed** — plausible but still missing evidence;
- **not covered** — not investigated, inaccessible or outside supplied evidence.

## Likely curated targets

Evidence may support `_curated/infra/` and linked component/flow/runbook/incident pages. Reviewed connection fields may later regenerate the infra/flow projections.

Do **not** hand-maintain generated map connections from staging. Curated Markdown fields remain the authoring source of truth.

## Immutability

After first commit, only top-level frontmatter `status` may change. The body, provenance, title, description, path and ID remain immutable; corrections require a follow-up staging record.

## Reviewer questions

Before accepting curated infra knowledge, confirm:

- Is the package/module/template boundary correct?
- Which environment differences materially affect behaviour or risk?
- Which resources are merely internal versus operationally significant?
- Why would any lower-level resource merit promotion?
- Which resource relationships are explicit versus inferred?
- Which components and flows actually use the resources?
- Are imports/exports/parameters and triggers represented accurately?
- Are permissions described without exposing sensitive values?
- Which monitors/alarms are genuinely operationally relevant?
- Is change/deletion impact known, only possible, or not covered?

## Security and sensitivity

Never stage credentials, tokens, secret values, customer data, raw sensitive production logs, connection strings or unnecessary security-sensitive configuration. Record identifiers/relationships where appropriate and link to authorised sources for restricted detail.

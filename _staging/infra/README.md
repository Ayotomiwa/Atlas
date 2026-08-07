# Infrastructure staging

## Purpose

`_staging/infra/` captures raw evidence about TeamA infrastructure packages, IaC definitions, configuration and resource relationships before any infrastructure claim is trusted.

## Belongs here

Capture evidence about:

- IaC/service-catalogue package identity and path;
- Terraform/CloudFormation/CDK/SAM definitions;
- environment configuration that matters;
- resources created/referenced/imported/exported;
- schedules, triggers and events;
- roles/permissions and monitoring;
- components or flows using resources when evidenced;
- deletion/change impact evidence.

## Does not belong here

Do not use this bucket for ordinary component implementation detail, a one-off MR summary, a complete flow narrative or unsupported resource relationships. Do not dump entire templates when targeted evidence is enough.

## Granularity

Stage the meaningful infra package/context first. Lower-level resources remain internal evidence unless they are shared, independently operated, incident/security/deletion sensitive, flow-critical or otherwise meaningful for impact analysis.

## Resource promotion evidence

A future curated page may promote important resources for impact analysis, but staging should record **why** a resource appears significant rather than assuming every cloud resource deserves first-class treatment.

## Evidence expectations

Prefer package/template paths, environment config, logical/resource IDs, parameters/imports/exports, IAM references, triggers/schedules, monitoring references and linked component/flow evidence. Mark inferred relationships as possible/unconfirmed.

## Likely curated targets

Evidence may support `_curated/infra/`, linked component/flow pages and regenerated infra/flow maps. Keep ordinary repo relationships separate from infrastructure relationships.

## Immutability

Once referenced by a curation proposal, do not modify or move the evidence. Add a corrective record.

## Reviewer questions

Confirm package boundaries, environment differences, important resources, users/consumers, permissions/triggers and which resources genuinely merit impact-analysis promotion.

# Flows staging

## Purpose

`_staging/flows/` captures raw evidence about an end-to-end TeamA operational or data path before the flow is trusted.

## Belongs here

Use this bucket when evidence primarily describes how multiple meaningful steps/components work together, including:

- entry point and end point;
- ordered observed steps;
- participating components/jobs;
- upstream inputs and downstream consumers;
- schedules/orchestration;
- data/API/event/file outputs;
- infrastructure used by the path;
- runbook or incident context.

## Does not belong here

Do not use it for a single component description, one MR/change, raw infra-package discovery or a full incident record. Do not invent missing steps to make the flow look complete.

## Flow boundary rule

A staged flow needs a defensible boundary. If the end-to-end boundary is not observed or user-confirmed, keep that gap explicit rather than creating a fake complete flow. The service-onboarding workflow should not stage unsupported flow placeholders.

## Evidence expectations

Useful evidence includes repository/config paths, orchestration definitions, schemas/contracts, component names, infra definitions, operational docs and engineer walkthroughs. Mark inferred ordering or relationships as possible/unconfirmed.

## Likely curated targets

Evidence may support `_curated/flows/` plus linked component/infra/schema/runbook/incident pages and generated relationship projections. Only propose targets supported by the evidence.

## Immutability

Once consumed by a curation proposal, this file and path are immutable. Add corrective evidence rather than rewriting history.

## Reviewer questions

Confirm the flow boundary, trigger, ordered steps, participants, upstream/downstream claims and missing consumers before accepting curated flow knowledge.

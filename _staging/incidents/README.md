# Incidents staging

## Purpose

`_staging/incidents/` captures raw but **sanitised reusable operational evidence** from incidents, near misses, exercises and failure investigations.

It exists to preserve what Atlas should learn, not to become a second incident-management system.

## Belongs here

Capture reusable evidence such as:

- observed impact/failure pattern;
- detection signals and gaps;
- confirmed or suspected technical cause, clearly distinguished;
- recovery observations;
- dependency/flow/infra context discovered during triage;
- runbook gaps;
- standard/process gaps;
- monitoring lessons;
- links to the authorised full incident record.

## Does not belong here

Do not store:

- the full major-incident record or exhaustive timeline;
- live incident status updates;
- raw sensitive logs/screenshots;
- customer data or unnecessary personal data;
- blame-oriented narrative;
- suspected cause presented as confirmed;
- a full reusable recovery procedure — use `_staging/runbooks/` when drafting one.

## Sanitisation and evidence rule

Stage only the minimum information needed for reusable engineering learning. Link to restricted incident systems for full detail.

Separate:

- observed impact;
- confirmed cause;
- suspected/possible cause;
- recovery actually performed;
- reusable learning inferred from the evidence.

## Granularity

One staging entry should cover a coherent incident/near-miss/exercise learning context. It may later produce multiple curated updates (incident learning, flow, component, infra, runbook, standard) if the evidence supports them.

## Curation outcomes

Curation may create/update a sanitised `_curated/incidents/` learning page and related governed context. It may also decide that an incident is too specific, sensitive or non-reusable for Atlas.

## Immutability

Once referenced by curation, do not edit/move the staging entry. Add a corrective/follow-up record if investigation findings change.

## Security and sensitivity

Redact aggressively. Never stage credentials, customer data, personal details, raw restricted logs, security-sensitive exploit detail or other content that should remain in the incident system.

# Components staging

## Purpose

`_staging/components/` captures raw, attributable evidence about a TeamA repository, service, job, API, library or other meaningful implementation component.

Use it to preserve **what was found and what is still unknown** before any component knowledge becomes trusted.

## Belongs here

Capture evidence such as:

- component/repository identity and location;
- observed responsibility;
- build/dependency metadata;
- important source/config/schema paths;
- known inputs and outputs;
- related flows or infrastructure when evidenced;
- internal units worth recording;
- operational/runbook/standard references;
- explicit engineer-supplied context.

A component record may be incomplete; missing context should be visible rather than guessed.

## Does not belong here

Do not use this bucket for a single MR/change (`changes/`), a full end-to-end flow (`flows/`), raw infrastructure discovery (`infra/`), or polished/authoritative conclusions (`_curated/components/`). Never invent owners, consumers, dependencies or runtime behaviour.

## Granularity

Stage the meaningful component first. Do not create one staging record per handler/Lambda/script merely because those files exist. Lower-level units can be listed as evidence unless independently meaningful.

## Evidence expectations

Prefer repository paths, README/CLAUDE guidance, build files, source/config/schema paths, infra definitions, runbooks, tickets/docs and clearly labelled engineer statements. Distinguish observed/user-confirmed from possible/unconfirmed.

## Likely curated targets

A component staging record may lead to:

- `_curated/components/`;
- component relationships that regenerate repo/flow/infra maps;
- linked flow/infra/schema/runbook/standard pages where evidence supports them.

Do not create empty linked evidence files just because a category is missing.

## Immutability

Once referenced by a curation proposal, do not alter or move this evidence. Add a corrective staging record instead.

## Reviewer questions

Before curation, ask whether identity, responsibility, consumes/produces relationships, flow participation and infrastructure use are actually evidenced and whether any key context is inaccessible.

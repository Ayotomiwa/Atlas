# Business Concepts staging

## Purpose

`_staging/business-concepts/` captures raw supplied meaning, terminology and boundary evidence before it becomes a reviewed TeamA business definition.

Use this bucket to preserve **what a source or knowledgeable person actually said**, including ambiguity or disagreement, without prematurely normalising it into a curated definition.

## Belongs here

Capture evidence such as:

- supplied definitions and terminology;
- inclusion/exclusion rules;
- aliases and variants;
- edge cases and examples;
- conflicting definitions from different sources;
- domain documentation references;
- user/SME explanations;
- links to schemas or components that use the term, clearly separated from semantic authority.

## Does not belong here

Do not use this bucket for:

- a physical schema/contract investigation — use `_staging/schema-info/`;
- implementation responsibility — use `_staging/components/`;
- a one-off Jira requirement that is not reusable business meaning;
- inferred definitions built from code, column or UI names alone;
- customer/case details used merely as examples;
- a silently reconciled "best" definition when sources disagree.

## Meaning-preservation rule

Preserve original wording where it helps reviewers understand provenance. If two sources conflict, record both and the conflict. Do not have Claude choose a winner without evidence/human review.

Observed implementation usage may show **where a term is used**; it does not by itself establish the approved meaning.

## Granularity

Stage one coherent concept or closely related terminology question per entry. Split unrelated terms so each future definition can be reviewed independently.

## Curation outcomes

A staging entry may become/update a `_curated/business-concepts/` page, or be deferred/rejected if the meaning is local, transient, duplicated or insufficiently approved. Related schema/component links may be proposed only when evidence supports them.

## Immutability

Once referenced by a curation proposal, do not edit/move the record. Add a follow-up staging entry for corrections or newly agreed meaning.

## Security and sensitivity

Do not include customer examples, personal data, confidential case detail or restricted policy text unnecessarily. Prefer sanitised examples and authorised links.

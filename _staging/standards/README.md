# Standards staging

## Purpose

`_staging/standards/` captures **candidate reusable engineering rules, conventions and evidence of team practice** before human review decides whether they are actually TeamA standards.

This bucket is especially important for `atlas-onboard-standards`: repository patterns can be evidence, but repeated code must not automatically become policy.

## Belongs here

Capture evidence such as:

- explicit team/lead guidance;
- repeated language/framework conventions;
- CI/build/test patterns;
- `.editorconfig`, linter or formatter conventions;
- AWS/infra patterns;
- data/testing/Git/Jira practices;
- documented exceptions;
- conflicting practices across repositories;
- candidate rationale and examples;
- source paths showing how consistently a rule appears.

## Does not belong here

Do not use this bucket for:

- a skill procedure — use `.claude/skills/`;
- one repo's local build/run commands;
- a one-off Jira instruction;
- organisation/security policy copied without authority;
- a pattern observed once and labelled mandatory;
- secrets or restricted configuration.

## Evidence versus authority

Classify findings carefully:

- **explicit** — a supplied/authoritative statement says this is the rule;
- **repeated practice** — multiple independent sources implement the same pattern;
- **local convention** — limited to one repository/context;
- **possible** — plausible but insufficient evidence.

Frequency is not the same as mandate. `mandatory` and scope are curation decisions backed by authority.

## Granularity and categories

Stage one coherent rule/theme per entry when practical. Record the likely category (`general`, `java`, `python`, `aws`, `infra`, `jira`, `data`, `testing`, `git`) but do not force a category when evidence is ambiguous.

Separate unrelated standards so reviewers can accept/reject them independently.

## Curation outcomes

A staged candidate may become/update `_curated/standards/<category>/...`, be merged into an existing standard, be scoped as repo-local and rejected from Atlas, or be deferred for stronger evidence.

## Immutability

Once consumed by a curation proposal, do not modify/move the staging record. Add follow-up evidence when practice changes or authority is clarified.

## Security and sensitivity

Do not copy secrets, credentials, internal restricted controls or sensitive policy text. Link to organisation-level authority when Atlas should reference rather than reproduce it.

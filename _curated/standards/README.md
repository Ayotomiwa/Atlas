# Standards policy

## Purpose

`_curated/standards/` stores reviewed, reusable TeamA engineering rules and conventions. Standards are team knowledge consumed by humans and skills such as `implement-jira`; reusable skill procedures should resolve standards from Atlas rather than hard-code team-specific choices.

A standard page should help answer: **what rule applies, to whom, how strong is it, why does it exist, what behaviour is required or recommended, and what exceptions are valid?**

## Trust level

Only merged `status: curated` standards are authoritative TeamA knowledge. Claude may author lifecycle metadata and consolidate evidence in a proposal, but human-reviewed merge approves mandate, scope and exceptions.

## When to use this area

Use a standard page for durable guidance that should be applied repeatedly across engineering work, including:

- language/framework conventions;
- AWS or infrastructure patterns;
- data and testing rules;
- Jira/implementation workflow expectations;
- Git/review conventions;
- team-wide mandatory or recommended behaviour;
- documented exceptions and specialisations.

## When not to use it

Do not use standards for:

- a one-off design decision or ticket-specific instruction;
- raw evidence of repeated practice — stage it first in `_staging/standards/`;
- repo-local commands better owned by the product repo README/`CLAUDE.md`;
- organisation/security policy rewritten without authority;
- a skill procedure that belongs in `.claude/skills/`;
- advice inferred from one repository and presented as a team rule.

## Granularity rule

Create one page per reusable rule or tightly coupled policy set that has a coherent scope and rationale. Avoid giant "all Java" or "all AWS" pages when independent rules need different evidence, mandatory status, scope or exceptions.

Conversely, do not split every sentence into a separate standard. A page should represent a rule engineers can meaningfully discover and apply.

## Storage/filename convention

Curated standards are grouped by category. Canonical categories are defined in `taxonomy/standard-categories.yaml`, for example:

```text
_curated/standards/general/<slug>.md
_curated/standards/java/<slug>.md
_curated/standards/python/<slug>.md
_curated/standards/aws/<slug>.md
_curated/standards/infra/<slug>.md
_curated/standards/jira/<slug>.md
_curated/standards/data/<slug>.md
_curated/standards/testing/<slug>.md
_curated/standards/git/<slug>.md
```

The category folder is organisational. The page remains `type: standard`, and moving a page does not change its stable ID. The physical category folder should match `standard_category`.

## Required frontmatter/type-specific fields

Start from `_template.md`. Use the common curated envelope plus:

```yaml
standard_category: general
requirement_level: unknown
```

`standard_category` must exist in the standard-category taxonomy and match the storage folder.

`requirement_level` is controlled by `taxonomy/concept-fields.yaml`: `required`, `recommended`, `mixed` or `unknown`. A `status: curated` standard cannot use `unknown`; applicability, exclusions and approved exceptions stay in the body with evidence.

## Relationship guidance

Use only page-link types registered in `contracts/map-fields.yaml`.

Common standard relationships include:

- `extends` when a standard specialises or adds constraints to another;
- `supersedes` when a new standard replaces an older one;
- `must-follow` from governed components/flows/concepts to this standard;
- `informed-by` when incident learning or reviewed evidence materially shaped the rule.

An extension may specialise a parent standard but should not silently weaken mandatory security, regulatory or organisation-level requirements.

## Evidence expectations

A standard should show why it is a **team standard**, not merely a pattern observed once. Useful evidence includes:

- explicit team/lead agreement;
- approved engineering documentation;
- repeated consistent repository evidence;
- `.editorconfig`, build, CI or scaffold conventions;
- policy references;
- reviewed incident learning;
- staging evidence from standards discovery.

Repeated code is evidence of practice, not proof of mandate. Keep `requirement_level: unknown` until authority supports a stronger classification; resolve it before authoritative curation.

## `not covered` rule

When a required section has no evidence, use exactly:

```markdown
*Not covered — no evidence in current staging material.*
```

Do not invent rationale, exceptions or mandatory status.

## Agent curation instructions

Before proposing a standard, read this README, `_template.md`, the root standards `index.md`, the target category `index.md`, `taxonomy/standard-categories.yaml` and existing related standards. Search for semantic overlap before creating a new page. Preserve disagreements and evidence strength, distinguish required from recommended behaviour, and never promote observed convention to mandatory policy without support.

## Reviewer checklist

Before approval, verify:

- the rule is reusable rather than ticket-specific;
- category and scope are correct;
- `requirement_level` is justified by evidence and is not `unknown` for a curated standard;
- required vs recommended behaviour is unambiguous;
- examples and anti-patterns match the rule;
- exceptions are explicit and bounded;
- overlaps/extensions/supersession with existing standards are resolved;
- the root and category indexes are updated;
- no sensitive internal policy content has been copied beyond what Atlas should store.

## Index maintenance rule

Every non-archived standard must be discoverable from `_curated/standards/index.md` and its category `index.md`. Archived standards remain in place/history but are excluded from normal routing.

## Security/sensitivity reminder

Do not weaken mandatory security or regulatory requirements through a team standard. Avoid copying secrets, restricted controls or sensitive configuration. Link to authoritative organisation-level policy where Atlas should reference rather than reproduce it.

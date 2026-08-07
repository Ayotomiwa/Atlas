# TeamA Atlas

## Purpose

TeamA Atlas is a governed engineering context layer for humans and AI agents. It exists so reusable engineering context can be discovered once, reviewed, versioned and routed back into future engineering work instead of being repeatedly rediscovered from repositories, chats and scattered documentation.

This public V1 is a **scaffold only**. It contains no real TeamA engineering facts.

Atlas is not a replacement for source code, incident-management systems, service catalogues, Jira or Confluence. It stores durable engineering context that is valuable to reuse across those systems while preserving links back to evidence.

## Pilot scope

V1 contains one TeamA package only: `teama`.

The owner name `team-a-engineering` is a placeholder and must be replaced before internal adoption or protected-branch review is enforced. V1 deliberately does not implement `atlas-core`, multi-team federation, an enterprise crawler, a vector database, a UI or autonomous semantic approval.

## Trust model

Atlas separates evidence from reviewed knowledge:

```text
source / repository / engineer evidence
        ↓
_staging/ — raw evidence + lifecycle status, never authoritative
        ↓
Claude-assisted curation proposal
        ↓
Atlas PR/MR + human review
        ↓
_curated/ — authoritative only when status: curated on the governed/default branch
```

A file being under `_curated/` does not automatically make it authoritative. `draft` and `proposed` pages are reviewable knowledge; only `status: curated` on the governed/default branch is trusted within the page's stated coverage.

Claude may discover, stage and propose. Claude does not self-approve or merge semantic knowledge.

## Repository structure

| Area | Responsibility |
|---|---|
| `_staging/` | attributable raw evidence, explicit uncertainty and per-record curation lifecycle |
| `_curated/` | durable reviewed/proposed engineering concepts |
| `_curated/maps/` | deterministic relationship projections generated from curated Markdown |
| `_curated/status/` | compact latest curation checkpoint, not a per-record ledger |
| `taxonomy/` | controlled types, relationships, statuses and standard categories |
| `onboarding/` | bounded evidence-capture guidance and questionnaires |
| `.claude/skills/` | reusable Claude workflows |
| `.claude/agents/` | specialist read/write roles with explicit boundaries |
| `scripts/` | lint, ID/link/taxonomy checks and map generation |
| `tests/` | deterministic unit tests, fixtures and skill evals |
| `log.md` | significant Atlas-level milestones only |

The Atlas PR/MR and Git history are the durable human review/audit trail for curation; V1 does not maintain a second `reviews/` Markdown system.

## File responsibilities

Atlas deliberately spreads responsibility across several file types rather than building one giant instruction file:

| File/type | Owns |
|---|---|
| root `CLAUDE.md` | rules for Claude maintaining Atlas itself |
| `package.md` | package identity, entrypoints, map/taxonomy routes |
| folder `README.md` | local semantic policy, scope, granularity, evidence and reviewer rules |
| `_template.md` | exact authoring/capture shape for a new page |
| `index.md` | compact routing/catalogue of existing knowledge |
| staging page | captured evidence plus its own lifecycle status |
| curated concept page | the actual durable engineering knowledge |
| `.claude/skills/*/SKILL.md` | procedures/workflows |
| generated map JSON | machine-readable projection of curated relationships |
| Atlas PR/MR | curation review reasoning, approvals, comments and merge history |

A template is not a substitute for its README, and an index is not a second source of truth.

## Knowledge model

### Components

`_curated/components/` describes meaningful repositories, services, deployable units, scheduled job groups and reusable libraries. Component pages explain responsibility, location, internal units, consumes/produces relationships, flow participation, infrastructure and operational context.

Do not create one component page for every handler, Lambda, SQL file or script. Lower-level artefacts normally remain internal units unless independently meaningful.

### Flows

`_curated/flows/` describes end-to-end operational or data paths across meaningful steps/components. A flow may cross multiple repositories. Flow pages explain the boundary, trigger, sequence, participants, contracts/hand-offs, upstream/downstream dependencies, schedules, infrastructure, failure modes and operational guidance.

### Infrastructure

`_curated/infra/` describes meaningful infrastructure packages/templates and selectively promoted resources. Package structure, environments, internal resources, parameters/imports/exports, schedules/triggers, permissions, monitoring and impact all matter; Atlas does not create one page for every cloud resource by default.

### Schema information and business concepts

`_curated/schema-info/` separates physical data/contract identity from reviewed semantics, while `_curated/business-concepts/` stores reviewed business definitions, boundaries and approved variants. A technically possible join or a column name is not automatically approved business meaning.

### Standards

`_curated/standards/` stores reusable TeamA engineering rules grouped by category. Repeated implementation can be evidence of practice, but frequency is not proof of policy or mandate.

### Runbooks and incident learnings

`_curated/runbooks/` stores reviewed operational procedures. `_curated/incidents/` stores sanitised reusable learning, not complete incident records. Safety, validation, rollback and uncertainty should remain explicit.

## Evidence and uncertainty

Material claims should be traceable to staging records, repository/config/schema paths, authorised external references or reviewer-confirmed sources.

Atlas distinguishes:

- **observed** — directly found in accessible evidence;
- **user-confirmed** — explicitly supplied/confirmed by a user or reviewer;
- **possible / unconfirmed** — plausible but not sufficiently evidenced;
- **not covered** — not investigated, inaccessible or unsupported by current evidence.

Missing evidence is not evidence of absence. Never claim `not affected` merely because Atlas has no relationship edge.

For required curated sections with no evidence, use exactly:

```markdown
*Not covered — no evidence in current staging material.*
```

## Maps and relationships

Relationships are authored on curated Markdown pages in frontmatter `relationships:` using the approved taxonomy.

The three V1 maps are generated projections:

- `_curated/maps/flow-component-map.json`
- `_curated/maps/repo-dependency-map.json`
- `_curated/maps/infra-dependency-map.json`

**Pages explain concepts; maps connect concepts.** Never hand-edit generated relationship data.

Use maps to route/traverse, then open the relevant pages for explanation, evidence and coverage limits.

## How to browse Atlas

Start at `index.md`, then follow the smallest relevant route:

- component/repository question → component index/page → repo map as needed;
- end-to-end behaviour → flow index/page → flow map;
- infrastructure or deletion/change impact → infra index/page → infra map;
- operational recovery → runbooks plus linked flow/component/infra and incident learning;
- standards → standards category index and applicable standard pages.

Do not read the entire Atlas repository before answering a targeted question.

## How to use Atlas from another repository

```bash
cd <product-repo>
claude --add-dir <path-to>/team-atlas
```

Cross-repo consumption relies on discovered skills plus `package.md` and indexes. The added directory's root `CLAUDE.md` is not the consumer contract.

A product repository remains the owner of exact build, test, lint and local-development commands. Atlas should reference those sources rather than duplicate drift-prone instructions.

Use `atlas-setup-repo` when a local repository should receive a small Atlas-managed routing block in its `CLAUDE.md`.

## Available Claude skills

| Skill | Use it for |
|---|---|
| `atlas-discover` | Atlas-first reusable context discovery |
| `atlas-impact` | read-only blast-radius analysis with known/possible/unknown separation |
| `atlas-stage` | capture one reusable fact as staging evidence |
| `atlas-onboard-service` | bounded deep service/repository onboarding into supported staging buckets |
| `atlas-onboard-standards` | discover candidate standards while separating policy from local/tool defaults |
| `atlas-setup-repo` | safely add/update the Atlas routing block in a product repo |
| `atlas-curate` | reconcile eligible staging evidence into a human-reviewable curated proposal |
| `implement-jira` | example reusable engineering workflow that resolves TeamA standards from Atlas |

Skills define procedures; folder READMEs/templates define the semantics and shape of the knowledge they operate on.

## Service onboarding

Use `atlas-onboard-service` for unfamiliar services. It performs bounded repository inspection, builds an evidence matrix, asks only high-value clarification questions, follows explicitly supplied accessible context locations, and stages only supported evidence.

A successfully identified service produces component staging. Flow, infra, schema, runbook or incident staging is conditional on actual evidence. Onboarding must not manufacture missing flow or infrastructure placeholders.

## Standards discovery

Use `atlas-onboard-standards` separately. It can inspect multiple repositories, but candidate findings must distinguish explicit authority, repeated practice, repo-local convention, tool defaults and unknown scope. Curation decides whether a candidate becomes a standard.

## Staging lifecycle and curation queue

Every newly captured staging record begins with:

```yaml
status: new
```

The lifecycle is:

| Status | Meaning |
|---|---|
| `new` | eligible for curation |
| `curating` | currently being reconciled; avoid duplicate work |
| `curated` | curation completed and accepted curated changes were produced |
| `no-change` | reviewed but no durable curated update was needed |
| `deferred` | blocked/insufficient evidence; not auto-eligible until explicitly reconsidered |
| `rejected` | not suitable for durable Atlas knowledge |

The record's status is the scalable queue. `_curated/status/curation-status.md` is only a latest checkpoint and must not become a giant list of staging items.

After a staging record is first committed, **only its top-level `status` may change**. Evidence content, provenance, title/description, ID and path remain immutable. Corrections and additional findings are new staging records.

For concurrent work, `atlas-curate` should also check active Atlas PR/MRs/branches for the staging ID when that context is available. An unmerged branch's status is proposed workflow state; the default branch remains the durable queue state.

## Staging and curation workflow

When reusable context is discovered during normal work:

1. choose the correct staging bucket;
2. read `_staging/README.md`, that bucket's `README.md` and `_template.md`;
3. preserve source/evidence and domain-specific detail;
4. keep known findings separate from possible/unconfirmed claims;
5. create a new staging record with `status: new`;
6. later use `atlas-curate`, which first checks lifecycle eligibility and duplicate active work;
7. reconcile against existing curated knowledge and propose only evidence-backed changes;
8. keep Claude-created curated pages at `status: proposed`;
9. regenerate maps from curated relationships and update indexes;
10. record the proposed staging outcome using a status-only change;
11. update the compact curation checkpoint when useful;
12. put curation reasoning in the Atlas PR/MR description;
13. human review decides whether accepted curated pages become `status: curated` before the approved change lands on the governed/default branch.

## Capturing learnings after engineering work

Atlas is worth updating when work reveals durable context such as:

- a non-obvious cross-component or cross-repo dependency;
- a changed API/event/table/file/job contract;
- flow sequencing or consumer information;
- infrastructure behaviour or blast-radius context;
- an operational failure pattern or runbook gap;
- a reusable standard/convention candidate;
- business/schema semantics that future engineers would otherwise rediscover.

### Code-derived changes

For working-code changes, Atlas capture should normally happen **after the product MR/PR is approved and merged to the repository's main/default branch**. This avoids documenting implementation that is still changing during review or never lands.

The normal monorepo case is one merged working-code MR/PR → one logical change → one `_staging/changes/` record. This is not rigid:

- several related MRs/PRs may be grouped when they are delivery pieces of one coherent engineering outcome;
- one broad MR/PR may be split when it contains materially independent reusable findings with different boundaries/targets.

MR/PR IDs, commits and release references are evidence/provenance, not the Atlas lifecycle controller.

### Findings not driven by a code MR/PR

Not all knowledge comes from code changes. Investigation of existing code, onboarding, architecture discussions, incident learning, runbook discovery, standards discovery or engineer-confirmed facts should be staged directly in the most appropriate bucket. Do not manufacture a `_staging/changes/` record when the logical source was simply a new finding.

Do not stage routine ticket status, implementation diary noise or facts that are cheaper and safer to derive from the owning repository every time.

## Curation and human review

`atlas-curate` reads staging evidence, lifecycle status, taxonomy, the target folder README/template/index and existing matching pages before deciding `CREATE`, `UPDATE`, `DEFER`, `REJECT` or `CONFLICT`.

Material conflicts are surfaced for human resolution rather than silently reconciled. Claude-created curated knowledge remains `status: proposed`; humans decide whether it becomes authoritative.

The **Atlas PR/MR is the review record**. Its description should identify:

- staging record(s) consumed;
- outcome per record/target;
- curated pages/indexes changed;
- material claims not promoted and why;
- relationship decisions/confidence;
- open questions/conflicts;
- map changes;
- validation results.

Git then retains reviewer identity, comments, approvals, requested changes, timestamps, diff and merge commit. V1 deliberately avoids duplicating this into a separate review-document folder.

## Curation checkpoint

`_curated/status/curation-status.md` stores only a compact latest checkpoint such as last run, last staging record(s), outcome, targets and related Atlas PR/MR. It is informational, not authoritative and not an ordering cursor. Staging records may be processed out of chronological order.

## Validation and map generation

Install development dependencies using Python 3.11+ and run:

```bash
python scripts/atlas_lint.py .
python scripts/rebuild_maps.py --check
pytest
python scripts/run_skill_evals.py --deterministic
```

After a curated relationship change, generate maps with:

```bash
python scripts/rebuild_maps.py
```

Then rerun `--check`. GitHub Actions and `.gitlab-ci.yml` invoke the same repository scripts so validation behaviour remains portable.

Linting checks structure and deterministic consistency; it does **not** decide whether engineering knowledge is true. `ATLAS021` enforces staging evidence immutability while allowing lifecycle `status` changes.

## Security and sensitive data

Never stage or curate:

- credentials, API keys, tokens or secret values;
- customer data or unnecessary personal data;
- raw sensitive production logs or extracts;
- connection strings or privileged values that belong in secure systems.

Redact or link to the authorised source instead. This repository is public, so fixtures/examples must remain generic and must not invent or expose real TeamA production facts.

## Contribution triggers

Before proposing an Atlas change, ask:

1. Is this context reusable beyond the immediate task?
2. Can the claim be attributed to evidence?
3. Which concept/bucket owns it?
4. What remains unknown or possible?
5. Does an existing page/evidence record already cover it?
6. Is the staging record actually `new`, or is it already active/terminal?
7. Will a relationship change require regenerated maps?
8. Have the deterministic checks passed?

## Non-goals / what not to capture

Do not:

- invent missing TeamA repositories, owners, dependencies, infrastructure, flows, standards or business definitions;
- treat inaccessible information as absence;
- mirror Confluence or incident systems verbatim;
- duplicate Git review history into a second review-document system;
- turn `_curated/status` into an unbounded per-staging ledger;
- create pages for every internal file/resource merely for completeness;
- manually author generated map relationships;
- allow Claude to approve or merge its own semantic proposal;
- expand V1 into multi-team federation, an enterprise crawler, UI, vector database or autonomous ingestion system.

## Placeholder values to replace before internal adoption

Replace `team-a-engineering` in ownership configuration and review controls before enforcing protected-branch review.

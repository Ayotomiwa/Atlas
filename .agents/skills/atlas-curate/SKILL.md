---
name: atlas-curate
description: Reconcile eligible staging evidence with existing curated Atlas knowledge and create a human-reviewable proposal without self-approval.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-curate

Curation turns evidence into a proposal; a human remains the authority. Staging lifecycle status is the scalable queue, and the Atlas PR/MR is the durable review/audit record.

## 1. Eligibility and duplicate-work preflight

1. Read `_staging/README.md` and the source staging record.
2. Read `taxonomy/statuses.yaml` and inspect the staging `status` on the default/current governed baseline.
3. Automatically curate only `status: new` records.
4. If the record is `status: curating`, do not start a second independent curation. Resume the known active work or report that the staging ID is already being handled. When Git-host context is available, check active Atlas PR/MRs/branches for the same staging ID before claiming concurrent work.
5. If the record is `status: curated`, `status: no-change`, `status: deferred`, or `status: rejected`, stop automatic curation and report the recorded outcome. `deferred` may be reconsidered only through an explicit lifecycle decision; new evidence should normally be a new staging record.
6. While working, the branch may set the staging record to `status: curating`. After the curation decision is known, the proposal should carry the appropriate terminal staging outcome. Only the top-level `status` field may change; never edit the captured evidence/path/ID.

A status transition on a branch is proposed workflow state. It becomes durable queue state only if the Atlas change is merged to the governed/default branch.

## 2. Reconcile evidence

1. Identify the source staging bucket and preserve its bucket-specific structure rather than flattening evidence into generic prose.
2. Read that staging bucket's `README.md` and `_template.md` whenever local capture semantics matter.
3. Read `atlas-package.json`, the registered taxonomy, and `contracts/map-fields.yaml` when controlled domains, classifications, structured map inputs or promoted resources are involved. Use the natural field for the connection and its specific qualifier when needed, such as `dependency_type`, `asset_type`, `entry_point_type`, or `resource_type`.
4. Resolve the target curated area from the staging record's own `## Suggested curated targets` section (curation destinations are not carried as a separate frontmatter field). If curating a batch of eligible records in one pass, scan each record's `## Suggested curated targets` section to group related evidence and route work efficiently. If the user explicitly states which curated area a record should go to, that stated target takes precedence over the record's suggestion, but the chosen target still must be validated against the target README's granularity rules before use.
5. Read the target folder `README.md` for semantic, granularity, evidence, relationship and reviewer rules.
6. Read the target `_template.md` for exact page shape and `index.md` for existing routable content.
7. For standards, also read `taxonomy/standard-categories.yaml` and the target category index.
8. Search existing concept pages by ID, alias, repository path and semantic match before creating anything new.
9. Choose exactly one curation decision per target: `CREATE`, `UPDATE`, `DEFER`, `REJECT`, or `CONFLICT`.
10. On a material conflict, stop automatic reconciliation and surface it for human resolution.
11. Create or update curated knowledge according to the local README/template; preserve evidence, domain-specific detail and uncertainty. Curating `staging.component` evidence may produce one `repo.*` page and multiple `comp.*` pages. Ask the user when the evidenced primary domain is uncertain.
12. Author each map-bound fact in its natural typed field. Use `id` for a stable local target and `name` for an external target; never repeat a generic relationship value. Architecture pages route `runbooks`, `standards`, and `incident_learnings` directly. Resolve reviewed local targets to real curated page or embedded `resource.*` IDs; do not silently upgrade possible claims. Flow steps are the sole participation source.
13. Use `*Not covered — no evidence in current staging material.*` in required sections where evidence is absent.
14. Codex-created/updated curated pages should use `status: curated` directly.
15. Do not hand-edit generated catalogue rows or managed page blocks.
16. Run `python scripts/rebuild_atlas.py`; never hand-edit generated JSON below `_curated/maps/` or generated Markdown blocks.
17. Update `_curated/status/curation-status.md` only as a compact latest checkpoint; never append a per-record history ledger.
18. Run `python scripts/atlas_lint.py .`, `python scripts/rebuild_atlas.py --check`, and tests relevant to the change unless the user has explicitly deferred validation for the current iteration.

## 3. Staging outcome

Use staging lifecycle status to record the proposed outcome:

- `status: curated` — the evidence produced accepted curated changes in this proposal;
- `status: no-change` — the evidence was reviewed but existing curated knowledge already covered it or no durable change was needed;
- `status: deferred` — evidence/blockers are insufficient for a safe decision;
- `status: rejected` — evidence is unsuitable, non-reusable or otherwise should not become durable Atlas knowledge.

Do not edit the staging record except for `status`. If additional facts or corrections are needed, create new staging evidence.

## 4. Atlas PR/MR review record

Do not create a `reviews/` Markdown record. The Atlas PR/MR itself should carry the review summary:

- staging record(s) consumed;
- curation outcome per record/target;
- curated pages and generated catalogues changed;
- structured connections/links proposed and confidence;
- material claims not promoted and why;
- open questions/conflicts;
- generated map changes;
- validation results;
- reminder that human review/approval is required.

Git retains reviewer identity, comments, approvals, changes requested, timestamps, diff and merge commit.

## 5. Human authority

Never merge or self-approve. A human reviewer decides whether proposed changes are accepted by approving the PR/MR. The PR merge itself serves as the approval, so you should author pages with `status: curated`.

---
name: atlas-curate
description: Reconcile staging evidence with existing curated Atlas knowledge and create a human-reviewable proposal without self-approval.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-curate

Curation turns evidence into a proposal; a human remains the authority.

1. Read the staging evidence to curate. Identify its staging bucket and preserve the bucket-specific structure (for example component consumes/produces, flow hand-offs, infra package/resource relationships, runbook safety, standards counterexamples) rather than flattening evidence into a generic summary.
2. When interpretation of the staging record depends on local capture semantics, read that staging bucket's `README.md` and `_template.md`; they explain what the source evidence was intended to represent.
3. Read `taxonomy/types.yaml`, `taxonomy/relationships.yaml`, and `taxonomy/statuses.yaml`.
4. Resolve the target curated area.
5. Read the target folder `README.md` for semantic, granularity, evidence, and reviewer rules.
6. Read the target `_template.md` for exact page shape.
7. Read the target `index.md` to understand existing routable content.
8. For standards, also read `taxonomy/standard-categories.yaml` and the target category `index.md`.
9. Search existing concept pages by ID, alias, repository path, and semantic match.
10. Choose exactly one decision: `CREATE`, `UPDATE`, `DEFER`, `REJECT`, or `CONFLICT`.
11. On a material conflict, stop automatic reconciliation and surface it for human resolution.
12. Create or update the proposed page according to the local README/template; preserve evidence, domain-specific detail and uncertainty. Rich staging evidence is input to curation, not permission to treat every captured field as reviewed fact.
13. Propose only taxonomy-approved relationships. Resolve reviewed local targets to real curated IDs; do not silently upgrade possible claims to reviewed edges.
14. Use `*Not covered — no evidence in current staging material.*` in required sections where evidence is absent.
15. Set curated page `status: proposed`, never `curated`.
16. Update the relevant concept/category index.
17. Run `python scripts/rebuild_maps.py`; never hand-edit `_curated/maps/*.json`.
18. Update `_curated/status/curation-status.md`.
19. Create or update the matching note under `reviews/` with the curation decision and validation results.
20. Run `python scripts/atlas_lint.py .`, `python scripts/rebuild_maps.py --check`, and tests relevant to the change.
21. Summarise pages changed, relationships proposed, relationship confidence, open questions, map diff, and validation results.
22. Never merge, self-approve, or convert the proposal to `status: curated`.

Once staging evidence is referenced by a curation proposal, do not alter or move that consumed evidence; add corrective evidence instead.

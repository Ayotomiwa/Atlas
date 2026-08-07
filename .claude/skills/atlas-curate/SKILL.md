---
name: atlas-curate
description: Reconcile staging evidence with existing curated Atlas knowledge and create a human-reviewable proposal without self-approval.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-curate

Curation turns evidence into a proposal; a human remains the authority.

1. Read the staging evidence to curate.
2. Read `taxonomy/types.yaml`, `taxonomy/relationships.yaml`, and `taxonomy/statuses.yaml`.
3. Resolve the target curated area.
4. Read the target folder `README.md` for semantic, granularity, evidence, and reviewer rules.
5. Read the target `_template.md` for exact page shape.
6. Read the target `index.md` to understand existing routable content.
7. For standards, also read `taxonomy/standard-categories.yaml` and the target category `index.md`.
8. Search existing concept pages by ID, alias, repository path, and semantic match.
9. Choose exactly one decision: `CREATE`, `UPDATE`, `DEFER`, `REJECT`, or `CONFLICT`.
10. On a material conflict, stop automatic reconciliation and surface it for human resolution.
11. Create or update the proposed page according to the local README/template; preserve evidence and uncertainty.
12. Propose only taxonomy-approved relationships. Resolve reviewed local targets to real curated IDs; do not silently upgrade possible claims to reviewed edges.
13. Use `*Not covered — no evidence in current staging material.*` in required sections where evidence is absent.
14. Set curated page `status: proposed`, never `curated`.
15. Update the relevant concept/category index.
16. Run `python scripts/rebuild_maps.py`; never hand-edit `_curated/maps/*.json`.
17. Update `_curated/status/curation-status.md`.
18. Create or update the matching note under `reviews/` with the curation decision and validation results.
19. Run `python scripts/atlas_lint.py .`, `python scripts/rebuild_maps.py --check`, and tests relevant to the change.
20. Summarise pages changed, relationships proposed, confidence, open questions, map diff, and validation results.
21. Never merge, self-approve, or convert the proposal to `status: curated`.

Once staging evidence is referenced by a curation proposal, do not alter or move that consumed evidence; add corrective evidence instead.

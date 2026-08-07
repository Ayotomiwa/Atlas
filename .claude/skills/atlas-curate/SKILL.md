---
name: atlas-curate
description: Use to reconcile staged evidence into proposed curated TeamA Atlas knowledge for human review.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-curate

1. Read the selected staging evidence.
2. Read `taxonomy/types.yaml`, `taxonomy/relationships.yaml`, and `taxonomy/statuses.yaml`.
3. Resolve the target curated area, then **read its `README.md`, `_template.md`, and `index.md`**. For standards also read the category index and standard-category taxonomy.
4. Search existing pages by ID, alias, repository path and semantic match.
5. Decide `CREATE`, `UPDATE`, `DEFER`, `REJECT`, or `CONFLICT`; stop automatic reconciliation on material conflict.
6. Create/update using target granularity/template as `status: proposed`, preserving evidence/uncertainty and using the exact not-covered marker where needed.
7. Propose typed relationships; resolve reviewed local targets to real IDs. Never turn possible claims into reviewed edges.
8. Update the relevant curated/category index.
9. Run `python scripts/rebuild_maps.py`.
10. Update `_curated/status/curation-status.md` and create/update `reviews/STG-...-review.md`.
11. Run `python scripts/atlas_lint.py .` and relevant tests.
12. Summarise pages, relationships/confidence, questions, map diff and validation. Never self-approve or merge.

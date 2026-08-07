---
name: atlas-curate
description: Reconcile staging evidence into proposed curated Atlas knowledge for human review.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-curate

1. Read staging evidence.
2. Read `taxonomy/types.yaml`, `taxonomy/relationships.yaml`, `taxonomy/statuses.yaml`.
3. Resolve target curated area.
4. Read target `README.md`.
5. Read target `_template.md`.
6. Read target `index.md`.
7. For standards, also read category index and category taxonomy.
8. Search existing pages by ID, alias, repository path and semantic match.
9. Decide CREATE, UPDATE, DEFER, REJECT or CONFLICT.
10. Stop automatic reconciliation on material conflict.
11. Create/update only `status: proposed` pages following granularity rules.
12. Preserve evidence and uncertainty.
13. Propose typed relationships and resolve reviewed local targets.
14. Use the exact not-covered marker where evidence is absent.
15. Never set `curated`.
16. Update relevant index/category index.
17. Run `python scripts/rebuild_maps.py`.
18. Update curation status.
19. Create/update review note.
20. Run lint and relevant tests.
21. Summarise pages, relationships, confidence, questions, map diff and validation.
22. Never merge or self-approve.

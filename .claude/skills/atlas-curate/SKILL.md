---
name: atlas-curate
description: >
  Use when promoting staged evidence into a curated Atlas page, or updating an
  existing page from new evidence. Handles components, flows, infra, schema-info,
  business concepts, standards, runbooks and incident learnings.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash
---

# Atlas curate

1. Read the staging file and `taxonomy/types.yaml`.
2. Determine target type from `target_type`; load that folder's `_template.md`.
3. Determine whether this updates, creates, or conflicts with an existing page. On conflict: stop and report.
4. Fill frontmatter per the Atlas contract. Never invent a DataLens fact; use the documented not-covered marker for unevidenced body sections.
5. Resolve each relationship target to a real Atlas `id`, set `kind` where required, set `confidence` honestly, and add a `note` for anything not `reviewed`.
6. Run `python scripts/rebuild_maps.py`.
7. Update the folder `index.md` and `_curated/status/curation-status.md`.
8. Run `python scripts/atlas_lint.py .` and fix every finding.
9. Set `status: draft-curated`. Never set `curated`; that is the reviewer's act.
10. Summarise pages touched, relationships proposed with confidence, and open questions.

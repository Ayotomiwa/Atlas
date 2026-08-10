---
name: atlas-impact
description: Use for blast-radius questions such as what may break when a TeamA repository, component, flow, schema or infrastructure item changes, fails or is deleted.
allowed-tools: Read, Grep, Glob, Bash
---

# atlas-impact

This is a read-only impact-analysis workflow.

1. Resolve the starting record with `python scripts/atlas_query.py resolve <id>` or an exact stable-ID search. Use a domain index only when the ID is unknown.
2. Run `python scripts/atlas_query.py impact <id> --direction downstream` with an appropriate depth. Use `--format json` when stable machine-readable paths are useful.
3. Preserve every direct/transitive distinction, `via` path, confidence value, and evidence route returned by the query library. Do not invent a link to close a traversal gap.
4. Open only the smallest useful set of map-routed pages for narrative meaning, evidence context, coverage limits, operational detail, or unresolved questions.
5. Bucket results as **known affected**, **possibly affected**, and **unknown or not covered**. Possible, unconfirmed, and conflicting links do not become reviewed facts through traversal.
6. Cite the supporting Atlas page ID/path and evidence route for each material result.
7. Never claim `not affected` merely because a connection is absent. Never use staging evidence as authority and never write Atlas or product files.

If the starting record is not covered by curated Atlas, report that limitation instead of constructing a confident graph from staging evidence.

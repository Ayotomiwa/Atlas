---
id: atlas.datalens.index.curation-status
type: atlas.index
package: datalens
schema_version: atlas/1.0
---

# Curation status

This table tracks proposed and reviewed Atlas knowledge. One row represents one curated Atlas page.

| Atlas ID | Type | Status | Owner | Last reviewed | Open questions |
|---|---|---|---|---|---|

## Column contract

- **Atlas ID** — canonical dotted page `id`.
- **Type** — active curated taxonomy type.
- **Status** — curated-layer status.
- **Owner** — accountable team or role when captured.
- **Last reviewed** — `YYYY-MM-DD` when reviewed.
- **Open questions** — known evidence gaps; never silently convert them into assumed facts.

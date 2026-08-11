# Datalens Atlas index

Route by question or trust layer:

- What Atlas record matches an ordinary description? Use `python scripts/atlas_query.py find "<question>"`; follow the selected page, or use the relevant curated index when candidates are weak or ambiguous.
- What package is this? Read [the repository guide](README.md); machine consumers use [`atlas-package.json`](atlas-package.json).
- What source repository or component is involved? Start with [curated architecture](_curated/index.md) or query a stable ID with `scripts/atlas_query.py`.
- How does an end-to-end path work? Use the [flow/component map](_curated/maps/flow-component/flow-component-map.json).
- What could an infrastructure change affect? Use the [infrastructure map](_curated/maps/infra-dependency/infra-dependency-map.json).
- What raw evidence is awaiting review? Use the [staging index](_staging/index.md).
- What staging evidence is active or historical across all buckets? Use `python scripts/atlas_query.py staging` with status, bucket, domain, date or target filters.
- Which merged monorepo changes have Atlas considered, or what should be staged next? Use `/atlas-stage-changes`; shared cursors are explained in [change intake](_intake/README.md).
- What is the latest curation checkpoint? Open [curation status](_curated/status/curation-status.md).
- How is new context captured? Start with [onboarding](onboarding/index.md).
- Which controlled values apply? Read [taxonomy](taxonomy/README.md).

Known-package access may route directly to a map, index, stable ID or page. Atlas-core federation uses package manifests only when package discovery is required.

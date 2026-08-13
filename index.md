# Datalens Atlas index

Route by question or trust layer:

- **Ask Atlas:** ask an ordinary engineering or change-impact question. Claude selects discovery/impact internally, follows curated links, and uses search or indexes only to resolve the starting record.
- **Teach Atlas:** say “Save this to Atlas” or “What does Atlas still need to know?” Claude prepares attributable evidence and asks once before writing.
- **Sync Atlas:** say “Onboard this repository”, “Update Atlas for this repository”, or “Learn the standards used here.” Claude chooses full onboarding, standards discovery or incremental merged-change processing.
- **Curate Atlas:** say “Curate pending evidence for this repository/domain/topic.” Claude scopes the queue, materialises supported knowledge and runs independent review.

- What Atlas record matches an ordinary description? Ask Claude; it uses deterministic candidates, follows the selected page and falls back to the relevant curated index when results are weak or ambiguous.
- What package is this? Read [the repository guide](README.md); machine consumers use [`atlas-package.json`](atlas-package.json).
- What source repository or component is involved? Start with [curated architecture](_curated/index.md), or name the stable ID in your question for direct resolution.
- How does an end-to-end path work? Use the [flow/component map](_curated/maps/flow-component/flow-component-map.json).
- What could an infrastructure change affect? Use the [infrastructure map](_curated/maps/infra-dependency/infra-dependency-map.json).
- What raw evidence is awaiting review? Use the [staging index](_staging/index.md).
- What staging evidence is active or historical across all buckets? Ask Claude for the desired status, bucket, domain, date or target scope.
- Which merged monorepo changes have Atlas considered, or what should be staged next? Ask Claude to update Atlas for the repository; shared cursors are explained in [change intake](_intake/README.md).
- What is the latest curation checkpoint? Open [curation status](_curated/status/curation-status.md).
- How is new context captured? Start with [onboarding](onboarding/index.md).
- Which controlled values apply? Read [taxonomy](taxonomy/README.md).
- Which exact skill or command is involved? Use the [advanced workflow reference](onboarding/advanced-reference.md).

Known-package access may route directly to a map, index, stable ID or page. Atlas-core federation uses package manifests only when package discovery is required.

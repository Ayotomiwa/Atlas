# Atlas prose patterns

Use these patterns as drafting guidance, not as text to copy mechanically.

## Lead with use

Weak: `This collection contains curated repository records governed by the repository contract.`

Plain technical: `Use repository pages to understand how source code is organised, who owns it, and where to start reading.`

Define the Atlas record type after the reader knows why it matters.

## Explain architecture causally

Repository:

`The monorepo project builds the billing service from services/billing. Its deployment definitions live under deploy/billing; shared database migrations are outside this repository boundary.`

Component:

`The billing worker reads approved invoices, creates settlement requests, and records the provider response. It does not decide whether an invoice should be approved.`

Flow:

`The scheduler starts the export. The worker reads approved rows, writes the file, then emits a completion event. On validation failure, the file is not published.`

Infrastructure:

`This package creates the queue and dead-letter queue used by the billing worker. The worker writes failed messages to the dead-letter queue; the package does not own message replay.`

These examples name the boundary and avoid inferring causality from nearby files or diagram order.

## Make policy actionable

Put the rule beside the decision:

- `Use a component page only for an independently addressable runtime or reusable unit.`
- `If the runtime identity is unresolved, keep it as an open question; do not substitute a folder-shaped component.`

Keep exact words such as `must`, `never`, `only`, `curated`, and controlled confidence values. Shorter prose must not weaken governance.

## Keep machine-owned structures stable

Do not edit YAML keys, generated markers, link targets, stable IDs, table headers consumed by scripts, or the `## Open questions` / `## Coverage limits` interfaces. Rewrite only the explanatory prose around them unless the owning workflow explicitly changes the interface.

## Separate a style repair from a knowledge repair

Style repair:

`The package is utilized by the service for the purpose of provisioning queues.`

becomes:

`The service uses this package to provision its queues.`

Knowledge repair:

`The service owns the queue.`

cannot become:

`The platform team owns the queue.`

without evidence and the correct staging/curation route.

## Final comparison

Compare the original and revised text for claims, qualifications, exclusions, dates, environments, and scope. If the revision changes what a reviewer could conclude, treat it as a semantic change and stop the prose-only workflow.

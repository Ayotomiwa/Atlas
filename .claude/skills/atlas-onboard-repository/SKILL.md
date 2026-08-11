---
name: atlas-onboard-repository
description: Onboard one datalens logical source boundary through broad inventory, targeted deep reading, one clarification round, and attributable staging evidence without curating it.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-onboard-repository

Read `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `../_shared/agent-handoffs.md`, `references/clarification-checklist.md`, and the staging component README/template. This workflow stages evidence only.

1. Establish one logical source boundary, its physical Git root/remote, candidate `repository_root`, enclosing boundary, included paths, exclusions and user-supplied references. Use typed repository/component `find` plus `context` to identify existing coverage; preserve ambiguity and `not-verified` status. If the boundary is already onboarded and the request is to process merged changes since a cursor, route to `atlas-stage-changes`.
2. Always delegate inspection to `atlas-repo-analyst`. Inventory broadly, then deeply read only material sources across every lens: boundary/ownership/domain, build/release topology, source roots, components, entrypoints/control flow, I/O, dependencies, infrastructure, flows, schemas/contracts and operations.
3. Follow only explicit references into shared or infrastructure paths. Do not recursively onboard sibling products. Report them as follow-up candidates.
4. Exclude VCS internals, environments, dependencies, generated frontends/source maps, build output, large data, samples, binaries and vendor trees unless directly relevant. Give every lens an evidence state and expand only when evidence conflicts or a required lens remains unresolved.
5. Ask one consolidated clarification round for material boundary/domain/identity/owner/external-context gaps; ask again only if safe staging is blocked.
6. Stage one `staging.component` repository/component discovery record with source paths traceable from every finding. Add flow, infrastructure, schema, runbook or incident records only when each has an independently evidenced reusable boundary. Never create placeholders or curated facts.
7. Report staged records, the analyst's evidence matrix, fuller scan manifest, exclusions, inaccessible references, stopping reasons, possible findings, questions and validation state with references.

An infrastructure-only folder normally becomes infrastructure evidence, not a redundant repository candidate. A component requires an independently addressable runtime/reusable boundary; a folder or job group alone is insufficient.

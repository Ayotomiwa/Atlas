# Curator semantic preflight

Run this gate before materialising a curation decision. A user clarification may supply evidence or choose among valid boundaries, but it cannot waive a taxonomy or collection contract.

- Component identity: each `comp.*` is an independently addressable runtime, job, API, library or reusable unit. A repository folder, ownership area, domain, delivery directory or job group is not a substitute. Defer unresolved runtime identities.
- Publication scope: for directory upload, sync or publication, require evidence of a clean assembled directory or an explicit allow-list. Otherwise defer the publication claim. Independently supported reads, consumption or deletion impact may still be curated.
- Sensitive exposure: identify source paths that could enter the published artifact without opening or copying their contents. Treat uncertain inclusion as a safety gap.
- Control flow: distinguish attempted ordering from success/failure gating. Visual adjacency, declaration order or similar timestamps do not prove a causal handoff.
- Shell control flow: a command sequence is only attempted order unless `set -e`, `&&`, explicit status checks or equivalent evidence establishes failure gating. Do not infer fail-fast behavior.
- Ownership: CODEOWNERS and approval rules establish review routing, not necessarily operational or product ownership. Keep them attributed in prose unless a source or user explicitly confirms the stronger `owners` claim.
- Runbook threshold: create a runbook only with an evidenced trigger/scope, ordered diagnostic or recovery procedure, safety/stop conditions, and objective validation or escalation. Otherwise retain the material as an operational note on its narrowest component or infrastructure page.
- Narrowest authorship: author each fact once on the most specific true record; derive reverse routes and avoid aggregate or reciprocal duplication.

Ask one clarification round. Ask required identity, scope, ownership, domain, promotion, conflict and safety decisions first. Present other gaps as one optional confirm-or-correct list; skipped non-blocking gaps remain explicit unknowns.

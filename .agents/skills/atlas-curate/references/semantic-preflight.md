# Curator semantic preflight

Before materialising, enforce strict component identity, evidenced publication scope, sensitive-path exposure, real success/failure gating, causal rather than visual handoffs, the full-runbook threshold, and narrowest-record authorship.

- A component must be an independently addressable runtime, job, API, library or reusable unit. A folder, ownership area, domain or job group is invalid; unresolved runtime identity is deferred.
- Directory upload/sync requires a clean assembled source or explicit allow-list. Otherwise defer the publication claim while retaining independently supported consumption or deletion impact.
- Identify potentially included sensitive paths without reading or copying their contents.
- Ordering is not success gating; adjacency is not causation.
- Shell command order is not fail-fast behavior without `set -e`, `&&`, explicit status checks or equivalent evidence.
- CODEOWNERS and approval rules establish review routing, not necessarily operational or product ownership; do not populate `owners` without stronger evidence or user confirmation.
- A runbook requires an evidenced trigger/scope, ordered diagnostic or recovery procedure, safety/stop conditions, and objective validation or escalation. Lesser material stays an operational note.
- Author each fact once on its narrowest true record and derive reverse routes.

Ask material identity, scope, ownership, domain, promotion, conflict and safety decisions in one clarification round. Put remaining gaps in one optional confirm-or-correct list and preserve skipped gaps as unknown.

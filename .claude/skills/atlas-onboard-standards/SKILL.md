---
name: atlas-onboard-standards
description: Use only for explicit datalens standards discovery, separating authoritative reusable policy from repeated practice, repository-local convention, tool defaults, exceptions, and conflicts.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-onboard-standards

Read `../_shared/human-intents.md`, `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `../_shared/agent-handoffs.md`, `references/clarification-checklist.md`, the staging standards README/template, taxonomy and curated standards indexes. This is the standards route behind **Sync Atlas**.

1. Delegate source comparison to `atlas-standards-analyst` with the authorised repositories/documents and scan boundary.
2. Require authority, recurrence, applicability, rationale, examples, sourced counterexamples, exceptions and conflicts. Classify each result as team-standard candidate, repository-local convention, tool default or unknown scope.
3. Compare candidates with curated standards. Repetition proves practice, not mandate. Report excluded local conventions/defaults with their sources.
4. Ask only for material authority/scope clarification. Normally do not stage a one-repository convention; stage it only when evidence shows authority or plausible datalens scope.
5. When staging is justified, preserve the full source ledger, uncertainty and counterexamples. Show one concrete staging preview and obtain one approval; pass it through any internal write handoff. Never create `must-follow` applicability from frequency alone or write curated standards.
6. Cite every candidate, counterexample, exclusion and duplicate route in the completion report.

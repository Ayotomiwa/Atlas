---
name: atlas-onboard-standards
description: Discover candidate reusable team standards without treating repo-local configuration or tool defaults as team policy.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
---

# atlas-onboard-standards

Read `_staging/standards/README.md`, its template and `taxonomy/standard-categories.yaml`. Inspect policy/config evidence including CONTRIBUTING, READMEs, CI templates, parent builds, lint/format/test config, PR templates, documented Jira conventions, IaC conventions, security checks, scripts and repeated patterns. Classify findings as `team-standard-candidate`, `repo-local-convention`, `tool-default`, or `unknown-scope`. Compare candidates with curated standards. Ask the user to confirm ambiguous high-value scope/authority. Stage a standards discovery record with category, rule, source paths, scope evidence, exceptions/unknowns and target. Never curate standards.

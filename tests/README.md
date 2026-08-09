# Tests

The test suite exercises deterministic V1 contracts offline. Synthetic fixtures never represent TeamA production knowledge.

- `unit/` covers frontmatter, IDs, links, lint rules, map projection, reverse views, map drift, canonical structure, and staging immutability.
- `fixtures/valid/curated-pages/` contains a passing synthetic example for every active curated concept type.
- `fixtures/invalid/` contains deliberately malformed synthetic inputs for lint error rules where a file fixture is practical.
- `fixtures/valid/service-repo/`, `infra/`, and `standards/` support the required onboarding/standards demonstrations.

Run `pytest`.

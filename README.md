# TeamA Atlas

## Purpose
TeamA Atlas is a governed engineering context layer for humans and AI agents. This public V1 is a scaffold only and contains no real TeamA engineering facts.

## Pilot scope
One TeamA package (`teama`) only. The owner name `team-a-engineering` is a placeholder and must be replaced before internal adoption.

## Repository structure
- `_staging/`: raw evidence, never authoritative.
- `_curated/`: reviewed/proposed knowledge and generated maps.
- `taxonomy/`: deterministic vocabularies.
- `.claude/skills/` and `.claude/agents/`: workflows and specialist roles.
- `scripts/` and `tests/`: validation, graph generation and evaluations.

## Trust model
Only curated pages with `status: curated` are authoritative. Claude may stage and propose but never self-approve or merge knowledge.

## File responsibilities
`CLAUDE.md` governs Atlas maintenance; `package.md` defines identity and entrypoints; folder READMEs define local policy; indexes route; templates define page shape; maps are generated projections.

## How to browse Atlas
Start at `index.md`, then follow the smallest relevant curated index or map.

## How to use Atlas from another repository
```bash
cd <product-repo>
claude --add-dir <path-to>/team-atlas
```
Cross-repo consumption relies on discovered skills plus `package.md` and indexes; the added directory's root `CLAUDE.md` is not the consumer contract.

## Available Claude skills
`atlas-discover`, `atlas-impact`, `atlas-stage`, `atlas-onboard-service`, `atlas-onboard-standards`, `atlas-setup-repo`, `atlas-curate`, `implement-jira`.

## Service onboarding
Use `atlas-onboard-service` to scan a bounded service repository and stage only evidenced context.

## Standards discovery
Use `atlas-onboard-standards` to distinguish reusable team-standard candidates from repo-local conventions and tool defaults.

## Curation and review
Use `atlas-curate`; proposals remain `proposed` until a human reviews and merges them.

## Map generation
Run `python scripts/rebuild_maps.py`; never hand-edit generated relationship data.

## Validation and tests
```bash
python scripts/atlas_lint.py .
python scripts/rebuild_maps.py --check
pytest
python scripts/run_skill_evals.py --deterministic
```

## CI
GitHub Actions and the GitLab CI file invoke the same repository scripts.

## Security and sensitive data
Never capture credentials, tokens, customer data, raw sensitive logs, connection strings or unnecessary personal data.

## Contribution triggers
Stage reusable context when discovered; curate only from evidence; rebuild maps after relationship changes; run deterministic checks before proposing a change.

## What not to capture
Do not invent missing context, duplicate routine logs, or turn inaccessible information into an absence claim.

## Placeholder values to replace before internal adoption
Replace `team-a-engineering` in ownership configuration and review controls before enforcing protected-branch review.

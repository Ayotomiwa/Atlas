# TeamA Atlas

## Purpose
TeamA Atlas is a governed engineering context layer for humans and AI agents. It separates raw evidence from human-reviewed knowledge and provides deterministic validation and generated relationship maps.

## Pilot scope
V1 contains one public prototype package only: `teama`. It deliberately contains no real TeamA production knowledge.

## Repository structure
- `_staging/` — raw evidence and uncertainty.
- `_curated/` — reviewed/proposed concept knowledge.
- `_curated/maps/` — generated projections of curated relationships.
- `taxonomy/` — type, relationship, status and standard-category vocabularies.
- `.claude/skills/` and `.claude/agents/` — Claude workflows and specialist roles.
- `scripts/` and `tests/` — deterministic tooling, tests and evals.

## Trust model
Only curated pages with `status: curated` are authoritative. Claude may stage and propose; humans approve and merge. Staging evidence is never authoritative.

## File responsibilities
`CLAUDE.md` governs Atlas maintenance; `package.md` defines package routing; folder READMEs define local policy; indexes route; templates define shape; reviews record reasoning; status records routine curation state.

## How to browse Atlas
Start at `index.md`, then route to the smallest relevant curated index, map or staging bucket.

## How to use Atlas from another repository
```bash
cd <product-repo>
claude --add-dir <path-to>/team-atlas
```
Cross-repo consumption relies on discovered skills plus `package.md` and indexes; the added directory's root `CLAUDE.md` is not the consumer contract.

## Available Claude skills
`atlas-discover`, `atlas-impact`, `atlas-stage`, `atlas-onboard-service`, `atlas-onboard-standards`, `atlas-setup-repo`, `atlas-curate`, and `implement-jira`.

## Service onboarding
Use `atlas-onboard-service` to perform a bounded repo scan, gather missing context, and stage only evidenced material.

## Standards discovery
Use `atlas-onboard-standards` to find candidate reusable standards without confusing tool defaults or repo-local conventions with team policy.

## Curation and review
Use `atlas-curate`; it must read the destination README, template and index, writes `status: proposed`, updates maps/status/review notes, and never self-approves.

## Map generation
Relationships are authored only in curated Markdown. Run `python scripts/rebuild_maps.py`; use `--check` in validation.

## Validation and tests
```bash
python scripts/atlas_lint.py .
python scripts/rebuild_maps.py --check
pytest
python scripts/run_skill_evals.py --deterministic
```

## CI
GitHub Actions and GitLab CI invoke the same repository scripts; CI is a gate, not a semantic approver.

## Security and sensitive data
Do not capture credentials, keys, tokens, customer data, raw sensitive logs/query output, unnecessary personal data, or inaccessible context.

## Contribution triggers
Contribute when reusable engineering context, relationships, operational learning, standards, or coverage gaps are discovered and can be evidenced.

## What not to capture
Do not fabricate missing facts, store secrets, create speculative production topology, or use Atlas as a general document dump.

## Placeholder values to replace before internal adoption
`team-a-engineering` in `package.md`/`CODEOWNERS` is a public-prototype placeholder and must be replaced before protected-branch review is enforced.

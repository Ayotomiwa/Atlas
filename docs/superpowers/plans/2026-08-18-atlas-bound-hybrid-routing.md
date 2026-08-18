# Atlas Bound-Repository Hybrid Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Atlas the preferred navigation and engineering-memory layer for explicitly bound repositories while preserving source authority, session reuse, and exact-change correctness.

**Architecture:** Extend the existing staging query with exact change-provenance filters, then encode the approved binding and hybrid-routing ladder in the existing Claude/Codex skills, shared contracts, managed blocks, and analyst profiles. Keep the current types, maps, flow model, onboarding lifecycle, and evaluation contracts unchanged.

**Tech Stack:** Python 3.11+, argparse, pytest, Markdown skill contracts, Claude Markdown profiles, Codex TOML profiles.

**Spec:** This plan embeds the approved user specification; there is no separate spec file.

## Global Constraints

- Automatic Atlas routing applies only to a repository with a valid Atlas-managed `AGENTS.md` or `CLAUDE.md` block; explicit **Ask Atlas** always consults Atlas.
- `matched` and `path-derived` bindings allow automatic routing; `not-verified` also allows routing but requires a visible identity advisory in every substantive answer that uses it.
- Retained context wins; one known source path/symbol may be read directly; uncertain navigation, broad search, multiple hops, Git archaeology, or durable/cross-boundary context routes to Atlas first.
- Exact volatile details remain source-authoritative even when Atlas locates the source.
- Atlas may answer fully, guide the smallest bounded read-only source lookup, or report unresolved coverage; missing coverage never proves absence.
- `_staging/` remains non-authoritative routing evidence. Exact-change completeness comes from referenced immutable evidence or a narrow Git diff/history inspection.
- Preserve semantic equivalence across Claude and Codex surfaces without requiring byte-identical prose.
- Add no Atlas type, schema, map, flow command, onboarding mechanism, daemon, embedding service, decision/ADR model, or evaluation version.
- Add no live or fictional curated/staging knowledge to the Atlas package.

---

### Task 1: Exact change-provenance query filters

**Files:**
- Modify: `scripts/lib/staging.py`
- Modify: `scripts/atlas_query.py`
- Modify: `tests/unit/test_staging_query.py`
- Modify: `onboarding/advanced-reference.md`

**Interfaces:**
- Extend `query_staging(..., source_key: str | None = None, branch: str | None = None, from_exclusive: str | None = None, through_inclusive: str | None = None) -> dict`.
- Add `staging` CLI flags `--source-key`, `--branch`, `--from-exclusive`, and `--through-inclusive`.
- Interpret `from_exclusive="start"` as an exact match for stored `null`; an omitted filter remains unfiltered.
- Normalize and echo `source_key`, `branch`, `from_exclusive`, and `through_inclusive` in the returned `filters` object.

- [ ] Add failing library tests for exact source/branch/range matching, `start`, multiple records sharing a range, ordinary records without `change_source`, and composition with existing filters.
- [ ] Add failing CLI tests for all four flags, normalized JSON output, and exit-code-1 validation of invalid source keys, blank branches, short/uppercase/malformed SHAs, and `start` on `through_inclusive`.
- [ ] Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 py -3.14 -m pytest tests/unit/test_staging_query.py -q` and record the expected RED failures.
- [ ] Implement exact matching using the existing `SOURCE_KEY_RE` and `COMMIT_RE` contracts. Do not add per-record schema validation; malformed or missing `change_source` simply cannot match a provenance filter.
- [ ] Preserve status defaults and `--include-terminal` behavior. Provenance filters are ANDed with status, bucket, domain, date, and target filters.
- [ ] Add a power-user example showing an exact-range `_staging/changes` query with `--include-terminal`.
- [ ] Re-run the focused tests, then the full unit suite, and commit the task.

### Task 2: Bound-repository hybrid routing and change readiness

**Files:**
- Modify: Claude/Codex copies of `_shared/runtime.md`, `_shared/answer-provenance.md`, and `_shared/agent-handoffs.md`
- Modify: Claude/Codex `atlas-discover` and `atlas-impact` skills
- Modify: Claude/Codex discovery and impact analyst profiles
- Modify: Claude/Codex `atlas-setup-repo/assets/managed-block.md`
- Create: `tests/unit/test_retrieval_routing_surfaces.py`

**Interfaces:**
- The managed block is the automatic-routing binding signal.
- Answer provenance labels are `Atlas`, `Repository (located via Atlas)`, `Inference`, and `Unresolved`.
- Exact-change prompts use the Task 1 filters against `_staging/changes`, including terminal records, before completeness-sensitive source verification.

- [ ] Add failing paired-surface tests proving both Claude and Codex contracts contain the same binding matrix, retrieval ladder, direct Ask Atlas behavior, source-authority rule, exact-change guard, flow answer shape, session reuse/re-entry, guided-source disclosure, and semantic-risk trigger.
- [ ] Add assertions that an unbound repository does not automatically invoke Atlas, while explicit Ask Atlas does; `not-verified` requires an advisory; bound uncertain/broad lookup routes Atlas before broad source search.
- [ ] Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 py -3.14 -m pytest tests/unit/test_retrieval_routing_surfaces.py -q` and record the expected RED failures.
- [ ] Replace the blanket simple-local bypass with this ordered ladder: retained context; one known targeted source read; Atlas before uncertain/broad/multi-hop/Git/durable lookup; complete Atlas answer; partial Atlas plus smallest source fallback; Atlas-guided source route; bounded source and unresolved gap.
- [ ] Require direct Ask Atlas to consult relevant curated types, follow answer-bearing links, synthesize all supported material, and either answer, guide the next evidence location, or report an unresolved boundary.
- [ ] Require source guidance to name repository, smallest path/symbol/config/IaC/document boundary, selection reason, route confidence, and Atlas coverage endpoint. Read-only fallback is automatic when the repository is unambiguous.
- [ ] Require flow answers to synthesize trigger/outcome/boundaries, ordered participants/handoffs, data and infrastructure transitions, branches/retries/failures, standards, incidents, runbooks, and coverage limits from the existing model.
- [ ] Require semantic-risk change readiness for API/schema/event/data/flow, AWS/IAM/account/environment/region/schedule/event-filter/monitoring/deployment/rollback, standards, operations, recovery, and cross-repository boundaries regardless of diff size.
- [ ] Require readiness output to combine standards/conflicts/exceptions, confirmed/possible/external/unknown impact, incidents/runbooks, source-owned exact commands, and Atlas-owned testing/compatibility/deployment/recovery obligations. Clear required standards are applied and reported; confirmation is reserved for exceptions, ambiguity, destructive/cross-team risk, or missing critical evidence.
- [ ] Preserve direct-before-transitive impact traversal, local isolated-edit bypass, missing-coverage honesty, ephemeral session reuse, and bounded re-entry.
- [ ] Re-run the focused surface tests, the full unit suite, Atlas lint, rebuild check, and diff check; then commit the task.

### Task 3: External promotion validation

**Files:**
- External only: fresh sealed destination outside the Atlas checkout
- Report: `.superpowers/sdd/2026-08-18-atlas-bound-hybrid-routing/task-3-report.md`

**Interfaces:**
- Consumes the reviewed Task 1 exact-range query and Task 2 routing contracts.
- Produces a promotion verdict and measured-or-null telemetry; it does not modify Atlas production files or evaluation v2.

After both reviewed tasks are complete, use a fresh external sealed destination and an unseen de-branded Atlas-bound fixture. Do not change evaluation v2 or store artifacts in live Atlas.

- Compare source-only with corrected hybrid on: known-path exact value; unclear local question answered by Atlas; transversal flow with one missing exact detail; zero-retrieval follow-up; docs/config conflict; exact-range clean revert requiring Git verification; unknown owner/SLA refusal.
- Separately pressure-test an AWS semantic-risk change with a frozen standard, flow, incident, runbook, and test/rollback obligation.
- Promote only if source control is correct, hybrid matches its accuracy, all fallbacks/provenance are disclosed, exact claims are source-supported, the follow-up uses zero retrieval calls, hybrid warm retrieval calls are lower, unbound automatic routing is absent, direct Ask Atlas works regardless of binding, and all repository validation gates remain clean.

# Sealed Atlas versus Source Comparison Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Harden Atlas evaluation tooling so new sealed runs can perform an auditable paired Atlas-only versus raw-source-only comparison from onboarding through incremental retrieval.

**Architecture:** Preserve v1 readers and scoring as a legacy path. Add a v2 run/freeze/result path with canonical paired questions, protected per-question telemetry, evidence-bearing gates, master freeze verification, and deterministic comparison derivation; bind the existing CLI to the sealed run for v2.

**Tech Stack:** Python 3.11 standard library, pytest, JSON/JSONL, existing Atlas CLI.

**Spec:** `docs/superpowers/specs/2026-08-18-sealed-atlas-source-comparison-design.md`

## Global Constraints

- Preserve v1 Harbor artifacts and behavior; never silently upgrade v1 guarantees.
- New runs default to v2 and never store fixture content in this Atlas repository.
- No new dependency, service, daemon, database, or network requirement.
- Observable telemetry is non-negative or `null`; never estimate it.
- Strict Atlas-only and raw-source-only remain the two primary paired arms.
- All result comparison metrics are derived from canonical grades and frozen telemetry, never trusted from judge-entered M6 summaries.
- Use TDD with a witnessed relevant failure before production changes.
- Preserve unrelated tracked/untracked work and do not push, merge, or publish.

---

### Task 1: Versioned run preparation, paired questions, gates, and master freeze

**Files:**
- Modify: `scripts/lib/evaluation.py`
- Modify: `scripts/atlas_eval.py`
- Modify: `evaluation/rubric.json`
- Modify: `tests/unit/test_evaluation.py`

**Interfaces:**
- Produces `RUN_SCHEMA_V2`, paired-question validation, v2 skeleton directories, `freeze_run`, and `verify_run_freeze`.
- Keeps `freeze_answers` and `verify_answer_freeze` operational for v1 runs.
- Produces rubric `gate_definitions` keyed exactly by G1-G8.

- [ ] Add tests proving v2 prepare creates questions/telemetry/manifests folders, records v2 metadata, and keeps destinations outside Atlas.
- [ ] Add tests proving malformed/duplicate paired questions and missing required manifest inputs block v2 freeze.
- [ ] Add tests proving master freeze detects mutation, addition, or removal in every protected root and detects immutable run-metadata drift.
- [ ] Run the focused tests and record the expected RED failures.
- [ ] Implement the minimal v2 preparation, validation, freeze, and verification behavior while retaining the v1 functions.
- [ ] Run focused and full evaluation tests; commit exact task files and the approved spec/plan documents.

### Task 2: Evidence-bearing v2 results and deterministic paired metrics

**Files:**
- Modify: `scripts/lib/evaluation.py`
- Modify: `tests/unit/test_evaluation.py`

**Interfaces:**
- Consumes the frozen v2 paired question manifest and per-arm telemetry records from Task 1.
- Produces v2 result validation, normalized paired grades, derived M5/M6 comparison metrics, condition summaries, and observable break-even values.
- Requires the caller-supplied `expected_freeze_manifest_sha256` trust anchor for v2 validation and scoring; it is never inferred from mutable run state and remains ignored for v1.
- Leaves `atlas-evaluation-result/1.0` validation/scoring unchanged.

- [ ] Add tests for exact pair membership/category matching and rejection of missing, extra, or duplicate question results.
- [ ] Add tests requiring `{passed, evidence}` for every v2 G1-G8 entry and frozen evidence paths.
- [ ] Add literal expected-value tests for accuracy delta, Atlas hit rate, fallback disclosure, read-cost reduction, per-condition summaries, and break-even values.
- [ ] Add boundary tests for null telemetry, zero control bytes, negative savings, and source-access protocol violations.
- [ ] Run focused tests and record the expected RED failures.
- [ ] Implement v2 validation and deterministic derivation without accepting judge-entered M6 values.
- [ ] Run focused and full evaluation tests; commit exact task files.

### Task 3: Bind CLI validation/scoring to the v2 sealed run

**Files:**
- Modify: `scripts/atlas_eval.py`
- Modify: `scripts/lib/evaluation.py`
- Modify: `tests/unit/test_evaluation.py`

**Interfaces:**
- Consumes Task 1 freeze verification and Task 2 result normalization.
- Adds optional `--run-root` for non-standard result placement and required v2 `--freeze-digest` on verify, validate, and score.
- For v2, infers the normal run root from `<run-root>/results/<result>.json`, rejects a conflicting override or run/result schema mismatch, verifies freeze against the caller-trusted digest, rejects any rubric not resolving to the frozen run rubric, and prints derived comparison metrics with the score.
- The judge captures the manifest SHA-256 outside the mutable run immediately after freeze and supplies it to both verification checks, validation, and scoring; coordinated in-run rewriting cannot rebind that original anchor.

- [ ] Add CLI tests showing v2 validate/score fail for a changed freeze, mismatched run-root, or substituted rubric.
- [ ] Add a CLI success test covering prepare → freeze → validate → score using a complete synthetic external run.
- [ ] Run focused tests and record the expected RED failures.
- [ ] Implement the CLI binding and error messages.
- [ ] Run focused and full evaluation tests; commit exact task files.

### Task 4: Operational contract, role profiles, examples, and integration validation

**Files:**
- Modify: `evaluation/README.md`
- Modify: `.agents/skills/atlas-evaluate/SKILL.md`
- Modify: `.agents/skills/atlas-evaluate/references/protocol.md`
- Modify: `.codex/agents/atlas-evaluation-fixture-preparer.toml`
- Modify: `.codex/agents/atlas-evaluation-user.toml`
- Modify: `.codex/agents/atlas-evaluation-interrogator.toml`
- Modify: `.codex/agents/atlas-evaluation-control.toml`
- Modify: `.codex/agents/atlas-evaluation-judge.toml`
- Modify: `tests/unit/test_evaluation.py` only if an executable example exposes a missing behavior

**Interfaces:**
- Documents the exact v2 artifact contract and two-arm boundaries implemented by Tasks 1-3.
- Keeps fixture content and run outputs external.

- [ ] Document v1 legacy versus v2 master-frozen guarantees without overstating cryptographic security.
- [ ] Document paired-question, telemetry, gate-evidence, freeze, validate, and score examples.
- [ ] Update each role with its allowed inputs and required v2 handoff.
- [ ] Exercise the documented synthetic v2 workflow in a temporary external directory.
- [ ] Run full pytest, Atlas lint, rebuild check, and diff check.
- [ ] Commit exact documentation/profile files and any required executable-example test.

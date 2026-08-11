---
name: atlas-evaluate
description: Prepare, run, or independently score a sealed Atlas end-to-end evaluation with isolated fixture, user, interrogation, control, and judge roles.
---

# atlas-evaluate

Resolve and validate Atlas, then read `evaluation/README.md`, `evaluation/rubric.json`, and `references/protocol.md`. Require an explicit sealed destination outside Atlas.

- `prepare`: run `scripts/atlas_eval.py prepare`; delegate provenance/de-branding/history/ground-truth separation to the fixture preparer; freeze cold and incremental fixture HEADs.
- `run`: use disposable worktrees; one simulated user supervises onboarding and curation, then fresh interrogation/control roles answer frozen questions. The control receives no Atlas or managed product instructions and scans hidden files. After all answers exist, run `scripts/atlas_eval.py freeze <run-root>` before ground truth is readable.
- `score`: only the independent judge reads the sealed key. It runs `verify-freeze` before opening truth and again before returning, verifies citations, assigns frozen grades/G1-G8, then runs deterministic validate/score.

Record only observable telemetry and use `null` when unavailable. Fixture-only commits are permitted only in the explicit external destination. Never publish or approve Atlas knowledge, contaminate real Atlas with fixture content, or let an evaluated role grade itself.

---
name: atlas-evaluate
description: Prepare, run, or independently score a sealed Atlas evaluation with isolated fixture, user, interrogation, control, and judge roles. Use for reproducible end-to-end Atlas benchmarking, regression evaluation, or scoring a frozen answer set; never for ordinary Atlas validation.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-evaluate

Read `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `references/protocol.md`. Determine whether the invocation is `prepare`, `run`, or `score`. Require an explicit external sealed destination and keep all fictional fixture knowledge, personas, keys, baselines and outputs outside Atlas.

## Prepare

1. Validate that the destination is outside `ATLAS_ROOT`; run `scripts/atlas_eval.py prepare` to create the run skeleton and freeze the rubric before results exist.
2. Delegate fixture work only to `atlas-evaluation-fixture-preparer`. Record source licence/provenance, de-branding, fixture-only history and frozen HEAD. Keep persona material separate from judge-only ground truth and question keys.
3. Create an incremental second fixture revision after the cold-start revision and record both immutable HEADs. Fixture-only commits are permitted only inside the explicitly requested external destination.

## Run

1. Use disposable Atlas and fixture worktrees. The same `atlas-evaluation-user` supervises onboarding and curation without reading ground truth. Fresh `atlas-evaluation-interrogator` and `atlas-evaluation-control` agents receive the frozen questions.
2. The control receives neither Atlas nor the managed product instructions. Include hidden files in its authorised scan. Both arms answer impact questions.
3. After every answer set exists, run `scripts/atlas_eval.py freeze <run-root>` before any tested role or parent workflow can read the sealed key. Record only observed bytes read, unique evidence sources, tool calls and latency; use `null` when unavailable.
4. Repeat on the incremental revision after the cold-start run. Never let result agents grade themselves.

## Score

1. Delegate only to `atlas-evaluation-judge`. The judge runs `scripts/atlas_eval.py verify-freeze <run-root>` and verifies the rubric hash before opening judge-only ground truth, then verifies the freeze again immediately before returning.
2. Independently verify citations, assign the frozen grades, complete G1-G8, and write the result schema described in `references/protocol.md`.
3. Run `scripts/atlas_eval.py validate`, then `score`. The deterministic script calculates; the judge interprets. Any fabrication, failed governance gate, or incomplete honest refusal yields `Not ready`.

Never commit, push, merge, approve or publish Datalens Atlas knowledge. Do not copy fixture facts into Atlas outside disposable evaluation worktrees. Preserve the sealed destination for reproducibility and report exact paths, HEADs, hashes, validation and observable telemetry.

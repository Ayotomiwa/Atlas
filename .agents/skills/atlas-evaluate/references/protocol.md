# Evaluation isolation protocol

## Experimental boundary

V2 compares a fully authored, independently reviewed Atlas snapshot with raw-source-only retrieval. Treat authoring as a separate fixed-cost phase and each canonical paired question as the primary experimental unit. The same frozen prompt is answered once by each retrieval arm and graded against the same frozen truth and rubric.

Keep every fixture, persona, question, truth, answer, telemetry record, result, worktree, and run output in the explicit external destination. The live Atlas checkout and source repository are not evaluation storage.

## Role handoffs

1. The fixture preparer sees source and the sealed destination. It records provenance/licence/de-branding, creates realistic immutable cold and incremental history, prepares canonical paired questions and judge-only truth, and supplies `manifests/fixture.json`, `manifests/tool-policy.json`, `manifests/model-config.json`, and `manifests/atlas-snapshot.json`. It never answers or grades.
2. The simulated author sees disposable Atlas and fixture worktrees plus an authoring persona only. It never receives paired questions, truth, answers, scores, or category quotas. It completes governed onboarding, staging, curation, validation, independent review, and frozen Atlas snapshot export without merge, push, publication, self-review, or self-grading.
3. The Atlas interrogator receives one frozen paired question and the frozen Atlas snapshot only. Product source and fixture worktrees are absent. There is no bounded source fallback, including under time pressure. It answers only from the snapshot and does not execute fixture/source/snapshot code unless the frozen tool policy explicitly permits that tool action. It writes the run-defined attributable answer and `telemetry/atlas/<question-id>.json` without reading truth, control answers, or prior reports.
4. The control receives the same frozen question and the raw fixture, including hidden files and relevant Git history. It receives no Atlas package/snapshot, managed Atlas or product instructions, network, persistent scratch index or retained cross-question/cross-run notes, truth, Atlas answers, or prior reports. Any working notes are transient and question-local; only its run-defined source-cited answer and `telemetry/control/<question-id>.json` persist. It never grades.
5. After both arms finish and all protected inputs exist, the coordinator creates the v2 master freeze, records the SHA-256 of `freeze-manifest.json` outside protected/mutable run state, and hands it to the judge separately. Without that external digest the judge stops before truth. Only after successful verification does the judge receive frozen answers and truth. The judge verifies against the caller-trusted digest before opening truth and again before returning, checks citations, assigns allowed question judgments and evidence-bearing G1-G8, and runs deterministic validate/score with the same digest. It never edits protected artifacts or enters M5/M6 summaries.

## V2 artifacts and telemetry

A v2 run uses `atlas-evaluation-run/2.0` and `atlas-evaluation-result/2.0`. Before freezing, every protected root must be non-empty: `fixture/`, `questions/`, `personas/`, `ground-truth/`, `answers/`, `telemetry/`, and `manifests/`. `questions/paired.jsonl` is canonical. Each line requires a unique non-empty `id`, supported `category` (`LOOKUP`, `SYNTHESIS`, `IMPACT`, `TRAP-CONFLICT`, `TRAP-UNKNOWABLE`, or `TRAP-ABSENCE`), supported `condition` (`cold`, `warm`, `fresh-session`, `transversal`, or `incremental`), `revision` (`cold` or `incremental`), and one non-empty `prompt` shared by both arms.

`manifests/tool-policy.json` is a required role input and freezes each role's exact tools, budgets/timeboxes, answer paths/formats, and citation representation. If it is absent, unreadable, or lacks any of those fields for the active role, stop before answering and report a protocol failure/`Not ready`; never improvise. Otherwise follow it and the v2 contract without inventing another answer schema.

Each arm has its own answer and `atlas-evaluation-telemetry/1.0` file. Record measured `bytes_read`, `unique_evidence_sources`, `tool_calls`, `latency_ms`, `input_tokens`, and `output_tokens`, using `null` when unavailable and never estimating. The strict Atlas record has `source_accessed: false`, `atlas_accessed: true`, `fallback_used: false`, and `fallback_disclosed: null`; `atlas_hit` is the observed boolean. A pure control record has `source_accessed: true`, `atlas_accessed: false`, and `atlas_hit`, `fallback_used`, and `fallback_disclosed` set to `null`. Any recorded Atlas source access or control Atlas access is a protocol violation and forces `Not ready`.

When observable, `telemetry/authoring.json` uses `atlas-evaluation-phase-telemetry/1.0`, `phase: "authoring"`, and the same six observable fields. Missing values remain `null` and earn no efficiency credit. Fixed authoring cost is never mixed into per-question telemetry.

The judge supplies exact paired question results, citation/provenance judgments, rationales, and all G1-G8 objects as `{passed, evidence}`. Evidence lists are non-empty and identify run-relative protected frozen files supporting the gate; the digest-bound `freeze-manifest.json` is also allowed as master-freeze evidence. The harness derives M5/M6, paired and condition summaries, arm-purity status, negative/null read reduction, and separate break-even values for every observable dimension with positive marginal savings.

## Freeze and judging order

For v2, execute these CLI forms from the Atlas checkout: `python scripts/atlas_eval.py prepare --destination <external-root> --run-id <id> --fixture <fixture> --fixture-head <cold-id> --incremental-head <incremental-id>`; populate the external run; then run `python scripts/atlas_eval.py freeze <run-root>`. Immediately hash `freeze-manifest.json` and retain that digest outside protected/mutable run state in a coordinator-controlled medium.

The judge receives the digest separately and runs `python scripts/atlas_eval.py verify-freeze <run-root> --freeze-digest <retained-digest>` before truth and again before returning. Standard `<run-root>/results/result.json` placement infers the run: use `python scripts/atlas_eval.py validate <run-root>/results/result.json --freeze-digest <retained-digest>` and the corresponding `score` form. For a non-standard result path, add `--run-root <run-root>` to both commands. Never recover the trusted value from `run.json` or other protected/mutable run state at judging time.

The first trusted verification happens before the judge opens truth or writes the unprotected result. The second happens after judging and before return. Hashes plus the separately trusted digest detect ordinary protected-file/metadata drift and coordinated in-run rebinding; they are not a signature and offer no protection when the actor can replace the out-of-band digest too.

Legacy `atlas-evaluation-run/1.0`, `atlas-evaluation-answer-freeze/1.0`, and `atlas-evaluation-result/1.0` remain an answer-only compatibility path. They do not acquire v2 master-freeze, paired-question, telemetry, or out-of-band digest guarantees.

A synthetic or single-fixture rehearsal proves process execution only. Confirmatory claims require new unseen external fixtures and must state fixture, question, condition/revision, and model scope.

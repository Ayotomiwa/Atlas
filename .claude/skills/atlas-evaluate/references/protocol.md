# Sealed evaluation protocol

## Isolation matrix

| Role | May read | Must not read |
|---|---|---|
| Fixture preparer | source fixture, external destination, reusable evaluation contract | real datalens knowledge unrelated to preparation |
| Simulated user | disposable fixture and Atlas worktrees, persona | ground truth, ideal answers, judge notes |
| Interrogator | disposable fixture, Atlas, frozen questions | ground truth, preparation/user reports, control answers |
| Control | fixture including hidden files, frozen questions | Atlas, managed product instructions, ground truth, Atlas answers |
| Judge | frozen rubric, frozen answers, ground truth, fixture | no restriction needed after freeze; never alters answers |

The source fixture, ground truth, questions, personas, baselines, worktrees and results live below the user-supplied sealed directory. Datalens Atlas contains only generic tooling.

## Frozen result contract

Use `schema_version: atlas-evaluation-result/1.0`, the exact `rubric_sha256`, G1-G8 booleans, and metrics M1/M2/M4/M5/M6. M5 question rows contain unique `id`, `arm` (`atlas` or `control`), frozen category, and grade. Impact must appear in both arms. Telemetry fields `bytes_read`, `unique_evidence_sources`, `tool_calls`, and `latency_ms` are non-negative observations or `null`; never estimate.

The rubric defines `PARTIAL = 0.5`, fixed weights and targets. `CORRECT` and `REFUSED-CORRECTLY` equal 1; wrong, fabricated and wrongly refused equal 0. The independent judge verifies citations and assigns grades before deterministic scoring.

## Freeze and cleanup

- Freeze fixture HEAD and rubric before running.
- Freeze Atlas/control answer bytes with `atlas_eval.py freeze` before exposing ground truth; the judge verifies the manifest before reading truth and before returning.
- Preserve the cold-start run, incremental revision, baseline and final result externally.
- Purge fictional pages/domains from the real Atlas checkout only after regression evidence is preserved and revalidate the clean package.

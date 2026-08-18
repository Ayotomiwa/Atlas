# Sealed Atlas versus source comparison design

## Goal

Make Atlas evaluations capable of an auditable paired comparison between a fully authored, curated Atlas snapshot and a raw-source-only control. New evaluations must expose Atlas's fixed onboarding and curation cost separately from marginal retrieval cost, while existing v1 sealed runs remain readable and verifiable as legacy answer-only evaluations.

## Boundaries

- The primary comparison has two retrieval arms: strict Atlas-only and raw-source-only.
- Atlas authoring may read the immutable fixture, but the frozen Atlas interrogator must not have product-source access.
- The control may read the same frozen source, hidden files, and Git history, but must not receive Atlas, managed Atlas instructions, network access, or a persistent scratch index.
- Fixture preparation, authoring, interrogation, control, and judging remain separate roles.
- Question text and ground truth remain hidden from authoring roles.
- Existing Harbor v1 artifacts must never be opened, migrated, rewritten, or described as master-frozen by this change.
- Do not add a service, daemon, database, dependency, or fixture content to this repository.

## Versioned contracts

New `prepare` runs use `atlas-evaluation-run/2.0`. Legacy `atlas-evaluation-run/1.0`, `atlas-evaluation-answer-freeze/1.0`, and `atlas-evaluation-result/1.0` remain supported without gaining v2 guarantees.

A v2 run contains:

- `questions/paired.jsonl`: one canonical paired question per line;
- `personas/`: frozen authoring/user prompts;
- `ground-truth/`: judge-only keys;
- `fixture/`: frozen fixture material or its prepared snapshot;
- `manifests/fixture.json`, `tool-policy.json`, `model-config.json`, and `atlas-snapshot.json`;
- `answers/`: immutable answer bytes;
- `telemetry/atlas/<question-id>.json` and `telemetry/control/<question-id>.json`, plus authoring telemetry when observed;
- `results/results.json`: judge grades and gate evidence;
- `freeze-manifest.json`: the master pre-judge digest manifest.

Every paired question has a unique `id`, one supported category, a condition (`cold`, `warm`, `fresh-session`, `transversal`, or `incremental`), a revision (`cold` or `incremental`), and one shared prompt. Atlas-specific routing diagnostics are not part of the primary paired score.

Every per-question telemetry record identifies the question and arm, records observable non-negative values or `null`, and records Atlas hit/fallback/source-access state without estimates. Answer grades reference the frozen telemetry record rather than supplying comparison summaries.

## Freeze integrity

The v2 freeze hashes the rubric and every file under fixture, questions, personas, ground truth, answers, telemetry, and manifests. It also records an immutable projection of run metadata. The required manifest files and paired question bank must exist and validate before freezing. Verification detects changed, missing, and unexpected protected files and rejects a changed immutable metadata projection.

The manifest does not provide a cryptographic signature against a malicious actor who can rewrite the entire sealed destination. Role isolation and an out-of-band recorded manifest digest remain required. Immediately after freeze, the judge records the manifest SHA-256 outside mutable run state and supplies that caller-trusted digest to both freeze-verification checks, result validation, and scoring. Coordinated rewriting of protected files, the manifest, run metadata, and result digest must not be accepted against that original anchor. The harness must not claim signature or access-control guarantees.

## Gates

The rubric defines G1-G8 with names, requirements, and expected evidence:

1. frozen fixture identity and de-branding/provenance;
2. live Atlas and source immutability;
3. question/truth isolation;
4. verified cold Atlas baseline;
5. governed authoring, validation, and independent review;
6. retrieval-arm purity;
7. citation, fabrication, absence, and refusal integrity;
8. pre-judge freeze and reproducible deterministic scoring.

In v2 results each gate contains `passed: bool` and a non-empty list of evidence paths. Every evidence path must identify a file protected by the master freeze. A false gate invalidates the run.

## Deterministic comparison

The judge supplies question grades and evidence-quality judgments, not M6 summary values. The harness pairs Atlas and control attempts by the canonical question ID and derives:

- mean Atlas and control correctness and their accuracy delta;
- Atlas hit rate;
- fallback disclosure rate (1.0 when no fallback was used);
- source/read-cost reduction from observable paired bytes only;
- per-condition comparison summaries;
- fixed-cost break-even values for every observable cost dimension with a positive marginal saving.

Missing telemetry remains `null` and earns no efficiency credit. Negative read savings remain visible in the comparison output and receive no positive score. The legacy M1-M6 score remains available for continuity; paired derived metrics are the authoritative v2 comparison values.

## CLI and role behavior

`prepare`, `freeze`, `verify-freeze`, `validate`, and `score` retain their names. For v2 result files, validate and score infer the run root from the normal `<run-root>/results/<result>.json` placement or accept an explicit `--run-root` for non-standard placement. They establish v2 from `run.json`, require the result schema to agree, verify the master freeze against required `--freeze-digest`, bind to the resolved `<run-root>/rubric.json`, validate paired questions and telemetry references, then derive comparison metrics. A v2 explicit `--rubric` must resolve to that frozen rubric. `verify-freeze` also requires the caller-trusted digest for v2. Legacy v1 validation, scoring, verification, and success wording remain unchanged without the digest.

Role profiles must instruct preparers to create the paired/manifests inputs, authoring roles not to inspect questions, strict interrogators to obey the frozen tool policy, controls to remain source-only, and judges to verify the master freeze before truth and again before returning.

## Acceptance

- All new production behavior is introduced test-first with observed failures.
- Mutation tests cover protected fixture/question/persona/ground-truth/answer/telemetry/manifest files and immutable run metadata.
- Result tests cover missing or mismatched pairs, bad gate evidence, null telemetry, negative/zero denominators, deterministic metrics, and legacy compatibility.
- CLI tests prove v2 validation/scoring cannot bypass the run freeze or substitute a rubric.
- Full unit tests, Atlas lint, and generated-surface check pass.

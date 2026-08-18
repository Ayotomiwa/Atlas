# Atlas evaluation tooling

All fixture content, personas, questions, ground truth, answers, telemetry, results, worktrees, and run outputs belong in an explicit sealed destination outside this Atlas checkout. This folder contains only the reusable harness and rubric.

The v2 evaluation compares the complete fixed cost of creating a governed, curated Atlas snapshot with the marginal retrieval performance of that snapshot against raw-source-only retrieval with no persistent preprocessing. Its primary experimental unit is one paired question: one canonical frozen prompt answered once by the strict Atlas-only arm and once by the raw-source-only control, then graded against the same frozen truth and rubric.

Authoring is a separate pre-retrieval phase. Repository selection and cold/incremental snapshot preparation, onboarding, staging, curation, validation, independent review, and Atlas snapshot export happen before interrogation. Their observable cost belongs only in authoring telemetry and is never mixed into per-question marginal telemetry. Authors may see source and an authoring persona, but never paired questions, ground truth, answers, scores, or category quotas.

## Versioned contracts

New runs use `atlas-evaluation-run/2.0`, a master run freeze, and `atlas-evaluation-result/2.0`. The master freeze covers the frozen rubric plus fixture, questions, personas, ground truth, answers, telemetry, and manifests. The Atlas interrogator receives only one frozen question and the frozen Atlas snapshot; product source is unavailable. The control receives the same question and frozen raw fixture, including hidden files and relevant Git history, but no Atlas package or snapshot, Atlas-managed instructions, network, or persistent scratch index.

Legacy `atlas-evaluation-run/1.0` runs retain their `atlas-evaluation-answer-freeze/1.0` and `atlas-evaluation-result/1.0` path. Those artifacts remain readable, verifiable, and scoreable as answer-only evaluations. They do not gain v2 master-freeze, paired-arm, telemetry, or caller-trusted-digest guarantees.

## V2 run layout

`prepare` creates the external skeleton; specialist roles populate it before the master freeze.

```text
<run-root>/
|-- run.json
|-- rubric.json
|-- fixture/
|-- questions/
|   `-- paired.jsonl
|-- personas/
|-- ground-truth/
|-- answers/
|-- telemetry/
|   |-- atlas/<question-id>.json
|   |-- control/<question-id>.json
|   `-- authoring.json                 # optional when observable
|-- manifests/
|   |-- fixture.json
|   |-- tool-policy.json
|   |-- model-config.json
|   `-- atlas-snapshot.json
|-- results/
|   `-- result.json
|-- worktrees/
`-- freeze-manifest.json               # created by freeze
```

Every protected root (`fixture`, `questions`, `personas`, `ground-truth`, `answers`, `telemetry`, and `manifests`) must be non-empty before `freeze`. The four named manifests are required. The fixture manifest records immutable cold and incremental identities; the tool policy fixes the allowed inputs, exact tools, budgets/timeboxes, answer paths/formats, and citation representation for each role; the model configuration records the evaluated model/setup; and the Atlas snapshot manifest identifies the independently reviewed frozen Atlas export. Roles follow those frozen answer and citation conventions rather than inventing another machine schema.

Each line of `questions/paired.jsonl` is one JSON object with these required fields:

- `id`: unique, non-empty question identifier;
- `category`: `LOOKUP`, `SYNTHESIS`, `IMPACT`, `TRAP-CONFLICT`, `TRAP-UNKNOWABLE`, or `TRAP-ABSENCE`;
- `condition`: `cold`, `warm`, `fresh-session`, `transversal`, or `incremental`;
- `revision`: `cold` or `incremental`;
- `prompt`: the single non-empty prompt shown unchanged to both retrieval arms.

## Telemetry, grades, and gates

Each arm writes a separate answer and a separate `atlas-evaluation-telemetry/1.0` record for every paired question. A question telemetry record contains `question_id`, `arm`, the observable fields `bytes_read`, `unique_evidence_sources`, `tool_calls`, `latency_ms`, `input_tokens`, and `output_tokens`, plus `atlas_hit`, `fallback_used`, `fallback_disclosed`, `source_accessed`, and `atlas_accessed`.

Every observable is a measured non-negative finite number or `null`; never estimate it. The strict Atlas record has `source_accessed: false`, `atlas_accessed: true`, `fallback_used: false`, and `fallback_disclosed: null`; `atlas_hit` is the observed boolean. It answers only from the frozen Atlas snapshot and does not execute fixture, source, or snapshot code unless the frozen tool policy explicitly permits that tool action. The control has `source_accessed: true`, `atlas_accessed: false`, and `atlas_hit`, `fallback_used`, and `fallback_disclosed` set to `null`. Its working notes are transient and question-local; only the answer and telemetry persist. Recorded Atlas source access or control Atlas access is a protocol violation, fails arm purity, and forces `Not ready`.

Optional authoring telemetry uses `atlas-evaluation-phase-telemetry/1.0`, `phase: "authoring"`, and the same six observable fields. It records the fixed cost of the entire pre-retrieval authoring phase. Missing per-question or authoring observables remain `null` and earn no efficiency or break-even credit.

The judge assigns only the rubric's allowed question judgments (`CORRECT`, `PARTIAL`, `WRONG`, `FABRICATED`, `REFUSED-CORRECTLY`, or `REFUSED-WRONGLY`), citation/provenance judgments, rationales, and evidence-bearing G1-G8 outcomes. Each gate has `passed` plus a non-empty list of run-relative evidence paths naming protected frozen files; the digest-bound `freeze-manifest.json` is also permitted as master-freeze evidence. Evidence should identify the protected fixture identity/provenance, immutable inputs, question/truth isolation, cold baseline, governed authoring and independent review, arm purity, answer integrity, and reproducible pre-judge freeze that the gate claims.

The harness derives M5/M6 summaries; the judge never enters them. It reports Atlas/control accuracy, accuracy delta, Atlas hit rate, fallback disclosure, observable read-cost reduction, and condition-specific accuracy/read summaries. Negative read reduction remains visible and receives no positive efficiency credit. A missing value or zero control denominator yields `null`.

Break-even is derived separately for `bytes_read`, `tool_calls`, `latency_ms`, `input_tokens`, and `output_tokens`: fixed authoring cost divided by the positive per-question marginal saving in that dimension. A dimension is `null` when authoring or paired retrieval observations are missing, or when the marginal saving is zero or negative. There is no universal break-even claim.

## Complete v2 workflow

Use a new external destination and immutable source revision identifiers. The following PowerShell sequence is copyable after replacing the placeholders and completing each indicated specialist handoff:

```powershell
$evaluationRoot = 'C:\sealed\atlas-evals'
$runId = 'sample-v2'
$fixture = 'C:\sealed\fixtures\sample-project'
$fixtureHead = '<cold-revision-id>'
$incrementalHead = '<incremental-revision-id>'
$runRoot = Join-Path $evaluationRoot $runId

python scripts/atlas_eval.py prepare `
  --destination $evaluationRoot `
  --run-id $runId `
  --fixture $fixture `
  --fixture-head $fixtureHead `
  --incremental-head $incrementalHead

# Fixture preparation and governed authoring now populate every protected root,
# both arms answer every paired question, and all required telemetry/manifests exist.
python scripts/atlas_eval.py freeze $runRoot

# Retain this value outside protected and mutable run state immediately.
$freezeDigest = (Get-FileHash (Join-Path $runRoot 'freeze-manifest.json') -Algorithm SHA256).Hash.ToLowerInvariant()
python scripts/atlas_eval.py verify-freeze $runRoot --freeze-digest $freezeDigest

# Hand the digest to the judge separately. Only now may the judge open frozen
# truth and write the standard results/result.json.
$result = Join-Path $runRoot 'results\result.json'
python scripts/atlas_eval.py verify-freeze $runRoot --freeze-digest $freezeDigest
python scripts/atlas_eval.py validate $result --freeze-digest $freezeDigest
python scripts/atlas_eval.py score $result --freeze-digest $freezeDigest
```

Both arms must finish and every protected artifact and telemetry file must exist before `freeze`. After the digest is captured out of band in a coordinator-controlled medium and handed separately to the judge, the first verification may run. Without that external digest the judge stops before truth. After verification, the judge may open truth and write only the unprotected result file. The judge verifies the master freeze again before returning, and supplies the same independently retained digest to `validate` and `score`; it never rereads a trusted digest from protected or mutable run state.

Normal `<run-root>/results/<result>.json` placement infers the v2 run. A copied result at a non-standard path requires the Task 3 override:

```powershell
$outsideResult = 'C:\sealed\judge-output\sample-v2-results.json'
Copy-Item $result $outsideResult
python scripts/atlas_eval.py validate $outsideResult --run-root $runRoot --freeze-digest $freezeDigest
python scripts/atlas_eval.py score $outsideResult --run-root $runRoot --freeze-digest $freezeDigest
```

The master manifest hashes the protected files and immutable run-metadata projection. Comparing it with the caller-supplied out-of-band manifest digest detects ordinary protected-file or metadata drift and coordinated in-run rebinding. It is not a signature or access-control boundary and cannot protect a run when an actor can also replace the separately trusted digest. Record that digest outside the run immediately after freezing.

A synthetic or single-repository rehearsal validates only that the process and isolation contract execute. Confirmatory effectiveness claims require new unseen external fixtures and must identify their fixture, question-bank, condition/revision, and model scope; do not generalize from one rehearsal.

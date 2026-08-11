# Atlas evaluation tooling

This folder contains reusable, non-fixture evaluation contracts. Fictional repositories, personas, ground truth, question keys, answer sets, baselines and run outputs belong in a separate user-supplied sealed directory outside Datalens Atlas.

The canonical Claude workflow is `/atlas-evaluate prepare|run|score`; the Codex adaptation in `.agents/skills/atlas-evaluate/` executes the same isolation and scoring contract when requested. `scripts/atlas_eval.py` creates a sealed run skeleton, freezes this rubric and answer bytes, validates result data and calculates the score after an independent judge has verified citations and assigned grades.

The frozen contract sets `PARTIAL = 0.5`, fixed family/internal weights, control-arm impact questions, hidden-file scanning, governance/fabrication gates and observable-only telemetry. Do not estimate missing bytes, evidence counts, tool calls or latency: store `null`.

```powershell
python scripts/atlas_eval.py prepare --destination C:\sealed\atlas-evals --run-id sample-run --fixture C:\fixtures\sample-project --fixture-head <sha>
python scripts/atlas_eval.py freeze C:\sealed\atlas-evals\sample-run
python scripts/atlas_eval.py verify-freeze C:\sealed\atlas-evals\sample-run
python scripts/atlas_eval.py validate C:\sealed\atlas-evals\sample-run\results\results.json
python scripts/atlas_eval.py score C:\sealed\atlas-evals\sample-run\results\results.json
```

`prepare` refuses a destination inside this Atlas checkout. It creates metadata and frozen-rubric files only; specialist agents own fixture provenance/de-branding, disposable worktrees and isolation. `freeze` records every answer file and digest; the judge runs `verify-freeze` before reading sealed truth and again before returning.

# Evaluation isolation

Fixture preparation sees sources and the sealed destination. The simulated user sees disposable Atlas/fixture worktrees and persona, never ground truth. The interrogator sees Atlas plus fixture and frozen questions, never prior reports. The control sees fixture including hidden files but no Atlas or managed instructions. Only the judge reads frozen answers and ground truth after answer freeze.

Use `atlas-evaluation-result/1.0`, exact rubric hash, G1-G8, M1/M2/M4/M5/M6, both-arm impact questions, and observable-or-null telemetry. Freeze answer content with `atlas_eval.py freeze`; the judge verifies that manifest before opening truth and before returning. Preserve cold, incremental, baseline and result artifacts externally; purge fictional knowledge from real Atlas after regression.

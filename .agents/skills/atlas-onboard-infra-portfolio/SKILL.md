---
name: atlas-onboard-infra-portfolio
description: Use when preparing, running, resuming, inspecting, or pausing a resumable onboarding campaign for many confirmed infrastructure product boundaries; use atlas-onboard-repository for one boundary.
---

# atlas-onboard-infra-portfolio

Read the shared human-intent, persistence, runtime, provenance, handoff and curation-safety contracts; `references/campaign-workflow.md`; `_intake/README.md`; and the existing `atlas-onboard-repository` skill. This is portfolio **Sync Atlas**.

Choose `prepare`, `run`, `resume`, `status`, or `pause`. Own only the confirmed inventory, pilot and queue. Every item uses `atlas-onboard-repository`, which uses the read-only `atlas-repo-analyst` and retains source-selection, semantic staging, validation and local-commit ownership.

Read and update `_intake/onboarding/<campaign-id>.json` only through `scripts/atlas_onboarding_campaign.py` and its compare-and-swap digest. A stopped session does not continue in the background.

- Prepare from CSV/JSON or direct children of one explicitly named directory level. Preview the normalized inventory; never recursively discover or infer boundaries.
- Pilot three items by default. Expand above three, up to six, only when three cannot represent the materially distinct portfolio shapes. Require confirmation after pilot completion. Pause normal rollout for a small trial when a genuinely new archetype appears, and state the evidence showing why the confirmed pilot does not cover it.
- Use a batch of five in rollout and at most three concurrent read-only analyses. Serialize decisions, staging writes, validation, commits and queue updates.
- Present one combined preview and obtain one approval for the unchanged batch. Pass both into each exact onboarding handoff without asking again.
- Treat missing application coverage as a candidate/open question and never recursively enqueue it.
- Reconcile committed `onboarding_source` staging evidence before retrying. A compare-and-swap conflict reloads and stops rather than overwriting state.

An item completes only when it is `staged` with validated committed evidence and recorded IDs/commit, `already-covered` by adequate existing evidence, or explicitly `skipped` with a reason. This skill never curates and never clones repositories, pushes, merges, publishes, schedules background work, or creates another agent. Authority remains separate curation and human-controlled publication.

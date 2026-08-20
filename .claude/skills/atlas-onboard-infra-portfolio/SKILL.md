---
name: atlas-onboard-infra-portfolio
description: Use when preparing, running, resuming, inspecting, or pausing a resumable onboarding campaign for many confirmed infrastructure product boundaries; use atlas-onboard-repository for one boundary.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Agent
---

# atlas-onboard-infra-portfolio

Read `../_shared/human-intents.md`, `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, `../_shared/agent-handoffs.md`, `../_shared/curation-safety.md`, `references/campaign-workflow.md`, `_intake/README.md`, and the existing `atlas-onboard-repository` skill. This is the portfolio form of **Sync Atlas**.

Choose `prepare`, `run`, `resume`, `status`, or `pause` from the request. The controller owns only inventory, pilot and queue coordination. It never performs semantic onboarding: every item uses `atlas-onboard-repository`, which uses the read-only `atlas-repo-analyst` and remains responsible for source selection, evidence meaning, staging, validation and its local commit.

Use `python <ATLAS_ROOT>/scripts/atlas_onboarding_campaign.py` for validated, compare-and-swap campaign reads and writes. Store only non-authoritative progress at `_intake/onboarding/<campaign-id>.json`; do not hand-edit it. A stopped session does not continue in the background.

Apply these fixed coordination limits:

- `prepare` accepts CSV/JSON or direct children from one explicitly named directory level, presents the complete normalized inventory, and writes only after approval. Never recursively discover or infer product boundaries.
- Start with a representative pilot of three items by default. Expand it above three, up to six, only when three cannot represent the materially distinct portfolio shapes. Require the user to accept the completed pilot before rollout. A genuinely new archetype pauses normal rollout for a small new-archetype trial, and the controller states the evidence showing why the confirmed pilot does not cover it.
- Rollout uses a batch of five. Run no more than three read-only repository analyses concurrently. Serialize all user decisions, semantic staging writes, validation, local commits and campaign updates.
- Show one combined preview and obtain one approval for the exact unchanged batch. Pass that approval and each exact item slice into repository onboarding; do not ask again at the handoff.
- Treat missing application coverage only as a routing candidate or open question. Never recursively enqueue or onboard an application repository.
- On resume, reconcile committed staging records through `onboarding_source` before retrying queued work. A compare-and-swap conflict stops the write; reload the campaign instead of overwriting it.

An item is complete here only when it is `staged` with validated committed evidence and recorded IDs/commit, `already-covered` by adequate existing evidence, or explicitly `skipped` with a reason. This skill never curates and never clones repositories, pushes, merges, publishes, schedules background work, or creates another onboarding agent. Authority remains the separate curation workflow and human-controlled publication.

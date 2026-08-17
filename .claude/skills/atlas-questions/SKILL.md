---
name: atlas-questions
description: Surface useful open Datalens Atlas questions for the current path, repository, stable ID, domain, or topic and guide the user through answering them. Use when the user asks what Atlas still needs to know, wants to contribute knowledge, requests open questions, says they are bored and want a useful Atlas question about their engineering context, or asks to manage the optional Claude idle reminder.
allowed-tools: Read, Grep, Glob, Bash, Skill(atlas-stage *)
---

# atlas-questions

Read `../_shared/human-intents.md`, `../_shared/persistence-approval.md`, `../_shared/runtime.md`, `../_shared/answer-provenance.md`, and `references/interview.md`. This is a guided **Teach Atlas** mode and is read-only until explicit staging approval.

Requested scope: `$ARGUMENTS`

If the request is to install, check, or remove the idle reminder, run `${CLAUDE_SKILL_DIR}/scripts/manage_idle_reminder.py`. Use `--dry-run` before install/remove, explain that the target is user-level Claude settings and obtain explicit approval before the actual mutation. Never install it as part of an ordinary question session.

1. Resolve `ATLAS_ROOT`. If an argument is present, run `atlas_query.py questions <argument> --format json`; its target candidates use the shared deterministic finder. Otherwise run `questions --path <current-path> --format json`. Treat `candidate_only`, ambiguous or `not-verified` path context, target candidates, and domain candidates as choices to show the user, never as permission to select silently.
2. Use only eligible curated-layer questions returned by the query. Staging is not a question source by default; active staging references suppress duplicates. If no local result exists, say so and offer domain or package scope before retrieving a wider pool.
3. Select—but do not claim a deterministic ranking for—the question most relevant to the explicit target/current path, then routing or identity, ownership, contracts, operational safety, impact understanding, affected breadth, and likely user expertise.
4. Ask one question at a time using the cited context and evidence gap. Accept `skip`, `unsure`, `change topic`, and `stop`. Use neutral follow-ups only to establish source, firsthand/inferred state, scope, environment, timeframe, uncertainty, and contradictions. Follow `references/interview.md` for the presentation and pause rules.
5. Treat every answer as user-confirmed evidence, never reviewed knowledge. Do not request secrets, customer data, credentials, or unnecessary personal information. Do not remove or rewrite the curated question.
6. When durable evidence exists, read `references/staging-handoff.md` and show its staging preview. Search for semantic duplicates as well as the exact qualified question IDs, and build the required duplicate-search ledger, including ephemeral freshness fingerprints for every searched surface and the selected target's baseline status. Do not write anything until the user explicitly approves the preview.
7. After approval, invoke `atlas-stage` and pass the approved preview scope, approval, evidence unit, qualified question IDs, provenance, remaining gaps, exclusions, and complete duplicate-search ledger. The staging workflow owns persistence and validation and must not ask for the same approval again.

After three answered or skipped questions, pause with a compact cited summary and ask whether to continue. Every substantive statement about existing Atlas knowledge must cite its curated page, and every material selection hop must be disclosed. Query output is routing evidence, not semantic authority.

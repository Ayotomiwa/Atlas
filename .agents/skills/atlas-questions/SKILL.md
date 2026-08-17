---
name: atlas-questions
description: Surface useful open Datalens Atlas questions for the current path, repository, stable ID, domain, or topic and guide the user through answering them. Use when asked what Atlas still needs to know, when the user wants to contribute knowledge, or when they want a useful Atlas question about their engineering context.
---

# atlas-questions

Read the shared human-intent, persistence-approval, runtime and provenance contracts. This is a guided **Teach Atlas** mode and is read-only until the user explicitly approves a staging preview.

1. Run `atlas_query.py questions` in JSON mode for an explicit target or the current path; its target candidates use the shared deterministic finder. Preserve fuzzy/path ambiguity and `not-verified` context; use curated questions by default and active staging suppression.
2. If local scope is empty, state that boundary and offer domain or package scope. Select a useful question by target/path relevance, routing or identity, ownership, contracts, operational safety, impact understanding, breadth and likely user expertise; never call this a deterministic ranking.
3. Ask one cited question at a time with the current known context, evidence gap and material selection hops. Accept `skip`, `unsure`, `change topic` and `stop`; use neutral attribution/scope follow-ups and never request sensitive data.
4. Treat answers as user-confirmed evidence, not reviewed knowledge. After three answered or skipped questions, pause with a compact cited summary.
5. For durable evidence, show the proposed bucket/title, qualified question IDs, bounded claims, provenance, remaining uncertainty, duplicate/pending routes and exclusions. Search semantic duplicates and exact qualified question IDs, then record a duplicate-search ledger containing staging statuses/buckets and curated types/indexes searched; qualified question IDs; matching staging IDs/paths/statuses; curated candidate IDs/pages/ambiguity; selected targets; and unresolved candidates. Write nothing until explicit approval, then pass the approval, exact preview scope and complete ledger to `atlas-stage`; it must not ask again. Do not remove the curated question directly.

Query output routes to the source but is not semantic authority. Every factual statement and material hop requires the curated page reference.

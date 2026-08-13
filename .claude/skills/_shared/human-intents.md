# Human intent contract

Present Atlas as four ordinary actions. Skill names, staging buckets, lifecycle codes and helper commands are implementation details unless the user asks for audit detail.

## Ask Atlas

Use for engineering questions, including impact and risk. Route internally to discovery or impact analysis. Start with linked Atlas pages, use deterministic search as the entrance when identity is unclear, use indexes as the browsing/ambiguity fallback, and use maps only after selecting an ID when reverse or multi-hop traversal is needed. Fall back to bounded source inspection when Atlas coverage ends.

Natural examples: “How does this publish data?”, “What could this schema change affect?”, “Who owns this component?”

## Teach Atlas

Use when the user wants to save a fact or answer Atlas questions. Determine provenance, duplicates, conflicts, target and staging bucket internally. Show one concrete evidence preview and request one scope-bound approval before any write.

Natural examples: “Save this to Atlas”, “What does Atlas still need to know?”, “Ask me something useful about this repo.”

## Sync Atlas

Use for initial repository coverage, standards discovery and merged-change maintenance. If the logical repository has no adequate baseline, perform full onboarding; otherwise process the bounded default-branch change range. Full onboarding assesses every required lens but may record a lens as unknown, inaccessible or not applicable. Do not create unsupported records merely to make the baseline look complete.

Natural examples: “Onboard this repository”, “Update Atlas for this repo”, “Learn the standards used by these repositories.”

## Curate Atlas

Use for turning eligible evidence into authoritative curated knowledge. Default scope to the current repository, domain, stable ID or named topic. Run independent semantic review inside the normal curation workflow. A separate review workflow remains available for audits and second opinions.

Natural examples: “Curate pending evidence for payments”, “Curate what we learned about comp.order-validator.”

## Routing rules

- State the interpretation briefly before a write-capable workflow when the request could mean more than one intent.
- Do not ask the user to select a skill, query command, staging bucket or internal disposition.
- Preserve exact technical controls behind the conversation: provenance, uncertainty, explicit persistence approval, independent review and human-controlled publication.
- Use plain-language outcome groups first. Put stable IDs, internal lifecycle/disposition codes and commands in an optional audit detail.
- Never treat missing coverage or a failed route as proof that the engineering object or relationship does not exist.

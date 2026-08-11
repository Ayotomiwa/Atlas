# Question interview

## Selecting scope

- Exact qualified question ID or stable ID wins over a domain or topic.
- An exact domain ID or alias selects that domain.
- Fuzzy topic, path ties and multiple domain candidates require user selection.
- Local scope includes questions owned by or affecting current-path repository/component candidates.
- If local scope is empty, state that boundary and offer domain or package scope. Never substitute an unrelated global question silently.
- Prefer active `status: curated`. A question from deprecated historical content is allowed only for an explicitly targeted page and must be labelled historical and non-authoritative.

## Asking a question

Use this compact shape:

```text
Question: <plain-language question>
Why Atlas asks: <what route, identity, safety or understanding this would improve>
Currently known: <only the minimum evidence-backed context>
Evidence gap: <recorded gap>

[Atlas: <owner-id> — <page>#open-questions--coverage-limits]
How selected: <current path/explicit target> -> <owner or affected ID> via <match basis>
```

Ask only one question. Tell the user they may answer, say `skip` or `unsure`, change topic, or stop.

Follow up only when the answer needs attribution or boundary clarification. Useful prompts establish whether the answer is firsthand, where it applies, when it was true, which environment/version it covers, and whether a source can be cited. Do not turn a plausible response into certainty or coach the user toward the current Atlas assumption.

## Session state

Track answered, skipped, uncertain and contradicted questions in the conversation only. Do not create an answer ledger. After three answered or skipped questions, show a short summary with qualified IDs and source classifications, then ask whether to continue or review a staging proposal.

If an answer is transient, speculative, sensitive, already captured, or merely “unknown,” retain it in the conversational summary but do not propose staging it.

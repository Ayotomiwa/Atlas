# Atlas resumable discovery agent

Date: 2026-10-08

Discussion record containing the original question and response. Recommendations are proposed changes, not implemented behaviour. Repository observations refer to the main branch inspected during this discussion.

## Original question

@GitHub Atlas. I found a that the discover skill loads reads into the context wasting tokens some of which is not relevant to the answer, I am think of having the discovery agent be there as long running with the context not necessary and output the answer or context it needs and I can across this - Its run ends, but the subagent isn't deleted. When the main agent sends it a message with SendMessage (by name or agent ID), it starts a new run under the same ID with its full previous history intact. To the main agent, that behaves like asking a long-running expert. The only cost is a short restart, and it doesn't have to re-read anything.
If you want an agent that's genuinely still running and waiting for questions, use an agent team teammate:
Enable it with "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } in settings.json.
Ask Claude to spawn a teammate, e.g. "spawn a teammate called context-keeper using the context-keeper agent type; have it load the repo context, then stay available for questions."
When it finishes a task, it goes idle but keeps running. Its row may disappear from the panel after 30 seconds, but it can still be messaged by name. The main session (the lead) or you can send it questions at any time.
Caveats with teammates:
The feature is experimental.
/resume doesn't bring in-process teammates back, so after a restart you have to spawn it again.
Each teammate is a separate Claude instance, so it uses more tokens.
Its prompt cache only lasts 5 minutes by default. Set subagentPromptCacheTtl to 1h if questions are spread out.
In practice, a resumable subagent is usually enough for "ask for context when needed." Use a teammate if you specifically want it alive the whole time.
Sources: Subagents, Agent teams

## Response and recommendations

**Yes. I would make Atlas discovery a resumable specialist, with a small routing skill in the main conversation.** It fits your goal of keeping exploratory reads out of the context used for implementation and answering.

I checked Atlas's current `main`. There are three concrete sources of overhead:

| Current behaviour | Why it matters |
|---|---|
| [`atlas-discover`](../.claude/skills/atlas-discover/SKILL.md) requires six shared documents before substantive work | Those instructions enter the caller's context before delegation. |
| The skill performs selection and potentially synthesis before handing off | Some discovery work has already happened in the main context. |
| [`atlas-discovery-analyst`](../.claude/agents/atlas-discovery-analyst.md) reads five overlapping documents and returns an answer plus a complete ledger, paths and traversal details | Delegation isolates its reads, but the return packet can still be large. |

The [handoff contract](../.claude/skills/_shared/agent-handoffs.md) already supports reusing session evidence. What is missing is an explicit instruction to resume the same analyst and a smaller default response contract.

**The explanation you found is substantially correct**, with one important correction: "the only cost is a short restart" understates the token cost.

Claude's current documentation confirms that `SendMessage` can resume a completed custom subagent by name or ID with its previous history. Agent teams are unnecessary for this. Subagents can also compact their own context, so retained history is not a guarantee that every old detail remains available verbatim indefinitely. See [Create custom subagents](https://code.claude.com/docs/en/sub-agents).

There are three separate things here:

- **Context isolation:** discovery reads stay outside the main conversation.
- **History retention:** resuming avoids starting the investigation from scratch.
- **Prompt caching:** reduces the cost of processing reusable input. Cached input still has a cost, and cache expiry does not erase the agent's history. Resumed agents can reuse their previous cache.

See [How Claude Code uses prompt caching](https://code.claude.com/docs/en/prompt-caching).

For Atlas, I would use this arrangement:

1. **Keep `atlas-discover` small.** It checks eligibility and supplies the question, Atlas root, product root, revision and permitted scope. Move detailed retrieval instructions and exploratory reads into the analyst. Preserve the existing shortcut for a genuinely small lookup using evidence already available.

2. **Start the analyst on demand.** Do not ask it to load the entire repository first. Let it read the records needed for the first question and accumulate useful knowledge through related follow-ups.

3. **Retain its agent ID.** Send related questions back to that instance. Keep only a small session record in the parent: agent ID, roots, scope and inspected revisions. If the instance is unavailable, create a replacement and retrieve the necessary sources.

4. **Offer two return modes.**

   | Mode | What comes back |
   |---|---|
   | Answer | A concise answer, supporting references and material uncertainty |
   | Context for work | Relevant facts, exact constraints, source locations and unresolved dependencies needed for the task |

   Keep exploratory results and the complete ledger with the analyst by default. Return enough supporting evidence for the parent to assess material claims, and expand it when verification or an audit requires it. Merely hiding a ledger from the user does **not** remove it from the main context.

5. **Check freshness before reuse.** A changed branch, commit or relevant working-tree file can invalidate remembered evidence. Re-read affected sources. For an unrelated domain, start a fresh specialist rather than continually enlarging one universal Atlas expert.

The alternatives are straightforward:

| Approach | My assessment |
|---|---|
| Fresh analyst per question | Good isolation, but repeats discovery across related questions |
| **Resumable analyst per related investigation** | **Best default for Atlas** |
| Always-available teammate | Useful for active collaboration between agents; unnecessary for ordinary context retrieval |

Teammates remain experimental, and `/resume` does not restore in-process teammates. That adds lifecycle complexity without solving this retrieval problem better. See [Orchestrate teams of Claude Code sessions](https://code.claude.com/docs/en/agent-teams).

`"subagentPromptCacheTtl": "1h"` is a valid optional setting from Claude Code **v2.1.242**, subject to provider support. Treat it as a cost optimisation after fixing routing and output size. It does not increase the context window. See [How Claude Code uses prompt caching](https://code.claude.com/docs/en/prompt-caching).

My first change would be **earlier delegation plus a smaller return packet**, followed by explicit analyst reuse. Then compare a first question and several follow-ups against today's flow, measuring main-context growth, total usage, latency and answer accuracy. That will establish whether you have reduced overall cost as well as kept the main conversation cleaner.

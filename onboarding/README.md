# Start using Datalens Atlas

Atlas helps Claude answer engineering questions with shared, traceable context. You can ask about a repository, component, data flow, infrastructure item, schema, operational procedure, owner, or standard. When Atlas does not cover enough, Claude can inspect a bounded part of the source repository and tell you where Atlas coverage ended.

You do not need to learn Atlas vocabulary or choose a skill before you begin.

## Your first question

Load the live Atlas checkout when starting Claude:

```powershell
claude --add-dir <ATLAS_ROOT>
```

Then ask an ordinary question, for example:

- "How does this service publish the monthly data?"
- "What could break if I change this schema?"
- "Where is this worker deployed?"
- "Which standards apply to this code?"

Claude decides whether Atlas can help. It opens the most likely reviewed page, follows its links, and uses generated maps only when it needs a reverse or multi-step route. If several records could match, it shows the candidates instead of silently choosing one.

Every substantive answer identifies where its claims came from. For a cross-system answer, Claude also shows the important page or source-file hops. When the current checkout is not a clean `main` or `master` checkout, it gives one short advisory and continues.

## If Atlas is unavailable

The product repository may contain a managed `CLAUDE.md` block that tells Claude Atlas exists, even when no Atlas skill triggered. If the Atlas root cannot be loaded, Claude must say that Atlas was not consulted and explain how to restart:

```powershell
claude --add-dir <path-to-current-Atlas-checkout>
```

Claude may continue with bounded source evidence. It must not imply that Atlas was checked. If a product repository lacks the managed block, Claude may offer to add it once; it writes only after approval and does not modify sibling products.

## Four things you can ask Atlas to do

### Ask

Ask how something works, where it lives, who owns it, or what a change could affect. Claude uses reviewed Atlas knowledge first and clearly marks repository-derived facts, user-confirmed facts, inferences, conflicts, and unknowns.

### Teach

Say "Save this to Atlas" when you know a durable fact, or ask "What does Atlas still need to know about this repo?" Claude checks whether the information already exists, records its source and uncertainty, then shows exactly what it proposes to save. One explicit approval covers that unchanged write scope.

The saved item is evidence waiting for review. It does not become reviewed knowledge merely because you supplied it.

### Sync

Say "Onboard this repository" for first coverage. Atlas performs a full baseline rather than creating a thin placeholder. It checks the source boundary, domain, ownership, build and release shape, real runtime components, causal behavior, flows, infrastructure, schemas, and operations. A missing or inaccessible area remains an explicit gap; Atlas does not create a record just to fill the list.

Say "Update Atlas for this repository" after changes merge to the source repository's default branch. Claude compares the shared checkpoint with the current remote branch, accounts for the relevant change range, and previews new evidence plus the checkpoint update together. It never guesses the first baseline or relies on a hosting-service API.

Say "Learn the standards used by these repositories" to compare policy and practice. Repeated code is not automatically a team requirement; Atlas keeps local conventions, tool defaults, exceptions, and conflicts separate.

All Sync routes create evidence. They do not create reviewed knowledge directly.

### Curate

Say "Curate pending evidence for this repository" (or name a domain, topic, or stable ID). Claude proposes the supported knowledge changes and asks only for decisions that require human judgment. After approval, it validates the scoped changes and sends them to an independent reviewer. Human Git review and merge remain the later publication step.

You normally do not need to invoke a separate review workflow after routine curation. The standalone review route remains available for audits, external diffs, and second opinions.

## Terms you may see later

| Atlas term | Plain meaning |
|---|---|
| Curated page | Reviewed reusable knowledge |
| Staging record | Attributable evidence waiting for curation |
| Intake checkpoint | The latest contiguous merged-source change Atlas has considered |
| Stable ID | A durable name for a concept that does not depend on its current path |
| Domain | The primary grouping used to store and route architecture pages |
| Coverage | What a page includes and what remains missing |
| Confidence | How strongly the evidence supports one fact or connection |
| Generated map | A machine-built routing view; not the source of the engineering claim |

The main architecture records answer different questions:

- A repository page explains a useful source boundary and how to navigate it.
- A component page explains an independently addressable runtime or reusable unit.
- A flow page explains an ordered path; each step may be a component, infrastructure item, external system, manual action, or unresolved participant.
- An infrastructure page explains an infrastructure package and the important resources it defines or uses.
- A schema page explains a physical API, event, table, file, or other data contract.

Paths and domains help route a record but do not define its identity.

## Trust and safety

- Reviewed active pages are authoritative Atlas knowledge.
- New observations remain evidence until curation and independent review succeed.
- Generated output helps navigation but does not prove a claim.
- Missing coverage means unknown, not safe or nonexistent.
- Claude never copies secrets, customer data, credentials, or unnecessary personal information into Atlas.
- Claude never merges or publishes Atlas changes.

Before any repository write, Claude states the current feature branch. It may reuse the existing feature branch; a new branch is not required for every write. If the checkout is on the default branch, detached, or unrelated to the default branch, Claude asks for a suggested, existing, or custom feature branch before editing.

## A practical first contribution

1. Load Atlas and ask a real engineering question.
2. Check the references and any stated coverage limit.
3. If you know a durable missing fact, ask Claude to save it.
4. Review the proposed evidence, scope, uncertainty, and files.
5. Approve only that displayed scope.
6. Later, ask Claude to curate the relevant repository, domain, or topic.
7. Review and publish the resulting Git change through your normal team process.

For skill names, query commands, intake cursor rules, generation, recovery, evaluation, and maintainer procedures, use the [advanced Atlas workflow reference](advanced-reference.md).

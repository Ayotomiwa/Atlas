# Adaptive Engineering Learning Loop for Atlas

## Context

After reviewing DeepLearning.AI's **Building Adaptive AI Agents** course against the current Atlas architecture and the proposed engineering lifecycle control plane, the main conclusion is:

> The course does not replace the Atlas design. It fills the missing learning loop between one engineering run and the next.

The course frames adaptation across three increasingly expensive layers:

1. **Behaviour adaptation** — improve agent behaviour through reusable skills.
2. **Knowledge adaptation** — improve retrieval through structured knowledge and graph relationships.
3. **Model adaptation** — modify model behaviour through techniques such as fine-tuning only when context and procedural adaptation are insufficient.

For Atlas, the most valuable contribution is the first layer and the memory model behind it.

---

## 1. Map the Course's Memory Model to Atlas

A useful way to describe the architecture is through four forms of memory:

| Memory type | Atlas / engineering equivalent |
|---|---|
| Working memory | Current session, current plan, Engineering Change Contract |
| Episodic memory | Previous engineering runs: failures, fixes, corrections, deviations, outcomes |
| Semantic memory | Atlas/context layer: architecture, components, flows, standards, infrastructure, ownership |
| Procedural memory | Skills, rules, engineering workflows, recovery procedures |

Atlas already has strong **semantic memory**.

The engineering plugin architecture provides **procedural memory**.

The Engineering Change Contract provides structured **working memory**.

The weak or missing piece is **episodic memory**, and particularly the promotion path from episodic experience into semantic or procedural knowledge.

The architecture should therefore evolve toward:

```text
WORKING
current Engineering Change Contract
current plan
current evidence
current tests
       │
       │ completed run
       ▼
EPISODIC
what happened?
what failed?
what fixed it?
what did the human correct?
what was unexpectedly difficult?
       │
       │ promotion
       ▼
┌─────────────────────┬──────────────────────┐
│ SEMANTIC            │ PROCEDURAL           │
│                     │                      │
│ Atlas               │ skills / workflows   │
│ architecture        │ rules                │
│ facts               │ techniques           │
│ standards refs      │ recovery procedures  │
└─────────────────────┴──────────────────────┘
```

This is the most important architectural change suggested by the course.

---

## 2. Behaviour Adaptation: Trajectory to Skill

The strongest lesson for Atlas is the idea that successful agent execution can become evidence for reusable procedures.

Conceptually:

```text
Agent runs
   ↓
observable traces
   ↓
find repeated/useful behaviour
   ↓
induction
   ↓
candidate skill
   ↓
human review
   ↓
approved skill
   ↓
future runs
```

However, Atlas should not implement this as a naive:

```text
trajectory → skill
```

Not every lesson belongs in a skill.

Instead, introduce an **Adaptation Router** or **Learning Router**.

```text
ENGINEERING RUN
       │
       ▼
 Run / Episode Record
       │
       ▼
   Learning Router
       │
 ┌─────┼────────┬───────────┬────────────┐
 ▼     ▼        ▼           ▼            ▼
none  semantic procedural  rule       standard?
       fact      lesson    candidate
        │          │          │            │
        ▼          ▼          ▼            ▼
      Atlas      Skill       Rule      NEVER infer
      staging   proposal    proposal    policy;
                                      find authority
```

### Example

Suppose an engineering session discovers that a Lambda Jackson deserialisation failure is caused by generated constructor behaviour.

The durable learning might be procedural:

```text
When debugging Lambda/Jackson DTO deserialisation:

1. Inspect generated constructors.
2. Confirm a usable no-args or explicit creator path.
3. Check Lombok annotations.
4. Reproduce without Lombok before blaming the Lambda runtime.
5. Re-run the smallest deserialisation test before broad integration tests.
```

That is a **procedural lesson** and therefore a skill candidate.

By contrast:

```text
TradeReconHandler consumes ClientEntity
```

is a **semantic fact** and should become Atlas evidence.

And:

```text
Every production deployment must have XRay evidence
```

is an **organisational policy**. The agent must not learn that from repetition. It should locate the authoritative standard.

This distinction should be explicit in the learning architecture.

---

## 3. Capture Observable Engineering Evidence, Not Hidden Reasoning

The system should not rely on hidden chain-of-thought or unstructured conversational history as its durable learning source.

Instead, capture observable execution evidence.

A proposed **Engineering Episode** could look like:

```yaml
run:
  task_type: bugfix
  objective: ...
  change_contract: ...

context_used:
  atlas_ids: [...]
  standards: [...]
  source_paths: [...]

actions:
  - searched: ...
  - opened: ...
  - executed_test: ...
  - modified: ...
  - reverted: ...

failures:
  - command: ...
    outcome: ...
    cause: ...

human_corrections:
  - correction: ...
    affected_decision: ...

verification:
  tests: ...
  lint: ...
  build: ...
  reviewers: ...

outcome:
  successful: true
  reusable_observations: [...]
```

This is deterministic enough to inspect, evaluate and compare across runs.

Most episodes should never become permanent knowledge.

---

## 4. Not Every Engineering Run Should Produce Learning

A learning system that promotes something after every task will rapidly become polluted.

The adaptation phase should first ask:

- Was anything actually learned?
- Is the behaviour likely to recur?
- Was the successful behaviour causal, or merely correlated with success?
- Does an existing skill already cover it?
- Is this actually project-specific semantic knowledge?
- Was there an explicit human correction?
- Can the proposed lesson be supported by observable evidence?
- Would promoting it create unnecessary instruction or context cost?

A useful disposition model is:

```text
boring successful run
        ↓
     discard

one-off weird failure
        ↓
episodic evidence only

repeatable technique
        ↓
skill candidate

stable system fact
        ↓
Atlas candidate

repeated agent mistake
        ↓
rule/skill candidate

organisation policy
        ↓
find authoritative standard
```

This prevents skill and rule bloat.

---

## 5. Human Approval Should Remain a Hard Promotion Boundary

A poor reusable skill is worse than one poor agent run because it can reproduce the error indefinitely.

Atlas already has the right conceptual model:

```text
evidence ≠ authority
```

The same rule should apply to procedural memory:

```text
observed technique ≠ approved engineering procedure
```

Therefore the promotion path should be:

```text
candidate
    ↓
evidence
    ↓
independent review
    ↓
evaluation
    ↓
human approval
    ↓
active skill
```

Avoid:

```text
Claude noticed something
    ↓
Claude silently edits SKILL.md
```

Skill induction should generate proposals, not directly modify active behaviour.

---

## 6. Evaluate Candidate Skills Before Promotion

Atlas already uses an evaluation mindset for semantic retrieval. The same principle should be applied to procedural memory.

Before activating an induced skill:

```text
             same scenarios
                  │
          ┌───────┴────────┐
          ▼                ▼
     WITHOUT skill     WITH skill
          │                │
          └───────┬────────┘
                  ▼
               compare
```

Possible measures:

- task completion;
- test correctness;
- number of retries;
- tool calls;
- unnecessary edits;
- human corrections;
- review findings;
- tokens;
- elapsed execution;
- regression rate;
- scope adherence.

This makes skill promotion closer to an A/B test for procedural memory.

It also provides a way to challenge existing rules and skills rather than continually accumulating them.

A useful future capability would be **procedural ablation**:

> Remove or disable a rule/skill, repeat representative scenarios, and determine whether it materially improves outcomes.

If not, delete or simplify it.

---

## 7. Knowledge Adaptation Through a Code Graph

The course also argues that large-repository agent performance is often limited by retrieval rather than generation.

Its code graph models relationships such as:

```text
file ──imports──> file

function ──calls──> function

file ──co-edited──> file
```

and uses those relationships to find source that may not be discoverable through lexical search alone.

This overlaps with Atlas, but it is not the same thing.

### Atlas graph

Atlas operates primarily at the semantic and architectural level:

```text
Component
Repository
Flow
Infrastructure
Schema
Standard
Runbook
Incident
```

with relationships such as:

```text
depends-on
consumes
produces
reads-from
writes-to
triggers
deployed-by
monitored-by
must-follow
informed-by
```

These are governed and durable engineering relationships.

### Course/source graph

The course graph is lower level:

```text
file
function
symbol
```

with relationships such as:

```text
imports
calls
references
co-edited-with
```

These solve different resolutions of the same retrieval problem.

---

## 8. Do Not Put a File/Symbol Graph Into Curated Atlas

Avoid turning every file or symbol into a curated Atlas page.

For example, do **not** create:

```text
_curated/
    files/
        40,000 markdown pages

    functions/
        190,000 markdown pages
```

That would make Atlas:

- too large;
- constantly stale;
- expensive to curate;
- noisy;
- duplicative of source intelligence;
- difficult to govern.

Instead, treat a source graph as a generated or ephemeral **retrieval layer**.

```text
                     QUESTION
                        │
                        ▼
                engineering-flow
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
       Atlas                     Source Graph
   semantic level                code level
          │                           │
 component / flow              file / symbol
 infrastructure                import / call
 standards                     co-edit
          │                           │
          └─────────────┬─────────────┘
                        ▼
                 exact source read
```

The source graph locates evidence.

It should not become authority.

---

## 9. Where the Source Graph Fits in Retrieval

A useful retrieval hierarchy is:

```text
known exact local source
          ↓
       source

architecture/system question
          ↓
        Atlas

unknown implementation boundary
          ↓
     source graph
          ↓
 candidate files/functions
          ↓
    exact source read
```

This preserves the principle that exact source remains the final implementation evidence while Atlas remains the durable semantic layer.

---

## 10. Co-Edit Relationships Are Particularly Useful

Static dependencies explain only some engineering relationships.

For example:

```text
Service.java
     │
     │ import
     ▼
Repository.java
```

A normal symbol graph can discover this.

But Git history may show that the following files repeatedly change together:

```text
OrderMapper.java
OrderContractTest.java
xray/order-processing.feature
deployment/order-stack.yaml
```

There may be no direct import path connecting them.

Co-edit history can expose that practical engineering relationship.

However, it must remain explicitly heuristic:

```text
relationship: co-edited-with
confidence: derived
```

Never reinterpret it as:

```text
relationship: dependency
```

Correlation is useful retrieval evidence, not architectural truth.

---

## 11. Keep the Source Graph Implementation Cheap Initially

Do not begin by introducing Oracle Graph, Neo4j or another database.

Start with generated or ephemeral data.

For example:

```text
.code-context/
    graph.json
```

A simple representation could be:

```json
{
  "nodes": [
    {"id": "src/Foo.java", "type": "file"},
    {"id": "Foo.handle", "type": "symbol"}
  ],
  "edges": [
    {
      "from": "Foo.handle",
      "to": "Bar.save",
      "type": "calls"
    }
  ]
}
```

An incremental implementation order could be:

1. Git commits and co-edit relationships.
2. File imports.
3. Obvious references.
4. Symbol relationships.
5. Language-aware indexing through compiler or LSP tooling.
6. More advanced graph ranking only if evaluation shows it improves retrieval.

The graph database should be an implementation choice reached through evidence, not a starting assumption.

---

## 12. Retrieval Ladder Before Embedding Adaptation

The course also discusses adapting embeddings when generic semantic retrieval fails to understand specialised domain relationships.

That is interesting, but Atlas should exhaust cheaper and more interpretable techniques first.

A sensible retrieval ladder is:

```text
exact ID/path
     ↓
lexical search
     ↓
Atlas typed relations
     ↓
source graph
     ↓
generic embeddings
     ↓
reranking
     ↓
domain embedding tuning
```

Atlas has enough explicit structure that domain embedding tuning may never be necessary.

---

## 13. Model Adaptation / LoRA Is Not a Priority

Model adaptation is the least useful part of the course for the Atlas engineering architecture today.

The desired behaviour can already be controlled through:

```text
rules
skills
standards
Atlas
source graph
agent orchestration
evaluation
```

Fine-tuning would also reduce portability across Claude, Codex and future models.

Current recommendation:

```text
LoRA                ❌
QLoRA               ❌
custom foundation   ❌

better skills       ✅
better retrieval    ✅
better context      ✅
better evaluation   ✅
```

Model adaptation could be reconsidered in the future for a narrow internal classifier or router, but not for the primary engineering agent.

---

## 14. Change the Final LEARN Phase

The current engineering lifecycle ended conceptually with:

```text
DEPLOY
  ↓
LEARN
docs / ADR / Atlas
```

That is too weak.

Replace it with:

```text
                 DEPLOY / COMPLETE
                        │
                        ▼
                REFLECT ON RUN
                        │
                        ▼
               ENGINEERING EPISODE
                        │
                  worth keeping?
                   /         \
                 no           yes
                 │             │
              discard          ▼
                       ADAPTATION ROUTER
                              │
       ┌──────────────────────┼───────────────────┐
       │                      │                   │
       ▼                      ▼                   ▼
 Semantic candidate     Procedural candidate   Rule candidate
       │                      │                   │
       ▼                      ▼                   ▼
 Atlas staging          Skill induction       Rule proposal
       │                      │                   │
       └──────────────┬───────┴──────────────┬────┘
                      ▼                      ▼
                 independent            evaluation
                    review
                      └─────────┬────────────┘
                                ▼
                          HUMAN APPROVAL
                                │
                                ▼
                      NEXT ENGINEERING RUN
```

This is the main architectural addition suggested by the course.

---

## 15. Pair the Engineering Change Contract With the Engineering Episode

At the beginning of engineering work:

```text
Engineering Change Contract
```

captures what we **intend** to do.

At the end:

```text
Engineering Episode
```

captures what **actually happened**.

Then compare them:

| Plan | Reality |
|---|---|
| anticipated files | actual files |
| expected tests | actual tests |
| expected risks | encountered failures |
| expected standards | standards actually needed |
| architecture assumptions | discovered constraints |
| expected workflow | recovery steps |

This delta is a far better learning input than handing a complete session transcript to another model and asking it to invent a skill.

The adaptation question becomes:

> Where did execution materially deviate from the Engineering Change Contract, and is any deviation reusable?

That significantly reduces noise.

---

## 16. This Integrates Naturally With TDD

Suppose the planned implementation cycle is:

```text
RED → GREEN → REFACTOR
```

but the actual episode is:

```text
test
 ↓
implementation
 ↓
mysterious build failure
 ↓
12 searches
 ↓
discover generated MapStruct source issue
 ↓
fix compiler configuration
```

The reusable learning is probably not the business implementation.

It may instead be:

```text
When MapStruct-related compilation fails after DTO changes,
inspect generated sources and annotation processing before
changing mapper behaviour.
```

That is exactly the sort of engineering knowledge future runs should not rediscover.

---

## 17. Recommended Implementation Priority

After incorporating the course, the implementation order should be:

| Priority | Capability | Decision |
|---|---|---|
| 1 | Engineering Change Contract | Build |
| 2 | `engineering-flow` orchestration | Build |
| 3 | Engineering Episode schema | **New — build** |
| 4 | Reflection / adaptation router | **New — build** |
| 5 | trajectory → candidate skill | **New — build** |
| 6 | skill evaluation + human promotion | **New — build** |
| 7 | source/code graph retrieval experiment | Prototype |
| 8 | co-edit ranking | Prototype |
| 9 | persistent graph database | Do not build yet |
| 10 | embedding fine-tuning | Do not build yet |
| 11 | LoRA/model adaptation | Do not build |

The critical addition is the **governed adaptive learning loop**, not the model-training layer.

---

## 18. Resulting Architecture

Before the course, the engineering design was essentially:

```text
CONTEXT + RULES + SKILLS
          ↓
   ENGINEERING FLOW
          ↓
       DEPLOY
```

The better design is cyclical:

```text
                 ┌────────────────────┐
                 │      CONTEXT       │
                 │ Atlas + standards  │
                 └─────────┬──────────┘
                           ↓
                   ENGINEERING FLOW
                           │
                           ↓
                        RESULT
                           │
                           ↓
                    RUN EXPERIENCE
                           │
                           ↓
                       LEARNING
                    ↙      ↓      ↘
                 Atlas   Skills   Rules
                    ↘      ↓      ↙
                      evaluation
                           ↓
                    human approval
                           │
                           └──────────────►
                             next run
```

This turns Atlas plus the engineering plugins from a static set of authored context and workflows into a governed system that can improve from engineering experience without silently converting agent behaviour into organisational truth.

---

## 19. Architectural Principle

The most important principle is:

> Completed engineering work may become evidence for improving semantic and procedural memory, but it must pass through classification, evidence, evaluation, review and human promotion before becoming durable behaviour or authoritative knowledge.

That fits Atlas's existing philosophy:

- raw evidence is not authority;
- missing coverage remains unknown;
- derived relationships must remain distinguishable from proven ones;
- durable knowledge should pass through validation and independent review;
- agent convenience must not silently rewrite engineering truth.

The adaptive learning loop should apply the same governance model to **skills and rules** that Atlas already applies to **knowledge**.

---

## Sources and Related Material

- DeepLearning.AI — *Building Adaptive AI Agents*: https://www.deeplearning.ai/courses/building-adaptive-ai-agents/
- Oracle Developers — course launch and adaptation overview: https://blogs.oracle.com/developers/we-just-launched-a-new-course-on-how-to-build-adaptive-ai-agents
- Community course notes and hands-on reproduction:
  - https://hasangoni.quarto.pub/hasan-blog-post/posts/series/course-notes/2026-08-27-adaptive-ai-agents.html
  - https://hasangoni.quarto.pub/hasan-blog-post/posts/series/course-notes/2026-08-27-adaptive-ai-agents-hands-on.html

## Relevant Atlas Surfaces

Current Atlas concepts that align with this proposal include:

- `README.md` — semantic context-layer role and trust model;
- `CLAUDE.md` — operating rules, persistence boundaries and independent review;
- `contracts/map-fields.yaml` — typed architecture relationships and impact direction;
- `.claude/skills/atlas-discover/SKILL.md` — semantic routing, bounded source fallback and provenance;
- `evaluation/README.md` — comparative evaluation, telemetry and controlled experimental setup;
- `docs/engineering-lifecycle-control-plane.md` — current end-to-end engineering workflow proposal.

This document should be treated as an extension of the engineering lifecycle design rather than a replacement for it.

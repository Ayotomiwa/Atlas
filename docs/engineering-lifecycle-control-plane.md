# Engineering Lifecycle Control Plane

## Goal

Design an end-to-end engineering workflow that coordinates rules, standards, skills, specialist agents, deterministic checks, and contextual knowledge from planning through deployment.

The target is not a fixed chain of agents. It is a context-aware engineering control plane that selects the right practices for the change being made.

The strongest separation is:

| Mechanism | Responsibility | Example |
|---|---|---|
| Rules | Constraints and invariants | Behaviour changes require verification; load the applicable testing standard |
| Standards | Organisation or team-specific truth | Java standard, XRay requirements, deployment policy |
| Skills | Reusable procedures and workflows | Grill requirements, plan a change, TDD cycle, verify, prepare deployment |
| Agents | Independent specialist analysis | Architect, reviewer, security reviewer, impact analyst |
| Hooks/scripts/tools | Deterministic evidence and actions | Gradle tests, lint, build, diff, deploy command, coverage |

The key design principle is to avoid turning TDD, SOLID, DRY, XP, anti-pattern detection, or similar paradigms into giant always-on rule sets. The engineering workflow should decide which principles matter at each phase.

---

## High-level lifecycle

```text
USER INTENT
    │
    ▼
┌─────────────────────┐
│ 1. CHANGE INTAKE    │
│ classify + context  │
└──────────┬──────────┘
           │
           ▼
     ambiguity?
      /        \
    yes        no
     │          │
     ▼          │
┌─────────────┐ │
│ 2. GRILL    │ │
│ AskUserQ    │ │
└──────┬──────┘ │
       └────┬────┘
            ▼
┌─────────────────────┐
│ 3. DISCOVER/IMPACT  │
│ code + Atlas + stds │
└──────────┬──────────┘
           ▼
     architecture
       relevant?
      /        \
    yes        no
     │          │
     ▼          │
┌─────────────┐ │
│ 4. DESIGN   │ │
│ alternatives│ │
└──────┬──────┘ │
       └────┬────┘
            ▼
┌─────────────────────┐
│ 5. ENGINEERING PLAN │
│ vertical slices     │
│ tests + acceptance  │
└──────────┬──────────┘
           │
           ▼
┌───────────────────────────┐
│ 6. IMPLEMENTATION LOOP    │
│                           │
│ RED → GREEN → REFACTOR    │
│  ↑                  │     │
│  └── next slice ────┘     │
└──────────┬────────────────┘
           ▼
┌─────────────────────┐
│ 7. VERIFY           │
│ deterministic gates │
└──────────┬──────────┘
           ▼
┌───────────────────────────┐
│ 8. INDEPENDENT REVIEW     │
│ quality │ security │ arch │
│         when applicable   │
└──────────┬────────────────┘
           ▼
┌─────────────────────┐
│ 9. DELIVERY READY   │
│ PR / migration /    │
│ rollback / release  │
└──────────┬──────────┘
           ▼
        APPROVAL
           │
           ▼
┌─────────────────────┐
│ 10. DEPLOY          │
│ + smoke validation  │
└──────────┬──────────┘
           ▼
┌───────────────────────────┐
│ 11. LEARN / ADAPT         │
│ episode → candidate learn │
│ → review → promotion      │
└───────────────────────────┘
```

This should be dynamically composed from the change rather than a fixed pipeline.

A documentation change does not need TDD. A small bug may not need an architect. A DTO rename may not need security review. An authentication change probably does. A database migration needs a different set of checks again.

---

## 1. Top-level owner: `engineering-flow`

Create one top-level skill:

```text
engineering-flow
```

This should be the controller rather than another specialist agent.

Its responsibilities are to determine:

```text
What kind of change is this?
How risky is it?
What context is required?
What standards apply?
Do we need grilling?
Do we need architecture?
What testing strategy applies?
Which specialists should review it?
What constitutes deploy-ready?
```

The parent workflow should own routing, scope, selected context, approvals, and final presentation. Specialist agents should operate on bounded handoff packets instead of rediscovering the problem independently.

---

## 2. Grilling belongs near the front

The Matt Pocock-style grilling skill adapted to Claude's `AskUserQuestion` tool fits naturally after intake, but it should not run for every request.

The engineering workflow should first identify uncertainty, for example:

```text
ambiguity:
  requirements: medium
  behavioural_expectation: high
  architecture: low
  rollout: unknown
```

Only meaningful uncertainty should trigger the grill skill.

Example:

```text
What should happen on duplicate reconciliation?
○ reject
○ update existing
○ silently ignore
○ other

Should existing API behaviour remain compatible?
○ yes
○ breaking change acceptable
○ unsure
```

Grill should remain a skill, not an agent.

---

## 3. Engineering Change Contract

Every engineering run should build one ephemeral structured object that carries the engineering state across phases.

Example:

```yaml
change:
  intent:
  type:
  behavioural_change:
  success_criteria:

scope:
  affected_components:
  affected_boundaries:

context:
  relevant_standards:
  architecture:
  known_constraints:

risk:
  data:
  security:
  compatibility:
  deployment:

engineering:
  architecture_required:
  tdd_strategy:
  verification:
  specialist_reviews:

delivery:
  migration:
  rollback:
  observability:
```

This can be called the **Engineering Change Contract**.

Each phase enriches it.

The planner should not send the architect an entire transcript. It should send only the contract fields and exact source/context boundaries the architect needs.

The reviewer receives the contract plus the implementation diff. Deployment receives the contract plus CI evidence and rollout information.

---

## 4. TDD should be selective, not universal

TDD should be a skill rather than a blanket global rule.

Recommended behaviour by change type:

| Change | TDD behaviour |
|---|---|
| New business behaviour | Red → Green → Refactor |
| Bug | Reproduce bug with failing test → fix → refactor |
| Refactor | Characterisation tests first if coverage is insufficient |
| API contract | Contract or integration test first |
| Data transformation | Example or property tests first |
| Infrastructure/config | Verification rather than artificial unit tests |
| Docs | No TDD |
| Spike/prototype | Explicit TDD exemption; tests when design stabilises |

The implementation loop should work in small vertical slices:

```text
acceptance behaviour
        ↓
failing test
        ↓
minimum implementation
        ↓
passing test
        ↓
refactor
        ↓
verification
        ↓
next behaviour
```

This uses TDD where it creates leverage rather than TDD theatre.

---

## 5. Where DRY, SOLID, XP, YAGNI, and anti-patterns belong

Avoid global rules such as "always follow SOLID and DRY".

Instead, treat engineering paradigms as phase-specific reasoning lenses.

### During design

Use:

- simple design;
- separation of concerns;
- domain ownership;
- dependency direction;
- SOLID where it provides clear value;
- YAGNI;
- avoiding premature abstraction;
- explicit trade-off analysis.

For meaningful architectural decisions, require at least two genuinely different designs before choosing a shape.

### During GREEN

The main rule is:

> Make the intended behaviour correct with the smallest reasonable implementation.

Do not prematurely introduce factories, strategy patterns, abstraction layers, or speculative extension points.

### During REFACTOR

Activate:

- DRY;
- SOLID;
- cohesion and coupling;
- naming;
- duplication;
- feature envy;
- god object/class;
- shotgun surgery;
- primitive obsession;
- leaky abstractions;
- unnecessary indirection.

DRY should mean duplicated knowledge, not merely duplicated text.

### During review

Use anti-patterns as diagnostic lenses rather than accusations.

The reviewer should ask:

> Did the implementation introduce a design smell that matters here?

rather than:

> Which principle can I claim this code violates?

---

## 6. Keep the agent set small

Avoid building an agent for every phase.

For example, avoid a mandatory stack of:

```text
planner-agent
developer-agent
tester-agent
refactor-agent
verify-agent
deploy-agent
```

That creates unnecessary context and coordination overhead.

Use agents where isolation improves quality.

Recommended initial specialists:

| Agent | Why it deserves isolation |
|---|---|
| `codebase-scout` | Large read-only investigation |
| `architect` | Independent architectural reasoning |
| `impact-analyst` | Cross-system and dependency analysis |
| `code-reviewer` | Independent review without inheriting implementation assumptions |
| `security-reviewer` | Specialist adversarial analysis |
| `delivery-reviewer` | Independent release and rollback readiness |

Implementation should normally remain in the parent session using the TDD skill so the Red → Green → Refactor loop retains continuity.

---

## 7. Rules should route to standards

Rules should mostly describe **when** standards apply rather than duplicate team-specific knowledge.

Instead of a huge `rules/java.md`, prefer something closer to:

```text
rules/testing.md

For behavioural source changes:
- identify the applicable testing standard
- load team-specific guidance when available
- use engineering:tdd for behaviour implementation
- do not invent coverage thresholds
```

The flow becomes:

```text
team standard
        ↓
rule points to it
        ↓
engineering workflow loads it
        ↓
skill applies it
```

This keeps the generic engineering plugin reusable while still allowing Datalens or another team to inject local Java, AWS, API, database, XRay, release, and deployment standards.

---

## 8. Suggested plugin structure

Prefer several focused plugins rather than one enormous engineering plugin.

```text
plugins/
│
├── engineering-core/
│   ├── skills/
│   │   ├── engineering-flow/
│   │   ├── grill/
│   │   ├── plan-change/
│   │   ├── design-change/
│   │   ├── tdd/
│   │   ├── verify/
│   │   └── deliver/
│   │
│   ├── agents/
│   │   ├── codebase-scout.md
│   │   ├── architect.md
│   │   ├── code-reviewer.md
│   │   ├── security-reviewer.md
│   │   └── delivery-reviewer.md
│   │
│   ├── rules/
│   │   ├── engineering.md
│   │   ├── testing.md
│   │   └── delivery.md
│   │
│   └── references/
│       ├── change-contract.md
│       ├── design-principles.md
│       ├── refactoring-principles.md
│       └── anti-patterns.md
│
├── java-engineering/
├── angular-engineering/
├── aws-engineering/
├── gitlab-delivery/
└── atlas-context/
```

`engineering-core` should know very little about Spring, Angular, AWS, or Datalens.

Those become optional capabilities or adapters around the core workflow.

---

## 9. Atlas should be a context provider, not the engineering orchestrator

The engineering workflow should be able to consult multiple context sources:

```text
engineering-flow
      │
      ├── local source
      ├── git history
      ├── Atlas/context layer
      ├── team standards
      └── ticket/Jira
```

Atlas can answer questions such as:

- What does this component depend on?
- Which standard applies?
- What flow could this affect?
- What deployment architecture exists?

`engineering-flow` owns the next question:

> Given that information, how should this change be engineered?

The generic engineering core should still work when Atlas is not installed.

---

## 10. Useful patterns from `everything-claude-code`

The useful ideas worth borrowing include:

- specialist planner, architect, TDD, reviewer, and security roles;
- structured handoffs;
- explicit orchestration;
- parallel independent reviews;
- an explicit verification phase;
- deterministic evidence from build, type-check, lint, tests, and other executable checks.

The parts that should not be copied directly into a generic engineering system include:

- fixed agent pipelines;
- blanket 80% coverage requirements;
- requiring all test types for all changes;
- TypeScript-centric structural conventions;
- arbitrary code-size or complexity heuristics;
- universal implementation patterns that belong in team or project standards.

---

## 11. Distinguishing idea

The target system is not merely a collection of Claude engineering skills.

It is:

> **A context-aware engineering workflow that dynamically assembles the right practices, standards, skills, specialist agents, and deterministic checks for a change, and carries verified context from intent through deployment.**

The combination of a grilling skill, dynamically injected standards, and an Atlas-style context layer gives the system three particularly strong properties:

1. requirement interrogation before implementation;
2. organisation-specific engineering knowledge without hard-coding it into generic skills;
3. contextual routing instead of a fixed process pipeline.

---

## 12. Add an adaptive learning loop

The lifecycle should not end at deployment. A completed engineering run is evidence about both the product and the engineering system itself.

The important distinction is between four kinds of memory:

| Memory | Role in this architecture |
|---|---|
| Working | Current conversation, Engineering Change Contract, selected source/context, active plan, tests, and review state |
| Episodic | What actually happened during a completed engineering run |
| Semantic | Durable system knowledge such as architecture, flows, ownership, standards, incidents, and runbooks; Atlas is the semantic layer |
| Procedural | Reusable behaviour encoded as skills, workflow instructions, and narrowly scoped rules |

Atlas already provides a governed semantic-memory layer and the plugin system provides procedural memory. The missing bridge is **episodic memory and governed promotion from episodes into semantic or procedural knowledge**.

The target loop is:

```text
WORKING STATE
Engineering Change Contract
        │
        │ execution
        ▼
ENGINEERING EPISODE
what actually happened
        │
        ▼
ADAPTATION ROUTER
        │
        ├── no durable lesson ───────────────→ discard
        │
        ├── stable system fact ──────────────→ Atlas candidate
        │
        ├── repeatable engineering method ──→ skill candidate
        │
        ├── recurring agent failure ─────────→ rule/skill candidate
        │
        └── apparent policy requirement ─────→ locate authoritative standard
                                                    │
                                                    ▼
                                      never infer policy from repetition
```

The system should learn from engineering work without allowing one successful or mistaken run to silently rewrite the engineering harness.

---

## 13. Engineering Episode

Introduce an ephemeral or short-lived **Engineering Episode** at the end of a meaningful engineering run.

The Change Contract records what the workflow intended to do. The Engineering Episode records what actually happened.

Example:

```yaml
episode:
  task_type: bugfix
  objective:
  result:
    successful:
    deployed:

change_contract:
  expected_scope:
  expected_tests:
  expected_risks:
  expected_reviews:

context_used:
  atlas_ids: []
  standards: []
  source_paths: []
  tickets: []

actions:
  commands: []
  files_read: []
  files_changed: []
  tools_used: []

failures:
  - symptom:
    failed_action:
    verified_cause:
    recovery:

human_interventions:
  - correction:
    affected_decision:
    outcome:

verification:
  tests:
  build:
  lint:
  security:
  reviews:

deviations:
  unexpected_files: []
  unexpected_dependencies: []
  unexpected_standards: []
  unexpected_failure_modes: []

candidate_learnings: []
```

Capture **observable engineering evidence**, not hidden chain-of-thought. Useful evidence includes tool calls, source paths, commands, test results, errors, human corrections, review findings, and verified causes.

Most episodes should not become permanent artifacts. They are an input to reflection, not a new document store.

---

## 14. Compare intent with reality

The best learning signal is often the delta between the Engineering Change Contract and the Engineering Episode.

```text
CHANGE CONTRACT                 ENGINEERING EPISODE
───────────────                 ───────────────────
anticipated files              actual files
expected dependencies          discovered dependencies
planned test strategy          tests actually needed
predicted risks                failures encountered
expected standards             standards actually required
planned implementation         recovery path
planned reviewers              findings from review
```

Reflection should focus on **material deviations**, not summarize the entire conversation.

Useful questions include:

- Where did execution materially diverge from the plan?
- Which assumption was wrong?
- Which investigation or recovery step is likely to recur?
- Did a human correction reveal a missing procedural guardrail?
- Did the run discover a stable system fact that Atlas does not know?
- Did an existing rule or skill cause unnecessary work?
- Was an apparent lesson causal or merely correlated with success?

This creates a much cleaner signal for adaptation than asking an LLM to mine an unrestricted session transcript for lessons.

---

## 15. Adaptation Router

Add a small reflection skill, conceptually:

```text
reflect-engineering-run
```

It should classify candidate learnings rather than directly changing any durable knowledge.

Recommended decisions:

| Observation | Route |
|---|---|
| Nothing meaningful or reusable happened | Discard |
| Stable architecture, ownership, flow, operational, or interface fact | Atlas staging candidate |
| Repeatable technique for performing engineering work | Skill candidate |
| Repeated agent error that should be prevented cheaply | Rule or skill candidate |
| Team or organisation policy | Resolve to an authoritative standard; do not learn policy from repetition |
| One-off incident/debugging context | Keep only if it belongs in incident/runbook knowledge |
| Heuristic correlation such as files frequently changing together | Generated source-graph signal, not semantic truth |

The router must not automatically persist anything.

A useful threshold for procedural promotion is:

```text
Is the behaviour likely to recur?
        │
        ├── no → discard
        │
        ▼
Does an existing skill/rule already cover it?
        │
        ├── yes → no new artifact; consider improving evaluation
        │
        ▼
Is the successful behaviour supported by observable evidence?
        │
        ├── no → keep as hypothesis only
        │
        ▼
Can it be expressed narrowly without encoding project-specific facts?
        │
        ├── no → semantic/context route instead
        │
        ▼
candidate skill/rule
```

---

## 16. Govern procedural-memory promotion

A learned technique should be treated like Atlas treats unreviewed evidence:

```text
observed technique ≠ approved engineering procedure
```

The promotion lifecycle should be:

```text
Engineering Episode
        ↓
candidate lesson
        ↓
candidate skill/rule
        ↓
independent review
        ↓
evaluation
        ↓
human approval
        ↓
active procedural memory
```

Never allow:

```text
Claude noticed something
        ↓
Claude silently edits SKILL.md or a rule
```

The review should check:

- provenance: which runs and evidence justify the candidate;
- specificity: is it reusable rather than project-specific;
- duplication: does another skill already own this behaviour;
- scope: when should it activate and when should it not;
- safety: could a poisoned or mistaken run institutionalise a bad behaviour;
- portability: does the candidate incorrectly encode Datalens-specific knowledge into a generic skill;
- cost: does it add context or process overhead disproportionate to its benefit.

Human approval remains the authority boundary.

---

## 17. Evaluate learned skills before promotion

Atlas already uses explicit evaluation rather than assuming that persistent context is automatically beneficial. Apply the same principle to procedural memory.

For a candidate skill or rule, run paired scenarios where possible:

```text
                 same task/scenario
                       │
              ┌────────┴────────┐
              ▼                 ▼
        WITHOUT candidate   WITH candidate
              │                 │
              └────────┬────────┘
                       ▼
                    compare
```

Useful measures include:

- task correctness;
- tests passed;
- build/lint/type-check outcomes;
- number of retries;
- unnecessary file edits;
- human corrections;
- reviewer findings;
- tool calls;
- input/output tokens when observable;
- elapsed execution when observable.

A candidate should not be promoted merely because its wording sounds sensible.

This is also the mechanism for removing stale procedural memory: periodically test whether an existing rule or skill still changes outcomes enough to justify its context and complexity cost.

---

## 18. Add a source graph as a generated retrieval layer, not Atlas authority

A code knowledge graph can improve retrieval when the exact implementation boundary is unknown. It should complement Atlas rather than become curated Atlas content.

The layers answer different questions:

```text
ATLAS / SEMANTIC GRAPH          SOURCE GRAPH
──────────────────────          ────────────
repository                      file
component                       symbol
flow                            function
infrastructure                  class
schema                          module
standard
runbook

depends-on                      imports
consumes                        calls
produces                        references
reads-from                      co-edited-with
writes-to
triggers
deployed-by
monitored-by
```

Do not create curated Atlas pages for every file or function. That would duplicate source intelligence, create huge curation cost, and become stale quickly.

Instead:

```text
                     QUESTION
                        │
                        ▼
                engineering-flow
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
       Atlas                     Source Graph
 semantic/system level        implementation level
          │                           │
          └─────────────┬─────────────┘
                        ▼
                 exact source read
                        ▼
                  evidence-backed
                      answer
```

The graph is a **locator**, not an authority. Exact source remains the evidence for executable implementation claims.

---

## 19. Source-graph routing

Extend retrieval routing conceptually to:

```text
known exact local source
        ↓
read source directly

architecture / system / ownership / standards question
        ↓
Atlas

unknown implementation boundary
        ↓
source graph
        ↓
candidate files / symbols
        ↓
exact source read

cross-system ambiguity
        ↓
Atlas first
        ↓
bounded source or source-graph fallback
```

Start cheaply.

Useful first edges:

1. Git co-edit relationships;
2. imports;
3. obvious static references.

Only add richer symbol and call-graph relationships when evaluation demonstrates retrieval value.

For Java and TypeScript, prefer language-aware compiler/LSP/code-intelligence output over maintaining custom parsers for every language.

---

## 20. Treat co-edit relationships as heuristics

Git history can reveal files that often change together even when no static import path connects them.

For example:

```text
OrderService.java
OrderMapper.java
OrderContractTest.java
xray/order-processing.feature
deployment/order-stack.yaml
```

This can be useful for impact discovery, but correlation is not architectural dependency.

Represent it explicitly as a derived heuristic, for example:

```yaml
relationship: co-edited-with
classification: heuristic
source: git-history
confidence: derived
```

Never automatically promote a co-edit edge into an Atlas `depends-on`, `consumes`, `produces`, or other semantic relationship.

---

## 21. Avoid premature model adaptation

The engineering harness should exhaust cheaper and more portable control surfaces before considering model adaptation.

Preferred order:

```text
exact source / identifiers
        ↓
better skills and rules
        ↓
team standards
        ↓
Atlas semantic context
        ↓
source graph
        ↓
generic lexical/vector retrieval
        ↓
reranking
        ↓
domain-specific embedding adaptation
        ↓
model fine-tuning
```

For the engineering control plane, model fine-tuning is currently out of scope.

Reasons include:

- reduced portability across Claude, Codex, and future models;
- governance and evaluation cost;
- most target behaviour is naturally expressible through skills, rules, standards, context, and deterministic tooling;
- a tuned model would not remove the need for source truth, current architecture, or organisation-specific policy.

Revisit model adaptation only for a narrowly bounded model-owned task after retrieval, procedural memory, and orchestration have been measured and found insufficient.

---

## 22. Revised lifecycle

The complete system is cyclical rather than linear:

```text
                 ┌─────────────────────┐
                 │ CONTEXT             │
                 │ Atlas + standards   │
                 └──────────┬──────────┘
                            ▼
                     CHANGE CONTRACT
                            │
                            ▼
                    ENGINEERING FLOW
                            │
                            ▼
                         RESULT
                            │
                            ▼
                  ENGINEERING EPISODE
                            │
                            ▼
                    ADAPTATION ROUTER
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   Atlas candidate     Skill candidate      Rule candidate
        │                   │                   │
        └──────────────┬────┴──────────────┬────┘
                       ▼                   ▼
                    review              evaluation
                       └─────────┬─────────┘
                                 ▼
                         human approval
                                 │
                                 ▼
                          next engineering run
```

The system therefore improves at two distinct levels:

1. **product/system understanding** improves through governed semantic knowledge;
2. **engineering behaviour** improves through governed procedural knowledge.

Neither should be updated directly from a single agent run.

---

## Revised implementation order

Build in this order:

1. `engineering-core`;
2. the **Engineering Change Contract**;
3. the **change classifier/router**;
4. the **Engineering Episode** schema;
5. `reflect-engineering-run` / adaptation routing;
6. candidate-skill and candidate-rule representation plus approval boundaries;
7. evaluation support for procedural candidates;
8. TDD, architecture, review, security, delivery, and language-specific capabilities;
9. a small source-graph retrieval experiment using Git co-edits plus imports/references;
10. richer code graph only if evaluation demonstrates value.

Do **not** start with a persistent graph database, embedding fine-tuning, or model fine-tuning.

The routing contract, lifecycle state model, and learning/promotion boundaries determine nearly every later component.

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
┌─────────────────────┐
│ 11. LEARN           │
│ docs / ADR / Atlas  │
└─────────────────────┘
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

## Recommended first implementation slice

Build these three pieces first:

1. `engineering-core`;
2. the **Engineering Change Contract**;
3. the **change classifier/router**.

Once those contracts are stable, TDD, architecture, review, security, deployment, and language-specific plugins become much cleaner additions.

Do not start by building every specialist skill and agent. The routing contract and lifecycle state model determine almost every later boundary.

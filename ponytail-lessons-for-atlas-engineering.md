# Cannibalizing Ponytail for the Atlas Engineering Workflow

## Context

The canonical Ponytail repository is `DietrichGebert/ponytail`.

Ponytail is not a complete end-to-end engineering workflow. Its strongest value for Atlas is as an **anti-overengineering control layer**: a compact decision policy that pushes agents toward YAGNI, reuse, simple design, root-cause fixes, deliberate debt, and subtraction.

The useful goal is not to copy Ponytail wholesale or import its "lazy senior developer" persona. The useful goal is to extract the mechanisms that strengthen Atlas's proposed engineering workflow.

---

## 1. The Core Idea Worth Keeping

Ponytail's central decision ladder is roughly:

```text
1. Does this need to exist at all?
2. Does it already exist in the codebase?
3. Does the standard library already solve it?
4. Does the native platform already solve it?
5. Does an installed dependency already solve it?
6. Can it be expressed much more simply?
7. Only then: write the minimum code that works.
```

The important qualifier is that this ladder runs **after understanding the problem**, not instead of understanding it.

For Atlas, the equivalent principle should be:

> **Build the smallest coherent solution that satisfies the required behaviour, verified constraints, standards, and safety obligations. Add complexity only when current evidence requires it.**

This should become part of `engineering-core`, not a separate Ponytail-branded plugin.

---

## 2. Ponytail to Atlas Mapping

| Ponytail idea | Atlas adaptation | Where it belongs |
|---|---|---|
| YAGNI / "does this need to exist?" | Challenge speculative requirements and architecture | Planning + design |
| Reuse before writing | Search local patterns/source/Atlas before inventing | Discovery |
| Stdlib/native/existing dependency first | Prefer existing capability before new ownership | Implementation |
| Minimum working change | Make GREEN deliberately boring/minimal | TDD loop |
| Root cause over symptom | Trace ownership/callers/impact before bug fix | Bugfix workflow |
| No speculative abstraction | Delay interfaces/factories/config until pressure exists | GREEN + REFACTOR |
| Deletion over addition | Dedicated subtraction pass | REFACTOR/review |
| Ponytail review | Independent simplicity reviewer | Review phase |
| Whole-repo audit | Optional complexity-maintenance skill | Maintenance, not normal delivery |
| `ponytail:` debt comments | Structured deliberate simplification with ceiling + trigger | Change Contract/Episode |
| lite/full/ultra | Replace with lifecycle-aware policy | engineering-flow |
| Always-on hooks | Inject a tiny engineering kernel; route richer rules by phase/role | plugin/runtime |
| Cross-agent rule injection | Ensure implementing agents inherit relevant invariants | handoff/runtime |
| Multi-agent portability | Canonical definitions + thin host adapters | plugin packaging |
| Agentic A/B benchmarks | Evaluate rules/skills before promotion | adaptation framework |
| LOC scoreboard | Secondary telemetry only | evaluation |
| "one small test" | Do not adopt literally | use risk/TDD strategy |

---

## 3. Where This Fits Into XP

Ponytail becomes most useful when combined with XP rather than used as an isolated coding style.

A good lifecycle is:

```text
                 VERTICAL SLICE
                       │
                       ▼
               ┌──────────────┐
               │     RED      │
               │ behaviour    │
               │ first        │
               └──────┬───────┘
                      ▼
               ┌──────────────┐
               │    GREEN     │
               │ Simple Design│
               │ minimum code │
               └──────┬───────┘
                      ▼
               ┌──────────────┐
               │   REFACTOR   │
               │ DRY / names  │
               │ cohesion     │
               │ SOLID where  │
               │ pressure is  │
               └──────┬───────┘
                      ▼
               ┌──────────────┐
               │    VERIFY    │
               │ tests/build  │
               │ standards    │
               └──────┬───────┘
                      ▼
        ┌─────────────┼──────────────┐
        ▼             ▼              ▼
   correctness     security      simplicity
     review         review         review
        └─────────────┼──────────────┘
                      ▼
                   DELIVER
```

### GREEN should be Ponytail-like

During GREEN:

> Pass the failing behavioural test with the smallest reasonable implementation.

Do not aggressively apply SOLID.

Do not add an interface because there may be a second implementation someday.

Do not create a strategy pattern because there are currently two branches.

Do not introduce configuration merely "for flexibility".

This is compatible with XP's Simple Design.

### REFACTOR is where DRY and SOLID get permission

Once behaviour works, ask:

- Is there actual duplication?
- Is ownership unclear?
- Is there an unstable boundary?
- Did implementation expose a meaningful variation point?
- Is coupling now making the next change harder?

Then apply:

```text
DRY
cohesion
coupling
naming
encapsulation
SOLID where real design pressure exists
```

The direction becomes:

```text
behaviour
   ↓
minimal implementation
   ↓
observed design pressure
   ↓
appropriate abstraction
```

rather than:

```text
SOLID
   ↓
design abstractions in advance
```

---

## 4. Extend the Engineering Change Contract

Add explicit simplicity and deliberate-shortcut information.

For example:

```yaml
design:
  simplest_viable_shape:
  reused_capabilities: []
  new_abstractions: []
  new_dependencies: []

deliberate_simplifications:
  - decision:
    ceiling:
    upgrade_trigger:
    evidence:
```

This is derived from one of Ponytail's strongest mechanisms: deliberate shortcuts are not merely marked "TODO". They should name both:

1. the **ceiling** of the simplified approach;
2. the **trigger** that justifies upgrading it.

Example:

```yaml
deliberate_simplifications:
  - decision: Use linear comparison instead of indexing
    ceiling: Suitable below ~100k records per run
    upgrade_trigger: p95 reconciliation exceeds 20 seconds
    evidence:
      - benchmark: recon-small-v2
```

This is much stronger than:

```text
TODO optimise later
```

because the compromise is explicit and testable.

---

## 5. Feed Deliberate Simplicity Into Engineering Episodes

The Engineering Change Contract records the intended simplification.

The Engineering Episode records what happened.

```text
Change Contract
    │
    ├─ expected simplifications
    │
    ▼
Implementation
    │
    ▼
Engineering Episode
    │
    ├─ which simplifications held?
    ├─ which ceilings were reached?
    ├─ did an upgrade trigger fire?
    └─ did the agent overbuild anyway?
```

That gives the Adaptation Router useful evidence.

Example:

```text
Episode:
Agent repeatedly creates a repository interface
for a service with one implementation.

         ↓

Adaptation Router

         ↓

Repeated procedural mistake

         ↓

Candidate rule:

"Do not introduce a polymorphic boundary solely
for hypothetical future implementations."
```

That candidate still goes through evaluation, review, and human approval before becoming active.

---

## 6. Add a Dedicated Simplicity Reviewer

Ponytail's review skill deliberately looks only for unnecessary complexity and leaves correctness, security, and performance to other reviewers.

Atlas should keep that separation.

Introduce a read-only specialist:

```text
simplicity-reviewer
```

Its input should include:

- approved Engineering Change Contract;
- implementation diff;
- relevant standards;
- passing verification evidence.

Its job is to find only things such as:

- behaviour not required by the contract;
- abstractions without current design pressure;
- duplicate capability already present;
- new dependency replaceable by approved existing/native capability;
- forwarding or wrapper layers with no owned responsibility;
- unnecessary configuration or flexibility;
- dead compatibility machinery;
- avoidable changed surface;
- opportunities to remove code while preserving behaviour.

It should not:

- challenge explicitly required behaviour;
- remove safety, validation, or integrity controls;
- redesign unrelated code;
- apply changes directly;
- replace correctness review.

A useful parallel review phase is therefore:

```text
correctness-reviewer
security-reviewer       if applicable
architecture-reviewer   if applicable
simplicity-reviewer
```

The outputs can then be merged by the owning workflow.

---

## 7. Optimize for Conceptual Surface, Not File Count

Do not adopt Ponytail's "fewest files" or "one line" ideas literally.

Sometimes:

```text
+ 2 classes
+ 1 interface
```

is genuinely simpler than adding a large conditional into an existing class.

Atlas should optimize for:

```text
minimum conceptual surface
```

not:

```text
minimum physical file count
```

A better rule is:

> **An abstraction earns its existence when it removes knowledge from callers, owns an invariant, isolates an external boundary, or responds to demonstrated variation.**

That is stronger than a simplistic "interfaces are bad until implementation #2" rule.

---

## 8. Integrate Root-Cause Debugging

Ponytail's bug-fix philosophy is useful:

A bug report names a symptom, not necessarily the ownership point.

For Atlas, use:

```text
BUG REPORT
    ↓
reproduce
    ↓
identify failing behaviour
    ↓
trace ownership / callers / Atlas impact
    ↓
find narrowest common cause
    ↓
RED regression test
    ↓
fix ownership point
    ↓
GREEN
```

Atlas can improve this further because the agent may have access to:

```text
source
+
source graph
+
Atlas architectural dependencies
```

This allows bug investigation to trace both implementation-level callers and system-level impact.

---

## 9. Cannibalize the Hook/Runtime Model

Ponytail's portability model is valuable.

Its core behaviour is reused across multiple hosts with thin platform-specific adapters.

Atlas should follow the same pattern:

```text
canonical engineering definitions
            │
            ├── Claude plugin adapter
            ├── Codex adapter
            ├── AGENTS.md adapter
            └── future host adapters
```

Do not independently maintain different Claude and Codex versions of the same engineering rule.

Add deterministic drift checks in CI:

```text
canonical rule
    ↓
render/adapt
    ↓
host surfaces

CI:
all generated/adapted surfaces still aligned?
```

This is especially important as Atlas becomes both a context layer and an engineering-agent distribution system.

---

## 10. Do Not Inject Every Rule Everywhere

The useful principle from Ponytail is persistent behavioural context.

The wrong implementation would be injecting every engineering principle into every agent.

Use a layered model:

### Tiny global kernel

```text
understand before changing
do not invent requirements
evidence beats assumption
required safety/standards win
prefer the simplest coherent solution
```

### Phase-specific guidance

```text
GREEN
→ simple design / YAGNI

REFACTOR
→ DRY / cohesion / ownership

VERIFY
→ deterministic evidence

REVIEW
→ role-specific review lenses
```

### Role-specific guidance

```text
implementer
→ TDD + simple design

architect
→ YAGNI + boundary/design principles

security reviewer
→ security rules, no minimalism pressure

discovery agent
→ evidence/provenance only

simplicity reviewer
→ aggressive subtraction lens
```

So the runtime model becomes:

```text
tiny invariant kernel
        +
phase rules
        +
role rules
        +
team standards
```

This avoids turning the agent context into a giant engineering handbook.

---

## 11. Cannibalize the Evaluation Approach

Ponytail's benchmark work is especially useful for the Atlas Adaptation Router.

Its evaluation evolved from simple single-shot generation benchmarks into more realistic agentic runs on real repositories with:

- control vs treatment arms;
- actual code execution;
- source diffs;
- safety checks;
- adversarial inputs;
- isolation between baseline and treatment.

The important principle for Atlas is:

> **Correctness and safety are gates. Simplicity is an optimization metric.**

For every candidate skill or rule:

```text
                     SAME TASKS
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
             CONTROL            TREATMENT
         current harness      + candidate
               │                   │
               └─────────┬─────────┘
                         ▼
                   HARD GATES
                correctness
                   safety
                  standards
                scope adherence
                         │
                         ▼
                 SOFT METRICS
                  tool calls
                   retries
                    time
                  code delta
               human corrections
```

The baseline must be isolated.

No global rule, hook, plugin, or inherited instruction should leak into the control arm.

This directly strengthens the procedural evaluation model already proposed in `adaptation-router.md`.

---

## 12. Do Not Use LOC as the Goal

Ponytail itself treats line count as an optimization metric while correctness remains a gate.

Atlas should do the same.

Do not reward an agent for:

```text
40 lines → 8 lines
```

if the smaller implementation:

- weakens validation;
- removes observability;
- breaks standards;
- obscures domain ownership;
- introduces unsafe assumptions.

A useful ordering is:

```text
correctness
safety
required standards
maintainable ownership
        ↓
simplicity
        ↓
cost / tool usage / code volume
```

Simplicity only optimizes inside the space of acceptable solutions.

---

## 13. Proposed `engineering-core` Additions

Evolve the engineering plugin roughly toward:

```text
engineering-core/
│
├── rules/
│   ├── engineering-kernel.md
│   └── simple-design.md
│
├── skills/
│   ├── engineering-flow/
│   ├── grill/
│   ├── tdd/
│   ├── minimal-change/
│   ├── deliberate-simplification/
│   ├── complexity-audit/
│   ├── verify/
│   └── deliver/
│
├── agents/
│   ├── codebase-scout.md
│   ├── architect.md
│   ├── impact-analyst.md
│   ├── code-reviewer.md
│   ├── simplicity-reviewer.md
│   ├── security-reviewer.md
│   ├── delivery-reviewer.md
│   └── adaptation-reviewer.md
│
├── references/
│   ├── engineering-change-contract.md
│   ├── engineering-episode.md
│   ├── simple-design-ladder.md
│   ├── deliberate-simplification.md
│   ├── design-principles.md
│   ├── refactoring-principles.md
│   └── anti-patterns.md
│
└── evaluation/
    ├── procedural/
    ├── rules/
    └── simplicity/
```

---

## 14. Revised Engineering Flow

With the useful Ponytail concepts integrated:

```text
INTAKE
  ↓
GRILL if needed
  ↓
DISCOVER / IMPACT
  ↓
DESIGN if needed
  ↓
VERTICAL SLICE PLAN
  ↓
RED
  ↓
GREEN
  │
  └── SIMPLE-DESIGN LADDER
  ↓
REFACTOR
  │
  ├── remove duplication
  ├── improve ownership/names
  └── introduce abstractions only where pressure exists
  ↓
VERIFY
  ↓
CORRECTNESS ─┐
SECURITY ────┼── parallel review
SIMPLICITY ──┘
  ↓
DELIVERY
  ↓
ENGINEERING EPISODE
  ↓
ADAPTATION ROUTER
```

---

## 15. Atlas-Specific Simple Design Rule

The most useful Ponytail philosophy can be reduced to one Atlas engineering rule:

> **Understand the behaviour and constraints first. Then prefer reuse, existing platform capabilities, and the smallest coherent implementation. During GREEN, do not build abstractions for hypothetical needs. During REFACTOR, introduce structure only in response to observed duplication, unclear ownership, unstable boundaries, or verified variation. Simplicity may never remove required correctness, security, data integrity, accessibility, or organisational standards.**

This gives XP a clear place inside the Atlas workflow:

- **TDD** provides the feedback cycle;
- Ponytail-style minimalism provides **Simple Design during GREEN**;
- **DRY/SOLID** become refactoring responses to demonstrated pressure;
- the **simplicity reviewer** provides a final subtraction pass;
- the **Engineering Episode** records whether deliberate simplifications held;
- the **Adaptation Router** can learn from repeated overengineering or underengineering patterns.

---

## 16. What Not to Copy

Do not copy Ponytail wholesale.

Avoid:

- the personality/persona as architecture;
- "fewest files" as an invariant;
- line-count minimization as the quality objective;
- one-test-only policy;
- always-on aggressive minimalism for security/reliability work;
- global application of the same intensity to every agent and phase;
- automatic conversion of every simplification into a rule.

Keep the mechanisms:

- simple-design decision ladder;
- YAGNI;
- reuse-first;
- root-cause fixes;
- deliberate simplification with ceiling + trigger;
- dedicated subtraction review;
- portable canonical rule definitions;
- controlled propagation to subagents;
- isolated control/treatment evaluation;
- explicit honesty about tradeoffs and workload-dependent results.

---

## Related Atlas Design Notes

This proposal complements the existing root and design documents:

- `docs/engineering-lifecycle-control-plane.md`
- `adaptive-engineering-learning-loop.md`
- `adaptation-router.md`

It should be treated as the **simple-design / XP layer** of the engineering control plane rather than as another independent workflow.

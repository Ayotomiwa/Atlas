# Atlas Adaptation Router

## Purpose

The **Adaptation Router** is a read-only decision layer between an `Engineering Episode` and any durable change to Atlas, skills, or rules.

Its job is not to learn automatically.

Its job is to answer:

> Does this episode contain a reusable finding, what kind is it, and what evidence and evaluation would be required before a human could promote it?

The router must preserve the existing Atlas ownership model:

- the parent workflow owns routing, scope, and approval;
- specialists operate on bounded evidence;
- persistence is a separate controlled operation;
- classification and promotion are separate state transitions;
- the router may propose durable learning but may never promote it.

---

## 1. Core Flow

```text
ENGINEERING EPISODE
        │
        ▼
┌──────────────────────┐
│ FINDING EXTRACTION   │
│ evidence-backed only │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ ADAPTATION ROUTER    │
│ classify + qualify   │
└──────────┬───────────┘
           │
   ┌───────┼────────────┬───────────┐
   ▼       ▼            ▼           ▼
DISCARD   HOLD      CANDIDATE    AUTHORITY
                      │          REQUIRED
             ┌────────┼────────┐
             ▼        ▼        ▼
         SEMANTIC PROCEDURAL  RULE
             │        │        │
             ▼        ▼        ▼
           route-specific evaluation
             │        │        │
             └────────┼────────┘
                      ▼
              INDEPENDENT REVIEW
                      ▼
                HUMAN DECISION
                /      |      \
           approve   defer   reject
              │
              ▼
            PROMOTE
```

Classification and promotion are deliberately separate.

---

## 2. Router Input

Do not feed the router a raw conversation transcript.

Feed it the completed `Engineering Episode` plus the original `Engineering Change Contract`.

Example:

```yaml
episode:
  id: episode.2026-09-21.recon-fix
  task_type: bugfix
  objective: Fix reconciliation mismatch

change_contract:
  expected_scope: [...]
  expected_tests: [...]
  expected_risks: [...]
  applicable_standards: [...]

observed:
  changed_paths: [...]
  commands: [...]
  test_results: [...]
  failures: [...]
  recoveries: [...]
  human_corrections: [...]
  review_findings: [...]

outcome:
  completed: true
  verification: passed
  deployment_result: passed

evidence:
  source_refs: [...]
  git_refs: [...]
  atlas_refs: [...]
  standard_refs: [...]
```

The adaptation workflow should derive a **plan-vs-reality delta** before classification.

```text
expected                     observed
──────────────────────       ──────────────────────
3 files                      8 files
unit test sufficient         integration issue found
no migration                 migration required
known dependency             hidden dependency discovered
normal build                 annotation processing failed
```

The router primarily examines those deltas, human corrections, recovery paths, review findings, and repeated friction.

---

## 3. Eligibility Gate: Was Anything Actually Learned?

Before deciding what type a finding is, apply an eligibility gate.

A finding is adaptation-worthy only when it is reasonably:

```text
Evidence-backed
      AND
Material
      AND
Reusable beyond this exact run
      AND
Not already adequately represented
```

A successful engineering run may therefore legitimately return:

```yaml
decision: discard
reason: no_reusable_learning
```

Discard should be a common outcome.

The system should prefer throwing away most episodes over manufacturing lessons from every successful execution.

---

## 4. Classification Contract

The router has three durable candidate types:

1. **Semantic**
2. **Procedural**
3. **Rule**

It also has terminal or non-promoting dispositions:

- `discard`
- `hold`
- `authority_required`

Each candidate type has a precise meaning.

---

## 5. Semantic Candidate

A semantic candidate is a **fact about the engineered system or its operating context**.

Classification question:

> Would this still be true if a different engineer or agent performed the same task tomorrow?

Examples:

```text
Component A publishes schema B.

This Lambda is deployed by Stack X.

Flow Y retries through queue Z.

Repository A depends on Repository B.

This system uses standard S for deployment.
```

Destination:

```text
Atlas staging → normal Atlas curation
```

Semantic candidates describe **the world**.

The Adaptation Router should not introduce another semantic governance path. Once classified, the finding should enter the existing Atlas Teach/staging/curation workflow.

---

## 6. Procedural Candidate

A procedural candidate is a **repeatable technique for achieving an engineering outcome**.

Classification question:

> Does this tell an engineer or agent how to perform some class of work better?

Examples:

```text
When Jackson deserialisation fails after adding Lombok,
inspect generated constructors before changing the handler.

When changing an API contract:
1. add a contract test;
2. update the producer;
3. update consumers;
4. run compatibility verification.
```

Destination:

```text
candidate skill / workflow
```

Procedural candidates describe **how to work**.

They should normally become scoped skills or workflow guidance rather than global rules.

---

## 7. Rule Candidate

A rule candidate is a **constraint on agent behaviour that should hold across applicable workflows**.

Classification question:

> Is this primarily about preventing unsafe or repeatedly harmful agent behaviour rather than teaching a multi-step technique?

Examples:

```text
Never infer an Atlas dependency from co-edit history alone.

Do not modify production implementation when a failing
characterisation test shows the existing behaviour is unknown.

Before altering generated files, identify their source generator.
```

Destination:

```text
candidate rule
```

Rules describe **what an agent must or must not do**.

Rules should be significantly rarer than procedures.

---

## 8. Authority-Required Route

The router needs a special terminal classification:

```yaml
classification: authority_required
```

This prevents observations from being converted into organisational policy.

Example:

Suppose three deployment episodes all include XRay tests.

The router must not conclude:

> All deployments must have XRay tests.

It should instead route:

```text
Observed recurring practice
        ↓
Could be policy?
        ↓
AUTHORITY_REQUIRED
        ↓
locate standard / owner / policy
```

Hard invariant:

> **Episodes may discover evidence that a policy exists; episodes cannot create organisational policy.**

Only an authoritative standard or owner can establish policy.

---

## 9. Hold and Discard

Not every finding should become a candidate.

### Discard

Use `discard` when the finding is:

- trivial;
- one-off noise;
- already adequately covered;
- merely correlated with success;
- unsuccessful behaviour without a supported lesson;
- immaterial;
- too specific to this one execution to be reusable.

### Hold

Use `hold` when the finding may matter but evidence is insufficient.

Example:

```yaml
classification: hold
reason: causal_link_unproven
settling_evidence:
  - reproduce failure
  - inspect generated source
```

Unresolved remains unresolved.

---

## 10. Adaptation Decision Schema

Every atomic finding should produce one structured `AdaptationDecision`.

Example:

```yaml
schema_version: atlas-adaptation-decision/1.0

episode_id: episode.2026-09-21.recon-fix
finding_id: finding.003

finding:
  statement: >
    Jackson DTO deserialisation failures involving Lombok
    should be diagnosed by inspecting generated constructors
    before changing Lambda handler code.

classification:
  disposition: candidate
  type: procedural
  confidence: high

evidence:
  direct:
    - test: ClientEntityDeserialisationTest
    - commit: abc123
    - human_correction: correction.02
  inferred: []

reuse:
  scope:
    languages: [java]
    technologies: [jackson, lombok]
  recurrence_signal: repeated
  existing_coverage: none

proposed_target:
  kind: skill
  id: java-debug-jackson-deserialisation

evaluation:
  required: true
  scenarios:
    - lombok-constructor-conflict
    - missing-json-creator
    - unrelated-malformed-json
  baseline: without_candidate
  treatment: with_candidate

human_gate:
  required: true

status: classified
```

The router cannot set approval or activation.

There should be no field equivalent to:

```yaml
approved: true
```

at router time.

---

## 11. Classification Decision Tree

The decision logic should be deterministic enough to document.

```text
Is the finding supported by observable evidence?
        │
       no
        ▼
      HOLD

       yes
        │
        ▼
Is it materially reusable?
        │
       no
        ▼
    DISCARD

       yes
        │
        ▼
Does it assert an organisation/team obligation?
        │
       yes
        ▼
 AUTHORITY_REQUIRED

       no
        │
        ▼
Does it describe a durable fact about a system?
        │
       yes
        ▼
    SEMANTIC

       no
        │
        ▼
Does it describe a reusable multi-step technique,
diagnostic approach or engineering procedure?
        │
       yes
        ▼
   PROCEDURAL

       no
        │
        ▼
Does it constrain undesirable agent behaviour
across applicable work?
        │
       yes
        ▼
       RULE

       no
        ▼
      HOLD
```

A single episode may yield multiple findings of different types.

---

## 12. Split Findings Before Classification

Classify one claim at a time.

Do not treat this as one finding:

```text
We discovered service A writes to DynamoDB,
the initial Atlas record was wrong,
and agents should always inspect Terraform before
modifying persistence logic.
```

Split it:

```text
Finding 1
Service A writes to DynamoDB.
→ SEMANTIC

Finding 2
Atlas currently says Service A writes to PostgreSQL.
→ SEMANTIC conflict

Finding 3
Inspect infrastructure ownership before modifying
persistence boundaries.
→ PROCEDURAL or RULE candidate
```

Principle:

> **One claim, one classification.**

This makes evaluation, ownership, and promotion much cleaner.

---

## 13. Semantic Candidate Evaluation

Do not invent a second semantic governance mechanism.

Semantic candidates should reuse Atlas.

```text
SEMANTIC CANDIDATE
        ↓
duplicate/conflict search
        ↓
source/provenance verification
        ↓
Atlas persistence preview
        ↓
HUMAN APPROVAL
        ↓
_staging
        ↓
normal curation
        ↓
independent semantic review
        ↓
_curated
```

The router's semantic responsibility should stop around:

```yaml
route: atlas-teach
candidate_claims: [...]
evidence: [...]
existing_conflicts: [...]
```

From that point, the current Atlas lifecycle owns persistence and promotion.

---

## 14. Procedural Candidate Evaluation

Procedural candidates need a dedicated evaluation path.

### Evidence validity

Did the episode actually support the proposed technique?

### Generalisation

Does the technique apply beyond the exact incident?

### Novelty

Does another skill or workflow already cover it?

### Specificity

Is its activation boundary clear?

Bad:

```text
Always inspect dependencies carefully.
```

Better:

```text
When a DTO deserialises correctly locally but fails through
an AWS Lambda handler, first reproduce using the handler's
actual ObjectMapper configuration before changing the DTO.
```

### Outcome evaluation

Run representative control/treatment scenarios.

```text
control:
  existing skills only

treatment:
  existing skills + candidate
```

Compare evidence such as:

```text
correctness
unnecessary modifications
tool calls
retries
review findings
scope violations
human intervention
```

Avoid a universal percentage threshold.

Use candidate-specific gates.

Example:

```yaml
promotion_criteria:
  must:
    - no treatment regression
    - resolves intended failure scenarios
    - no new scope violations
  desirable:
    - fewer unnecessary edits
    - fewer tool calls
```

---

## 15. Rule Candidate Evaluation

Rule candidates require stricter evaluation than procedural candidates.

Rules tend to be loaded more broadly and can distort unrelated engineering work.

### A. Require repeated or high-severity evidence

A rule can originate from:

```text
repeated agent mistake
```

or:

```text
single high-consequence failure
```

It should not originate from stylistic preference.

### B. Require negative scenarios

Evaluate both where the rule should activate and where it must not activate.

Example candidate:

> Never edit generated code directly.

Evaluation:

```text
Scenario A: generated MapStruct implementation
→ should block direct edit

Scenario B: checked-in generated-but-owned fixture
→ project policy may explicitly permit edit

Scenario C: ordinary handwritten class
→ rule must not interfere
```

False positives matter substantially for rules.

### C. Evaluate context cost

Ask:

> Does this need to be a global rule at all?

It may belong inside:

```text
Java skill
```

rather than:

```text
always-on engineering rules
```

Promotion preference:

```text
skill-local instruction
      >
conditional rule
      >
global rule
```

Use the least powerful mechanism that solves the problem.

---

## 16. Candidate Lifecycle

Use one common lifecycle for procedural and rule candidates:

```text
observed
   ↓
classified
   ↓
proposed
   ↓
evaluating
   ↓
reviewed
   ↓
awaiting-human
   ├──────── rejected
   ├──────── deferred
   │
   ▼
approved
   ↓
active
   ↓
monitoring
   │
   ├──────── retained
   ├──────── revised
   └──────── retired
```

Semantic candidates should leave this lifecycle once routed into existing Atlas staging/curation.

Do not add these states to Atlas's existing semantic-content status taxonomy. They belong to procedural adaptation, not curated semantic records.

---

## 17. Human Approval Gate

Human approval should receive a compact proposal rather than the complete episode.

Example:

```text
Candidate: java-debug-jackson-deserialisation
Type: Procedural

Observed:
Two deserialisation incidents were resolved only after
generated constructor behaviour was inspected.

Proposed behaviour:
When Jackson deserialisation fails for a Lombok DTO, inspect
the effective constructor/creator shape before changing the
handler or ObjectMapper.

Evidence:
- episode A …
- episode B …

Evaluation:
4/4 target scenarios succeeded
3/3 negative scenarios unaffected
no additional scope violations
median tool calls reduced 11 → 7

Existing coverage:
No equivalent active skill found.

Will change:
plugins/java-engineering/skills/...

Will not change:
team standards
global rules
Atlas semantic records

Decision:
Approve / Revise / Defer / Reject / Merge
```

This should follow Atlas's existing **one concrete preview, one scope-bound approval** philosophy.

---

## 18. Human Decisions

Human decisions should have explicit semantics.

### APPROVE

Activate exactly the evaluated candidate.

### REVISE

The candidate idea is accepted, but its content or scope changes.

Material revision requires re-evaluation.

### DEFER

Keep the candidate and evidence, but do not activate it.

### REJECT

Do not activate the candidate from the current evidence.

### MERGE

Useful learning exists but belongs inside an existing skill or rule rather than becoming a new artifact.

`MERGE` is important for preventing skill explosion.

---

## 19. Promotion Gate Invariant

No non-human component can promote a durable procedural or rule candidate.

```text
router
   cannot promote

reviewer
   cannot promote

evaluator
   cannot promote
```

Eligibility for activation requires:

```text
candidate
+ supported evidence
+ required evaluation passed
+ independent review completed
+ explicit human approval
────────────────────────────────
= eligible for activation
```

A deliberate human override may exist, but it must remain visible:

```yaml
approval:
  mode: human_override
  failed_gates: [...]
```

Never silently mark failed evaluation gates as passed.

---

## 20. Independent Adaptation Reviewer

Introduce one read-only specialist:

```text
adaptation-reviewer
```

Its job is not to run the behavioural evaluation.

Its job is to independently review the candidate and evidence.

Questions include:

- Does the candidate accurately derive from the episode evidence?
- Is the classification correct?
- Does it duplicate existing knowledge or behaviour?
- Is the scope too broad?
- Does it encode project-specific behaviour as a generic rule?
- Does it convert correlation into causation?
- Does it invent organisational policy?
- Are negative cases missing?
- Is a weaker mechanism sufficient?
- Does an existing skill or rule deserve amendment instead?

The reviewer must remain read-only and cannot activate the candidate.

---

## 21. Ownership Boundaries

Keep the responsibilities narrow.

```text
reflect-engineering-run
        │
        ├── extracts findings
        │
        ▼
adaptation-router
        │
        ├── eligibility
        ├── classification
        ├── duplicate routing
        └── evaluation requirements
                 │
       ┌─────────┼──────────┐
       ▼         ▼          ▼
 semantic   procedural     rule
   route     evaluator   evaluator
       │         │          │
       └─────────┼──────────┘
                 ▼
       adaptation-reviewer
                 ▼
          human approval
                 ▼
         promotion workflow
```

The router should remain small.

Do not turn it into an agent that:

- reflects;
- classifies;
- writes skills;
- runs its own evals;
- judges its own evals;
- activates the resulting behaviour.

That would destroy the separation of responsibilities.

---

## 22. Suggested Plugin / Module Shape

Conceptually:

```text
engineering-core/
│
├── skills/
│   ├── reflect-engineering-run/
│   ├── adaptation-router/
│   ├── evaluate-procedural-candidate/
│   ├── evaluate-rule-candidate/
│   └── promote-adaptation/
│
├── agents/
│   └── adaptation-reviewer.md
│
├── references/
│   ├── engineering-episode.md
│   ├── adaptation-decision.md
│   ├── procedural-candidate.md
│   └── rule-candidate.md
│
└── evaluation/
    └── ...
```

Semantic promotion should not get a separate adaptation-specific evaluator because Atlas already owns the semantic lifecycle.

Semantic candidates should route to:

```text
Teach Atlas → staging → curation
```

---

## 23. Router Behavioural Contract

The Adaptation Router can be summarised as:

> **The Adaptation Router classifies evidence-backed findings from completed Engineering Episodes into semantic, procedural, rule, authority-required, hold, or discard dispositions. It never persists or activates learning. Semantic candidates are routed into Atlas's existing evidence and curation lifecycle. Procedural candidates are converted into bounded skill proposals and evaluated against representative control/treatment scenarios. Rule candidates require stronger justification, negative-case evaluation, and proof that a narrower procedural mechanism is insufficient. All durable procedural or rule changes require independent review and explicit human approval after evaluation. Episode observations may suggest that an organisational standard exists, but may never establish policy without an authoritative source.**

The resulting architecture is:

```text
               ENGINEERING EPISODE
                       │
                       ▼
                 FINDING EXTRACTION
                       │
                       ▼
                ADAPTATION ROUTER
                       │
        ┌──────────────┼───────────────┐
        │              │               │
        ▼              ▼               ▼
    SEMANTIC       PROCEDURAL         RULE
        │              │               │
        ▼              ▼               ▼
   Atlas route     skill proposal   rule proposal
        │              │               │
        ▼              └──────┬────────┘
existing evidence              ▼
+ curation               controlled eval
        │                       │
        │                       ▼
        │              adaptation-reviewer
        │                       │
        └───────────────┬───────┘
                        ▼
                  HUMAN APPROVAL
                        │
               ┌────────┴─────────┐
               ▼                  ▼
             PROMOTE             STOP
```

---

## 24. Recommended Implementation Sequence

Implement the adaptation subsystem in this order:

1. define the **Engineering Episode** schema;
2. define the atomic **Finding** schema;
3. define `atlas-adaptation-decision/1.0`;
4. implement the classification router;
5. implement duplicate / existing-coverage checks;
6. reuse Atlas Teach/staging/curation for semantic candidates;
7. define procedural candidate representation;
8. define rule candidate representation;
9. implement procedural and rule evaluation harnesses;
10. introduce the read-only `adaptation-reviewer`;
11. define the human approval/promotion workflow;
12. add monitoring, revision, ablation, and retirement later.

Do not begin by writing an induction prompt.

The key contracts are:

```text
Episode
  ↓
Finding
  ↓
AdaptationDecision
  ↓
Candidate
  ↓
Evaluation
  ↓
Review
  ↓
Human Approval
  ↓
Promotion
```

If these contracts are clean, the LLM that extracts or classifies findings becomes replaceable implementation detail rather than the architecture itself.

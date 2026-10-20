# Atlas Engineering Toolbox and CLI Runtime

## Context

Atlas is evolving beyond a governed engineering context layer into a broader engineering-agent capability.

The proposed engineering workflow already includes:

- an `engineering-flow` controller;
- an Engineering Change Contract;
- contextual discovery through Atlas and product source;
- selective grilling;
- design/architecture when needed;
- TDD / RED → GREEN → REFACTOR;
- XP/simple-design principles;
- deterministic verification;
- independent review;
- delivery/deployment handling;
- Engineering Episodes;
- an Adaptation Router that can propose semantic, procedural, or rule candidates.

Recent work also introduced the idea of a source-routing layer so Atlas can locate the **smallest relevant source slice** instead of repeatedly loading whole files or scanning repositories.

A useful external comparison is Qodo's Agentic Toolbox and public `qodo-skills` repository.

Qodo's architecture separates:

```text
host coding agent
      │
      ▼
complete local skills / workflows
      │
      ▼
CLI or MCP tool runtime
      │
      ▼
managed context, standards, review, history and cross-repo capabilities
```

The important lesson is not to reproduce Qodo's product architecture literally.

The useful pattern is:

> **The agent owns the engineering task and reasoning. A toolbox supplies reliable specialist capabilities through narrow interfaces.**

Qodo also authors canonical skill workflows once and generates provider-specific projections. Its CLI primarily owns runtime/tool access rather than the complete coding workflow.

This raises a design question for Atlas.

---

## Question

> Should Atlas build a CLI tool that the engineering workflow calls, similar in spirit to Qodo's runtime, or are skills plus the existing Atlas scripts sufficient?

More specifically:

- Should the engineering workflow directly call Python scripts such as `atlas_query.py`, `atlas_source_snapshot.py`, and other utilities?
- Should Atlas expose a stable `atlas ...` command surface?
- Which responsibilities belong in the CLI versus skills/agents?
- Should a future MCP surface exist as well?
- How much runtime infrastructure is justified before the engineering workflow itself is proven?

---

# Recommendation

## Build an Atlas CLI, but keep it thin

An Atlas CLI is strategically useful, but it should **not** become the engineering workflow.

The clean boundary is:

> **Skills and agents own engineering reasoning and workflow.  
> The CLI owns deterministic mechanics shared across those workflows.**

Conceptually:

```text
Claude / Codex / other host
          │
          ▼
   engineering-flow
          │
          │ reasoning / orchestration
          ▼
      Atlas CLI
          │
          │ deterministic operations
          ▼
  Atlas + Git + source
  + build/test tooling
```

The CLI should initially be a thin façade over the Python libraries and scripts Atlas already has.

Do not rebuild Atlas into a second platform before proving the workflow.

---

# 1. Why a CLI becomes useful

Atlas already has useful functionality spread across scripts.

Examples include:

```text
atlas_query.py
atlas_source_snapshot.py
rebuild_atlas.py
validation/generation utilities
```

Without a stable runtime interface, each skill has to know implementation details such as:

- which Python script to call;
- where it lives;
- which flags it accepts;
- how to locate `ATLAS_ROOT`;
- how to parse its output;
- how errors are represented;
- how source revisions are resolved;
- which operations are read-only versus mutating.

That creates several problems.

### Skill/runtime coupling

A skill becomes coupled to internal script names and flags.

Refactoring a script requires editing multiple skills.

### Repeated mechanics

Different skills may independently implement:

- repository/revision detection;
- JSON parsing;
- source-range calculation;
- standards lookup;
- validation;
- temporary-state handling.

### Harder portability

Claude, Codex, future hosts, and a possible MCP surface all need to understand the same underlying operations.

### Context and token waste

If deterministic mechanics are left to the model, the model spends tokens repeatedly deciding how to perform operations that should have one stable implementation.

A CLI can remove this mechanical reasoning from the model's context.

---

# 2. The key architectural boundary

Use the following split.

```text
           NON-DETERMINISTIC
           reasoning / workflow
                 │
                 ▼
        ┌───────────────────┐
        │ Skill / Agent     │
        │ engineering-flow  │
        └─────────┬─────────┘
                  │
                  │ structured request
                  ▼
        ┌───────────────────┐
        │    Atlas CLI      │
        │ deterministic     │
        └─────────┬─────────┘
                  │
         ┌────────┼─────────┐
         ▼        ▼         ▼
       Git      Atlas     source
       CI       maps      tooling
```

### Skills / agents decide

Examples:

- What kind of change is this?
- Is the request ambiguous?
- Should the user be grilled?
- Is architecture/design needed?
- What testing strategy fits this change?
- Does this require TDD?
- Which standards may be relevant?
- Is a reviewer finding valid?
- Is a simplification appropriate?
- Should an episode finding become a procedural or rule candidate?
- Is more source evidence needed?

### CLI executes or resolves

Examples:

- resolve an Atlas ID;
- find candidate Atlas records;
- traverse known impact edges;
- resolve a repository revision;
- locate an exact source anchor;
- return a source slice;
- compute a diff;
- run a predefined verification command;
- parse test output;
- validate an Engineering Episode schema;
- persist or queue approved runtime artifacts;
- resolve known scoped rules/standards from structured inputs.

The CLI should not become a hidden second planner.

---

# 3. A useful rule for CLI membership

A capability belongs in the CLI when:

> **Multiple workflows need it, its mechanics should be deterministic, and there is no value in having the model reinvent those mechanics.**

Good CLI candidates:

```text
resolve Atlas record
search Atlas routes
resolve current Git revision
locate source anchor
read exact source range
compute Git diff
run known verification
parse structured test results
validate/store Engineering Episode
resolve scoped rule metadata
```

Poor CLI candidates:

```text
choose architecture
decide whether TDD applies
judge a reviewer finding
invent a test strategy
decide whether a lesson is reusable
decide whether a rule should be promoted
```

Those remain reasoning responsibilities.

---

# 4. Start with three commands

Do not begin with a large runtime.

The first useful CLI can be:

```text
atlas
├── context
├── source
└── doctor
```

These three commands already remove a large amount of skill/runtime coupling.

---

# 5. `atlas context`

This should initially wrap the existing Atlas query functionality.

Examples:

```bash
atlas context find "reconciliation"
atlas context resolve comp.reconciliation
atlas context impact comp.reconciliation
atlas context questions comp.reconciliation
```

The current lower-level implementation can continue using the same Python query library.

The CLI is primarily providing a stable public contract.

Possible JSON result:

```json
{
  "record": "comp.reconciliation",
  "status": "curated",
  "trust": "authoritative",
  "page": "_curated/components/data/reconciliation.md",
  "related": [
    "flow.daily-reconciliation",
    "schema.reconciliation-result"
  ]
}
```

The CLI output is routing/evidence metadata.

The parent skill still decides what it means.

---

# 6. `atlas source`

This is probably the strongest early justification for a CLI.

The source-routing design aims to take an Atlas semantic boundary and return the smallest useful source slice.

Example:

```bash
atlas source locate \
  --record comp.reconciliation \
  --intent "active row validation"
```

Possible output:

```json
{
  "repository": "repo.reconciliation",
  "revision": "4ae781...",
  "routes": [
    {
      "path": "src/main/java/.../ClientValidator.java",
      "kind": "symbol",
      "anchor": "ClientValidator.validateActiveRecord",
      "start_line": 42,
      "end_line": 79,
      "role": "business-rule",
      "basis": "atlas-evidence"
    }
  ]
}
```

Then:

```bash
atlas source read \
  --path src/main/java/.../ClientValidator.java \
  --start 42 \
  --end 79
```

This gives the model a precise, context-efficient read interface.

The source-routing ladder remains:

```text
exact source anchor
      ↓
exact symbol/section/object
      ↓
adjacent local section
      ↓
whole file
      ↓
repository_path/source_root search
      ↓
broader repository search
```

The model should consume only the result required for the current claim.

---

# 7. `atlas doctor`

A small diagnostic command is useful because many Atlas failures are environmental rather than semantic.

Example:

```bash
atlas doctor
```

It could verify:

- Atlas root resolution;
- `atlas-package.json`;
- Atlas schema/runtime compatibility;
- product repository detection;
- product Git revision;
- whether the configured product boundary is available;
- optional dependencies;
- source-route cache state;
- whether required commands are executable.

Example output:

```json
{
  "atlas_root": {
    "status": "ok",
    "path": "..."
  },
  "product_repo": {
    "status": "ok",
    "revision": "abc123..."
  },
  "source_routes": {
    "status": "stale",
    "indexed_revision": "def456..."
  }
}
```

This avoids embedding environment-recovery logic into every skill.

---

# 8. Add `atlas standards` after the core runtime proves useful

A later command can provide scoped standards/rule resolution.

Example:

```bash
atlas standards applicable \
  --change .atlas/change.json
```

Possible output:

```json
{
  "required": [
    {
      "id": "standard.java",
      "reason": "Java production source affected"
    },
    {
      "id": "standard.testing.shift-left",
      "reason": "production behaviour changes"
    }
  ],
  "conditional": [
    {
      "id": "standard.data.pii",
      "reason": "classified fields may be affected"
    }
  ],
  "not_applicable": [
    {
      "id": "standard.aws.lambda",
      "reason": "no Lambda boundary affected"
    }
  ]
}
```

The important distinction remains:

```text
STANDARD
authoritative human/team policy
        │
        ▼
RULE
agent-facing executable projection
```

The CLI can resolve known relationships and scopes.

It should not invent policy.

The engineering workflow remains responsible for interpreting whether unresolved standards need clarification or authority.

---

# 9. Verification can eventually get a normalized interface

Later:

```bash
atlas verify plan
atlas verify run
```

Example:

```json
{
  "checks": [
    {
      "id": "unit-tests",
      "command": "./gradlew test",
      "status": "passed"
    },
    {
      "id": "shift-left",
      "status": "required",
      "evidence": "..."
    }
  ]
}
```

However, Atlas should not wrap every build system just to appear unified.

The CLI should orchestrate existing project-native tooling when normalization provides value.

Examples:

```text
Gradle remains Gradle.
Maven remains Maven.
npm remains npm.
GitLab remains GitLab.
XRay remains XRay.
```

Atlas can provide a common evidence/result envelope without replacing these tools.

---

# 10. Review runtime is valuable but should come later

Qodo's CLI provides an independent review engine and structured result lifecycle.

Atlas could eventually expose:

```bash
atlas review start \
  --change-contract .atlas/change.json \
  --base origin/main

atlas review status <operation-id>
atlas review findings <operation-id>
```

The implementation underneath might later be:

- a fresh Claude subagent;
- another model;
- a bank-approved internal review service;
- static analysis;
- several specialist reviewers.

The engineering-flow skill should receive a stable finding format regardless of implementation.

Example:

```json
{
  "findings": [
    {
      "id": "R1",
      "severity": "major",
      "category": "correctness",
      "location": {
        "path": "src/.../ClientService.java",
        "start_line": 84,
        "end_line": 92
      },
      "issue": "Multiple active SCD rows may be created",
      "evidence": [],
      "required_outcome": "Preserve one-active-row invariant"
    }
  ]
}
```

Do not build this first.

Prove the lighter context/source/runtime interfaces before creating a review platform.

---

# 11. Episode handling is a good CLI responsibility

The engineering workflow should produce structured Engineering Episode data.

The CLI can validate and store/queue it.

Conceptually:

```bash
atlas episode validate --input .atlas/episode.json
atlas episode complete --input .atlas/episode.json
```

or a single:

```bash
atlas episode complete --input .atlas/run.json
```

The CLI's responsibilities:

- schema validation;
- revision metadata;
- deterministic IDs;
- storage/routing mechanics;
- rejection of malformed episodes.

The CLI should not decide whether the episode contains a reusable lesson.

That remains:

```text
Engineering Episode
        ↓
Adaptation Router
```

---

# 12. Do not put workflow decisions into the CLI

Avoid implementing logic such as:

```python
if change_type == "feature":
    use_tdd = True

if diff_size > 500:
    call_architect = True
```

This would duplicate the workflow across:

```text
SKILL.md
+
Python
```

and the two would eventually drift.

The skill/agent layer should make context-sensitive engineering decisions.

The CLI executes stable operations and returns structured evidence.

---

# 13. Recommended internal architecture

Atlas is already Python-heavy, so Python is the sensible initial implementation.

There is no demonstrated performance problem that justifies Go or Rust.

A possible structure:

```text
atlas/
├── cli/
│   ├── context.py
│   ├── source.py
│   ├── doctor.py
│   ├── standards.py
│   ├── verify.py
│   └── episode.py
│
├── core/
│   ├── query.py
│   ├── source_routes.py
│   ├── runtime.py
│   ├── standards.py
│   ├── verification.py
│   └── episodes.py
│
└── __main__.py
```

Existing script logic should be refactored toward reusable `core` functions rather than rewritten.

Then:

```bash
atlas context ...
```

is a thin adapter over:

```python
core.query...
```

---

# 14. CLI first, MCP later

The strongest long-term shape is likely:

```text
                 atlas-core
                     │
             ┌───────┴────────┐
             ▼                ▼
          Atlas CLI        Atlas MCP
             │                │
        shell agents      MCP-native hosts
```

Both adapters must call the same core implementation.

Do not implement CLI and MCP behaviour independently.

Example core functions:

```python
resolve_context(...)
locate_source(...)
resolve_standards(...)
run_verification(...)
record_episode(...)
```

Then the adapters become:

```text
atlas context find
        │
        └── resolve_context(...)

MCP atlas_context_find
        │
        └── resolve_context(...)
```

This makes Atlas portable without duplicating domain logic.

---

# 15. Why not build MCP first?

MCP may eventually be useful, especially when several agent hosts need Atlas capabilities.

But CLI is the lower-cost first abstraction because:

- Atlas already has Python scripts;
- Claude Code and similar hosts can invoke local commands;
- it is easy to inspect and debug;
- output can be JSON;
- it adds little infrastructure;
- the same core can later power MCP.

Build MCP when there is demonstrated value such as:

- several hosts need identical capabilities;
- local command integration becomes awkward;
- long-running services are needed;
- controlled remote access is required;
- tool schemas improve discoverability materially.

Do not build an MCP server solely because Qodo has one.

---

# 16. How this fits the Atlas Engineering Toolbox

The engineering design becomes:

```text
                         USER TASK
                            │
                            ▼
                    engineering-flow
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
          CONTEXT       STANDARDS     CHANGE INTAKE
              │             │             │
              ▼             ▼             ▼
         atlas CLI      atlas CLI        Change
        context/source   standards       Contract
              │             │             │
              └─────────────┼─────────────┘
                            ▼
                         DESIGN
                         if needed
                            │
                            ▼
                   VERTICAL-SLICE PLAN
                            │
                            ▼
                     RED → GREEN → REFACTOR
                            │
                     coherent milestone?
                          /       \
                        no         yes
                        │           │
                        │           ▼
                        │      FAST REVIEW
                        │           │
                        └─────┬─────┘
                              ▼
                         NEXT SLICE
                              │
                              ▼
                       FULL VERIFICATION
                              │
                              ▼
                   INDEPENDENT FINAL REVIEW
                              │
                         findings?
                         /       \
                       no         yes
                       │           │
                       │           ▼
                       │     FINDING RESOLVER
                       │           │
                       │        VERIFY
                       │           │
                       │        RE-REVIEW
                       │           │
                       └─────┬─────┘
                             ▼
                           PR
                             │
                             ▼
                          DEPLOY
                             │
                             ▼
                    ENGINEERING EPISODE
                             │
                             ▼
                    ADAPTATION ROUTER
```

The CLI supports the workflow.

It does not become the workflow.

---

# 17. Relationship to Qodo's Toolbox

The Qodo patterns worth reusing are architectural rather than product-specific.

## Complete skills own the workflow

Qodo's public skill architecture keeps complete reviewed workflows in its skills rather than dynamically fetching task-time playbooks from the CLI.

Atlas should follow the same principle.

```text
PLUGIN / SKILL
contains HOW

ATLAS / SOURCE / RUNTIME
contain WHAT + deterministic operations
```

Do not make `engineering-flow` a thin loader that fetches its basic workflow from the CLI.

## CLI owns runtime capability access

Qodo's CLI provides runtime access to managed tools, review, and standards APIs.

Atlas does not need all of those immediately.

The analogous useful boundary is that the Atlas CLI provides stable access to:

- Atlas context;
- exact source routing;
- scoped standards/rules;
- verification evidence;
- episode mechanics;
- eventually review execution.

## Canonical workflow, generated host projections

Qodo authors workflows once and generates provider-specific packaging.

Atlas should eventually use the same pattern.

Conceptually:

```text
engineering/
  canonical/
    skills/
    agents/
    rules/

distribution/
  claude/
  codex/
  ...
```

Provider packages should not become independently maintained copies.

---

# 18. Security and administration boundary

Another useful Qodo idea is separating normal engineering capabilities from standards administration.

For Atlas:

```text
engineering-core
```

could expose:

```text
engineering-flow
engineering-context
engineering-standards-read
engineering-tdd
engineering-verify
engineering-review
engineering-resolve
```

while:

```text
engineering-admin
```

could contain:

```text
manage-standards
approve-rule
retire-rule
promote-adaptation
manage-skill
evaluate-rule
```

This is particularly useful in a bank environment because installation of engineering tooling should not automatically grant authority to change organisational standards or activate learned behaviour.

---

# 19. Keep write authority explicit

The CLI must expose a clear distinction between:

```text
READ / RESOLVE / VERIFY
```

and:

```text
WRITE / PROMOTE / ACTIVATE
```

Read operations can normally be used by workflow skills within the user's permitted environment.

Durable mutations such as:

- updating curated Atlas knowledge;
- promoting a rule;
- changing a standard;
- activating an adaptation;
- modifying shared runtime configuration;

must continue to use explicit Atlas approval/governance.

A CLI must not become a way to bypass those controls.

---

# 20. Recommended implementation sequence

Do not build the complete toolbox at once.

Recommended sequence:

```text
1. Refactor existing scripts toward reusable core functions
      ↓
2. Add CLI entrypoint: atlas
      ↓
3. Implement atlas doctor
      ↓
4. Implement atlas context
      ↓
5. Implement atlas source
      ↓
6. Move relevant skills to stable CLI contracts
      ↓
7. Evaluate context/token/tool-call improvements
      ↓
8. Add atlas standards
      ↓
9. Add Engineering Episode validation/storage support
      ↓
10. Add normalized verification only where valuable
      ↓
11. Prototype independent review runtime
      ↓
12. Consider MCP adapter over the same atlas-core
```

Do not begin with:

- a daemon;
- a remote service;
- a full MCP server;
- a hosted review engine;
- a custom build/test framework;
- a large plugin manager.

The thin local CLI should prove the boundary first.

---

# 21. Initial MVP

A practical first milestone could be:

```bash
atlas doctor

atlas context find "client reconciliation"
atlas context resolve comp.client-reconciliation
atlas context impact comp.client-reconciliation

atlas source locate \
  --record comp.client-reconciliation \
  --intent "SCD2 active row validation"

atlas source read \
  --path ... \
  --start ... \
  --end ...
```

The engineering workflow should then use those commands rather than directly knowing Atlas's Python script paths.

The MVP should demonstrate:

1. less skill complexity;
2. fewer broad source reads;
3. fewer tool calls;
4. lower input-token consumption;
5. unchanged or improved answer correctness;
6. stable host-independent command contracts.

Atlas's evaluation harness should measure these rather than assuming the CLI is beneficial.

---

# 22. Success criteria

The CLI is successful if an engineering skill can say conceptually:

```text
Find the Atlas context for this change.
Locate the exact implementation evidence.
Resolve applicable standards.
Run the selected verification.
Record the resulting episode.
```

without knowing:

- Atlas internal file layout;
- Python module paths;
- individual script names;
- parser implementation;
- source-index storage;
- generated-map implementation.

The model still owns the engineering reasoning.

The runtime hides deterministic mechanics.

---

# Final Design Principle

The useful Qodo-inspired architecture for Atlas is:

> **Author engineering behaviour in inspectable skills. Put shared deterministic mechanics behind a stable Atlas runtime. Let both CLI and future MCP interfaces use the same core library. Do not move engineering judgement into the runtime.**

In compact form:

```text
Skills / Agents
= WHY + WHAT NEXT

Atlas CLI
= HOW TO PERFORM A DETERMINISTIC OPERATION

Atlas / Source / Git / CI
= EVIDENCE AND STATE
```

The CLI is therefore not strictly necessary to prove the engineering workflow.

It becomes worthwhile because Atlas is accumulating enough reusable deterministic capabilities that a stable runtime contract will reduce duplicated mechanics, context usage, and host-specific coupling.

The recommended path is to build it now as a **thin façade over existing Atlas code**, not as a Qodo-scale platform.

---

## Related Atlas Design Notes

This document complements:

- `docs/engineering-lifecycle-control-plane.md`
- `adaptive-engineering-learning-loop.md`
- `adaptation-router.md`
- `ponytail-lessons-for-atlas-engineering.md`
- `atlas-source-routing-minimal-context.md`

It should be treated as the runtime/tooling layer beneath the engineering control plane, not as a replacement for the workflow design.

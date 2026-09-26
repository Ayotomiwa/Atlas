# Atlas Source Routing for Minimal-Context Fallback

## Context

This design was recomputed against the current `main` branch of Atlas.

The original idea remains valuable: when Claude needs to fall back from Atlas knowledge to product source, it should read the smallest relevant source slice rather than loading an entire document, source file, component folder, or repository.

However, the current Atlas architecture already solves more of this problem than earlier versions did.

Current Atlas now includes:

- a three-way runtime entrance: retained evidence, exact source boundary, or Atlas-first;
- bounded source fallback using the smallest useful source check;
- repository onboarding with breadth discovery followed by targeted architecture depth;
- per-component architecture capsules;
- exact source anchors;
- explicit stopping reasons;
- separation between durable Atlas knowledge and exact volatile source-authoritative values.

Therefore the right improvement is **not a new parallel repository-map knowledge system**.

The right improvement is:

> **Add a deterministic source-slice resolution layer underneath Atlas's existing source fallback.**

---

## 1. What Current Atlas Already Does

The current runtime routing model is conceptually:

```text
1. Retained evidence
2. Exact source boundary
3. Atlas first
```

For Atlas-first requests:

```text
curated Atlas
    ↓
answer-bearing routes
    ↓
coverage endpoint
    ↓
smallest bounded source check
```

Atlas also explicitly treats exact volatile values such as:

- commands;
- source code;
- configuration;
- infrastructure literals;

as source-authoritative rather than content that should routinely be copied into Atlas.

Repository onboarding now follows:

```text
PHASE 1
breadth discovery
        ↓
PHASE 2
targeted architecture depth
```

Every material component is expected to receive an architecture capsule covering:

- purpose and independent boundary;
- entrypoint or trigger;
- causal path;
- dependencies and state;
- infrastructure interactions;
- durable outputs/effects;
- failure or partial-completion behaviour;
- completion signals;
- exact source anchors;
- coverage limits;
- stopping reason.

This means Atlas already knows **which source boundary matters**.

The remaining problem is efficiently turning that knowledge into a minimal source read.

---

## 2. Revised Architecture

The improvement should extend the existing runtime rather than replace it.

```text
                         QUESTION
                            │
                            ▼
                    CURRENT ATLAS ROUTER
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        retained        exact-local    Atlas-first
        evidence          source
                                          │
                                          ▼
                                   curated knowledge
                                          │
                                    enough?
                                    /     \
                                  yes      no
                                   │        │
                                   ▼        ▼
                                answer   SOURCE ROUTER
                                            │
                                            ▼
                                    exact source anchor
                                            │
                                            ▼
                                      SOURCE SLICE
                                            │
                                      enough?
                                      /     \
                                    yes      no
                                     │        │
                                     ▼        ▼
                                  answer    expand
```

The semantic routing stays unchanged.

The new source-routing layer makes the existing fallback cheaper.

---

## 3. SourceRouteResolver

Introduce a deterministic capability conceptually named:

```text
SourceRouteResolver
```

Optionally backed by a generated:

```text
SourceRouteIndex
```

Responsibilities remain deliberately narrow.

### Atlas answers

> What matters?

### SourceRouteResolver answers

> Where exactly should I read?

### Product source answers

> What does the current implementation actually say?

The resulting flow is:

```text
QUESTION
   │
   ▼
ATLAS
"What matters?"
   │
   ▼
SOURCE ROUTER
"Where exactly?"
   │
   ▼
SOURCE SLICE
"What is actually implemented?"
   │
   ▼
ANSWER
```

The resolver is routing infrastructure, not semantic authority.

---

## 4. Exploit Existing Exact Anchors Before Building a Full Source Graph

Do not begin by indexing every symbol in a repository.

Use three routing levels:

```text
LEVEL 1
Exact anchors captured by Atlas/onboarding
        ↓
highest value

LEVEL 2
Component repository_paths / repository source_roots
        ↓
bounded structural lookup

LEVEL 3
Generated local source index
        ↓
only when the exact anchor is not already known
```

If onboarding already knows:

```text
comp.reconciliation
    ↓
ReconciliationService#compareActiveRecords
```

there is no value in searching 30,000 source symbols again.

The current onboarding work should seed source routing directly.

---

## 5. Formalise the Existing "Exact Source Anchor" Concept

Current Atlas requires exact source anchors, but the concept should become reusable and machine-readable.

A proposed shape:

```yaml
source_anchor:
  repository: repo.reconciliation
  revision: a17b93...

  path: src/main/java/.../ReconciliationService.java

  kind: symbol

  anchor:
    name: ReconciliationService.compareActiveRecords

  role: business-rule
```

When resolved against a product checkout:

```yaml
resolved:
  start_line: 86
  end_line: 141
  file_hash: abc123
```

Critical identity rule:

```text
symbol / heading / object
        =
stable locator intent

line range
        =
generated acceleration hint
```

Do not make line numbers the durable identity.

A comment inserted near the top of a file must not invalidate the logical route.

---

## 6. Source Anchor Kinds

The mechanism should support multiple source formats.

### Code symbol

```yaml
kind: symbol
path: ReconciliationService.java
anchor:
  name: ReconciliationService.compare
```

### Markdown/documentation heading

```yaml
kind: heading
path: architecture.md
anchor:
  name: SCD2 handling
```

### SQL object

```yaml
kind: sql-object
path: recon.sql
anchor:
  name: active_client_comparison
```

Possible SQL anchors may include:

- named CTE;
- view;
- MERGE;
- stored procedure;
- named query section.

### DDL object

```yaml
kind: ddl-object
path: client.sql
anchor:
  name: client_dimension
```

### Configuration key

```yaml
kind: config-key
path: application.yml
anchor:
  name: reconciliation.batch-size
```

### Infrastructure resource

```yaml
kind: infrastructure-resource
path: main.tf
anchor:
  name: aws_sfn_state_machine.reconciliation
```

### Test

```yaml
kind: test
path: ReconciliationServiceTest.java
anchor:
  name: shouldRejectMultipleActiveRows
```

The resolver turns each logical anchor into the smallest currently valid range.

---

## 7. Context Saving Through Exact Source Slices

The practical value is large-file avoidance.

Example documentation file:

```text
architecture.md
1,900 lines
```

Instead of reading all 1,900 lines:

```text
architecture.md
heading: SCD2 handling
resolved: lines 821–903
```

Claude reads approximately 83 lines.

Example source file:

```text
ReconciliationService.java
780 lines
```

Instead:

```text
compareActiveRecords()
lines 202–253
```

Only the relevant function enters model context.

This same mechanism applies to:

- Markdown;
- Java;
- TypeScript;
- SQL;
- DDL;
- YAML;
- Terraform;
- CloudFormation;
- tests;
- configuration.

---

## 8. Progressive Source Disclosure

Formalise fallback expansion as a ladder.

```text
1. Exact source anchor
       ↓
2. Exact symbol / heading / SQL object
       ↓
3. Adjacent local section
       ↓
4. Whole file
       ↓
5. repository_path / source_root search
       ↓
6. broader repository search
```

Stop as soon as the material claim is established.

This directly supports the existing source-analysis principle:

> Continue only while another known source route could materially change the claim, confidence, coverage, or stopping decision.

The retrieval mechanism should now enforce the same restraint.

---

## 9. The Model Should Never Load the Routing Index

Do not solve context bloat by creating another giant file for Claude to read.

Bad:

```text
source-index.json
50,000 entries

Claude reads/searches source-index.json
```

Better:

```text
Claude asks:
"Where is active-record validation implemented?"

            ↓

deterministic source resolver

            ↓

small result:

1. ClientValidator.validateActiveRecord
   ClientValidator.java:42–79
   basis: curated component evidence

2. ClientValidatorTest.shouldRejectTwoActiveRows
   ClientValidatorTest.java:71–103
   basis: linked test evidence
```

Claude then reads only those ranges.

The source-routing system exists specifically to reduce context.

---

## 10. Integrate With `atlas_query.py`

The current query interface already supports:

```text
resolve
find
route
context
questions
staging
neighbors
impact
```

Add a source-routing command conceptually like:

```text
source
```

Example:

```bash
python scripts/atlas_query.py source \
  comp.client-reconciliation \
  --query "active record validation" \
  --repo /path/to/product
```

Example output:

```json
{
  "record": "comp.client-reconciliation",
  "revision": "4ae781...",
  "routes": [
    {
      "path": "src/.../ClientValidator.java",
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

This respects the current Atlas runtime principle:

> Scripts resolve, traverse, compile, and validate; they do not decide what evidence means.

The parent workflow still decides:

- whether more evidence is needed;
- how a claim should be interpreted;
- whether another source route should be followed;
- what should be presented to the user.

---

## 11. Generated Routing Metadata, Not Curated Knowledge

The source-route layer must preserve Atlas's existing trust separation.

```text
_curated
→ reviewed semantic knowledge

_staging
→ non-authoritative evidence

_intake
→ operational processing state

generated maps
→ navigation aids

product source
→ executable/current truth

source-route index
→ generated navigation acceleration
```

A source route should be explicitly:

```text
generated
revision-bound
regeneratable
semantic authority: none
```

It may say:

> Read this symbol.

It may not assert:

> This symbol proves the business meaning.

That remains the job of source analysis plus Atlas knowledge/provenance rules.

---

## 12. Prefer a Local Revision-Bound Cache

A detailed structural source index is likely best stored as a local/regeneratable cache initially.

Conceptually:

```text
~/.atlas/cache/
    source/
        repo-client/
            4ae781....jsonl
```

The exact location is an implementation decision.

Useful characteristics:

- revision-specific;
- regeneratable;
- non-authoritative;
- potentially large;
- not reviewed by humans;
- meaningful only alongside the relevant source checkout.

If shared indexing later proves useful, CI could publish a revision-bound artifact.

Do not start with shared infrastructure unless local generation is measurably insufficient.

---

## 13. Generate High-Value Routes From Existing Onboarding Work

Do not perform another broad repository scan after onboarding.

Current onboarding already does:

```text
BREADTH
    ↓
important roots

TARGETED DEPTH
    ↓
important exact sources

ARCHITECTURE CAPSULE
    ↓
exact source anchors
```

Use the exact anchors generated during this process as source-route seeds.

```text
breadth packet
      │
      ▼
targeted depth
      │
      ├── semantic findings
      │      ↓
      │    staging
      │
      └── exact source anchors
             ↓
       source-route seeds
```

One analysis effort supports both:

- semantic Atlas knowledge;
- future low-context source fallback.

This aligns with the current rule not to restart broad discovery unnecessarily.

---

## 14. Incremental Maintenance

Source routes are revision-bound.

Suppose routes were generated for:

```text
revision A
```

and the product repository moves to:

```text
revision B
```

Use the changed paths:

```text
git diff A..B --name-only
```

Then:

```text
changed files
     ↓
invalidate routes for those paths
     ↓
re-resolve anchors in changed files
     ↓
retain untouched routes
```

Expected behaviour:

```text
symbol moved within same file
→ regenerate range

symbol renamed
→ anchor invalid
→ bounded local re-resolution

file moved
→ re-resolve using repository/component source boundary

cannot resolve
→ mark unresolved
→ fallback expands progressively
```

Never silently use a stale line range against a different revision.

---

## 15. Add Purpose/Role to Source Routes

Not every source anchor is equally useful for every question.

Possible roles:

```text
entrypoint
business-rule
transformation
persistence
external-call
configuration
schema-definition
deployment
failure-recovery
monitoring
test
documentation
```

Example:

Question:

> How is this Lambda deployed?

Prefer:

```text
role = deployment
```

rather than returning Java business methods.

Question:

> Why is this customer record excluded?

Prefer:

```text
role = business-rule
```

Role is routing metadata, not semantic authority.

---

## 16. Data and Schema Use Case

This mechanism strongly complements the recent Atlas data-semantic work.

Example:

```text
schema.client-dimension
```

Atlas provides reviewed semantic meaning.

If implementation verification is needed:

```text
schema.client-dimension
        │
        ▼
source routes
        │
        ├── schema-definition
        │   ddl/client.sql
        │   CREATE TABLE client_dimension
        │   relevant object only
        │
        ├── transformation
        │   ClientMapper.java
        │   mapQuantity()
        │
        └── historical-query
            client-volume.sql
            relevant CTE only
```

This avoids broad DDL/SQL/repository scans during ordinary data questions.

The same mechanism can support data onboarding after DDL and historical-query evidence has been reviewed and linked.

---

## 17. Do Not Build a Full Source Graph Yet

A richer graph may eventually include:

- imports;
- calls;
- references;
- co-edit relationships.

That remains potentially valuable.

However, given the current Atlas architecture, implement in this order:

```text
1. Formal source-anchor contract
       ↓
2. Exact source-slice resolver
       ↓
3. Generated local source-route cache
       ↓
4. Routing evaluation
       ↓
5. Measure remaining misses
       ↓
6. Only then consider call/import/co-edit graph
```

Exact anchors plus bounded structural lookup may solve most source fallback cheaply.

Do not build a graph before demonstrating that the simpler locator is insufficient.

---

## 18. Revised Atlas Architecture

```text
                           USER QUESTION
                                 │
                                 ▼
                        ATLAS RUNTIME ROUTER
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
   retained evidence      exact source boundary    Atlas first
                                                       │
                                                       ▼
                                             SEMANTIC KNOWLEDGE
                                             ─────────────────
                                             component
                                             flow
                                             schema
                                             concept
                                             infra
                                             standard
                                                       │
                                                 gap remains
                                                       │
                                                       ▼
                                             SOURCE ROUTE RESOLVER
                                             ─────────────────────
                                             exact evidence anchor
                                             component paths
                                             repository roots
                                             local structural index
                                                       │
                                                       ▼
                                                 SOURCE SLICE
                                             ─────────────────────
                                             symbol
                                             heading
                                             SQL object
                                             DDL object
                                             config key
                                             IaC resource
                                                       │
                                                       ▼
                                                SOURCE ANALYSIS
                                                       │
                                                       ▼
                                                    ANSWER
```

This preserves Atlas's current architecture while adding context-efficient source fallback.

---

## 19. Recommended Initial Implementation

Start with four changes.

### 1. Define a machine-readable `source-anchor` contract

Formalise the exact source anchors that onboarding already requires.

### 2. Implement `SourceRouteResolver`

Resolve:

```text
repository + revision + path + logical anchor
```

into:

```text
exact current source range
```

### 3. Add `atlas_query.py source`

Return a very small set of source routes without interpreting their meaning.

### 4. Extend routing evaluation

Add scenarios that verify fallback reads:

```text
exact relevant slice
```

instead of:

```text
whole file / broad repository
```

Measure:

- bytes read;
- input tokens;
- tool calls;
- number of source files opened;
- answer correctness;
- fallback completeness.

The existing Atlas evaluation framework can then determine whether source routing produces real efficiency improvements.

---

## 20. Design Principle

The resulting source-retrieval philosophy is:

> **Atlas uses semantic knowledge to choose the evidence boundary, source-routing metadata to choose the smallest source slice within that boundary, and product source itself to establish executable truth.**

Or more compactly:

```text
Atlas       → What matters?
SourceRoute → Where exactly?
Source      → What is actually true?
```

The important discovery is that source fallback does not need more semantic knowledge.

It needs **better precision when retrieving source evidence**.

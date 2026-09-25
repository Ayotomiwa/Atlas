# Atlas Data Knowledge Onboarding from Repositories, DDLs, and Historical SQL

## Goal

Bootstrap Atlas data knowledge from evidence already available in:

- product/ETL repositories;
- DDLs and migrations;
- historical SQL/query archives;
- lead and SME operational knowledge.

The objective is not to automatically convert source files into authoritative documentation.

The objective is to:

1. extract what the sources can establish;
2. identify ambiguity, conflicts, and gaps;
3. present a compact evidence-backed understanding to leads/SMEs;
4. ask only the questions that source evidence cannot safely answer;
5. route approved reusable knowledge through normal Atlas staging and curation.

---

## 1. Overall Workflow

```text
PRODUCT REPOSITORY + DDLs + HISTORICAL SQL
                       ↓
             Inventory and snapshot
                       ↓
            Extract technical evidence
                       ↓
          Reconcile sources and conflicts
                       ↓
             Draft Atlas understanding
                       ↓
           Generate targeted questions
                       ↓
             Lead review / correction
                       ↓
           Preview the knowledge changes
                       ↓
          Approved staging and curation
                       ↓
       Test Atlas with realistic data requests
```

There are two different validation stages:

### Knowledge review

An appropriate expert confirms or corrects the extracted meaning.

### Behavioural evaluation

Atlas is tested against realistic data requests to verify that the reviewed knowledge actually supports correct interpretation and query planning.

Both are required.

---

## 2. Evidence Roles by Source

Each source should have a defined evidentiary role.

| Source | What to extract | What not to assume |
|---|---|---|
| DDLs and migrations | tables, columns, data types, constraints, comments, physical changes | that the file matches the deployed database or that names establish business meaning |
| ETL/application repository | transformations, mappings, filters, deduplication, update logic, schedule/completion behaviour | that implemented behaviour is necessarily intended policy |
| Historical SQL | observed joins, aggregations, filters, aliases, date choices, recurring request shapes | that saved SQL is correct, current, or generally approved |
| Lead/SME knowledge | meaning, purpose, exceptions, operational caveats, ownership, rationale | that one expert's statement applies globally across teams/environments |

Source classifications should remain visible.

Do not collapse:

```text
observed implementation
documented intent
historical usage
expert-confirmed meaning
organisational policy
```

into one undifferentiated "truth".

---

## 3. Snapshot and Scope the Source Before Interpretation

Before extracting meaning, preserve the identity and scope of the source.

Useful metadata includes:

- repository revision;
- file path and fingerprint;
- migration or DDL version;
- known environment;
- query creation/modification period where available;
- owner/team;
- whether the source appears current, historical, or unknown.

Example:

```text
This join occurs in a saved investigation query from an older schema version.
```

is a useful observation.

It is not equivalent to:

```text
This is the approved current join for the dataset.
```

A newer file should not automatically overwrite an older interpretation when they may describe different periods or environments.

---

## 4. DDL Ingestion

Use DDLs to establish technical structure.

Extract:

- schema/table names;
- column names;
- data types;
- declared keys;
- constraints;
- comments/descriptions;
- partition/distribution/sort information where relevant;
- views;
- migrations/renames;
- relationships explicitly declared by the platform.

Do not infer business meaning from names alone.

Example:

```text
column name: volume
```

does not establish whether the value is:

- monetary amount;
- physical quantity;
- transaction count;
- another domain-specific measure.

### Database-specific caveat

For platforms where declared constraints are informational rather than enforced, record that distinction.

For example, if a platform permits unenforced key declarations, Atlas should distinguish:

```text
DDL declares uniqueness
```

from:

```text
runtime data has been verified unique
```

and:

```text
ETL logic enforces uniqueness
```

These are different claims.

---

## 5. Repository / ETL Source Ingestion

Application and ETL code can establish how data currently moves and transforms.

Extract evidence such as:

- source → target field mappings;
- calculations;
- filters;
- deduplication logic;
- null handling;
- SCD/versioning behaviour;
- current/latest-record selection;
- merge/upsert logic;
- input/output datasets;
- scheduling/triggers;
- data-completion conditions;
- error/dead-letter paths;
- known runtime dependencies.

Keep behaviour separate from intent.

Example:

```text
Observed:
The ETL filters status = 'ACTIVE'.

Unknown:
Whether ACTIVE is the approved business definition
or merely the current implementation.
```

Where intent is not supported, generate a question instead of converting code into business policy.

---

## 6. Historical SQL as Evidence

Historical SQL is one of the strongest sources for understanding how engineers and consumers actually use the data.

Analyse saved queries for:

- tables commonly queried together;
- join keys;
- join direction/cardinality assumptions;
- filters;
- date fields;
- temporal/latest-record conditions;
- aggregation expressions;
- aliases;
- derived measures;
- exclusions;
- grouping dimensions;
- query purpose where names/comments provide evidence.

### Query families

Cluster materially similar queries into query families rather than reviewing every SQL file separately.

Example:

```text
Customer monthly quantity
├── query A
├── query B
└── query C
```

Preserve meaningful differences.

A changed date field, status filter, or temporal join may represent an entirely different business question.

### Historical SQL generates hypotheses

Do not promote:

```text
Observed join
```

directly into:

```text
Approved join
```

Similarly:

```text
Frequently used filter
    ≠ universal business rule

Alias named "amount"
    ≠ proof the field is monetary
```

Use the archive to locate what needs review.

---

## 7. Deduplicate Before Using Frequency

Historical archives often contain copied SQL.

Ten saved copies of the same query should not become ten independent confirmations.

Before using frequency as evidence:

- normalize obvious formatting differences;
- fingerprint materially equivalent queries;
- group copies;
- preserve lineage where available;
- distinguish independent query patterns from repeated copies.

Frequency can prioritize review but should not establish authority.

---

## 8. Produce an Evidence-Backed Understanding Packet

Do not immediately generate hundreds of polished curated pages.

For each coherent data area, generate a compact review packet.

Example:

| Section | Example |
|---|---|
| Established from source | ETL maps `source.quantity` to `target.volume` |
| Observed usage | saved queries aggregate `target.volume` by customer |
| Hypothesis | field may represent a quantity measure |
| Conflict | another query labels it `total_amount` |
| Unknown | units, exclusions, valid aggregation scope |
| Questions | targeted clarifications needed |

The packet must distinguish:

- direct evidence;
- inference;
- conflict;
- missing coverage;
- reviewer-confirmed knowledge.

---

## 9. Readiness Should Be Topic-Specific

Do not assign one broad confidence badge to an entire table.

Track readiness by dimension.

Example:

```text
Physical structure: verified against selected source
Business meaning: unresolved
Grain: lead-confirmed
Temporal rules: conflicting
Join behaviour: not yet tested
Quality caveats: partial
```

This allows technical knowledge to remain useful while semantic knowledge is still being reviewed.

---

## 10. Expert Review Skill

Create a skill conceptually named:

```text
atlas-review-data-knowledge
```

Purpose:

> Review a bounded set of Atlas data findings with an appropriate expert, resolve high-impact uncertainties, capture missing operational knowledge, and prepare evidence-backed corrections for normal Atlas persistence and curation.

The interaction should feel like:

> "Review Atlas's understanding"

rather than:

> "Take a quiz."

The expert is validating Atlas, not being examined.

---

## 11. Question Types

Use several kinds of targeted questions.

### A. Meaning questions

Example:

```text
Topic:
trade_fact.volume

Observed:
One saved query sums this field and labels the result total_amount.
Another labels the same aggregation total_volume.

Question:
What does this field measure, and in what units?

Possible responses:
- monetary value
- units/quantity
- transaction count
- context dependent
- something else
- unsure / refer to another owner
```

Allow uncertainty.

Do not force a definition.

---

### B. Conflict questions

Example:

```text
Observed:
Two query families join the same dimension differently.

Query family A:
current active dimension row

Query family B:
dimension row effective on transaction date

Question:
Do these answer different business questions,
or is one pattern obsolete?
```

Both may be valid under different contexts.

The goal is not to pick one unless evidence supports that choice.

---

### C. Operational knowledge questions

These should capture what code and DDL often fail to explain.

Examples:

- What can make this dataset look valid but produce a misleading answer?
- How do you know a daily load is complete enough to query?
- Are there known late-arriving records?
- Do backfills temporarily duplicate rows?
- Is there a period during which totals should not be trusted?
- Which field should be used for historical reporting?
- Which joins are known to multiply rows?

Prefer observable completion/readiness conditions over vague time-based assumptions.

---

### D. Scenario questions

Use synthetic examples to test whether a definition is precise.

Example:

```text
An order contains 3 units priced at £20 each.

A requester asks for "volume".

In this context should Atlas return:
- 3
- £60
- transaction count 1
- ask for clarification
```

Scenario questions are particularly useful for:

- temporal data;
- cancellations;
- corrections;
- SCD records;
- multiple business meanings;
- join cardinality.

---

## 12. Ask Only Material Questions

Lead time is expensive.

Prioritize questions where the answer could materially change:

- selected dataset;
- selected field;
- aggregation;
- row grain;
- currency/unit;
- date semantics;
- join cardinality;
- temporal/latest-record rule;
- population/exclusion;
- readiness/quality interpretation.

Lower-priority documentation gaps can remain unknown.

A useful review session should contain a small batch of high-value questions about one data area rather than a giant warehouse questionnaire.

---

## 13. Ask the Right Expert

Do not treat one lead as authority for all meanings.

Distinguish:

```text
Confirmed for our dataset by operational owner
```

from:

```text
Confirmed terminology used by requesting team
```

Cross-team terminology may require the other team to confirm its own language.

The review workflow should preserve:

- reviewer identity/role;
- review date;
- dataset/team scope;
- environment/version scope;
- exceptions;
- remaining uncertainty.

---

## 14. Expert Confirmation Does Not Erase Conflicting Evidence

Example:

```text
Lead says:
Cancelled records should be excluded.

Current SQL shows:
No cancellation filter.
```

Atlas should record:

```text
Intended/reviewed rule:
Cancelled records excluded.

Observed implementation/query:
No cancellation filter.

Status:
Conflict requiring investigation.
```

Do not silently rewrite implementation history to match the expert statement.

Atlas should preserve disagreement until the underlying issue is settled.

---

## 15. Proposed Skills

### `atlas-onboard-data`

A data-focused onboarding entry point that reuses Atlas source snapshot, provenance, handoff, staging, validation, and review machinery.

Additional responsibilities:

- inventory DDLs;
- inspect ETL/repository mappings;
- analyse historical SQL;
- cluster query families;
- draft understanding packets;
- identify high-value semantic gaps;
- prepare review questions.

It must report the exact source scope it covered.

It must not claim full repository onboarding if only the data boundary was inspected.

### `atlas-review-data-knowledge`

An expert-review interaction that:

- selects highest-value unresolved questions;
- presents source evidence and conflicts;
- captures expert corrections;
- preserves scope and attribution;
- prepares a persistence preview;
- hands approved changes into existing Atlas staging/curation.

Read-only analysts may investigate source, but the parent skill should own the human interaction.

---

## 16. Do Not Execute Historical SQL During Ingestion by Default

Historical SQL should initially be treated as source material.

Do not automatically run it.

Reasons include:

- unknown environment assumptions;
- outdated schemas;
- expensive queries;
- sensitive data access;
- write-capable SQL;
- unsafe functions;
- stale semantics.

Execution, where needed, should be an explicitly controlled validation step in an authorised environment.

---

## 17. Persist Reusable Knowledge, Not Raw Archives

Do not copy every DDL and SQL file into curated Atlas.

Persist:

- durable business meaning;
- schema/data-asset identity;
- reviewed important fields;
- grain;
- keys;
- temporal rules;
- approved joins;
- quality/operational caveats;
- reusable query patterns;
- evidence references.

Keep detailed extracted inventories and duplicate query archives outside the curated semantic layer.

The source remains the source.

Atlas stores the reusable reviewed understanding.

---

## 18. Demand-Driven Semantic Onboarding

Do not manually document every table before Atlas becomes useful.

Use two streams.

### Automated technical onboarding

```text
DDL/catalog/repository
     ↓
tables
columns
types
mappings
query patterns
source evidence
```

This produces evidence and candidate understanding.

### Demand-driven semantic onboarding

```text
real data requests
      ↓
which concepts/tables repeatedly block engineers?
      ↓
prioritize those for expert review
```

If 80% of requests depend on 20 high-value datasets, understand those extremely well before documenting rarely used tables.

---

## 19. Pilot Scope

Start with one coherent data area.

Include:

- relevant repo boundary;
- DDLs;
- ETL/transformation source;
- representative historical SQL;
- one lead/SME who knows the area;
- a set of realistic historical requests.

Complete the path end-to-end before expanding.

---

## 20. Evaluation

After extraction and expert review, test Atlas against realistic requests.

Useful tests:

| Test | Expected behaviour |
|---|---|
| Ambiguous measure | Ask a necessary clarification |
| Known terminology | Resolve using correct team/dataset context |
| Historical request | Select correct temporal interpretation |
| Risky join | Surface grain/cardinality conditions |
| Incomplete dataset | Surface operational caveat |
| Unknown concept | Report coverage gap instead of guessing |

Keep some reviewed historical requests out of the initial extraction/review corpus.

These become holdout evaluation cases.

The goal is not memorization.

The goal is successful semantic generalisation.

---

## 21. Success Metric

Do not measure success by:

```text
number of Atlas pages created
```

Measure whether:

```text
another engineer
        ↓
receives a realistic data request
        ↓
uses Atlas
        ↓
correctly interprets terminology
        ↓
finds the right dataset
        ↓
understands grain/time/join caveats
        ↓
produces the right query plan
        ↓
without interrupting a lead
```

The target outcome is fewer expert interruptions with no loss of semantic correctness.

---

## 22. Relationship to Existing Atlas Governance

This design should reuse:

- source snapshots and revision binding;
- staging as non-authoritative evidence;
- business-concept governance;
- schema-info/data-asset governance;
- conflict preservation;
- open questions;
- one preview / one approval;
- independent curation review;
- bounded source fallback;
- provenance and coverage rules.

It should not create a parallel knowledge lifecycle.

The new capability is primarily a **data-specific evidence extraction and expert-review workflow** built on top of Atlas's existing governance model.

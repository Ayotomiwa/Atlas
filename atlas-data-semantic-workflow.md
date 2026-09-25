# Atlas Data Semantic Workflow

## Goal

Use Atlas as the semantic translation layer between a human data request and the physical data needed to answer it.

The primary problem is not SQL generation. The expensive part is translating ambiguous business language into the correct meaning, dataset, grain, time semantics, join path, filters, and aggregation.

Example:

```text
Requester says "volume"

Possible meanings:
- monetary amount
- quantity / units
- transaction count
- domain-specific measure
```

Atlas should resolve the meaning from reviewed context before any SQL is generated.

---

## 1. High-Level Architecture

```text
┌───────────────────────────────────────┐
│ REQUEST                               │
│ "Give me volume by customer..."       │
└──────────────────┬────────────────────┘
                   ▼
┌───────────────────────────────────────┐
│ SEMANTIC LAYER — ATLAS                │
│                                       │
│ What does "volume" mean?              │
│ What does "customer" mean?            │
│ Which team's terminology is this?     │
│ What inclusion/exclusion applies?     │
└──────────────────┬────────────────────┘
                   ▼
┌───────────────────────────────────────┐
│ DATA CONTRACT LAYER — ATLAS           │
│                                       │
│ Which dataset represents it?          │
│ Which field?                          │
│ What grain?                           │
│ Which date?                           │
│ Which joins are valid?                │
└──────────────────┬────────────────────┘
                   ▼
┌───────────────────────────────────────┐
│ QUERY LAYER                           │
│                                       │
│ approved joins                        │
│ reusable query patterns               │
│ SQL generation                        │
└──────────────────┬────────────────────┘
                   ▼
┌───────────────────────────────────────┐
│ EXECUTION / RESPONSE                  │
│                                       │
│ validate → human review → execute     │
│ → return/draft response               │
└───────────────────────────────────────┘
```

Atlas remains the knowledge layer. Execution and workflow automation should consume Atlas rather than be embedded into Atlas itself.

---

## 2. Existing Atlas Types Already Cover Most of the Model

The current Atlas taxonomy already includes:

- `business-concept`
- `schema-info`
- embedded `data-asset`
- reserved `join-path`
- reserved `query-pattern`

This means the data-request workflow should extend the existing model rather than create a second metadata system.

### Business concepts

Use `business-concept` for durable meaning:

- business entities;
- measures;
- classifications;
- inclusion/exclusion rules;
- terms with context-dependent meaning;
- terminology that repeatedly causes ambiguity.

### Schema information and data assets

Use `schema-info` and `data-asset` for physical representation:

- table / dataset / event / API identity;
- grain;
- keys;
- temporal behaviour;
- important fields;
- physical platform;
- compatibility;
- approved joins;
- quality limitations.

The semantic and physical layers should remain distinct.

---

## 3. Do Not Treat Ambiguous Terms as Global Aliases

A term such as `volume` may have different meanings across teams.

Example:

```text
                       "volume"
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          Payments     Inventory      Trading
              │            │            │
              ▼            ▼            ▼
         AMOUNT        QUANTITY     TRADE COUNT
```

Do not silently add `volume` as a global alias for one concept.

The resolution must preserve context.

Conceptually:

```yaml
term: volume

contexts:
  - team: payments
    maps_to: concept.transaction.amount

  - team: inventory
    maps_to: concept.item.quantity

  - team: trading
    maps_to: concept.trade.count
```

The current business-concept `Terminology and variants` section can hold this initially.

Only make contextual terminology machine-readable once repeated use proves the need.

---

## 4. What Atlas Ultimately Needs to Know for a Data Request

Resolving a concept is not enough.

Atlas needs enough reviewed information to answer:

```text
What is it?
↓
Where is it represented?
↓
At what grain?
↓
Which time dimension applies?
↓
How is it aggregated?
↓
What population does it cover?
↓
What joins are valid?
↓
What quality/operational caveats apply?
```

Example:

```text
concept:
    Customer order quantity

implementation:
    asset.orders

field:
    item_qty

grain:
    one row per order line

time:
    order_created_date

aggregation:
    SUM(item_qty)

excludes:
    cancelled orders

joins:
    orders.customer_id
        →
    customers.customer_id
```

The business concept explains the meaning.

The schema/data-asset record explains how that meaning is represented.

---

## 5. Join Knowledge Is First-Class Data Knowledge

A major source of data-team tribal knowledge is not the table definition, but how tables may safely be joined.

Examples:

- a technically valid join duplicates rows;
- a dimension must be filtered to the active record;
- a historical request must use the version effective on the transaction date;
- a field that looks like a key is not unique;
- two tables use different identifiers for the same business entity.

The existing schema-info page can record reviewed joins initially.

When join knowledge becomes reusable and independently addressable, activate the reserved `join-path` type.

Example shape:

```yaml
id: join.customer-orders

from:
  asset.customer

to:
  asset.order

keys:
  - customer.customer_id
  - order.customer_id

cardinality:
  one-to-many

conditions:
  - customer.active = true

temporal_rule:
  latest customer version as of order date
```

Do not infer approved joins merely because two fields share a name.

---

## 6. Query Patterns Are the Bridge to Repeated Productivity

Historical and future common requests should eventually be represented as reusable query patterns.

Example:

```text
query.customer-volume-by-month
```

could describe:

```text
Inputs:
- start_date
- end_date
- customer_id optional

Concepts:
- customer
- order quantity

Assets:
- customer
- order

Join:
- join.customer-orders

Output grain:
customer × calendar month

Aggregation:
SUM(item_qty)

Required filters:
cancelled = false
```

Then the workflow becomes:

```text
human request
     ↓
semantic interpretation
     ↓
query pattern found?
    /          \
 yes            no
  │              │
  ▼              ▼
instantiate     compose from
pattern         Atlas knowledge
```

Do not activate `query-pattern` as a fully governed type until repeated use justifies it. Existing schema-info records can hold initial query knowledge.

---

## 7. Data Request Contract

Every request should become ephemeral structured working state.

Example:

```yaml
request:
  id: ...
  requester_team: inventory
  raw_intent: >
    Can you give me customer volume for August?

concepts:
  customer:
    status: resolved
    atlas_id: concept.customer

  volume:
    status: ambiguous
    candidates:
      - concept.order.quantity
      - concept.transaction.amount

dimensions:
  - customer

time:
  period: August
  date_semantics: unresolved

grain:
  requested: unknown

output:
  format: unknown

purpose:
  value: not-specified

ambiguities:
  - meaning of volume
  - which August/year
  - customer-level vs order-level output
```

This is the data-request equivalent of the Engineering Change Contract.

It should not itself become curated Atlas knowledge.

---

## 8. Semantic Resolution Rules

Each requested term should be resolved with explainable evidence.

Example:

```text
Term: volume

Candidate 1:
Order quantity

Evidence:
- requester team = Inventory
- reviewed local terminology maps "volume" to item quantity
- requested dimension = product

Candidate 2:
Monetary amount

Evidence:
- term exists in Finance vocabulary
- no supporting request context

Resolution:
Order quantity

Confidence:
reviewed-context match
```

If more than one meaning remains materially plausible:

```text
DO NOT GENERATE SQL YET
```

Ask the smallest clarifying question.

Example:

> When you say "volume", do you mean number of units or monetary value?

Ambiguity must remain visible rather than being resolved by model confidence alone.

---

## 9. Data Request Workflow

For Outlook or another request channel:

```text
                     NEW REQUEST
                            │
                            ▼
                  DATA REQUEST CLASSIFIER
                            │
                   data request?
                     /          \
                   no            yes
                   │              │
                ignore            ▼
                         EXTRACT REQUEST CONTRACT
                                  │
                                  ▼
                         RESOLVE WITH ATLAS
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
                 resolved      ambiguous      unknown
                    │             │             │
                    │             ▼             ▼
                    │       clarification    engineer
                    │          needed        investigation
                    │             │
                    └──────┬──────┘
                           ▼
                    DATA QUERY PLAN
                           │
                           ▼
                    QUERY GENERATION
                           │
                           ▼
                       VALIDATE
                           │
                           ▼
                    ENGINEER REVIEW
                           │
                           ▼
                       EXECUTE
                           │
                           ▼
                   DRAFT RESPONSE
                           │
                           ▼
                       APPROVE/SEND
```

Initially, stop before execution and present the engineer with an evidence-backed interpretation and proposed query.

---

## 10. Progressive Autonomy

### Level 1 — Assisted

```text
request
→ interpret
→ propose query
→ engineer executes
```

### Level 2 — Reviewed execution

```text
request
→ interpret
→ build query
→ engineer approves
→ workflow executes
→ workflow drafts response
```

### Level 3 — Controlled auto-fulfilment

Only for requests satisfying explicit conditions such as:

```text
known requester/team
+
known data product
+
approved query pattern
+
no sensitive-access issue
+
all semantics resolved
+
known output limits
────────────────────────────
→ automated execution
```

Do not begin with Level 3.

A syntactically valid query can still answer the wrong business question.

---

## 11. The Request Workflow Can Feed the Atlas Learning Loop

Completed requests create evidence.

Example:

```text
request
    ↓
ambiguity
    ↓
human clarification
    ↓
successful query
```

The Engineering/Adaptation learning layer can produce a semantic candidate such as:

```text
Within Inventory Analytics requests,
"volume" commonly refers to item quantity.
```

But:

```text
request episode
    ≠
authoritative truth
```

The correct route is:

```text
episode
   ↓
semantic candidate
   ↓
Atlas staging
   ↓
SME review
   ↓
curated terminology mapping
```

The same applies to new join knowledge and reusable query patterns.

---

## 12. Keep Raw Requests Out of Atlas

Do not store incoming emails or requester-specific operational chatter as curated Atlas knowledge.

Keep them transient in the Data Request Contract or execution system.

Only promote reusable knowledge:

- reviewed terminology;
- durable concept definitions;
- dataset meaning;
- approved joins;
- temporal rules;
- quality caveats;
- query patterns.

This keeps transient and potentially sensitive request details out of the long-lived knowledge layer.

---

## 13. Split the Product Into Three Pieces

```text
                 ┌───────────────────────┐
                 │      ATLAS DATA       │
                 │   KNOWLEDGE LAYER     │
                 │                       │
                 │ concepts              │
                 │ schemas               │
                 │ terminology           │
                 │ joins                 │
                 │ query patterns        │
                 └──────────┬────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
     ┌─────────────────┐        ┌────────────────────┐
     │ ASK DATA        │        │ DATA REQUEST FLOW  │
     │                 │        │                    │
     │ interactive     │        │ Outlook intake     │
     │ self-service    │        │ triage             │
     │ query planning  │        │ approval/execution │
     └─────────────────┘        └────────────────────┘
```

Atlas remains knowledge.

Ask Data provides interactive consumption.

Data Request Flow provides operational automation.

---

## 14. Capability Ladder

Build capabilities in this order:

```text
1. Explain terminology
       ↓
2. Locate data
       ↓
3. Explain grain / keys / time
       ↓
4. Recommend reviewed joins
       ↓
5. Produce query plan
       ↓
6. Generate SQL
       ↓
7. Validate SQL
       ↓
8. Human-approved execution
       ↓
9. Controlled auto-fulfilment
```

The highest early value is likely in stages 1–5 because that is where expert knowledge currently consumes engineer/lead time.

---

## 15. Initial MVP

Start with:

```text
one requesting team
+
one receiving/data-owning team
+
5–10 common business concepts
+
5–10 important datasets
+
key fields
+
3–5 reviewed joins
+
5 recurring query patterns
```

Test Atlas against historical requests.

Success questions:

- Could Atlas interpret the terminology?
- Could it locate the right dataset?
- Could it identify genuine ambiguity?
- Could it explain grain and time semantics?
- Could it recommend the reviewed join?
- Could it reproduce the correct query plan?

Do not measure success by number of generated documentation pages.

The target is fewer expert interruptions with equal or better semantic correctness.

---

## Related Atlas Surfaces

Current Atlas concepts relevant to this workflow include:

- `_curated/business-concepts/`
- `_curated/schema-info/`
- `taxonomy/types.yaml`
- `contracts/map-fields.yaml`
- `.claude/skills/atlas-discover/SKILL.md`

This design should extend those surfaces rather than introduce a parallel data catalogue.

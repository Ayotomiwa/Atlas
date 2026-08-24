# Plan an efficient API-to-Redshift SCD2 reconciliation flow

Work in planning mode. Inspect the current repository and produce an implementation-ready plan. Do not change application code, infrastructure, configuration, SQL, or tests.

## Goal

Plan the smallest safe change that gives a simple entity a full reconciliation across this path:

```text
source API -> staging table -> SCD2 dimension table
```

The plan must fit the code that exists. Treat the design targets in this prompt as requirements and hypotheses to verify, not proof of how the repository currently works. Prefer existing project patterns when they satisfy the requirements. Do not add an abstraction merely because this prompt names one.

## Known constraints

Use these constraints unless the repository proves that one is stale or inaccurate. Call out any conflict instead of silently choosing one version.

- The main ETL Step Function loads the API response into a Redshift staging table and then applies SCD2 changes to a dimension table.
- A separate reconciliation Step Function runs only after the main ETL Step Function succeeds. A failed ETL run does not start reconciliation.
- Reconciliation calls the API again shortly after the load with the same date range and filters.
- The API has a dedicated count endpoint. Reconciliation must call it.
- The API data endpoint normally returns up to 5,000 records per page.
- A reconciliation can cover about 7 million records.
- The Lambda has previously run out of memory when code accumulated roughly 1 million records. Do not solve this by increasing Lambda memory.
- Do not introduce a new permanent table or a temporary table.
- An existing reconciliation-results table stores pass or fail status and the reason. Reuse it.
- The staging table contains only the most recent successful load when reconciliation runs. It does not need a business-date predicate to identify the run.
- The workflow clears or replaces staging as part of its daily lifecycle. Reconciliation must not race with staging cleanup or the next load.
- Staging has source data and limited load metadata. It does not have the dimension's SCD2 start date, end date, or active flag.
- A shared Java API transport class contains fields used by many entities. The API client deserializes records into this class and ignores unknown JSON properties.
- The reconciliation should not duplicate the main pipeline's transformation logic in a way that lets the same mapping defect pass both loading and reconciliation. Reusing API authentication, transport, pagination, and deserialization may be acceptable.
- For the first implementation, scope the content comparison to one simple entity. Do not implement flattening for nested child arrays. Identify a clean extension point for that later case.

## Required reconciliation outcome

The proposed flow must establish all of the following for the selected simple entity:

1. The API count equals the staging count for the same source selection.
2. Required staging keys and available staging metadata are populated.
3. Staging has no duplicate business key, unless the source contract defines a composite key. In that case, validate the complete key.
4. Every API record matches the corresponding staging record across the approved business columns.
5. Every staged record matches exactly one active dimension record across their common business columns.
6. Each staged business key has exactly one active dimension version.
7. Active dimension rows have valid start-date, end-date, active-flag, and required load metadata combinations.
8. A new or changed entity creates the expected current-business-date version, and the superseded version becomes inactive with the correct end date.
9. The existing reconciliation-results table receives a useful, idempotent final result with the failed check and enough bounded diagnostic detail to investigate it.

Do not assume that the API count must equal the number of dimension rows inserted on the current business date. Unchanged source records may continue to use an older active SCD2 version. Verify the actual pipeline behavior and state the correct count relationships.

## Start with repository evidence

Find the real entry points and follow the runtime path before recommending changes. Inspect at least the following areas when they exist:

- The main ETL and reconciliation Step Function definitions
- Lambda handlers, input and output models, retry policies, catches, timeouts, and memory settings
- The API client, count call, page call, continuation-token handling, filters, date range, sorting options, and source snapshot or watermark support
- The shared API transport class and Jackson configuration for unknown properties
- Entity or table configuration, field-name definitions, mapping code, and normalization rules
- Staging load and cleanup code
- Redshift connection management, JDBC driver settings, query helpers, fetch size, transaction boundaries, and whether result helpers materialize complete result sets
- SCD2 merge SQL and the meaning of the business date, start date, end date, and active flag
- The current reconciliation checks and reconciliation-results write
- Existing tests, fixtures, logs, metrics, alarms, and deployment templates

For each material finding, cite the repository path and the class, method, state, or SQL symbol. Keep verified current behavior separate from recommendations. Mark anything that cannot be verified as an open question.

## Evaluate the API-to-staging comparison

First determine whether the API can return a stable, deterministic order by the complete business key for the whole source selection. Confirm that pagination preserves this order and that the order can be matched safely by Redshift. Check collation and composite-key behavior rather than assuming that Java string ordering and Redshift ordering are equivalent.

If stable ordering is available, plan an ordered streaming merge:

```text
one API page of at most 5,000 records
                  +
one forward-only Redshift staging stream
                  ->
compare keys and selected values as records advance
```

The Lambda must retain only the current API page, the JDBC fetch buffer, the current comparison values, bounded mismatch diagnostics, and continuation state. It must never collect all API pages or all staging rows.

Use one projected staging query per Lambda invocation, not one query per API page. Select only the complete business key and approved comparison columns. Do not use `SELECT *`, JPA `getResultList()`, or a helper that builds a list for the full result.

Before starting another API page, check the Lambda's remaining time. Continue only when enough time remains to fetch and compare the complete page. Checkpoint only at a page boundary so that retry behavior is clear. The Step Function state may carry bounded values such as:

```json
{
  "runId": "...",
  "entity": "...",
  "businessDate": "...",
  "apiCount": 7000000,
  "nextApiToken": "...",
  "lastCompletedBusinessKey": "...",
  "comparedCount": 2250000
}
```

Plan sequential continuation invocations of the same comparison Lambda when the remaining time is low. Do not propose one Lambda invocation per 5,000-record API page. Explain how retries remain idempotent and how the next staging stream resumes after the last completed key.

If the API cannot provide stable ordering, do not pretend that an ordered merge is exact. Compare the realistic alternatives under the no-table constraint. Include page-key lookups against staging, bounded external state if the existing architecture already permits it, and probabilistic techniques. Quantify database-call and correctness trade-offs. Do not use sampling or aggregate hashes as the sole pass criterion unless the stakeholders explicitly accept probabilistic reconciliation.

## Decide how entity-specific comparison is represented

The shared API transport class does not remove the need to define which fields belong to the selected entity. Inspect how the repository already expresses table names, business keys, API fields, database columns, and data types.

Compare at least these implementation shapes against the current code:

1. A direct entity-specific comparator for the first simple entity.
2. A small, configuration-driven comparator that reuses one streaming loop and declares each entity's tables, key, and comparison columns.

Recommend the least complex shape that fits the expected number of entities and existing conventions. Avoid creating a Java reconciliation record for every entity unless type safety or current code patterns make that the better choice. Avoid per-row reflection, `ObjectMapper.convertValue` to a map, or another allocation-heavy mechanism across millions of records. If dynamic property access is justified, resolve and cache accessors once per entity or Lambda execution environment.

Define normalization and equality rules for each relevant type. Cover nulls, empty strings, whitespace policy, decimals and scale, timestamps and time zones, dates, booleans, and any code values. The API-to-staging comparison must be independent enough to detect a pipeline mapping defect.

Assess the risk created by ignored unknown JSON properties. Keep source-schema monitoring separate from business-column reconciliation. Recommend whether the current application should fail, warn, or record unknown property names without retaining unknown values for every record.

## Keep staging-to-dimension work inside Redshift

Plan set-based SQL that compares staging with active dimension rows for the business keys present in the current staging table. Compare only the common business columns. Do not try to compare SCD2 metadata with staging columns that do not exist.

Plan separate dimension checks for:

- Zero or multiple active rows for a staged business key
- An active row with a non-null end date
- An inactive historical row with a missing end date
- Missing required metadata on dimension versions created for the current business date
- Incorrect closure of a superseded version
- A current active dimension value that differs from staging

Use Redshift to return scalar counts and a small bounded sample of failing keys. Do not return millions of dimension rows to Lambda. Consider the current distribution keys, sort keys, table statistics, and query plans before proposing a join or bidirectional `EXCEPT` query.

## Arrange checks to fail cheaply

Recommend the final Step Function order based on the code and likely cost. Start by evaluating this candidate sequence:

```text
main ETL succeeds
  -> call API count endpoint
  -> run cheap staging and SCD2 integrity checks
  -> run the Redshift staging-to-active-dimension comparison
  -> run the full paged API-to-staging comparison
  -> write the final reconciliation result
  -> allow staging cleanup or the next load
```

The plan may change this sequence when repository evidence supports another order. Minimize bytes transferred and repeated table scans, not merely the number of SQL statements. State how many API calls, Redshift statements, Lambda invocations, and Step Function transitions a successful 7-million-record run is expected to use. Separate unavoidable calls from design overhead.

## Required plan output

Return one implementation plan with these sections:

1. **Current flow.** Show the verified runtime path from the main ETL success state through reconciliation and the result write.
2. **Gaps and risks.** Explain where the current flow falls short of the required outcome. Rank the findings by data-correctness and operational risk.
3. **Design options.** Compare at least two meaningful shapes for the API-to-staging comparison and choose one. State why the rejected option loses in this repository.
4. **Recommended flow.** Show the proposed Step Function states, Lambda boundaries, Redshift work, continuation loop, failure paths, and staging-cleanup boundary.
5. **Code change map.** Name each file, class, method, state-machine definition, SQL builder, or configuration entry to add or change. State the responsibility of each change. Do not invent paths when the repository does not yet contain the proposed file.
6. **Data contracts.** Define the Step Function state, comparison-column definition, business key, normalization rules, mismatch result, and final reconciliation-result payload.
7. **SQL plan.** Give representative SQL or precise pseudocode for counts, duplicate keys, active-row uniqueness, SCD2 metadata checks, and staging-to-active-dimension differences. Adapt names to the actual schema.
8. **Java pseudocode.** Show the page-bounded comparison loop, streaming JDBC access, timeout checkpoint, resume behavior, and bounded diagnostics using the project's existing Java and AWS patterns.
9. **Capacity estimate.** Estimate heap use, Redshift result transfer, API calls, database calls, Step Function transitions, and likely timeout pressure for 5,000-row pages and 7 million rows. State assumptions.
10. **Failure and retry behavior.** Cover duplicate invocation, API throttling, an expired page token, Redshift interruption, a source that changes between ETL and reconciliation, partial result writes, and staging cleanup or replacement.
11. **Test plan.** Include unit, SQL integration, state-machine, retry, memory, timeout, and realistic high-volume tests. Explain how to prove that the code never accumulates pages or complete result sets.
12. **Delivery sequence.** Break implementation into reviewable changes. Start with one simple entity and preserve an extension point for nested child entities without implementing them.
13. **Decisions and open questions.** List only choices that repository evidence cannot resolve. Name the owner or evidence needed for each one.

## Planning rules

- Do not implement the plan in this pass.
- Do not recommend a new table, a temporary table, or more Lambda memory.
- Do not assume that fewer database calls always means lower Redshift cost.
- Do not use sampling as proof of a full match.
- Do not reuse the production transformation method as the reconciliation oracle.
- Do not invent API ordering, snapshot, schema, or Redshift-driver capabilities.
- Prefer one simple entity-specific implementation over a vague framework. Recommend a shared comparator only when it removes real duplication in the current code.
- Cite code evidence for current-state claims and label estimates as estimates.
- End with a concise recommended decision and the first implementation change.

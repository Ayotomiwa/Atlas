# Shift-left test readiness and Xray execution plan

| Field | Value |
|---|---|
| Status | Parked for later |
| Created | 2026-08-26 |
| Scope | Design only. This plan does not author a standard, create a skill, change tests, or update Xray. |
| Proposed skill | `atlas-shift-left-readiness` |
| Proposed standard | `standard.shift-left-production-test-evidence` |

This file is a planning artifact. It is not authoritative Atlas knowledge and must not be routed as a curated standard.

## Goal

Give engineers and agents one workflow that can answer these questions for production-bound work:

1. Does the change require shift-left test coverage?
2. Do existing tests already cover every changed behaviour?
3. Should the team reuse, update, add, split, supersede, or deprecate tests?
4. What evidence must the pipeline record in the Xray Test Execution?

The workflow must cite its evidence and stop when policy or test coverage is unclear. It must not treat a small diff or an empty search result as proof that no testing is required.

## Confirmed system model

The current discussion established these facts:

- Executable shift-left tests live in a separate source repository.
- The team runs a pipeline and passes an Xray Test Execution Jira ID.
- The pipeline executes tests from the shift-left repository.
- The exact mapping from repository tests to Xray Tests still needs confirmation.
- The exact way that the pipeline imports or updates Xray results still needs confirmation.

The intended ownership is:

| Source | Responsibility |
|---|---|
| Delivery Jira issue | Requirement, acceptance criteria, delivery scope, and business context |
| Implementation repository | Production behaviour and the exact change under assessment |
| Atlas curated standard | Applicability rules, exemptions, required evidence, and approval rules |
| Shift-left test repository | Executable test definitions and their version history |
| Pipeline | Execution of an exact test-repository revision against an exact target |
| Xray Test Execution | Run identity, environment, status, evidence, and traceability |

The Test Execution Jira ID belongs to the execution phase. It must not determine whether testing is required.

## Atlas knowledge design

### Primary standard

The proposed curated target is:

`_curated/standards/testing/shift-left-production-test-evidence.md`

Use:

```yaml
id: standard.shift-left-production-test-evidence
type: standard
standard_category: testing
requirement_level: required
```

Set `requirement_level: required` only after authoritative evidence confirms that every applicable production change must follow the procedure.

Testing is the primary category because the standard governs production validation and test evidence. Add routing aliases and keywords for Jira, Xray, Test Execution, production readiness, and shift-left testing.

Create a separate Jira standard only if the Xray procedure has different ownership, evidence, exceptions, or change cadence. The Jira standard should extend the testing standard and must not repeat it.

### Evidence route

Use `atlas-onboard-standards` or an approved `atlas-stage` workflow to capture:

- the authoritative procedure or policy;
- the definition of production-bound work;
- required and exempt change types;
- the approved Xray and pipeline process;
- representative test cases;
- counterexamples and exceptions;
- ownership and review requirements.

Stage the evidence under `_staging/standards/` before curation. Repeated test patterns prove practice, not mandate.

### Required standard content

The standard must settle these points:

- which production changes require an assessment;
- which change characteristics require shift-left coverage;
- valid exemptions and the person or role that approves them;
- minimum coverage for changed behaviour and safety facts;
- rules for reusing, updating, adding, splitting, superseding, and deprecating tests;
- required links among the delivery issue, implementation revision, test-repository revision, pipeline run, and Test Execution;
- required target environment, build, revision, result, and evidence;
- review and ownership rules;
- failure, retry, and incomplete-execution handling;
- retention rules for historical executions;
- the source of truth when the repository and Xray disagree.

Store stable rules in Atlas. Link to repository-owned pipeline syntax and other details that are likely to change.

## Skill design

### User-facing usage

An engineer should be able to ask:

- "Does ABC-123 need shift-left tests?"
- "Check this pull request against the existing shift-left tests."
- "Do we need a new test, or should we update an existing one?"
- "Verify that Test Execution ABC-456 contains the expected results for this change."

The user should not need to know the skill name or Atlas storage paths.

### Inputs

The assessment requires:

- the delivery Jira issue or equivalent requirement;
- an exact implementation diff, pull request, commit, or immutable commit range;
- an exact shift-left test-repository revision;
- the target environment or production scope;
- the curated Atlas standard.

The Test Execution Jira ID is optional during assessment. It becomes required when the workflow verifies an execution.

### Internal design

Use one user-facing skill with two read-only modules.

#### Policy gate

The policy gate reads the Atlas standard and classifies the change.

```text
REQUIRED
EXEMPT
NEEDS_HUMAN_DECISION
BLOCKED
```

`BLOCKED` means that required policy, source, repository, or Jira evidence was unavailable or stale. The skill must never convert `BLOCKED` into `EXEMPT`.

The policy gate should reuse the existing Atlas change-risk method. It should derive the behavioural change, safety facts, affected contracts, and testing obligations from the exact implementation change.

#### Coverage planner

The coverage planner inspects the shift-left repository and maps each safety fact to existing tests.

```text
REUSE
UPDATE
ADD
SPLIT
SUPERSEDE
DEPRECATE
NEEDS_HUMAN_DECISION
```

The planner should narrow candidates with stable metadata before semantic comparison. Candidate signals may include:

- Xray Test key;
- Jira requirement key;
- component, flow, endpoint, event, schema, or table;
- test tags and annotations;
- test class, file, scenario, or method;
- owner;
- supersession or deprecation metadata.

Inspect the actual shift-left repository before introducing a new metadata schema or index. Prefer a deterministic index generated from the existing test format over a manually maintained catalogue.

### Required output

Return a cited coverage matrix:

| Safety fact | Existing test | Coverage | Proposed action | Evidence |
|---|---|---|---|---|
| Changed behaviour or condition | Xray key, test ID, or repository path | Full, partial, conflicting, or none | Reuse, update, add, split, supersede, deprecate, or escalate | Atlas rule, Jira field, implementation change, and test definition |

The result must also contain:

- the applicability decision and the exact rule that produced it;
- the implementation and test-repository revisions inspected;
- candidate tests considered and rejected;
- missing or contradictory evidence;
- shared consumers or linked requirements that an update could affect;
- the proposed reviewer or owner;
- the smallest check needed to settle each unresolved item.

## Test lifecycle rules

Use these working rules until authoritative team policy replaces them.

### Reuse

Recommend `REUSE` when an existing test still covers:

- the same behaviour and requirement;
- the required preconditions;
- meaningful data variations;
- the expected result;
- the relevant failure or negative path.

A new Test Execution does not require a new test definition.

### Update

Recommend `UPDATE` when the test keeps the same purpose and requirement, but its steps, data, setup, or assertions must follow the changed behaviour.

Before recommending an update, inspect other requirements and consumers that use the test. Escalate when the test is shared and the effect of the update is unclear.

### Add or split

Recommend `ADD` when the change introduces a distinct acceptance criterion, observable outcome, permission rule, negative path, failure mode, or independently owned behaviour.

Recommend `SPLIT` when one existing test now represents two valid behaviours or when changing a shared test would erase valid coverage.

### Supersede or deprecate

Recommend `SUPERSEDE` when a new test replaces an old test but the old history must remain traceable.

Recommend `DEPRECATE` when a test no longer applies. Preserve historical execution evidence.

## Execution and verification

After reviewers approve and merge any required test-repository changes:

1. Resolve the exact implementation and test-repository revisions.
2. Create or select the approved Xray Test Execution.
3. Run the pipeline with the Test Execution Jira ID.
4. Record the target environment, build, and revisions.
5. Verify that every expected repository test reported into the selected Test Execution.
6. Separate passed, failed, missing, skipped, and unexpected results.
7. Report whether the Test Execution provides the evidence required by the Atlas standard.

Do not reset, overwrite, close, or otherwise mutate existing execution evidence without explicit approval and confirmed team rules.

## Mutation boundary

The first version remains read-only. It produces an assessment and a proposed test change.

A later authoring workflow may:

- prepare a local or feature-branch patch in the shift-left repository;
- show the exact proposed tests and affected files;
- run repository validation;
- create a commit or pull request after approval.

Keep Xray mutation separate from test-repository mutation. They have different permissions, reviewers, and failure modes.

The workflow must never self-approve, merge a test-repository change, or mark a production change ready.

## Implementation options

| Option | Shape | Decision |
|---|---|---|
| One-shot assessment | Search the Jira issue, implementation change, test repository, and Xray on each run | Suitable for a short pilot |
| Policy gate and coverage planner | Apply a deterministic policy gate, build a test inventory, and use semantic comparison on a filtered candidate set | Recommended target |
| Automated pull-request or release gate | Run the same assessment automatically for production-bound changes | Consider only after the read-only workflow performs well on historical cases |

## Rollout

1. Inspect the real shift-left repository, test format, and pipeline.
2. Confirm how repository tests map to Xray Test identities.
3. Gather the authoritative policy, exceptions, owners, and representative evidence.
4. Stage and curate the Atlas standard.
5. Build a deterministic test inventory from the existing repository format.
6. Implement the read-only policy gate and coverage planner.
7. Evaluate the skill against historical changes with known reviewer decisions.
8. Add proposal generation for new or changed tests.
9. Consider a separate approval-gated authoring workflow.
10. Consider pipeline or pull-request enforcement only after measuring false decisions and reviewer overrides.

## Evaluation cases

The evaluation set should include:

- a documentation-only change with an approved exemption;
- a behaviour change fully covered by an existing test;
- a partial match that requires an update;
- a new negative path that requires a new test;
- a shared test that must be split;
- an obsolete test that should be deprecated;
- a small diff with material API, schema, data, permission, scheduling, or configuration impact;
- no matching test found;
- inaccessible or stale test-repository evidence;
- conflicting policy rules;
- incomplete Jira acceptance criteria;
- a cross-repository change where only one repository is available;
- a pipeline run with missing or unexpected Xray results.

Measure agreement with human reviewers for both applicability and coverage actions. Record false exemptions separately because they carry more risk than conservative escalations.

## Open questions

Resolve these questions before implementation:

1. What repository contains the shift-left tests, and how will the skill access it?
2. Which test framework and file formats does the repository use?
3. How does each repository test map to an Xray Test?
4. Does the source contain an Xray key, tag, annotation, or another stable identifier?
5. Does the pipeline create missing Xray Tests or require existing ones?
6. Which pipeline parameter accepts the Test Execution Jira ID?
7. How does the pipeline publish passed, failed, skipped, and evidence data?
8. Is the team using Jira and Xray Cloud or Data Center?
9. Is Xray Standard or Enterprise in use?
10. Who creates and closes the Test Execution?
11. Is the assessment mandatory for every production-bound change while test creation remains conditional?
12. Which change types always require coverage?
13. Which exemptions exist, and who approves them?
14. Can existing tests change after execution, or must the team version or replace them?
15. What happens when the repository and Xray describe different test identities?
16. Who approves changes to tests shared by several services or requirements?
17. What is the usual entry point: a Jira issue, implementation pull request, release issue, or a combination?
18. Should the first skill only report, or may it prepare an uncommitted patch?

## Inputs needed when this plan resumes

Bring these items to the next design session:

- one sanitised test file;
- the relevant pipeline job or script;
- an example delivery Jira issue;
- an example Test Execution;
- the internal shift-left procedure or a sanitised summary;
- one historical change that reused a test;
- one historical change that added or updated a test.

The Atlas repository is public. Do not add internal Jira keys, repository names, URLs, restricted policy text, customer data, credentials, or production evidence to this plan.

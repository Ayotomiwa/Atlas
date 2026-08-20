# Curated flows

Use a flow page to answer: **what ordered path produces this outcome, which conditions move it forward, and where do material handoffs cross boundaries?**

A step is an activity in the path, not a second kind of component. Its participant may be a component, infrastructure package or resource, external system, manual action, or unresolved item. The structured steps are the single authoring source for participant identity, order, material handoffs, and optional branch topology.

## Domain and boundary

Store each flow at `_curated/flows/<primary-domain>/<record>.md`. Use one evidenced primary domain and record secondary involvement in `related_domains`; ask the user rather than inventing ownership.

Define where the flow starts and ends. A flow may cross repositories, infrastructure and external systems, but missing steps remain explicit coverage gaps.

## Steps and participants

Every step requires a page-local stable `step_id`, positive display `order`, name, typed participant, role, confidence and evidence/note. Participant types are controlled in taxonomy. A known unonboarded component may retain a readable name without an ID; never invent a `comp.*` ID.

Order implies the normal linear path. Add transitions only for evidenced success, failure, conditional, retry or always paths. Flow steps own participation; component and infrastructure pages do not author reciprocal `participates-in` entries.

## I/O and infrastructure

Author whole-flow boundary `inputs` and `outputs`. Add step `receives`/`emits` only for durable or operationally meaningful handoffs. Missing handoff data means not captured, not none.

An infrastructure package or promoted resource that performs work is simply a typed step participant. Use `runbooks`, `standards` and `incident_learnings` for governed routes. Possible/unconfirmed/conflicting entries remain in their natural collection.

## Generated views

`python scripts/rebuild_atlas.py` renders the step table and, when `diagram: true`, an accessible Mermaid flowchart. Use a diagram for one question with roughly three to eight meaningful steps; keep the table as the text fallback. Components, infrastructure, resources, external systems and manual actions use distinct shapes. Dashed borders mark uncertain steps, while dashed edges mark failure or retry paths, so meaning never depends on color.

When no transition is authored anywhere, the diagram connects steps by order. Once a flow authors any transition, the diagram renders only explicit transitions; capture every evidenced branch needed to understand that topology. Never hand-edit the generated block. Use `atlas-diagram` to review whether a diagram is useful and readable without changing its meaning.

The map does not duplicate steps into later component or infrastructure rosters. It derives only `downstream_flows`; the query tool derives participant and impact views from the steps.

Maps connect; pages explain boundary, failure behavior, evidence and question context.

## Review

Before approving a flow page, confirm that:

- the start and end of the flow are stated, and everything outside them is explicitly out of scope;
- step order reflects evidenced execution rather than reading order of the source;
- each participant is typed correctly, and an unonboarded participant keeps a readable name instead of an invented `comp.*` ID;
- transitions exist only where a branch, retry or failure path is evidenced;
- boundary `inputs`/`outputs` and step `receives`/`emits` describe durable handoffs, and missing handoff data is recorded as not captured rather than none;
- entry points match real triggers, with `entry_point_type` supported by a schedule, event or caller;
- failure paths and their operational consequences are evidenced, not inferred from the happy path;
- gaps in the chain are declared as coverage limits, so a partial flow is never read as complete.
- a requested diagram answers one question, stays readable at normal width, and preserves a useful table/prose fallback.

This README defines the flow page model and review rules. Flow discovery and curation workflows own investigation, approvals, persistence, validation, and independent review.

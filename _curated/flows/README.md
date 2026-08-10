# Curated flows

Flow pages describe an evidenced end-to-end path and its outcome. The structured steps are the authority for participant identity, order, material handoffs and optional branch topology.

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

`python scripts/rebuild_atlas.py` renders the step table. Set `diagram: true` only when a generated Mermaid view helps; diagram necessity remains curator judgment. The map does not duplicate steps into later component or infrastructure rosters. It derives only `downstream_flows`; the query tool derives participant and impact views from the steps.

Maps connect; pages explain boundary, failure behavior, evidence and question context.

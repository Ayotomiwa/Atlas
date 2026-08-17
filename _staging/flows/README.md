# Staging flow evidence

This bucket captures attributable evidence about an apparent end-to-end path, ordering, participants, handoffs, infrastructure and gaps. It is not a curated flow and never authoritative.

Group records one level below the bucket by candidate domain: use `_staging/flows/<domain>/<STG-ID>.md` only when the primary candidate domain is evidenced or user-confirmed; otherwise use `_staging/flows/unassigned/<STG-ID>.md`. Do not use repository paths or nested folders as grouping. Because committed staging paths are immutable by policy, uncertain evidence must not be forced into a domain.

Capture the observed normal path plus branches, retries and failure-only routes when evidence exists. Participants may be components, jobs, infrastructure, external systems, manual actors or unresolved items. Do not invent stable IDs or missing steps.

A curation-ready flow record includes a readable execution narrative as well as the routing tables. It explains why each material handoff occurs, which conditions gate it, where state crosses a boundary and what remains unknown. Sequential declarations or timestamps alone establish attempted order, not causal success.

Keep raw evidence in the body. Curation decides whether facts become structured entry points, boundary I/O, ordered steps, material step handoffs, transitions or compact question routes. A package/resource that performs work becomes a typed step participant; passive infrastructure connections belong on component or infrastructure records.

Use `python scripts/atlas_query.py staging --bucket flows` to inspect this evidence; add `--domain <domain>` when needed.

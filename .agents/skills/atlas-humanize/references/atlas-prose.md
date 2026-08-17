# Atlas prose patterns

Lead with the engineer's use before naming the Atlas record type.

- Repository: explain source organisation, ownership, reading routes, and boundaries.
- Component: explain what the independently addressable runtime or reusable unit does, uses, produces, and does not own.
- Flow: explain ordered steps, conditions, material handoffs, and failure paths without treating visual adjacency as causality.
- Infrastructure: explain what the package/resource creates, who uses it, why it matters, and its operational boundary.

Put policy beside the decision it controls. Keep exact governance words such as `must`, `never`, and `only`; shorter prose must not weaken the rule.

Do not edit YAML keys, stable IDs, generated markers, link targets, parser-owned headings, structured table interfaces, code, or commands in a prose cleanup. A change to a fact, scope, relationship, confidence, or requirement is a knowledge change and needs the owning evidence/curation workflow.

Before finishing, compare original and revised claims, qualifications, exclusions, environments, dates, and unknowns. If a reviewer could reach a different conclusion, stop and classify the edit as semantic.

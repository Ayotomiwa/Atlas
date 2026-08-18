# Answer provenance and file hops

Every substantive factual answer needs clean references near its material claims. Classify each material claim as **Atlas**, **Repository (located via Atlas)**, **Inference**, or **Unresolved**. Treat active curated pages as authoritative for reviewed durable context, standards, conflicts, exceptions and obligations. Repository source is authoritative for current implementation and owns exact commands, code, configuration and IaC literals; Atlas can locate that source but never overrides it. Add only one short checkout advisory when an answer-bearing page is not `main-clean`, and always disclose `not-verified` context.

## Answer labels

- **Atlas**: cite `<stable-id> — <curated-page>#<heading>`.
- **Repository (located via Atlas)**: cite `<repository-relative-path>:<line-or-symbol>`.
- **Inference**: state the inference and cite every material premise.
- **Unresolved**: state the missing evidence or coverage boundary.

## Evidence references

Attach supporting evidence kinds beneath the chosen answer label:

- `Map route: <map>/<record-id>.<natural-field> -> <target-id>`;
- authorised external artifact/URL;
- user-confirmed current-task fact;
- relevant Atlas or repository references.

Do not cite scripts or pasted query output as factual sources. Maps may disclose a route; the curated page or repository evidence supplies meaning.

Use adaptive detail: keep ordinary direct answers concise; add `How this was traced` for material cross-system traversal or source fallback, and expand automatically for impact, safety, absence, conflict and audit questions. Expose every answer-bearing source/target hop, natural field or flow step, confidence, supporting page/source and whether it came from Atlas or fallback. State exactly where Atlas coverage ended.

When Atlas guides source fallback, name the repository; the smallest path, symbol, config, IaC, or document boundary; the selection reason; route confidence; and the Atlas coverage endpoint. If the repository is unambiguous and the boundary is authorised, read-only fallback is automatic. Otherwise preserve the ambiguity as Unresolved.

When a selected repository/context hop has `locator_match: not-verified`, include a visible advisory in every substantive answer using it: the path match aided routing but did not prove repository identity. Do not leave this only in an internal ledger.

List materially consulted files/pages when useful. Include checked-but-not-found paths when an absence or coverage limit affects the conclusion and say where the search stopped. Omit administrative/exploratory files that did not influence the answer; onboarding retains a full scan manifest.

Keep the full claim ledger internal unless the user requests it or the answer is an audit artifact.

# Answer provenance and file hops

Every substantive factual answer needs clean references near its material claims. Classify each material claim as **Atlas**, **Repository (located via Atlas)**, **Inference**, or **Unresolved**. Treat active curated pages as authoritative for reviewed durable context, standards, conflicts, exceptions and obligations. Repository source is authoritative for current implementation and owns exact commands, code, configuration and IaC literals; Atlas can locate that source but never overrides it. Add only one short checkout advisory when an answer-bearing page is not `main-clean`, and always disclose `not-verified` context.

Treat an Atlas connection with confidence possible, unconfirmed, or conflicting as a coverage limit: never promote it to confirmed. Curated page authority never upgrades an individual field or edge confidence. When a definitive, executable, or complete claim depends on it, qualify the claim or perform the smallest source verification of precisely the uncertain edge. Treat external targets and unknown coverage as separate states: preserve them as external or unresolved rather than reclassifying their connection confidence. Exact volatile values are source-authoritative, including commands, code, configuration, and IaC literals.

Repository documentation alone supports documented or intended behavior; it does not confirm executable or deployed wiring. Verify with current executable or deployed evidence appropriate to the boundary, such as code, configuration, IaC, tests, or runtime/control-plane state.

Source reuse must match the requested revision. Resolve a named revision or range to an immutable commit or range and associate every inspected source path with it. For past implementation, cite Git at that resolved revision; current curated Atlas may locate the boundary but is not historical evidence.

When already verified repository evidence remains current, revision-compatible and supports every material follow-up claim at the required confidence, a follow-up may use it with zero new retrieval; do not force fallback merely because the original Atlas edge was possible; related evidence must not upgrade a different uncertain edge.

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

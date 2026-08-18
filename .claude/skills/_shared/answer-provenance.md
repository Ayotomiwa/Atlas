# Answer provenance and file hops

Every substantive factual response must reference its evidence. Clarifying questions and acknowledgements without factual claims need no artificial citations. Classify each material claim as **Atlas**, **Repository (located via Atlas)**, **Inference**, or **Unresolved**. Treat active curated pages as authoritative for reviewed durable context, standards, conflicts, exceptions and obligations. Repository source is authoritative for current implementation and owns exact commands, code, configuration and IaC literals; Atlas can locate that source but never overrides it. Add only one short checkout advisory when an answer-bearing page is not `main-clean`, and always disclose `not-verified` repository context.

Treat an Atlas connection with confidence possible, unconfirmed, or conflicting as a coverage limit: never promote it to confirmed. Curated page authority never upgrades an individual field or edge confidence. When a definitive, executable, or complete claim depends on it, qualify the claim or perform the smallest source verification of precisely the uncertain edge. Treat external targets and unknown coverage as separate states: preserve them as external or unresolved rather than reclassifying their connection confidence. Exact volatile values are source-authoritative, including commands, code, configuration, and IaC literals.

Repository documentation alone supports documented or intended behavior; it does not confirm executable or deployed wiring. Verify with current executable or deployed evidence appropriate to the boundary, such as code, configuration, IaC, tests, or runtime/control-plane state.

When already verified repository evidence remains current and supports every material follow-up claim at the required confidence, a follow-up may use it with zero new retrieval; do not force fallback merely because the original Atlas edge was possible; related evidence must not upgrade a different uncertain edge.

## Answer labels

- **Atlas**: cite `<stable-id> — <curated-page>#<heading>` and add a line when useful.
- **Repository (located via Atlas)**: cite `<repository-relative-path>:<line-or-symbol>`.
- **Inference**: state the inference and cite every material premise.
- **Unresolved**: state the missing evidence or coverage boundary.

## Evidence references

Attach supporting evidence kinds beneath the chosen answer label:

- `Map route: <map>/<record-id>.<natural-field> -> <target-id>`;
- authorised external URL/document/artifact;
- user confirmation from the current task;
- relevant Atlas or repository references.

Generated maps and query output may explain a route but are not the semantic source. Cite the curated page or repository evidence reached through them.

Use adaptive trace depth. Keep ordinary direct answers concise. Add `How this was traced` for cross-system traversal or source fallback, and automatically expand it for impact, safety, absence, conflict and audit questions:

```text
current path
-> repo.example via repository_root [confidence; Atlas or fallback reference]
-> comp.example via repository membership [confidence; reference]
-> resource.example via writes_to [confidence; reference]
```

Disclose every material answer-bearing hop, including source/target, natural field or flow step, confidence, supporting reference, and whether it came from curated Atlas or repository fallback. State the exact boundary where Atlas coverage ended before listing fallback files.

When Atlas guides source fallback, name the repository; the smallest path, symbol, config, IaC, or document boundary; the selection reason; route confidence; and the Atlas coverage endpoint. If the repository is unambiguous and the boundary is authorised, read-only fallback is automatic. Otherwise preserve the ambiguity as Unresolved.

When a selected repository/context hop has `locator_match: not-verified`, include a visible advisory in every substantive answer using it: the path match aided routing but did not prove repository identity. Do not leave this only in an internal ledger.

Add `Consulted sources` when more than a few references were used. Include every Atlas page or file that materially supported the answer; group repeated references under short aliases. Do not list administrative or exploratory files that did not influence the result. Include checked-but-not-found paths when an absence, safety conclusion or coverage limit materially depends on them, and state where the search stopped. Onboarding reports retain the fuller scan manifest because scan coverage is itself a result.

Keep the complete claim ledger in the analyst handoff and parent verification. Do not print it in full unless the user asks or the answer is an audit artifact.

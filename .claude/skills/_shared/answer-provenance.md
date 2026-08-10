# Answer provenance and file hops

Every substantive factual response must reference its evidence. Clarifying questions and acknowledgements without factual claims need no artificial citations.

Place a compact reference next to each material claim:

- `Atlas: <stable-id> — <curated-page>#<heading>` (add a line when useful);
- `Repository: <repository-relative-path>:<line-or-symbol>`;
- `Map route: <map>/<record-id>.<natural-field> -> <target-id>`;
- `External: <authorised URL/document/artifact>`;
- `User-confirmed: current task`;
- `Inference: ...` followed by references for every material premise.

Generated maps and query output may explain a route but are not the semantic source. Cite the curated page or repository evidence reached through them.

For discovery and impact answers with material traversal, add `How this was traced`:

```text
current path
-> repo.example via repository_root [confidence; Atlas or fallback reference]
-> comp.example via repository membership [confidence; reference]
-> resource.example via writes_to [confidence; reference]
```

Disclose every material answer-bearing hop, including source/target, natural field or flow step, confidence, supporting reference, and whether it came from curated Atlas or repository fallback. State the exact boundary where Atlas coverage ended before listing fallback files.

Add `Consulted sources` when more than a few references were used. Include every Atlas page or file that materially supported the answer; group repeated references under short aliases. Do not list administrative or exploratory files that did not influence the result. Include checked-but-not-found paths when an absence, safety conclusion or coverage limit materially depends on them, and state where the search stopped. Onboarding reports retain the fuller scan manifest because scan coverage is itself a result.

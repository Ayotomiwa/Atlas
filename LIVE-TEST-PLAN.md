# Atlas live use-case test plan

An end-to-end rehearsal of the whole Atlas loop against a synthetic product repository:
onboard → stage → curate → review → generate → route → answer. It exercises the package
the way a TeamA engineer would, using the specialist agents rather than hand-writing pages.

This is a **test of Atlas**, not a source of TeamA knowledge. Every fact below is invented
for the rehearsal, and nothing produced by it should be merged into a real Atlas package.

---

## 1. What this test is trying to prove

| # | Claim under test | Fails if |
|---|---|---|
| C1 | A cold Atlas can be adopted by a repository it has never seen | Onboarding cannot start, or needs hand-authored curated pages first |
| C2 | Onboarding produces attributable evidence, not conclusions | Staging asserts unevidenced ownership, flows or dependencies |
| C3 | Curation reconciles evidence into governed pages without self-approving | A page appears with no evidence, or the agent claims approval |
| C4 | Generated surfaces stay derivable and drift-checked | `rebuild_atlas.py --check` or lint fails after curation |
| C5 | Routing answers architecture questions from maps before opening pages | The query tool cannot resolve IDs, context or impact |
| C6 | Discovery answers natural questions with cited provenance | An answer is unattributed, or Atlas coverage is overstated |
| C7 | Impact separates known / possible / unknown | Absence from a map is reported as "not affected" |
| C8 | Atlas declines to invent what it cannot see | Any agent fabricates the inaccessible upstream repository |
| C9 | The recent fixes hold under real use | See §7 |

---

## 2. Test fixture: `acme-orders-platform`

A synthetic monorepo created **outside** the Atlas package, under the session scratchpad,
so it is never linted as Atlas content and never committed:

```
<scratchpad>/testbed/acme-orders-platform/
├── README.md                       platform overview; references an external repo
├── CONTRIBUTING.md                 team conventions → standards candidates
├── .editorconfig                   tool default → must NOT become a team standard
├── .github/workflows/ci.yml        build/test pipeline
├── libs/orders-common/             shared library (pyproject.toml, src/)
├── services/order-ingest/          service: S3 → Glue raw table
│   ├── pyproject.toml
│   ├── README.md
│   └── src/order_ingest/…
├── services/order-enrich/          job: raw table + pricing API → Redshift
│   ├── pyproject.toml
│   └── src/order_enrich/…
├── infra/orders-platform/          Terraform: bucket, Glue DB/table, EventBridge, Lambda
│   └── main.tf
└── schemas/
    ├── orders_raw.json             event/table contract
    └── orders_enriched.sql         DDL
```

Deliberate gaps, present so the test can prove Atlas does not fill them in:

- **G1** `README.md` references `../acme-pricing-api` — a repository that does not exist on disk.
- **G2** No `CODEOWNERS`, no owner named anywhere.
- **G3** `order-enrich` reads a config key whose source is never defined in-repo.
- **G4** `.editorconfig` is a bare tool default with no supporting policy.
- **G5** The Redshift load step has no evidenced schedule — only an EventBridge rule for ingest.

---

## 3. Preconditions

1. Working tree clean apart from the current change set; `python scripts/atlas_lint.py .` reports 0 errors.
2. `python scripts/rebuild_atlas.py --check` reports clean.
3. `atlas-package.json` still has `"domains": []` — the first phase must register the domain,
   because that is itself under test.

---

## 4. Phases

Each phase records: what runs, who runs it, and what must be true afterwards.

### Phase 0 — Build the fixture

Create the tree in §2. No Atlas files change.

**Pass:** the fixture exists and contains all five gaps G1–G5.

### Phase 1 — Cold-start domain registration (tests C1, F1)

Attempt to place an architecture page before any domain exists, confirm the failure is
self-explaining, then register the `orders` domain in `atlas-package.json`.

**Pass:**
- the pre-registration failure names `atlas-package.json` and the `domains` array;
- after registration, `python scripts/atlas_lint.py .` is clean.

### Phase 2 — Repository onboarding (tests C1, C2, C8)

Run **`atlas-repo-analyst`** over the fixture with the onboarding contract from
`.claude/skills/atlas-onboard-repository/`.

**Pass:**
- returns an evidence matrix with per-finding source paths and observed/possible states;
- identifies the monorepo root plus the two services and the shared library as *candidates*;
- flags G1 as inaccessible rather than describing the pricing API;
- flags G2 as unknown ownership rather than guessing;
- does **not** write curated pages.

### Phase 3 — Stage the evidence (tests C2)

Write the onboarding record into `_staging/components/orders/` using the bucket template.

**Pass:**
- filename equals the staging ID; frontmatter matches the staging envelope exactly;
- `status: new`; known and possible claims are in separate sections;
- lint clean.

### Phase 4 — Standards discovery (tests C2, C8)

Run **`atlas-standards-analyst`** over the fixture.

**Pass:**
- `CONTRIBUTING.md` conventions surface as team-standard candidates with sources;
- G4 (`.editorconfig`) is classified as a tool default, **not** a team standard;
- single-repo habits are labelled repo-local rather than team policy;
- output is staged to `_staging/standards/`, not curated.

### Phase 5 — Curation (tests C3, C4)

Run **`atlas-curator`** against a decision matrix resolved from the staged evidence,
producing under `_curated/`:

- 1 `repo.*` monorepo root plus logical project boundaries as evidence supports;
- `comp.*` pages for the two services and the shared library;
- 1 `flow.*` for order ingest → enrich, with G5 left as an explicit coverage gap;
- 1 `infra.*` for the Terraform package, promoting only resources that meet the
  criteria in `_curated/infra/README.md`;
- `schema.*` pages for the two contracts.

Then `python scripts/rebuild_atlas.py`.

**Pass:**
- every material claim carries evidence; unevidenced items sit at non-`reviewed` confidence with a note;
- no page claims approval or merge;
- `atlas_lint.py` and `rebuild_atlas.py --check` are both clean;
- all three maps and every catalogue regenerate with content.

### Phase 6 — Independent review (tests C3)

Run **`atlas-reviewer`** over the curated change set.

**Pass:** produces findings only — no edits, no approval — and its checks match the
review sections now present in every collection README.

### Phase 7 — Machine routing (tests C5)

```powershell
python scripts/atlas_query.py resolve comp.order-ingest
python scripts/atlas_query.py context <fixture>/services/order-enrich
python scripts/atlas_query.py neighbors comp.order-ingest
python scripts/atlas_query.py impact schema.orders-raw --direction downstream
```

**Pass:**
- `resolve` returns the page, status and route;
- `context` returns ordered repository/component candidates from a path inside the fixture;
- `neighbors` shows direct connections with confidence preserved;
- `impact` distinguishes direct from transitive and terminates without cycling.

### Phase 8 — Natural discovery questions (tests C6, C8)

Run **`atlas-discovery-analyst`** from inside the fixture for:

- Q1 "What does order-enrich do and what does it depend on?" — covered.
- Q2 "Which team owns this platform?" — **not** covered (G2).
- Q3 "What does the pricing API return?" — **not** covered (G1).
- Q4 "Where is the raw orders contract defined?" — covered via `schema.*`.

**Pass:** Q1/Q4 cite page IDs and paths; Q2/Q3 state the gap plainly and neither infers an
owner nor describes the inaccessible repository.

### Phase 9 — Impact questions (tests C7)

Run **`atlas-impact-analyst`** for:

- I1 "What breaks if the raw orders Glue table is dropped?"
- I2 "What is affected if the shared library changes?"
- I3 "Is the pricing API affected if we change the enrich job?" — unknowable.

**Pass:** results bucket into known / possible / unknown with evidence; I3 is reported as
unknown, never as "not affected".

### Phase 10 — Regression probes (tests C9)

See §7. Each probe is reverted immediately after it is observed.

### Phase 11 — Teardown

Revert every Atlas file the rehearsal touched, leaving only the fix-phase change set and
this plan. Confirm with `git status` plus a clean lint and `--check`.

---

## 5. Agent roster

| Phase | Agent | Must not |
|---|---|---|
| 2 | `atlas-repo-analyst` | write any Atlas or product file |
| 4 | `atlas-standards-analyst` | promote a tool default to a team standard |
| 5 | `atlas-curator` | approve, merge, or invent an unevidenced connection |
| 6 | `atlas-reviewer` | edit anything, or approve on a human's behalf |
| 8 | `atlas-discovery-analyst` | answer without provenance |
| 9 | `atlas-impact-analyst` | infer safety from absence |

---

## 6. Global invariants

Checked after every phase that writes:

- `python scripts/atlas_lint.py .` → 0 errors;
- `python scripts/rebuild_atlas.py --check` → clean;
- no generated JSON, catalogue block or managed table edited by hand;
- no staging record's body, path or ID modified after its first write;
- no secret, credential or synthetic personal data anywhere in the package.

---

## 7. Regression probes for the current change set

Each probe injects one fault, observes the diagnostic, and reverts.

| Probe | Injected fault | Required diagnostic |
|---|---|---|
| P1 | Three component pages each reference a non-existent target | Three separate `ATLAS009` errors, one per page, in a single run |
| P2 | A page under `_curated/decisions/` | `ATLAS005` reserved-type error, not a generic unknown-type error |
| P3 | `grain:` re-added to a schema page | `ATLAS025` retired-field error |
| P4 | `routing.domains: []` re-added to a standard | `ATLAS025` retired-field error |
| P5 | A required body section emptied | Deterministic lint remains silent; `atlas-lint-analyst` or `atlas-reviewer` surfaces the body-quality gap with a file reference |
| P6 | `last_exercised: soon` on a runbook | `ATLAS025` ISO-date error |
| P7 | `resource_type: gcs-bucket` on a promoted resource | Rejected against the allowed values in `taxonomy/concept-fields.yaml` and attributed to the owning infra page |
| P8 | A curated standard added without touching any index | Catalogue regenerates automatically; hand-editing it instead makes `rebuild_atlas.py --check` report the drifted index |

---

## 8. Reporting

The run produces a single result table — phase, claim, pass/fail, evidence — plus any
Atlas defect the rehearsal exposed, separated into:

- **package defects** — Atlas behaved wrongly;
- **fixture artefacts** — the synthetic repo was unrealistic;
- **out of scope** — unit-test execution and runtime exercise of the Codex adaptation;
  this rehearsal uses the canonical Claude workflow.

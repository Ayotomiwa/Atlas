# Contract / Regression Test Placement — Next Steps and Decision Plan

## Recommended direction

Aim for the service-specific regression/contract tests to live inside the same Gradle project as the production code they protect, but keep them as a distinct test suite/source set rather than mixing them into the normal unit-test suite.

Target shape:

```text
service-module/
├── src/main/java/
├── src/test/java/
└── src/contractTest/java/
```

The shared testing framework should remain a separate reusable module/artifact containing annotations, configuration, extensions, utilities, and common test infrastructure.

The service-specific tests should depend on that framework, but their execution lifecycle should belong to the service itself.

The preferred CI relationship is:

```text
production code changes
        ↓
EP --diff selects the service project
        ↓
service CI lifecycle task
        ↓
contractTest
        ↓
merge is blocked if regression tests fail
```

Do not move all 32 tests immediately. First prove how the existing Engineering Platform lifecycle behaves and then choose the smallest compatible implementation.

---

## Next steps

### 1. Trace the actual MR build path

Find the implementation/configuration for:

- `--diff`
- project selection
- generated child pipelines
- the task invoked for a selected Gradle project
- `ciBuildTestComponent`
- any EP JUnit/test lifecycle plugin applied to the service

Answer these questions:

1. Is `--diff` purely path/project based?
2. Does it ever traverse Gradle project dependencies or reverse dependencies?
3. Once a service project is selected, which Gradle task or lifecycle chain is executed?
4. Is `ciBuildTestComponent` invoked on every selected service during MR builds?
5. Is `ciBuildTestComponent` deliberately provided as an extension hook?
6. Are there existing tasks that depend on it or that it depends on?

### What this decides

This determines whether the regression gap can be closed entirely inside the selected service's Gradle lifecycle, without changing the EP-wide `--diff` algorithm.

If `ciBuildTestComponent` is part of every selected service's MR build, it is the first hook to try.

---

### 2. Prove the lowest-change bridge

Before moving tests, temporarily wire the production/service project's CI test lifecycle to the existing separate contract-test module.

Conceptually:

```text
service:ciBuildTestComponent
        ↓
contract-test-module:contractTest
```

or, if the separate module only exposes its normal `test` task:

```text
service:ciBuildTestComponent
        ↓
contract-test-module:test
```

Then make a production-only change in the service and execute the same `--diff` path used by an MR.

Verify that:

- the service is selected;
- the separate regression tests execute;
- a failing regression test fails the service build;
- unrelated domains are not added to the build;
- the normal unit-test lifecycle still behaves as expected.

### What this decides

If this works cleanly, it gives a low-risk short-term fix and proves that the service lifecycle can own regression-test execution even before the files are moved.

It also gives a fallback if the dedicated source-set approach later conflicts with the EP Gradle plugins.

This bridge should be treated as tactical rather than automatically becoming the final architecture.

---

### 3. Search the monorepo for an existing convention

Before inventing a new pattern, search for:

- additional Java/JVM source sets;
- `contractTest`, `integrationTest`, `componentTest`, or similar tasks;
- Gradle `testing.suites`;
- manually registered `Test` tasks;
- use of `ciBuildTestComponent`;
- one project executing tests against another project's production classes;
- JUnit 5 tag filtering;
- test tasks attached to `check` or EP-specific lifecycle tasks.

### What this decides

If the monorepo already has a supported convention, prefer consistency with that convention unless it fails the MR regression requirement.

This also reduces the chance of creating a pattern that works locally but conflicts with EP build conventions, reporting, or generated pipelines.

---

### 4. Build a small same-project proof of concept

Inside the production/service module, create a dedicated regression/contract-test suite with only a few representative tests first.

Preferred structure:

```text
service-module/
├── src/main/java/
├── src/test/java/
└── src/contractTest/java/
```

The dedicated suite should:

- compile against the service's production classes;
- depend on the shared test framework;
- use JUnit 5;
- retain the existing `@Contract`/tagging model where useful;
- expose an independent test task;
- be runnable locally on its own;
- be attached to the service's MR CI lifecycle.

Then run four scenarios:

1. Production code changes, contract-test files do not.
2. Only a contract-test file changes.
3. Only a normal unit-test file changes.
4. An unrelated project changes.

### What this decides

The proof of concept answers the main architectural question:

> Can the tests live with the service, remain independently runnable/categorised, and automatically execute whenever the service is selected by `--diff`?

If yes, this should become the target structure.

---

## 5. Choose the Gradle implementation mechanism

The architectural decision and the Gradle API decision should be kept separate.

### Option 5A — JVM Test Suite

Use Gradle's JVM Test Suite mechanism if the repository's Gradle version and EP plugins support it cleanly.

Conceptually:

```kotlin
testing {
    suites {
        register<JvmTestSuite>("contractTest") {
            useJUnitJupiter()

            dependencies {
                implementation(project())
                // shared testing framework dependency
            }
        }
    }
}
```

Then attach the suite to the appropriate service CI lifecycle task.

### Option 5B — Traditional source set + Test task

If the JVM Test Suite API conflicts with EP conventions or the repository's Gradle version, use a conventional source set and explicit `Test` task instead.

Conceptually:

```text
sourceSets
  └── contractTest

tasks
  └── contractTest (Test)
```

### What this decides

This determines implementation detail, not test ownership.

Both approaches preserve the desired architecture:

```text
service project owns service-specific regression tests
shared framework remains reusable
MR selection of service causes regression suite to execute
```

---

## 6. Confirm the shared framework's responsibility

Keep the shared framework focused on reusable capabilities such as:

- `@Contract`
- `@Integration`
- `@Operational`
- `@Smoke`
- common JUnit extensions
- shared configuration
- test helpers/utilities
- common environment/test setup

Continue publishing that framework to Nexus if multiple services consume it.

Do not move service-specific regression cases into the shared framework merely to make them reusable or discoverable.

### What this decides

This creates a clean ownership boundary:

```text
Reusable testing capability
    → shared framework

Tests that assert one service's behaviour
    → that service
```

The shared framework should not need a major role change for the recommended solution.

---

## 7. Migrate the remaining tests

Once the proof of concept works:

1. Move the remaining contract/regression tests into the dedicated service suite.
2. Preserve their current assertions and mocking behaviour during the move.
3. Preserve useful JUnit tags.
4. Run the old and new arrangements during the migration if needed to prove equivalent behaviour.
5. Remove the service-to-separate-test-module relationship once the migration is complete.
6. Remove the old test module if it has no remaining responsibility.
7. Update any project registration/configuration that referenced the old module.
8. Remove temporary lifecycle wiring introduced for the bridge.

Avoid combining this migration with unrelated test refactors.

---

## 8. Validate the final CI behaviour

The final implementation should pass these checks:

| Scenario | Expected result |
|---|---|
| Service production code changes | Unit tests and contract/regression suite run |
| Contract/regression test changes | Contract/regression suite runs |
| Contract/regression test fails | MR build fails |
| Unrelated domain changes | This service's regression suite does not run unnecessarily |
| Nightly build | Full repository behaviour remains unchanged |
| Local development | Developer can run the contract suite independently |
| Normal unit-test run | Contract suite can remain separately selectable if desired |

Also compare MR runtime before and after the change. With a small, fast regression suite, merge-time execution should be preferable to relying on delayed nightly detection.

---

# Alternatives

## Alternative A — Dedicated `contractTest` suite/source set in the service

```text
service-module
├── src/main
├── src/test
└── src/contractTest
```

### Advantages

- Test ownership follows the production code.
- Existing path-based `--diff` naturally selects the correct Gradle project.
- Unit and regression tests remain structurally separate.
- No repository-wide change to affected-project calculation is required.
- The suite can have its own dependencies, task, reporting, filters, and lifecycle.
- Scales cleanly if other services later adopt the same convention.

### Costs / risks

- Requires checking compatibility with EP Gradle plugins.
- Requires explicit lifecycle wiring.
- Introduces another test source set/suite convention.

### Recommendation

**Recommended target architecture.**

Prefer this once the small proof of concept confirms compatibility.

---

## Alternative B — Put the regression tests in normal `src/test` and separate them only with JUnit tags

```text
service-module/
└── src/test/java/
    ├── unit tests
    └── contract/regression tests tagged @Contract
```

### Advantages

- Simplest Gradle structure.
- Production changes naturally trigger the project.
- Very low integration risk with existing Java/JUnit plugins.
- Existing tag-based filtering can be reused.

### Costs / risks

- Weaker structural separation.
- Dependency/configuration differences between unit and regression tests become harder to express.
- Developers can more easily run the wrong category unintentionally.
- The test tree may become noisy as the suite grows.

### Recommendation

**Best fallback if the dedicated suite/source-set model conflicts with EP.**

For only 32 fast tests it is still a valid solution, but it is less explicit than a dedicated suite.

---

## Alternative C — Keep the separate module and invoke it from the service lifecycle

```text
service selected by --diff
        ↓
service:ciBuildTestComponent
        ↓
separate-regression-module:test
```

### Advantages

- Minimal file movement.
- Can close the MR regression gap quickly.
- Preserves the existing separate test module.

### Costs / risks

- Creates cross-project task coupling.
- Test ownership remains separated from the production module.
- Future maintainers need to understand the hidden lifecycle relationship.
- May become harder to scale or reason about across many domains.

### Recommendation

**Useful tactical bridge, not the preferred final structure.**

Use it to close the gap quickly or as a fallback if moving the tests is currently too disruptive.

---

## Alternative D — Make EP `--diff` dependency-aware

Change the platform so a changed project also selects projects that depend on it, or allow explicit affected-project relationships.

Conceptually:

```text
changed service
    ↓
resolve reverse dependency/verification relationships
    ↓
service + dependent regression module selected
```

### Advantages

- Keeps the separate regression module.
- Could solve similar cross-project verification problems across the monorepo.
- Makes affected-project calculation more semantically aware.

### Costs / risks

- Changes platform-wide behaviour.
- May increase MR fan-out substantially.
- Requires decisions around direct/transitive dependants.
- Must distinguish production, runtime, test, publishing, and verification relationships.
- Can increase pipeline duration for unrelated teams.
- Much larger blast radius than solving this at the service lifecycle level.

### Recommendation

**Do not make this the first fix for one service.**

Revisit it only if investigation shows that many domains have legitimate cross-project verification relationships that the current `--diff` model cannot represent.

At that point it becomes an Engineering Platform feature rather than a workaround for this regression suite.

---

## Alternative E — Keep nightly-only coverage

### Advantages

- No implementation change.

### Costs / risks

- The known merge-time regression gap remains.
- A breaking production change can merge before the suite runs.
- Feedback moves away from the change that introduced the problem.

### Recommendation

**Do not use nightly execution as the primary protection for these tests.**

Nightly runs can remain as additional coverage, but the relevant suite should run before merge when the protected service changes.

---

# Recommended decision sequence

Use this order rather than choosing the final structure immediately:

```text
1. Trace --diff + service CI lifecycle
                ↓
2. Understand ciBuildTestComponent
                ↓
3. Try service → existing test-module bridge
                ↓
4. Search repository for an established pattern
                ↓
5. Prototype dedicated contractTest in the service
                ↓
6. If compatible:
       adopt dedicated service-owned suite
   else:
       use src/test + tags
       or retain the lifecycle bridge temporarily
                ↓
7. Move all 32 tests
                ↓
8. Validate MR behaviour and remove obsolete structure
```

## Final recommendation

The target should be:

```text
shared-test-framework
        │
        │ dependency
        ▼
service-module
├── src/main
├── src/test
└── src/contractTest
        │
        ▼
service CI lifecycle / ciBuildTestComponent
```

Keep the shared framework reusable and published separately.

Make the service own the tests that protect its behaviour.

Use the service's existing CI lifecycle to execute the dedicated regression suite whenever `--diff` selects that service.

Only change the Engineering Platform's global `--diff` behaviour if the same cross-project verification problem is found to be common across the monorepo.

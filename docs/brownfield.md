# Working with Existing Code (Brownfield Safety)

This document describes how to safely modify, refactor, or
extend **existing codebases** using AI agents, grounded in
Michael Feathers' *Working Effectively with Legacy Code* and
adapted with practitioner guidance.

The core paradox Feathers names: before changing code, you
need tests; but to put tests in place, you have to change
code. The solution is **minimal, safe refactorings to get tests
in place first**.

## Definition

**Legacy code** = code without automated regression tests.

This definition is **independent of age**. A six-month-old
project with no test suite is legacy. A twenty-year-old
codebase with a comprehensive test suite is not.

## The Legacy Code Change Algorithm

Per Feathers, the steps for changing legacy code safely:

1. **Identify change points.** Where does the code need to
   change? Look for the seam.
2. **Find seams.** Places where behavior can be altered
   without editing the code in place (most often an object
   seam in OO languages, or a function seam in FP languages).
3. **Break dependencies** at the seam. Substitute or extract
   so the code is testable.
4. **Write the tests.** Characterization tests, not TDD — the
   goal is to capture current behavior.
5. **Make your changes** with the tests as a safety net.
6. **Refactor.** Improve structure with the tests still green.

> Reference: [Key points of Working Effectively with Legacy Code](https://understandlegacycode.com/blog/key-points-of-working-effectively-with-legacy-code/)

## Characterization tests

> "A characterization test is a test that characterizes the
> actual behavior of a piece of code."

Characterization tests **do not assert intended behavior**. They
assert **current behavior**, however surprising. The test
exists to lock down what the code actually does so you can
change it safely.

Process:

1. Write a test that calls the code with a representative input.
2. Run the test; it will likely fail.
3. Capture the actual output.
4. Update the assertion to match the actual output (with a
   comment: "characterizes current behavior, not ideal").
5. Commit. Now you have a safety net.

These are also called **Approval Tests**, **Snapshot Tests**,
or **Golden Master tests**, depending on tooling.

> Reference: [Characterization Tests — Daedtech](https://daedtech.com/characterization-tests/)

## The Sprout technique

When you cannot test existing code in time, **isolate new
functionality elsewhere**:

1. Create the new code in a new method or class.
2. Unit test the new code thoroughly.
3. Identify the insertion point in the legacy code.
4. Call the new code from the legacy code.

Example: a `uniqueEntries()` method with tested dedupe logic,
called from an untested legacy method that needs deduplication.

## The Wrap technique

When new logic must run before or after existing code:

1. Rename the old method to something like `_old_<name>`.
2. Create a new method with the original name and signature.
3. Call the old method from the new method.
4. Add new logic before and/or after the call.

The old method becomes a seam you can override in tests of the
new method.

## Seams

A **seam** is a place where you can alter behavior without
editing the code in place. Common seams:

- **Object seam** — subclass and override in tests.
- **Function seam** — pass a function as a parameter.
- **Preprocessor seam** — `#ifdef` for C-family languages.
- **Link seam** — replace a deployed dependency at test time.

When the code has no seam at the change point, the first job
is to **create one** (Sprout, Wrap, parameterize, extract
interface). Once a seam exists, characterization tests can be
written.

## Brownfield protocol for agent-driven projects

When an agent is asked to modify existing code:

1. **Inspect the system first.** Read existing files, identify
   patterns, run the test suite (if any), and inventory debt.
2. **Reconstruct the implicit specification.** If the code has
   tests, the spec is the tests. If it does not, the spec is
   observable behavior plus documentation.
3. **Propose incremental changes.** Do not rewrite the
   architecture as the first move.
4. **Preserve compatibility when it is a requirement.** A
   breaking change requires an explicit decision, not a side
   effect.
5. **Identify consumers before changing public interfaces.**
   Grep, dependency analysis, or runtime logs.
6. **Add characterization tests at the seam** before changing
   behavior.
7. **Make the change small.** One PR-sized diff.
8. **Re-run the existing suite** plus the new characterization
   tests.
9. **Refactor only with green tests.** Not before.

## Agent-specific cautions

Per Mitchell Hashimoto's experience with agent adoption:

- **"End-of-day" agents** for brownfield are an acceptable
  pattern: agents produce research or triage reports overnight
  without writing code, and humans review in the morning.
- **Do not let agents ship code to legacy systems unsupervised.**
  Risk of breaking undocumented behavior is too high.
- **Slower, more thoughtful models for harder changes.**
  Trade speed for fewer regressions.
- **Give agents verification hooks.** The most effective agent
  pattern for brownfield is: tests + linters + screenshots +
  diff scripts, paired with AGENTS.md describing them.

> Reference: [My AI adoption journey — Mitchell Hashimoto](https://mitchellh.com/writing/my-ai-adoption-journey)

## When "improvement" is the wrong move

Do not "improve" legacy code without first asking:

- Are other components depending on this behavior?
- Is the behavior documented anywhere outside the code?
- Is the change reversible?
- Will the existing test suite catch unintended effects?

If you cannot answer these, **characterize first, change
later**.

## Brownfield safety checklist

Before merging an agent's changes to legacy code:

- [ ] Existing tests still pass.
- [ ] Characterization tests added for the modified path.
- [ ] Public interfaces unchanged or breaking change documented.
- [ ] Consumers identified; breaking consumers updated.
- [ ] Side effects observed and recorded.
- [ ] Documentation updated where it exists.
- [ ] No "drive-by" refactors beyond the change scope.
- [ ] Reversibility analyzed; rollback plan recorded.
- [ ] Diff is small enough to review end-to-end.

## Cross-references

- `docs/tdd.md` — TDD red-green-refactor (not the same as
  characterization tests).
- `docs/sdd.md` — REQ→AC→Test→Impl traceability for greenfield.
- `docs/adr-template.md` — record significant brownfield
  decisions as ADRs.
- `evals/catalog.md` — EVAL-002 (ingestion) and EVAL-007
  (handoff/restart) apply when assessing existing systems.
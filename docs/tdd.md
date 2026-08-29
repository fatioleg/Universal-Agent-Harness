# Test-Driven Development

This document describes how to apply **TDD** and **test
discipline** in agent-driven projects, grounded in
established practice and adapted for AI-agent work.

The guidance here is **opt-in**. Not every project needs full
TDD; not every test belongs at the same pyramid layer.

## What TDD is

Test-Driven Development (TDD), per Kent Beck (described by
Martin Fowler): a technique for building software that guides
software development by writing tests.

The three-step cycle:

1. **RED** — Write a test for the next bit of functionality you
   want to add. The test fails for the right reason.
2. **GREEN** — Write the functional code until the test passes.
   Minimum code; no extra features.
3. **REFACTOR** — Improve the code. Both new and old code. No
   behavior change.

Fowler notes that the most common failure mode is **skipping
refactor**: "neglecting the third step" leaves a "messy
aggregation of code fragments," though at least with tests.

> Reference: [TestDrivenDevelopment — Martin Fowler](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

## When TDD applies

TDD is a good fit when:

- Behavior is deterministic or near-deterministic.
- Acceptance criteria can be expressed as executable checks.
- The cost of a regression is high relative to writing the
  test.
- The interface is being designed (TDD forces interface thinking
  before implementation).
- The team (or agent) has discipline to actually run the cycle.

## When TDD does NOT apply

TDD is **not** mandatory everywhere. Skip or soften TDD when:

- **Exploration** — investigating what is even possible.
- **Disposable prototypes** — code that will be rewritten.
- **Initial scientific investigation** — running computations to
  discover behavior, not to ship behavior.
- **Trivial configuration** — boilerplate, glue, paths.
- **Experimental visualization** — pictures to inform a design
  decision.
- **Generated code** — produced by tools, validated by other
  means.
- **Non-deterministic outputs** — pure LLM prose, image
  generation.

When skipping TDD:

1. Record that this is exploration.
2. Keep the experiment isolated.
3. Decide when the behavior will be stabilized.
4. Introduce tests when exploration becomes production code.

## The Test Pyramid

Per Martin Fowler's [Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html):

| Layer | Scope | Quantity | Speed | Cost |
|---|---|---|---|---|
| **Unit** | One function, class, component | Many | Fast | Cheap |
| **Integration** | Two or more components together | Some | Slower | Moderate |
| **End-to-end** | Full system flow | Few | Slow | Expensive |

Shape matters: lots of small unit tests, fewer integration
tests, very few e2e tests. The inverted "ice-cream cone"
anti-pattern (many e2e, few unit) is the wrong shape.

Rules from the pyramid:

- "Push your tests as far down the test pyramid as you can."
- "If a higher-level test spots an error and there's no
  lower-level test failing, you need to write a lower-level
  test."
- Aim to reduce e2e tests to a bare minimum of high-value user
  journeys.
- Tests should describe **observable behavior**, not
  implementation. "If I enter values `x` and `y`, will the
  result be `z`?" — not "will the method call class A first?"
- "Don't test trivial code" — no unit tests for getters/setters.

## The Agent Testing Pyramid

LLM-agent systems have a parallel pyramid (LangWatch, June 2025;
[Rafal Wilinski](https://rwilinski.ai/posts/evals-pyramid/)):

| Layer | What it covers | When |
|---|---|---|
| **Deterministic unit tests** | API connections, data transformations, memory, auth, rate limiting, error handling | Always. Catches pipeline breaks that manifest as confusing agent failures. |
| **Evals & optimization** | Retrieval accuracy, response quality metrics, prompt optimization, fine-tuning | When a component has a "data science feeling" — datasets and metrics. Requires ML discipline. |
| **Simulations** | Multi-turn conversation, edge cases, binary business outcomes | To verify the agent solves real problems end-to-end. Carefully crafted scenarios because "a dataset for multi-turn optimization would be prohibitively expensive." |

The pyramid is not rigid. Early-stage agents may skip
simulations; mature systems may invest heavily in evals.

Practical guidance: **always** keep deterministic unit tests for
the plumbing. Without them, agent failures look like model failures.

## Mutation testing and approved scenarios

Böckeler argues that **coverage is insufficient**. Two
complementary practices:

- **Mutation testing** (Stryker for JS/TS): introduce small code
  mutations and check whether the test suite catches them.
  Reveals tests that exercise code without asserting on it.
- **Approved scenarios**: pre-validated reference outputs that
  new runs must match within tolerance. Acknowledges that humans
  cannot review every LLM output but can review a curated set.

> Reference: [Sensors for coding agents — Birgitta Böckeler](https://martinfowler.com/articles/sensors-for-coding-agents.html)

## Characterization tests (brownfield)

For legacy code, the discipline is **characterization tests**,
not TDD.

Per Michael Feathers:

> "A characterization test is a test that characterizes the
> actual behavior of a piece of code."

These tests capture **current behavior** (not intended
behavior), creating a safety net before refactoring. Also
known as Approval Testing or Golden Master testing.

`docs/brownfield.md` in this repo expands on Feathers' legacy
code change algorithm in detail.

> Reference: [Working Effectively with Legacy Code — Michael Feathers (key points)](https://understandlegacycode.com/blog/key-points-of-working-effectively-with-legacy-code/)

## Test-driven red-green-refactor in agent work

When the agent is the implementer:

1. The agent writes the test **before** the implementation.
2. The agent runs the test to confirm it fails for the right
   reason.
3. The agent writes the minimum implementation to pass.
4. The agent runs the test to confirm it passes.
5. The agent refactors without changing behavior, with the test
   still green.

The harness does **not** enforce this discipline; the agent (or
the orchestrator) does. The Universal Harness provides
**observability** (`observability-run.schema.json`) so each
cycle can be recorded.

Böckeler's warning applies: AI-generated tests are often
insufficient. Mutation testing closes the gap.

## Test discipline rules (from sources)

Synthesized from Fowler, Feathers, Böckeler, Beck:

1. **Write the test first** — even a sloppy test beats no test.
2. **Tests describe behavior, not implementation.** Refactors
   must not break tests.
3. **Push tests down the pyramid** — small and fast at the
   bottom.
4. **Each behavior change needs a test** — otherwise regressions
   hide.
5. **Coverage is a visibility indicator, not a quality
   measure.** Pair coverage with mutation testing.
6. **One condition per test** — given/when/then structure.
7. **Test code is production code.** Review it accordingly.
8. **Bugs found become regression tests** — exploratory findings
   feed the pyramid.
9. **Don't test trivial code** — getters, setters, pure forwarders.
10. **When TDD is wrong** — record why and move on.

## Definition of Done for tests

A task is not done when the code runs. Per the SDD archetype, a
task is done when, as applicable:

- Requirement satisfied.
- Acceptance criteria satisfied (executable checks passed).
- Tests added at the right pyramid layer.
- No regressions introduced (regression suite green).
- Integration validated where applicable.
- Errors handled.
- Documentation updated.
- No critical hypothesis left hidden.

## Cross-references

- `docs/sdd.md` — SDD workflow, REQ→AC→Test→Impl traceability.
- `docs/brownfield.md` — Feathers' algorithm and characterization tests.
- `docs/adr-template.md` — ADR format for major test strategy decisions.
- `evals/catalog.md` — universal eval categories that map to
  agent-test pyramid layers.
- `core/schemas/extension/test-case.schema.json` — test case
  record shape.
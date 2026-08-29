# Test Cases — <Project>

Each acceptance criterion (`AC-NNNN-NN`) has one or more test
cases (`TEST-NNNN-NN`). Each test has a pyramid layer and an
approach.

## Pyramid mix

| Layer | Count | Approach mix |
|---|---|---|
| Unit | n | mostly TDD |
| Integration | n | mostly contract |
| End-to-end | n | critical journeys only |
| Regression | n | from bug reports |
| Characterization | n | brownfield only |
| Scientific / numerical | n | from known datasets |
| Agent / LLM eval | n | from `evals/catalog.md` |
| Simulation | n | end-to-end agent scenarios |

## Tests

### TEST-0001-01 — <name>

- **AC**: AC-0001-01
- **Pyramid layer**: unit
- **Approach**: tdd
- **Given**: <preconditions>
- **When**: <action>
- **Then**: <expected observable behavior>
- **Last result**: passed / failed / not-run
- **Sensor**: <sensor-id or `n/a`>

### TEST-0001-02 — <name>

- **AC**: AC-0001-02
- **Pyramid layer**: unit
- **Approach**: tdd
- **Given**: ...
- **When**: ...
- **Then**: ...
- **Last result**: ...
- **Sensor**: ...

## Mutation coverage

If mutation testing is wired (Böckeler recommendation):

- Mutation tool: <tool>
- Threshold: <killed mutants / total mutants>
- Last run: <date>
- Surviving mutants: <list, or `none`>

## Notes

- Each test asserts **observable behavior**, not implementation.
  Refactors must not break tests.
- One condition per test (given/when/then).
- Tests at the bottom of the pyramid first.
- For agentic / LLM components, prefer the Agent Testing
  Pyramid: deterministic unit (base) → evals (middle) →
  simulations (peak).
- For brownfield work, write characterization tests first,
  TDD-style unit tests later.
# Archetype: software-development

## When to use

- Primary deliverable is code or a deployable artifact.
- Tests, linters, and CI are the primary sensors.
- The project follows a conventional software lifecycle.

## Inherits from

- `core/`
- `bootstrap/`

## Differs from base by

- **Knowledge strategy**: lexical (code, docs).
- **Default sensors**: EVAL-006 (artifact), EVAL-008
  (coordination), plus project-specific tests, linters, type
  checkers, mutation testing.
- **Permission defaults**: read/write inside project; execute
  declared tools; network task-justified.
- **Required scaffolds**: project conventions (tests, CI config).

## Required sensors

- Project-defined tests (unit, integration, contract, e2e —
  see `docs/tdd.md` for the pyramid)
- Linter (ESLint, Ruff, etc.)
- Type checker (mypy, tsc, etc.)
- EVAL-006 artifact generation
- Mutation testing (Stryker for JS/TS; optional but recommended
  per Böckeler — coverage alone is insufficient)

## Typical tool profile

- Test runner
- Linter and formatter
- Type checker
- Build/CI system
- dependency-cruiser for module boundaries (Böckeler)
- Stryker for mutation testing (Böckeler)

## Evidence & provenance requirements

- Every commit references a task or issue.
- Every PR has a CI run record.
- Every release has a tag and a changelog entry.

## Agent topology default

Level A. Tools and CI gates suffice. Escalate to B for critical
infrastructure changes.

## Autonomy defaults

- Run tests: L4.
- Apply formatting: L4.
- Refactor: L2.
- Modify public API: L1.
- Publish a release: L0.

## Open questions / not-yet-defined

- How to handle generated code (provenance of generated files).
- When to require a second reviewer for security-sensitive paths.

## Example instantiation

A library maintained by one or two engineers with conventional CI.
The harness runs tests on every commit, applies formatting,
updates the changelog, and opens a PR with the changes.

## Cross-references

- `docs/tdd.md` — TDD red-green-refactor and the test pyramid.
- `docs/brownfield.md` — when modifying existing code rather
  than greenfield.
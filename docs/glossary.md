# Glossary

Terms used across the Universal Agent Harness repository and
generated project harnesses.

## Agent

An LLM-based entity that reasons and acts using a model, tools, and
context. An agent is one component of a harness; the harness
includes the controls, environment, and feedback mechanisms.

## Archetype

A reference pattern for a recurring scientific or engineering
workflow. Archetypes in `archetypes/` are documentation only; they
are NOT H1 packages and cannot be merged into a project's lock.
Promotion requires at least two real pilots and an AD.

## Bootstrap Report

The 12-section report produced at the end of dry-run discovery
(see `bootstrap/BOOTSTRAP.md` §10). Ends with `APPROVE`, `REVISE`,
or `BLOCK`.

## Bootstrap state machine

```
INITIAL → DISCOVERED → PROPOSED → APPROVED → MATERIALIZED → VALIDATED
```

Every project starts in dry-run; do not move to MATERIALIZED without
human approval when the proposal contains material scientific,
strategic, external, irreversible, permission, publication, or cost
decisions.

## Capability overlay

A cross-cutting behavior pack (e.g., scientific evidence) that
applies regardless of domain. Distinct from a lifecycle profile
and a domain pack.

## Computational sensor

A deterministic check executed by a tool: type checker, RDKit
SMILES canonicalization, schema validator, dependency-cruiser,
Stryker mutation, DOI resolver, GitLeaks. Preferred over
inferential sensors when the property is deterministically
testable (Böckeler).

## Domain pack

Domain terminology, tools, sensors, and conventions for a single
domain (e.g., computational chemistry, plant physiology).

## Evidence ledger

A durable record of claims with their sources, locations, evidence
types, and validation status. Schema in
`core/schemas/extension/evidence-ledger.schema.json`.

## Failure registry

A durable record of failures with their root causes, harness
patches, and regression sensors. Schema in
`core/schemas/extension/failure-registry.schema.json`. The harness
learns from failures by promoting them into sensors, evals, or
guides.

## Guides

Feedforward controls: specifications, instructions, constraints,
examples, architecture documents, conventions, tool descriptions.

## H0 / H1 / H2 / H3

Configuration layers:

- H0: universal invariants, defaults, schemas (this repository).
- H1: optional lifecycle profile, capability overlay, or domain pack.
- H2: project configuration and bindings.
- H3: short-lived task restrictions and context.

Resolution is typed and pinned via `core/merge-policy.yaml`.

## Harness

The environment, controls, context, capabilities, feedback
mechanisms, and limits within which an agent operates. A harness
makes correct behavior easy to perform and verify, and makes
incorrect behavior visible, recoverable, traceable, or impossible
to pass through gates.

## Inferential sensor

An LLM-judge review prompt. Reserved for properties that genuinely
require inference (semantic meaning, ambiguity, scientific
interpretation).

## Lifecycle profile

A recurring project workflow (e.g., long-running literature review).

## Lock file

`harness.lock.yaml` in a generated project. Pins the upstream
H0 version and commit, the H1 packages, the H2 project hash, and
the resolved permissions, capabilities, topology, and assurance
floors.

## Material gate

A human approval step required when a decision is scientific,
strategic, external, irreversible, publication-related, sending-
related, spending-related, or permission-expanding (INV-006).

## Permission profile

Per-agent-role capability scope. Schema in
`core/schemas/extension/permission-profile.schema.json`.

## Sensor

A feedback control. See computational sensor and inferential
sensor.

## Tool contract

A specification describing a tool's capability, input/output
schema, permissions required, side effects, failure modes, and
eval status. Schema in
`core/schemas/extension/tool-contract.schema.json`. Contracts
ship without implementations per AD-003 / AD-010.

## Validation vs QA vs Eval

Three distinct assurance questions:

- Validation: "Is this execution/result correct?"
- QA: "Does this artifact satisfy its requirements?"
- Eval: "Does this harness still perform across representative
  cases?"

Validation checks a single result. QA checks an artifact against
its spec. Eval checks the harness itself across a representative
test set.

## Source references

- OpenAI — Harness engineering blog post.
- Anthropic — Managed agents, Harness design for long-running apps.
- Mitchell Hashimoto — My AI adoption journey.
- Birgitta Böckeler — Sensors for coding agents (Martin Fowler site).
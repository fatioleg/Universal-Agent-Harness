# Principle 03: Least Privilege

## Statement

Effective agent permissions must be limited to the capabilities
required by the approved task. Expansion beyond the universal defaults
requires an explicit human gate.

## Why this is a principle

Anthropic managed-agents describes a structural fix where credentials
are bundled with the resource and never reachable from the agent
sandbox; this prevents prompt injection from extracting tokens.
Hashimoto's adoption story recommends running agents one at a time
and disabling desktop notifications to control context switching.
Both rely on a least-privilege baseline.

## What it requires

- A permission profile (`core/schemas/extension/permission-profile.schema.json`)
  per agent role.
- Universal defaults from `core/universal.yaml` (`delete: denied`,
  `install: denied`, `publish: denied`, `send: denied`, `spend: denied`,
  `merge: denied`).
- Expansion requires recording the decision in
  `core/schemas/extension/decisions.schema.json` with `decided_by: human`.

## When this can be overridden

Overridable per task with explicit human approval recorded in the
decision log. Cannot be silently removed by a more specific layer
(INV-010).

## How to verify

- INV-005, INV-006, INV-010 lock checks.
- The lock file's `permissions` field matches the approved profile.

## Failure mode if ignored

A prompt-injection-style prompt causes the agent to publish, send,
spend, or merge. The blast radius scales with the permissions that
were granted.
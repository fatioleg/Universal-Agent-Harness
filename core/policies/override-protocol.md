# Override Protocol

H0 principles (and the invariants they map to) are defaults, not
absolutes. A project may deviate, but not silently. This protocol
defines the conditions, the recording requirements, and the
non-overridable principles.

## When an override is allowed

A principle can be deviated from only when:

1. The deviation is recorded in the project's decisions file (schema
   in `core/schemas/extension/decisions.schema.json`).
2. The decision lists the principle(s) affected.
3. The decision lists a compensating control.
4. The decision is approved by a human (`decided_by: human`).
5. The deviation is logged in the lock file or its companion
   manifest so a reviewer can audit.

## Non-overridable principles

Three principles are bedrock. They cannot be deviated from by any
layer, including the project layer, because removing them collapses
the harness's ability to function:

- **Preserve sources** — without sources, evidence provenance has no
  referent. INV-001.
- **Maintain provenance** — without provenance, claims cannot be
  distinguished from hallucinations. INV-002.
- **Expose failures** — without failure visibility, the harness stops
  learning from its own mistakes. INV-009.

These map to invariants with `enforcement: locked` in
`core/invariants.yaml` and to the non-silent-weakening rule (INV-010).

## Overridable principles

The other six principles can be deviated from with the protocol
above:

- Least privilege (INV-005, INV-006)
- Verify critical outputs (INV-008)
- Maintain state (INV-003, INV-004)
- Progressive disclosure (INV-007)
- Prefer deterministic (INV-008)
- Reproducibility (INV-003, INV-012)

## Compensating controls

A compensating control is any mechanism that reduces the risk of the
overridden principle. Examples:

- For an overridden least-privilege: scope the expansion to one path,
  one task, one human approver; require a post-task audit.
- For an overridden verify-critical-outputs: add a human review
  step; require a second observer.
- For an overridden progressive-disclosure: split the entrypoint into
  nested files; validate the split with a readability test.

## Recording format

```yaml
- decision_id: DEC-0001
  title: "Allow network read for literature agent"
  context: "..."
  options_considered:
    - option: "keep network denied"
      tradeoffs: "literature search is impossible"
    - option: "allow network read"
      tradeoffs: "expands default-deny surface"
  decision: "allow network read for literature agent role only"
  rationale: "literature search is the primary capability; alternatives
    require ingesting a local corpus that does not yet exist"
  decided_by: "human:owner"
  supersedes: null
  created_at: "2026-08-29T12:00:00Z"
```

## Reviewer checklist

When auditing a project's overrides:

- [ ] Every override has a decision record with a human approver.
- [ ] No override targets a non-overridable principle.
- [ ] Each override has a named compensating control.
- [ ] The compensating control is itself observable (sensor, eval, or
      human gate).
- [ ] The override expires (a duration field) or is reviewed on a
      cadence.

## Reference

See `core/principles/` for the full principle texts and the
invariant mappings.
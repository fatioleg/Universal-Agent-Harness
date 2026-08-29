# Examples

Placeholder for worked examples. Each example will demonstrate a
full end-to-end harness resolution for a real or representative
project.

## Why this folder is empty in v0.3.0

AD-003 defers executable tooling until pilots demonstrate stable
classifiers. A worked example is most valuable once at least one
real project has used the harness end-to-end. Until then, this
folder exists to commit to the intent.

## What an example will contain

A future example will include:

- `project.yaml` (project input)
- `harness.lock.yaml` (resolved harness)
- `evidence/` (sample entries)
- `decisions/` (sample decisions)
- `runs/` (sample observability records)
- A short narrative explaining the choices

## When to add the first example

Add an example after:

1. At least one real project has been bootstrapped via the
   protocol.
2. The Bootstrap Report and lock file have been human-approved.
3. The pilot's results (with private content redacted) can be
   shared.

Until then, refer to:

- `bootstrap/project-input.example.yaml` — a project input shape.
- `templates/project/project.yaml.template` — the project input
  template.
- `templates/project/harness.lock.yaml.template` — the lock
  template.
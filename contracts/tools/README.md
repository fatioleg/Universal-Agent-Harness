# Tool Contracts

YAML specifications of agent-invokable tools. Each contract describes
what a tool does, what it requires, and what it returns. **No
implementations ship in v0.3.0** (AD-003, AD-010).

## What a contract gives an agent

A contract tells the agent:

- which capability the tool provides;
- which inputs the tool accepts and which outputs it produces;
- which permissions the tool requires;
- which side effects the tool has;
- which failure modes the tool exhibits and how to detect and recover
  from each;
- the current `eval_status` (untested at v0.3.0 launch).

A contract does NOT tell the agent:

- how the tool is implemented (Python, Bash, MCP, HTTP);
- where the tool runs (local, container, cloud);
- whether the tool is currently available.

## Relationship to schemas

Every contract here conforms to
`core/schemas/extension/tool-contract.schema.json`. The validator
(`scripts/validate_repo.py`) parses each contract against that
schema.

## Promotion path: contract → implementation

1. At least two real projects reference the contract in their
   `harness.lock.yaml` capability list.
2. The contract's `eval_status` field has been moved from `untested`
   to a documented state after a pilot.
3. An AD records the promotion and the implementation language.
4. The implementation lands in `scripts/` (or a designated tool
   location) at v0.4.0+.

Until then, the contract is a planning artifact, not a callable.

## The 7 contracts

| ID | Capability | Primary source |
|---|---|---|
| check-invariants | Verify a project's lock honors locked invariants | Hashimoto, this repo's INV series |
| diff-harness | Show changes between current and target H0 version | This repo's migration rule |
| verify-artifact | Generic artifact verifier with sensor profile | Hashimoto, Böckeler |
| list-events | Read event log / state for debugging | Anthropic managed-agents |
| sensor-trend | Aggregate sensor pass/fail trends | Böckeler (sensors-cli) |
| lock-drift-check | Verify project's pinned upstream commit matches actual | This repo INV-010 |
| scaffold-project | Generate project-specific harness from input | OpenAI templates |
| caveman-compress | Compress a retrieved text slice to fit a token budget | This repo's knowledge-digestion pipeline (Stage 1) |
| markitdown-normalize | Convert PDF/DOCX/PPTX/XLSX/HTML/image to canonical Markdown | Microsoft MarkItDown (Stage 2) |
| graphify-build | Build a knowledge graph with evidence pointers on every edge | Graphify (Stage 3) |
| obsidian-interface | Sync a canonical directory to an Obsidian vault and back | Obsidian (Stage 4) |
| notebooklm-explore | Send a corpus and query to NotebookLM via MCP, ephemeral by default | NotebookLM MCP (Stage 5, optional) |
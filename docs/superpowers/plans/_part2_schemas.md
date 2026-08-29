## Task 2: Create core/schemas/extension/ directory and 8 JSON Schemas

**Files:**
- Create: `core/schemas/extension/state.schema.json`
- Create: `core/schemas/extension/evidence-ledger.schema.json`
- Create: `core/schemas/extension/decisions.schema.json`
- Create: `core/schemas/extension/tool-contract.schema.json`
- Create: `core/schemas/extension/permission-profile.schema.json`
- Create: `core/schemas/extension/failure-registry.schema.json`
- Create: `core/schemas/extension/eval-result.schema.json`
- Create: `core/schemas/extension/observability-run.schema.json`

- [ ] **Step 1: Create state.schema.json**

Write `core/schemas/extension/state.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://local.myharness/schemas/extension/state.schema.json",
  "title": "Project State",
  "type": "object",
  "additionalProperties": false,
  "required": ["project_id", "phase", "updated_at"],
  "properties": {
    "project_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{1,63}$"},
    "phase": {
      "enum": [
        "understand", "discover", "specify", "configure",
        "plan", "execute", "observe", "sense",
        "repair", "verify", "evaluate", "persist", "learn"
      ]
    },
    "current_task": {"type": ["string", "null"]},
    "active_agents": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
    "pending_gates": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
    "blockers": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["id", "description", "owner", "since"],
        "properties": {
          "id": {"type": "string"},
          "description": {"type": "string"},
          "owner": {"type": "string"},
          "since": {"type": "string", "format": "date-time"}
        }
      }
    },
    "next_action": {"type": "string"},
    "updated_at": {"type": "string", "format": "date-time"}
  }
}
```

- [ ] **Step 2: Create evidence-ledger.schema.json**

Write `core/schemas/extension/evidence-ledger.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://local.myharness/schemas/extension/evidence-ledger.schema.json",
  "title": "Evidence Ledger Entry",
  "type": "object",
  "additionalProperties": false,
  "required": ["claim_id", "claim", "source_id", "evidence_type", "status", "created_at"],
  "properties": {
    "claim_id": {"type": "string", "pattern": "^CLAIM-[0-9]{4,}$"},
    "claim": {"type": "string", "minLength": 1},
    "source_id": {"type": "string"},
    "source_location": {"type": "string"},
    "evidence_type": {
      "enum": ["experimental", "observational", "theoretical", "computational", "citation", "derivation", "quote"]
    },
    "confidence": {"enum": ["high", "medium", "low", "unverified"], "default": "unverified"},
    "status": {"enum": ["active", "superseded", "disputed", "retracted"]},
    "used_in": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
    "validation_status": {
      "enum": ["unvalidated", "computational-check", "peer-reviewed", "expert-verified"],
      "default": "unvalidated"
    },
    "created_at": {"type": "string", "format": "date-time"}
  }
}
```

- [ ] **Step 3: Create decisions.schema.json**

Write `core/schemas/extension/decisions.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://local.myharness/schemas/extension/decisions.schema.json",
  "title": "Decision Record",
  "type": "object",
  "additionalProperties": false,
  "required": ["decision_id", "title", "context", "decision", "decided_by", "created_at"],
  "properties": {
    "decision_id": {"type": "string", "pattern": "^DEC-[0-9]{4,}$"},
    "title": {"type": "string", "minLength": 1},
    "context": {"type": "string"},
    "options_considered": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["option"],
        "properties": {
          "option": {"type": "string"},
          "tradeoffs": {"type": "string"}
        }
      }
    },
    "decision": {"type": "string"},
    "rationale": {"type": "string"},
    "decided_by": {"type": "string"},
    "supersedes": {"type": ["string", "null"]},
    "created_at": {"type": "string", "format": "date-time"}
  }
}
```

- [ ] **Step 4: Create tool-contract.schema.json**

Write `core/schemas/extension/tool-contract.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://local.myharness/schemas/extension/tool-contract.schema.json",
  "title": "Tool Contract",
  "type": "object",
  "additionalProperties": false,
  "required": ["tool_id", "capability", "input_schema", "output_schema", "side_effects", "eval_status"],
  "properties": {
    "tool_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{1,63}$"},
    "capability": {"type": "string"},
    "input_schema": {"type": "string"},
    "output_schema": {"type": "string"},
    "permissions_required": {
      "type": "array",
      "items": {"enum": ["read", "write", "modify", "delete", "execute", "network", "install", "publish", "send", "spend", "merge"]},
      "uniqueItems": true
    },
    "side_effects": {"enum": ["none", "read", "write", "external", "irreversible"]},
    "failure_modes": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["mode", "detection", "recovery"],
        "properties": {
          "mode": {"type": "string"},
          "detection": {"type": "string"},
          "recovery": {"type": "string"}
        }
      }
    },
    "cost_estimate": {"type": "string"},
    "latency_estimate": {"type": "string"},
    "validation_method": {"type": "string"},
    "eval_status": {"enum": ["untested", "passing", "flaky", "failing"]}
  }
}
```

- [ ] **Step 5: Create permission-profile.schema.json**

Write `core/schemas/extension/permission-profile.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://local.myharness/schemas/extension/permission-profile.schema.json",
  "title": "Permission Profile",
  "type": "object",
  "additionalProperties": false,
  "required": ["profile_id", "agent_role", "capabilities", "granted_by"],
  "properties": {
    "profile_id": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{1,63}$"},
    "agent_role": {"type": "string"},
    "capabilities": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "read": {"type": "array", "items": {"type": "string"}},
        "write": {"type": "array", "items": {"type": "string"}},
        "modify": {"type": "array", "items": {"type": "string"}},
        "delete": {"type": "boolean"},
        "execute": {"type": "array", "items": {"type": "string"}},
        "network": {"enum": ["none", "read", "full"]},
        "install": {"type": "boolean"},
        "publish": {"type": "boolean"},
        "send": {"type": "array", "items": {"type": "string"}},
        "spend": {"type": "string"},
        "merge": {"type": "boolean"}
      }
    },
    "duration": {"type": "string"},
    "granted_by": {"type": "string"}
  }
}
```

- [ ] **Step 6: Create failure-registry.schema.json**

Write `core/schemas/extension/failure-registry.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://local.myharness/schemas/extension/failure-registry.schema.json",
  "title": "Failure Registry Entry",
  "type": "object",
  "additionalProperties": false,
  "required": ["failure_id", "pattern", "root_cause", "status", "occurred_at"],
  "properties": {
    "failure_id": {"type": "string", "pattern": "^FAIL-[0-9]{4,}$"},
    "pattern": {"type": "string"},
    "root_cause": {"type": "string"},
    "harness_patch": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "modified_files": {"type": "array", "items": {"type": "string"}},
        "schema_changes": {"type": "array", "items": {"type": "string"}},
        "new_sensor": {"type": ["string", "null"]},
        "new_policy": {"type": ["string", "null"]}
      }
    },
    "regression_sensor": {"type": ["string", "null"]},
    "status": {"enum": ["detected", "analyzing", "patching", "fixed", "monitoring"]},
    "linked_eval": {"type": ["string", "null"]},
    "occurred_at": {"type": "string", "format": "date-time"},
    "fixed_at": {"type": ["string", "null"], "format": "date-time"}
  }
}
```

- [ ] **Step 7: Create eval-result.schema.json**

Write `core/schemas/extension/eval-result.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://local.myharness/schemas/extension/eval-result.schema.json",
  "title": "Eval Result",
  "type": "object",
  "additionalProperties": false,
  "required": ["eval_id", "category", "expected", "actual", "passed", "harness_version", "timestamp"],
  "properties": {
    "eval_id": {"type": "string", "pattern": "^EVAL-[0-9]{3,}$"},
    "category": {
      "enum": [
        "retrieval", "ingestion", "extraction", "numerical-audit",
        "citation", "artifact-generation", "handoff", "coordination",
        "conflict-resolution", "recovery", "archetype-specific"
      ]
    },
    "input": {"type": "string"},
    "expected": {"type": "string"},
    "actual": {"type": "string"},
    "passed": {"type": "boolean"},
    "metrics": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "tokens": {"type": "integer", "minimum": 0},
        "cost": {"type": "number", "minimum": 0},
        "latency_ms": {"type": "integer", "minimum": 0},
        "tool_failures": {"type": "integer", "minimum": 0},
        "human_interventions": {"type": "integer", "minimum": 0}
      }
    },
    "harness_version": {"type": "string"},
    "model_id": {"type": "string"},
    "timestamp": {"type": "string", "format": "date-time"}
  }
}
```

- [ ] **Step 8: Create observability-run.schema.json**

Write `core/schemas/extension/observability-run.schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://local.myharness/schemas/extension/observability-run.schema.json",
  "title": "Observability Run Record",
  "type": "object",
  "additionalProperties": false,
  "required": ["run_id", "task_id", "agent_id", "harness_version", "started_at", "final_status"],
  "properties": {
    "run_id": {"type": "string"},
    "task_id": {"type": "string"},
    "agent_id": {"type": "string"},
    "model_id": {"type": "string"},
    "harness_version": {"type": "string"},
    "started_at": {"type": "string", "format": "date-time"},
    "ended_at": {"type": ["string", "null"], "format": "date-time"},
    "tools_used": {"type": "array", "items": {"type": "string"}, "uniqueItems": true},
    "inputs_hash": {"type": "string"},
    "outputs_hash": {"type": "string"},
    "tokens_in": {"type": "integer", "minimum": 0},
    "tokens_out": {"type": "integer", "minimum": 0},
    "cost": {"type": "number", "minimum": 0},
    "compute_seconds": {"type": "number", "minimum": 0},
    "retries": {"type": "integer", "minimum": 0},
    "sensor_results": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["sensor_id", "result"],
        "properties": {
          "sensor_id": {"type": "string"},
          "result": {"type": "string"}
        }
      }
    },
    "failures": {"type": "array", "items": {"type": "string"}},
    "final_status": {"enum": ["success", "failed", "escalated", "partial"]}
  }
}
```

- [ ] **Step 9: Verify all 8 schemas parse as JSON Schema**

Run:

```bash
python -c "
import json
from pathlib import Path
from jsonschema import Draft202012Validator
for p in sorted(Path('core/schemas/extension').glob('*.json')):
    Draft202012Validator.check_schema(json.loads(p.read_text()))
    print(f'OK: {p}')
"
```

Expected: 8 lines, each `OK: core/schemas/extension/<name>.schema.json`
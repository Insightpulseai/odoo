# Auto-Claude Framework Implementation Plan

## Phase 1: Core Enhancements

### 1.1 Enhance ipai_agent_core

**Files to modify:**
- `addons/ipai/ipai_agent_core/models/skill.py`
  - Add `rate_limit_per_minute` (Integer)
  - Add `timeout_seconds` (Integer, default=300)
  - Add `cooldown_seconds` (Integer, default=0)
  - Add `required_group_ids` (Many2many to res.groups)

- `addons/ipai/ipai_agent_core/models/run.py`
  - Add `external_ref` (Char) for external correlation IDs
  - Add `artifacts` (One2many) for output files
  - Add timeout enforcement in `_execute_workflow`

- `addons/ipai/ipai_agent_core/security/security.xml`
  - Add group `ipai.group_agent_user` for API access

### 1.2 Add Artifact Model

**New file:** `addons/ipai/ipai_agent_core/models/artifact.py`
```python
class IpaiAgentArtifact(models.Model):
    _name = "ipai.agent.artifact"
    _description = "Agent Run Artifact"

    run_id = fields.Many2one("ipai.agent.run", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    artifact_type = fields.Selection([
        ("file", "File"),
        ("patch", "Git Patch"),
        ("log", "Log Output"),
        ("report", "Report"),
    ])
    content = fields.Text()
    attachment_id = fields.Many2one("ir.attachment")
```

## Phase 2: REST API Module

### 2.1 Create ipai_skill_api

**Structure:**
```
addons/ipai/ipai_skill_api/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── services/
│   ├── __init__.py
│   ├── skill_service.py
│   └── run_service.py
├── datamodels/
│   ├── __init__.py
│   ├── skill_datamodel.py
│   └── run_datamodel.py
└── security/
    ├── ir.model.access.csv
    └── security.xml
```

**Endpoints (base_rest pattern):**
```python
class SkillService(Component):
    _inherit = "base.rest.service"
    _name = "skill.service"
    _usage = "skills"
    _collection = "ipai.skill.api"

    @restapi.method(...)
    def search(self, **params):
        """GET /api/v1/skills"""

    @restapi.method(...)
    def get(self, key):
        """GET /api/v1/skills/{key}"""


class RunService(Component):
    _inherit = "base.rest.service"
    _name = "run.service"
    _usage = "runs"
    _collection = "ipai.skill.api"

    @restapi.method(...)
    def create(self, **params):
        """POST /api/v1/runs"""

    @restapi.method(...)
    def get(self, _id):
        """GET /api/v1/runs/{id}"""

    @restapi.method(...)
    def execute(self, _id):
        """POST /api/v1/runs/{id}/execute"""
```

## Phase 3: Knowledge Graph Integration

### 3.1 Supabase Schema

**Migration:** `supabase/migrations/20250106000000_kg_schema.sql`

Tables:
- `kg.nodes` - entities with kind/key/label/attrs
- `kg.edges` - relationships with predicate/weight
- `kg.evidence` - provenance links
- `kg.node_embeddings` - pgvector embeddings

RPCs:
- `kg.neighborhood(tenant, start, depth, predicates)`
- `kg.top_related(tenant, start, limit)`
- `kg.semantic_search(tenant, embedding, limit)`

### 3.2 KG Tool in Odoo

**New tool registration:**
```python
# In seed data
tool_kg_context = env['ipai.agent.tool'].create({
    'name': 'Fetch KG Context',
    'key': 'kg.fetch_context',
    'target_model': 'ipai.kg.bridge',
    'target_method': 'fetch_context',
    'description': 'Expand entity neighborhood from Knowledge Graph',
})
```

**Bridge model:** `addons/ipai/ipai_kg_bridge/`
- Calls Supabase RPC via `requests`
- Returns structured context for agent consumption

## Phase 4: Queue Integration

### 4.1 Add queue_job Dependency

**Update:** `addons/ipai/ipai_agent_core/__manifest__.py`
```python
"depends": [
    "base",
    "web",
    "mail",
    "queue_job",  # OCA
],
```

### 4.2 Async Execution

**Update:** `addons/ipai/ipai_agent_core/models/run.py`
```python
def action_execute_async(self):
    """Enqueue execution via queue_job."""
    for rec in self:
        rec.with_delay(
            priority=10,
            channel="root.agent",
            description=f"Execute skill: {rec.skill_id.name}"
        ).action_execute()
    return True
```

## Phase 5: E2E Testing

### 5.1 Odoo Unit Tests

**File:** `addons/ipai/ipai_agent_core/tests/test_skill_execution.py`
```python
class TestSkillExecution(TransactionCase):
    def test_skill_workflow_execution(self):
        """Test deterministic tool chain execution."""

    def test_run_state_transitions(self):
        """Test draft → running → ok/failed states."""

    def test_rate_limiting(self):
        """Test rate limit enforcement."""
```

### 5.2 API Contract Tests

**File:** `tests/api/test_skill_api.py`
```python
def test_list_skills():
    """GET /api/v1/skills returns active skills."""

def test_execute_run():
    """POST /api/v1/runs creates and executes."""

def test_unauthorized_access():
    """Requests without auth are rejected."""
```

### 5.3 Playwright Smoke Test

**File:** `tests/e2e/playwright/agent-core.spec.ts`
```typescript
test('Agent Core menu navigation', async ({ page }) => {
  // Login → Agent Core menu → Skills list
});

test('Create and execute run', async ({ page }) => {
  // Skills → select → Create Run → Execute
});
```

## Phase 6: Skill Definitions

### 6.1 Core Skills to Ship

| Skill Key | Description | Tools |
|-----------|-------------|-------|
| `odoo.module.audit` | Audit module against OCA standards | lint, manifest_check, deps_check |
| `odoo.module.scaffold` | Scaffold new module structure | create_dirs, write_manifest, write_models |
| `finance.ppm.health` | Check Finance PPM health | query_moves, check_balances, report |
| `kg.entity.expand` | Expand entity context | fetch_node, expand_neighbors, format |
| `ci.run.validate` | Validate CI pipeline | fetch_status, check_gates, summarize |

### 6.2 Skill Pack Structure

**File:** `skills/odoo-module-audit/skill.yaml`
```yaml
name: odoo_module_audit
version: 1.0.0
key: odoo.module.audit
description: Audit Odoo module against OCA standards

tools:
  - key: lint.python
    target_model: ipai.lint.runner
    target_method: run_python_lint
  - key: lint.manifest
    target_model: ipai.lint.runner
    target_method: check_manifest
  - key: lint.deps
    target_model: ipai.lint.runner
    target_method: check_dependencies

workflow:
  - lint.python
  - lint.manifest
  - lint.deps

intents:
  - audit this module
  - check OCA compliance
  - validate module structure

guardrails:
  - Do not modify source files
  - Report findings only
```

## Execution Order

1. **Week 1**: Phase 1 (core enhancements) + Phase 4 (queue_job dep)
2. **Week 2**: Phase 2 (REST API) + Phase 3 (KG schema)
3. **Week 3**: Phase 5 (E2E tests) + Phase 6 (skill definitions)
4. **Ongoing**: Iterate based on agent feedback

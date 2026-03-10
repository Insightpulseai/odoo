# IPAI Skills

Agent skills for the Auto-Claude framework. Each skill defines a deterministic workflow
that agents can execute via the Skill API.

## Skill Structure

```
skills/<skill-slug>/
├── skill.yaml          # Skill definition (required)
├── README.md           # Documentation (optional)
├── fixtures/           # Test fixtures (optional)
└── tests/              # Golden tests (optional)
```

## Skill Definition Schema

```yaml
name: skill_name
version: 1.0.0
key: namespace.skill.name  # Unique identifier
description: |
  Multi-line description of what the skill does.

intents:
  - natural language trigger 1
  - natural language trigger 2

guardrails:
  - safety constraint 1
  - do not do X

tools:
  - key: tool.key
    name: Human Name
    target_model: odoo.model.name
    target_method: method_name
    description: What this tool does

workflow:
  - tool.key.1
  - tool.key.2
  - tool.key.3

input_schema:
  type: object
  properties:
    param_name:
      type: string
      description: What this param is for

output_schema:
  type: object
  properties:
    result_field:
      type: string

agentInstructions: |
  Instructions for the agent on how to use this skill.
```

## Available Skills

| Skill Key | Description | Status |
|-----------|-------------|--------|
| `odoo.module.audit` | Audit module against OCA standards | Draft |
| `odoo.module.scaffold` | Scaffold new module structure | Draft |
| `kg.entity.expand` | Expand entity context from KG | Draft |
| `ci.run.validate` | Validate CI pipeline status | Draft |
| `finance.ppm.health` | Check Finance PPM health | Draft |

## Skill Categories

### Development Skills
- `odoo.module.audit` - Code quality and OCA compliance
- `odoo.module.scaffold` - Generate module boilerplate

### Knowledge Graph Skills
- `kg.entity.expand` - Entity context and relationships

### CI/CD Skills
- `ci.run.validate` - Pipeline status and gate checks

### Finance Skills
- `finance.ppm.health` - Accounting health checks

## Using Skills

### Via API

```bash
# List available skills
curl -X GET http://localhost:8069/api/v1/skills

# Execute a skill
curl -X POST http://localhost:8069/api/v1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "skill_key": "odoo.module.audit",
    "input_json": {"module_path": "addons/ipai/ipai_finance_ppm"},
    "execute": true
  }'

# Check run status
curl -X GET http://localhost:8069/api/v1/runs/{run_id}
```

### Via Odoo UI

1. Navigate to **Agent Core → Skills**
2. Select a skill
3. Click **Create Run**
4. Fill in inputs
5. Click **Execute**
6. Monitor progress in **Agent Core → Runs**

## Creating New Skills

1. Create directory: `skills/<skill-slug>/`
2. Define `skill.yaml` following schema above
3. Implement tool target methods in Odoo module
4. Register tools via seed data
5. Test via API or UI

## Tool Implementation

Tools map to Odoo model methods. Example:

```python
# In addons/ipai/ipai_lint/models/runner.py

class IpaiLintRunner(models.Model):
    _name = "ipai.lint.runner"

    def run_python_lint(self, **kwargs):
        """
        Tool: lint.python
        Runs flake8/black on Python files.
        """
        module_path = kwargs.get("module_path")
        # ... implementation ...
        return {"passed": True, "errors": []}
```

## OCA Dependencies

Skills leverage OCA modules for infrastructure:

- `queue_job` - Async execution
- `base_rest` - REST API endpoints
- `component` - Plugin architecture
- `auth_jwt` - API authentication

See `addons/oca/manifest.yaml` for full dependency list.

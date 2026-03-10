# Plan: Odoo App Agent Skills

## Implementation Steps

### Phase 1: Skill Definitions (16 YAML files)
1. Create skill.yaml for each of the 16 service domains
2. Each skill defines: name, version, key, description, intents, guardrails, tools, workflow, input/output schemas, agentInstructions
3. Skills organized in skills/<skill-slug>/skill.yaml

### Phase 2: Odoo Module (ipai_agent_skills)
1. Create ipai_agent_skills module in addons/ipai/
2. Models: ipai.skill.definition, ipai.skill.execution, ipai.skill.tool
3. Views: skill registry list/form, execution log
4. Security: ir.model.access.csv with proper ACL
5. Data: seed skills from YAML definitions

### Phase 3: Slash Commands
1. Create .claude/commands for key workflows
2. Commands reference skill definitions for orchestration

### Phase 4: Integration
1. Wire skills to existing ipai_agent and ipai_ai_copilot modules
2. Skills become available as copilot tools

## Dependencies
- ipai_ai_core (AI provider framework)
- ipai_agent (agent execution runtime)
- base, mail (Odoo core)

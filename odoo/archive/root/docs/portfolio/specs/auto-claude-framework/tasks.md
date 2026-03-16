# Auto-Claude Framework Tasks

## Phase 1: Core Enhancements

- [x] Review existing ipai_agent_core models
- [ ] Add rate_limit_per_minute to ipai.agent.skill
- [ ] Add timeout_seconds to ipai.agent.skill
- [ ] Add cooldown_seconds to ipai.agent.skill
- [ ] Add required_group_ids M2M to ipai.agent.skill
- [ ] Add external_ref to ipai.agent.run
- [ ] Create ipai.agent.artifact model
- [ ] Add timeout enforcement in _execute_workflow
- [ ] Create group_agent_user security group
- [ ] Update views for new fields

## Phase 2: REST API Module

- [ ] Create ipai_skill_api module structure
- [ ] Implement SkillService (list, get)
- [ ] Implement RunService (create, get, execute)
- [ ] Add OpenAPI documentation
- [ ] Add JWT/API key auth support
- [ ] Write API integration tests

## Phase 3: Knowledge Graph

- [ ] Create kg schema migration in Supabase
- [ ] Implement kg.neighborhood RPC
- [ ] Implement kg.top_related RPC
- [ ] Implement kg.semantic_search RPC (pgvector)
- [ ] Create ipai_kg_bridge Odoo module
- [ ] Register kg.fetch_context tool
- [ ] Test KG integration end-to-end

## Phase 4: Queue Integration

- [ ] Add queue_job to OCA manifest
- [ ] Update ipai_agent_core depends
- [ ] Implement action_execute_async method
- [ ] Configure agent channel in queue_job
- [ ] Test async execution flow

## Phase 5: E2E Testing

- [ ] Create test_skill_execution.py
- [ ] Create test_run_state_transitions.py
- [ ] Create API contract tests
- [ ] Create Playwright smoke test spec
- [ ] Add CI workflow for E2E tests
- [ ] Document test execution

## Phase 6: Skill Definitions

- [ ] Create odoo.module.audit skill
- [ ] Create odoo.module.scaffold skill
- [ ] Create finance.ppm.health skill
- [ ] Create kg.entity.expand skill
- [ ] Create ci.run.validate skill
- [ ] Load skills via seed data
- [ ] Validate skill execution

## Documentation

- [x] Create constitution.md
- [x] Create prd.md
- [x] Create plan.md
- [x] Create tasks.md
- [ ] Update CLAUDE.md with agent framework section
- [ ] Add API documentation to docs/
- [ ] Create skill authoring guide

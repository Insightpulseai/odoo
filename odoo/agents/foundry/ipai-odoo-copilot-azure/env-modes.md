# Environment Modes — IPAI Odoo Copilot

## BUILD

Local development environment. No Azure connectivity required.

- Foundry integration disabled by default
- Mock responses for testing UI flow
- Audit logging active (local DB)
- No API key required

## STAGING

Pre-production validation environment.

- Foundry enabled, pointing to staging agent
- Read-only mode enforced
- Full audit logging
- Uses staging Azure AI Foundry project
- Knowledge index may be a subset

## PROD-ADVISORY (Default Production Mode)

Production environment with read-only copilot.

- Foundry enabled, pointing to production agent
- **read_only_mode = True** (enforced)
- Agent can answer questions, navigate, and read data
- Agent CANNOT create, update, or delete records
- Full audit logging with 90-day retention
- Knowledge grounded on production index

## PROD-ACTION (Opt-in Production Mode)

Production environment with write capabilities.

- Foundry enabled, pointing to production agent
- **read_only_mode = False** (explicit opt-in by admin)
- Agent can execute transactional operations
- All writes require confirmation prompts
- Full audit logging with 180-day retention
- Restricted to users with `ipai_copilot.group_copilot_action` permission

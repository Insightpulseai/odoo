# Constitution — Parallel Control Planes

## Identity

**Feature**: A1 Control Center + Close Cycle Orchestration
**Version**: 1.0.0
**Status**: Implemented
**Owner**: Platform Engineering

## Core Principles

1. **Separation of Concerns**
   - A1 Control Center: Configuration layer (templates, workstreams, roles)
   - Close Orchestration: Execution layer (cycles, tasks, exceptions, gates)

2. **Idempotent Operations**
   - All seed imports use external keys for deduplication
   - Task generation is repeatable without creating duplicates

3. **Role-Based Assignment**
   - Role codes (RIM, JPAL, BOM, CKVC, FD) are canonical identifiers
   - Role resolver maps codes to Odoo groups/users per company

4. **Multi-Company First**
   - All entities are company-scoped
   - Record rules enforce company isolation

5. **Webhook Events**
   - State changes trigger webhooks for n8n integration
   - Payload follows stable JSON schema

## Non-Negotiables

- Never bypass workflow states
- Never create duplicate tasks for same period + template
- Never execute close without all gates passed
- Never escalate exceptions without audit trail
- Always log cron execution results

## Success Criteria

1. Both modules install without errors
2. Smoke test passes all 8 test scenarios
3. Cron jobs execute without crashes
4. Webhook payloads conform to schema
5. Multi-company record rules enforced

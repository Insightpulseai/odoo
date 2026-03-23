# Staging Architecture: Control Surface Split

## Hierarchy

```mermaid
graph TD
    subgraph "Platform Control Plane (Authority)"
        Engine[Staging Lifecycle Engine]
        Sanitizer[Data Sanitizer]
        Gate[V2 Release Gate]
        Pipeline[Azure DevOps Pipeline]
    end

    subgraph "Odoo Transactional Plane (SoR)"
        OdooUI[Operator Dashboard]
        AuditLog[ipai.deployment.status]
        Button[Request Refresh Button]
    end

    Button -- "Webhook/API" --> Engine
    Engine --> Pipeline
    Pipeline --> Sanitizer
    Sanitizer --> Gate
    Gate -- "Status Update" --> AuditLog
    AuditLog --> OdooUI
```

## Implementation Rules
1. **No Local DB Mutations**: Odoo shall NOT perform its own DB cloning or sanitization logic.
2. **Asynchronous Feedback**: Odoo calls the Engine API and waits for a background callback to update status.
3. **Evidence First**: All staging refreshes must generate a machine-readable evidence pack before the environment is marked 'Healthy' in Odoo.

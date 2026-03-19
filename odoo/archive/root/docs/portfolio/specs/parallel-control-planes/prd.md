# Product Requirements — Parallel Control Planes

## Overview

Two converging Odoo modules for month-end close management:

1. **ipai_ppm_a1** (A1 Control Center)
   - Configuration and planning layer
   - Workstreams, Templates, Tasks, Checks
   - Seed import/export for version control

2. **ipai_close_orchestration** (Close Cycle Orchestration)
   - Execution and tracking layer
   - Cycles, Tasks, Checklists, Exceptions, Gates
   - Automated cron for reminders and escalations

## Key Features

### A1 Control Center

| Feature | Description |
|---------|-------------|
| Roles | Canonical role codes (RIM, JPAL, etc.) mapped to groups |
| Workstreams | Organizational units owning templates |
| Templates | Reusable task definitions with steps |
| Tasklists | Period-specific task generation |
| Checks/STCs | Validation scenarios for task completion |
| Seed Export | YAML/JSON configuration export |

### Close Orchestration

| Feature | Description |
|---------|-------------|
| Cycles | Period-based closing runs |
| Tasks | Individual items with prep→review→approval workflow |
| Checklists | Verification items per task |
| Exceptions | Issue tracking with escalation |
| Gates | Approval checkpoints before close |
| Crons | Due reminders, auto-escalation, gate checks |

## Bridge Pattern

A1 entities bridge to Close Orchestration:

```
a1.workstream      → close.task.category
a1.template        → close.task.template
a1.tasklist        → close.cycle
a1.task            → close.task
a1.check           → close.approval.gate.template
```

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    A1 Control Center                        │
│  Workstreams → Templates → Tasklist → Generate Tasks        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ Instantiate Close Cycle
┌─────────────────────────────────────────────────────────────┐
│               Close Cycle Orchestration                      │
│  Cycle → Tasks → Prep → Review → Approval → Done            │
│           ↓                                                  │
│        Exceptions ←→ Escalation                             │
│           ↓                                                  │
│        Gates → All Pass → Cycle Closed                      │
└─────────────────────────────────────────────────────────────┘
```

## Webhook Events

| Event | Trigger |
|-------|---------|
| close.cycle.state_changed | Cycle state transition |
| close.cycle.tasks_generated | Task generation complete |
| close.task.state_changed | Task state transition |
| close.gate.passed | Gate approval |
| close.gate.blocked | Gate blocked |

## Technical Requirements

- Odoo 18.0 compatible
- PostgreSQL 15+
- Multi-company support with record rules
- Timezone-aware (Asia/Manila default)

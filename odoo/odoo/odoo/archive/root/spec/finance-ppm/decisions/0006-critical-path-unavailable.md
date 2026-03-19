# ADR-0006: Critical Path / Resource Leveling / Interactive Gantt — Unavailable

| Field | Value |
|-------|-------|
| **Capability** | Critical path analysis, resource leveling, interactive Gantt |
| **Parity target** | Bridge (planned, not implemented) |
| **Date** | 2026-02-16 |
| **Status** | Acknowledged gap |

## Context

SAP FCC provides critical-path designation, resource leveling, and interactive
Gantt charts. These were initially claimed as "solved" via OCA modules.

## What OCA Actually Provides

| Module | Verified series | Capability |
|--------|----------------|------------|
| `project_timeline` | 19.0 | Timeline bar view (read-only, limited interaction) |
| `project_task_dependency` | 19.0 | Task predecessor/successor relationships |
| `project_timeline_critical_path` | ≤14.0 | Critical-path highlighting on timeline |

### Key Limitations

1. **`project_timeline`** is a **timeline visualization**, not a Gantt chart.
   It does not provide drag-and-drop resource allocation or interactive scheduling.

2. **`project_timeline_critical_path`** is verified only for Odoo ≤14.0.
   It is **NOT verified for Odoo 19.0**. It cannot be claimed as available
   without independent installation testing and evidence.

3. **Resource leveling** does not exist in any CE or OCA module.

## Decision

These three capabilities are acknowledged as **unavailable** in Finance PPM v1:

| Capability | Status | Workaround |
|-----------|--------|------------|
| Critical path analysis | Planned (unverified) | Task dependencies + deadline tracking provide implicit ordering |
| Resource leveling | Out of scope | Manual workload balancing via `v_assignee_workload` Superset view |
| Interactive Gantt | Out of scope | Timeline view provides read-only visualization |

## Action Items

- All documentation updated to remove "critical path solved" claims
- Install script renamed from "Gantt bridge" to "timeline bridge" in output
- parity_map.yaml lists these as `status: planned`
- If `project_timeline_critical_path` is verified for 19.0 in the future,
  update this decision record and promote to `status: verified`

## Consequences

- Finance PPM v1 does not have critical-path computation
- Deadline-based task ordering is the primary scheduling mechanism
- Future work may verify `project_timeline_critical_path` for 19.0

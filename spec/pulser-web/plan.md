# Plan — Pulser Assistant: Experience Layer

## Status
Draft

## Architecture Approach

### Surface Separation
- **Production surfaces**: Ask Pulser chat widget, operator workbench — publicly routed, Entra-authenticated
- **Preview surfaces**: Preview chat, preview workbench — restricted access, visually distinct (banner/badge)
- **Internal surfaces**: Admin shell, evaluation viewer — not publicly routed, developer-only access

### Target Structure

```text
web/
  pulser/
    chat/                # Production Ask Pulser chat widget
    preview/             # Preview assistant UI (visually distinct)
    workbench/           # Operator console for formations/capabilities
    grounding/           # Grounding management console
    evaluation/          # Eval results and trace viewer
    approval/            # HITL checkpoint approval surfaces
    admin/               # DevUI-like internal test shell
    shared/              # Shared components (auth, layout, design tokens)
```

### Integration Points

| Backend | Protocol | Used By |
|---------|----------|---------|
| Foundry Agent Service | SSE / REST | Chat Surface, Preview Chat, Admin Shell |
| Platform Registry APIs | REST | Workbench, Grounding Console |
| Platform Evidence Store | REST | Evaluation Viewer |
| Agent Platform Checkpoint API | REST / WebSocket | Approval Surface |
| Foundry Eval APIs | REST | Evaluation Viewer |
| Foundry Tracing | REST | Admin Shell (trace inspection) |

### Environment-Aware UI

- Preview surfaces show a persistent **"PREVIEW"** banner in a distinct color
- Production surfaces show no banner (clean production UX)
- Admin shell shows **"INTERNAL — NOT PRODUCTION"** warning
- Environment context is resolved from Entra token claims + platform formation metadata

## UX Principles

1. **Preview and production must be visually distinct**: Operators must never confuse preview with production
2. **Admin/test surfaces are separate from production**: DevUI-like shells are internal-only, never publicly routed
3. **Long-running actions expose state and evidence**: Workflow checkpoints show status, history, and approval trail
4. **Grounding changes are operator tasks**: Source registration and pipeline management are explicit operator workflows, not hidden backend operations
5. **Chat is one surface, not the only surface**: Workbench, grounding console, and approval surfaces are equally important
6. **Capability-type rendering**: UI adapts response rendering based on capability type (informational shows evidence, navigational shows targets, transactional shows confirmation)

## Cross-Repo Dependencies

| Repo | `web` consumes |
|------|----------------|
| `agents` | Agent API endpoints (chat, workflow status, trace data) |
| `platform` | Formation metadata, capability package state, grounding source registry, evidence store |
| `data-intelligence` | Gold marts via Power BI Embedded (dashboards alongside assistant) |
| `odoo` | None directly (agents mediate Odoo interactions) |

### Phase W5 — Tax Guru Web Surfaces

- Implement PulserTaxDecisionCard component (treatment summary, confidence, evidence, actions)
- Implement PulserTaxExceptionQueueView (filterable exception list, bulk actions)
- Implement PulserTaxEvidenceView (audit-ready evidence bundle display)
- Add tax preview/admin shell for capability testing

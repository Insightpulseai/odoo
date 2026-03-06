# Odoo Workspace OS — Implementation Plan

> 4-phase rollout from operational core to advanced intelligence.

## Phase 1: Operational Core (Q1-Q2)
**Goal**: Replace core SaaS tools with Odoo CE + OCA baseline.

| Module | Scope | Dependencies |
|--------|-------|-------------|
| ipai_ppm | Portfolio views, milestone tracking, resource planning | Odoo Project, Timesheet, OCA project |
| ipai_expense_ai | OCR receipt scanning, policy validation | Odoo Expense, PaddleOCR-VL service |
| ipai_close_control | Close checklist, reconciliation tracking | Odoo Accounting, OCA accounting |

**Exit Criteria**:
- PPM dashboard live with 3+ active projects
- Expense OCR processing receipts end-to-end
- First month-end close completed via checklist

## Phase 2: AI Augmentation (Q2-Q3)
**Goal**: Layer intelligence onto operational modules.

| Module | Scope | Dependencies |
|--------|-------|-------------|
| ipai_expense_ai | Anomaly detection, auto-categorization | Phase 1 expense data, ML models |
| ipai_close_control | Variance analysis, blocker prediction | Phase 1 close data, Databricks analytics |
| ipai_workspace | Document grounding, semantic search | Odoo Documents, embedding service |

**Exit Criteria**:
- Expense anomaly detection catching >80% of policy violations
- Close cycle time reduced by 20% via automated blockers
- Semantic search returning relevant results across Odoo records

## Phase 3: Copilot (Q3-Q4)
**Goal**: Natural language ERP interaction.

| Module | Scope | Dependencies |
|--------|-------|-------------|
| ipai_copilot | NL queries, guided workflows, bulk operations | All Phase 1-2 modules, LLM service |
| ipai_workspace | Meeting summaries, task extraction | Phase 2 workspace, transcription service |

**Exit Criteria**:
- 5+ common workflows accessible via natural language
- Meeting → task extraction accuracy >85%
- User adoption: >50% of active users using copilot weekly

## Phase 4: Advanced Intelligence (Q4+)
**Goal**: Predictive and optimization capabilities.

| Capability | Scope | Dependencies |
|-----------|-------|-------------|
| Predictive Close | Forecast close completion date, identify risk items | Phase 2-3 close data, ML pipeline |
| Portfolio Optimization | Resource rebalancing recommendations, risk scoring | Phase 1-3 PPM data, optimization models |
| Anomaly Detection | Cross-module anomaly detection (expense + time + project) | All modules, Databricks ML |

**Exit Criteria**:
- Close date prediction within ±1 day accuracy
- Resource optimization recommendations accepted >60%
- Cross-module anomalies surfaced before human detection

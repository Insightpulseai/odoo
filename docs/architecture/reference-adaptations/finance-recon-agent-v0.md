# Finance Reconciliation Agent — v0 Reference Adaptation

| Field | Value |
|-------|-------|
| Status | v0 shipped 2026-04-14 |
| ADO Epic | [#524 Finance Agents Parity](https://dev.azure.com/insightpulseai/ipai-platform/_workitems/edit/524) |
| D365 Benchmark | Account Reconciliation Agent (preview, Wave 1) |
| Plane | B — Copilot Finance agent (see `feedback_d365_two_plane_doctrine.md`) |
| Runtime | microsoft-agent-framework (HandoffWorkflow + FileCheckpointStorage) |
| Model | `claude-sonnet-4-6` via `ipai-copilot-resource` (East US 2) |

## IPAI Implementation

- **Workflow**: `agents/workflows/payment_reconcile_workflow.py`
- **Skill metadata**: `agents/skills/recon_agent/SKILL.md`
- **Operator guide**: `agents/skills/recon_agent/README.md`
- **Tests**: `agents/tests/test_payment_reconcile_workflow.py`

## Wave-01 Issue Task Coverage (Epic #524)

All four tasks under the "Financial Reconciliation Agent" issue in Epic #524
are covered by this v0 delivery:

| Task | Coverage |
|------|----------|
| Define parity scope (bank recon + intercompany WHT) | `payment_reconcile_workflow.py` module docstring + scope section |
| Define data sources (bank statements, AR/AP, intercompany) | 5 read-only tools: `get_bank_statement_lines`, `get_open_ar_lines`, `get_open_ap_lines`, `get_intercompany_transactions`, `match_bank_line_to_move` |
| Define workflow + approval gates | HandoffWorkflow with 4 specialist agents; `@tool(approval_mode="always_require")` on both mutating tools |
| Define UAT + release gating | Unit tests in `agents/tests/test_payment_reconcile_workflow.py`; SKILL.md test command; this adaptation doc |

## D365 Benchmark Alignment

The D365 Account Reconciliation Agent (preview) covers:
- Automated matching of bank transactions to journal entries
- Exception surfacing for manual review
- Intercompany reconciliation

IPAI v0 delivers equivalent scope via:
- BankMatcher agent (automated matching, confidence scoring)
- ExceptionHandler agent (low-confidence + unmatched surfacing, 30-day escalation)
- IntercompanyClearer agent (WHT clearing between Odoo companies)
- BankClearer agent (approval-gated posting)

## Gaps for v1 (Planned)

| Gap | Notes |
|-----|-------|
| Real-time bank feed | v0 uses manual import; v1 will use bank statement API or OCA `account_bank_statement_import` |
| Multi-currency reconciliation | v0 assumes single currency per period |
| VAT/WHT clearing generalization | v0 targets Dataverse ↔ TBWA\SMP WHT; v1 will generalize to all intercompany pairs |
| Multi-tenant company scope expansion | v0 targets `dataverse_pasig`; v1 will accept any `res.company` in the Odoo instance |
| Databricks analytics lane integration | v0 is Odoo-only; v1 will push matched/unmatched stats to Databricks for Power BI reporting |

## Anchors

- Doctrine: `CLAUDE.md` §"Pulser — canonical classification"
- Two-plane doctrine: `.claude/projects/memory/feedback_d365_two_plane_doctrine.md`
- D365 agent parity matrix: `.claude/projects/memory/reference_d365_agent_parity_matrix.md`
- ADO normalization matrix: `docs/backlog/azdo_normalization_matrix.md`
- Platform authority split: `ssot/governance/platform-authority-split.yaml`

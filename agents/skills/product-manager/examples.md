# Examples — product-manager

## Example 1: Complete spec bundle validation

**Input**: Validate spec bundle at `spec/control-room-platform/`

**Output**:
- Spec bundle path: `spec/control-room-platform/`
- Completeness: PASS (all 4 files present: constitution.md, prd.md, plan.md, tasks.md)
- Acceptance criteria: PASS (12 criteria, all measurable — e.g. "Plane API responds < 500ms p95")
- OKR linkage: LINKED (parent: Platform OKR Q1-2026 "Unified control room for ops visibility")
- SSOT boundaries: CROSSING (touches Plane + Databricks + Odoo — contract `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` exists)
- Dependencies: Plane MCP server, Databricks Apps SDK, Odoo ERP module `ipai_workspace_core`
- Risks: medium — Databricks Apps SDK is alpha status
- Evidence: `docs/evidence/20260317-1430/product/control-room-platform/`

## Example 2: Incomplete spec — missing acceptance criteria

**Input**: Validate feature request for "AI-powered invoice matching"

**Output**:
- Spec bundle path: `spec/ai-invoice-matching/`
- Completeness: FAIL (missing `tasks.md`)
- Acceptance criteria: FAIL — 3 of 5 criteria are unmeasurable:
  - "Should handle most invoice formats" — no quantified threshold
  - "Fast matching" — no latency target
  - "Good accuracy" — no precision/recall target
- OKR linkage: ORPHAN — no parent OKR found in enterprise or platform goals
- SSOT boundaries: CROSSING (touches Odoo accounting + Azure Document Intelligence — no contract)
- Dependencies: `ipai_bir_tax_compliance`, Azure Document Intelligence API
- Risks: high — orphan spec with vague criteria and missing contract
- Remediation:
  1. Create `tasks.md` with assignable work items
  2. Rewrite criteria: "Matches >= 95% of standard PDF invoices within 3 seconds"
  3. Add parent OKR or request new OKR from portfolio-manager
  4. Create contract `docs/contracts/INVOICE_AI_CONTRACT.md` for cross-boundary work

## Example 3: Scope creep detection

**Input**: Review updated PRD for `spec/ee-parity-helpdesk/` — 3 new features added since last review

**Output**:
- Spec bundle path: `spec/ee-parity-helpdesk/`
- Completeness: PASS
- Acceptance criteria: PASS (all measurable)
- OKR linkage: LINKED (parent: "EE parity >= 80%")
- SSOT boundaries: CLEAR
- Dependencies: `ipai_helpdesk`, OCA `helpdesk` module
- Risks: high — scope creep detected
  - 3 features added not in original OKR scope: SLA escalation rules, customer portal widget, satisfaction survey
  - Combined effort exceeds remaining capacity for this OKR cycle
- Remediation: Escalate to portfolio-manager for capacity review; defer new features to next quarter or request OKR amendment

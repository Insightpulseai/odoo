# Expense Liquidation Agent - Tasks

## Phase 29: Implementation & Verification (EL-01)

### 1. Specification & Schema (DONE)
- [x] Author Constitution, PRD, and Plan.
- [x] Define **Submission Envelope** schema for Odoo/n8n.
- [x] Frozen 8-state lifecycle as v1 contract.

### 2. Odoo Backend (IN PROGRESS)
- [x] Add orthogonal state dimensions: `channel_state`, `document_state`, `policy_state`, `settlement_state`.
- [x] Implement **Submission Envelope** listener (idempotent Odoo Service Layer).
- [x] Wire Foundry extraction persistence.
- [ ] Implement **Policy Rule Pack**:
    - [ ] 30-day overdue liquidation check.
    - [ ] Receipt matching requirement.
    - [ ] Category cap enforcement.
    - [ ] Client field completeness.
- [ ] Implement settlement computation logic.

### 3. Orchestration (n8n)
- [x] Add Telegram adapter contract.
- [x] Create n8n normalization workflow (Telegram -> Envelope -> Odoo).
- [ ] Implement duplicate handling using `source_message_id`.

### 4. Phase 29 Closeout Gate (CRITICAL)
- [ ] **Runtime Evidence Collection**:
    - [ ] Scenario 1: Client Artifact Parity (Matching the Cash Advance form fields/math).
    - [ ] Scenario 2: End-to-End Happy Path (Telegram -> n8n -> Odoo -> Foundry -> Audit).
    - [ ] Scenario 3: Idempotency & Duplicate Safety (Double-webhook trigger).
    - [ ] Scenario 4: Policy - 30-Day SLA Breach (Detection & Flagging).
    - [ ] Scenario 5: Policy - Missing Evidence & Low Confidence (Fail-Closed behavior).
    - [ ] Scenario 6: Policy - Client-Chargeable completeness (Missing CE Number).
    - [ ] Scenario 7: Settlement - Employee Owes Company (Cash return requirement).
    - [ ] Scenario 8: Settlement - Company Owes Employee (Reimbursement requirement).
    - [ ] Scenario 9: Orthogonal State Isolation (States evolve without corrupting 8-state model).
- [ ] **Verification Pack Assembly**: Generate the `phase-29-verification.md` artifact with the scenario matrix.
- [ ] **Final Sign-off**: Project ready for mission-closeout once evidence is verified.

## Acceptance Criteria
- 100% of receipts ingested via Telegram result in an Odoo draft within <10s.
- 100% of policy violations (missing receipt, overdue) are flagged autonomously.
- Settlement outcome exactly matches (Advance - Validated Expenses).

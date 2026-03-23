# Plan: Bank Reconciliation Agent Implementation

## Phase 1: Infrastructure & Contracts (Current)
- [ ] Define SSOT contracts for reconciliation evidence.
- [ ] Define workflow states and transition rules.
- [ ] Setup `ipai_bank_recon` Odoo module skeleton.

## Phase 2: Ingestion & Routing
- [ ] Implement statement line normalization.
- [ ] Wire the **Advisory Agent** for document lookup tools.
- [ ] Implement the **Deterministic Router** for recon tasks.

## Phase 3: Matching Logic & Evidence
- [ ] Build the multi-vector matching engine (Amount/Ref/Date).
- [ ] Integrate **TaxPulse** classification for VAT/EWT verification of matches.
- [ ] Implement evidence pack generation.

## Phase 4: Posting & Safety
- [ ] Implement the **Actions Agent** for `account.bank.statement.line` mutations.
- [ ] Build the **Fail-Closed Guard** for auto-posting thresholds.
- [ ] Wire the **Supervisor** for Exactly-Once issuance.

## Phase 5: Verification & Evals
- [ ] Create bank recon golden dataset (fixtures).
- [ ] Run groundedness and safety evals.
- [ ] Conduct "Red Team" drill for incorrect amount handling.

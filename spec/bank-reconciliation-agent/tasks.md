# Tasks: Bank Reconciliation Agent

## [ ] Phase 1: Spec & Contracts
- [x] Create core spec files (Constitution, PRD, Plan)
- [ ] Define `reconciliation_contracts.yaml` SSOT
- [ ] Define Odoo model surface area in `ipai_bank_recon` plan

## [ ] Phase 2: Tooling & Agents
- [ ] Define `bank_recon_advisory_tools` (Read-only lookup)
- [ ] Define `bank_recon_action_tools` (Write-gated posting)
- [ ] Implement statement normalizer (Python)

## [ ] Phase 3: Integration
- [ ] Connect to `ipai_bir_tax_compliance` for tax-aware matching
- [ ] Setup Azure AI Foundry prompt manifests for Recon Agent

## [ ] Phase 4: Verification
- [ ] Add 10 baseline reconciliation fixtures
- [ ] Validate fail-closed behavior on amount mismatches
- [ ] Generate reconciliation acceptance artifact

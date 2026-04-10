# Tasks: Pulser for Odoo

> **Canonical Slug**: `pulser-odoo`
> **Human-facing title**: `Pulser for Odoo`

---

## Phase 1: Consolidation & Renaming
- [x] Merge PRD, Constitution, and Plan from legacy folders.
- [ ] Merge Task lists (Wave/Phase mapping).
- [ ] Rename legacy spec folders after verification.
- [ ] Update SSOT keys in `release_contract.yaml`.

## Phase 2: Bridge Implementation
- [ ] P2-1: Implement finance Q&A context packager (account, partner, bank).
- [ ] P2-2: Build reconciliation assistance flow with native Odoo API.
- [ ] P2-3: Build collections assistance drafting in Odoo Mail.
- [ ] P2-4: Implement approval-gated action mediation in `tool_executor.py`.
- [ ] P2-5: Achieve 100% audit coverage for all bridge interactions.

## Phase 3: Documentation & Foundry Patch
- [ ] D-1: Update `docs/release/FEATURE_SHIP_READINESS_CHECKLIST.md` -> `MVP_SHIP_CHECKLIST.md`.
- [ ] D-2: Patch Foundry agent descriptions with Odoo CE 18.0 assistant wording.
- [ ] D-3: Update examples in `FOUNDRY_TOOL_POLICY.md` and `MCP_POLICY.md`.

## Phase 4: Runtime Unblocking (Dockerfile)
- [ ] R-1: Patch `Dockerfile.odoo-copilot` with mission OCA project/timesheet modules.
- [ ] R-2: Patch `Dockerfile.odoo-copilot` with IPAI Copilot and Knowledge Bridge modules.
- [ ] R-3: Remove `ipai_finance_ppm` from production build.
- [ ] R-4: Verify `addons_path` consistency for the consolidated build.

---

*Last updated: 2026-04-10*

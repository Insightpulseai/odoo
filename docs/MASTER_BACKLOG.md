# MASTER BACKLOG: IPAI Agent Factory Post-Pilot

This document consolidates all deferred features, future-phase roadmaps, and architectural refinements for the IPAI Agent Factory V2.

## 1. High-Priority: Expansion (Phase 31)

### Multi-Channel Ingress
- [ ] **WhatsApp Ingress**: Implement `n8n` adapter for WhatsApp Cloud API.
- [ ] **Email Auto-Capture**: Implement IMAP/POP3 listener for `finance@domain.com` with attachment parsing.
- [ ] **Mobile OCR Polish**: Fine-tune Document Intelligence for high-skew/low-light mobile receipt photos.
- [ ] **Hybrid MCP Governance**: Integrate Microsoft-Official MCP suite (Markitdown, Entra, Sentinel, Fabric, Learn) for total-stack autonomy.

### Expense Liquidation
- [ ] **Payroll Integration**: Direct bridge to Odoo Payroll for "Unliquidated Balance Deduction" execution.
- [ ] **Category Caps**: Automated flagging of expenses exceeding department-level thresholds.
- [ ] **Travel Policy Audit**: Cross-reference flight/hotel bookings with official travel manifests.

## 2. Medium-Priority: Architectural Refinement

### Governance & Reliability
- [ ] **AF-07.1**: Normalize all subsystem acceptance artifacts (Unified schema for all pilots).
- [ ] **AF-08.1**: Validate actual runtime topology vs SSOT (Continuous infrastructure drift detection).
- [ ] **Predictive Matching**: Implement "Next Best Action" UI for ambiguous bank reconciliation candidates.

### Multi-Currency & Globalization
- [ ] **Forex Revaluation**: Automated revaluation of foreign currency supplier bills via Odoo `res.currency.rate`.
- [ ] **Cross-Border Tax**: Integration of TaxPulse-Global for multi-jurisdiction compliance.

## 3. Low-Priority: Marketplace & Community

### Commercialization
- [ ] **Marketplace Assets**: Finalize screenshots, pricing models, and support docs for Microsoft Partner Center.
- [ ] **Managed App Packaging**: Refactor ACA manifests into a single Azure Managed Application bundle.

### Community Edition
- [ ] **UI Portability**: Ensure Copilot Chat OWL widget remains resilient across multiple Odoo 17/18/19 sub-versions.

---
**Status**: Consolidated from V2 Pilot Evidence.
**Last Updated**: 2026-03-21T07:55:00Z

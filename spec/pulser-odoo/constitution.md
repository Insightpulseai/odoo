# Constitution: Pulser for Odoo

> **Canonical Slug**: `pulser-odoo`
> **Human-facing title**: `Pulser for Odoo`
> **Subtitle**: `Pulser Assistant for Odoo`
> **Product**: Thin Odoo adapter layer for the Pulser Assistant platform.

---

## 1. Governing Principles

### 1.1 Odoo is an Adapter, Not an Authority
All transactional data remains in Odoo. The `pulser-odoo` layer provides context (Tier 6) and execution benchmarks (Tier 5), but does not determine policy. Intelligence and reasoning live in the Pulser Agent plane (Foundry/Agents).

### 1.2 Thin-Bridge Architecture
The Odoo Python footprint is restricted to:
- Context packaging (reading records user is authorized to see).
- Request delegation to external Pulser endpoints.
- UI rendering of assistant responses and suggested actions.
- Audit logging of every interaction.
- Admin configuration for connectivity and safety policies.

### 1.3 Read-Only Default
Assistant interactions are read-only by default. Write actions (posts, updates, approvals) require:
- Explicit admin-configured allowlists.
- Mandatory user confirmation in the UI.
- Direct ORM execution with audit linking.

### 1.4 Identity-First (Entra ID)
Every interaction must carry the authenticated Odoo user's identity. Production calls use Microsoft Entra ID for user-scoped authorization.

---

## 2. Invariants & Technical Constraints

1. **CE Only**: No dependencies on Odoo Enterprise or odoo.com IAP services.
2. **No LLM/Vector code in Odoo**: No `langchain`, `openai`, or vector stores inside the Odoo process.
3. **Audit Completeness**: Every interaction (including timeouts/failures) produces a non-deletable `ipai.copilot.audit` record.
4. **Graceful Degradation**: Odoo UI remains functional if the Pulser runtime is unavailable.
5. **Safe Models**: Standard Odoo models (`account.move`, `res.partner`) are accessible, but high-risk models are blocked at the adapter layer.
6. **Module Naming**: Legacy modules use `ipai_odoo_copilot` prefix. Future modules follow the `ipai_pulser_*` pattern.
7. **Canonical Path**: Specs live in `spec/pulser-odoo/`.

---

## 3. Tax & Compliance Rules (PH Benchmark)

1. **Dual-Basis Citations**: Every tax action must cite both the legal basis (Tier 1-2 BIR authority) and the localization mapping (Tier 5 Odoo config).
2. **ERP Records are Tier 6**: Never use transaction data to override legal authority.
3. **ATC Codes**: Use official BIR prefixes (WI/WC/WB) for all withholding classifications.
4. **Exception Handling**: Tax exceptions are immutable and must be resolved with evidence before the case is closed.

---

*Last updated: 2026-04-10*

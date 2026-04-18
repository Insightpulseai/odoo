# Pulser Odoo 18 Multi-Agent Bridge

This reference defines the canonical grounding logic and API interaction patterns for all Pulser specialized agents.

## 1. Grounding Invariants
- **Domain**: `erp.insightpulseai.com`
- **Engine**: Odoo 18.0 Community Edition (CE) 
- **API Surface**: JSON-RPC over HTTPS (Internal) / REST via Agent Plugin (External)

## 2. Model Field Mappings
| Entity | Logic Scope | Key Multi-Tenant Fields |
|--------|-------------|-------------------------|
| Project | `project.project` | `x_studio_margin_tracking`, `x_studio_burn_rate` |
| Account | `account.move` | `l10n_ph_is_bir_compliant`, `x_taxpulse_verification_id` |
| Expense | `hr.expense` | `x_approval_band_id`, `state` |

## 3. Interaction Protocol
1. **Search**: Use the `search_project_operations` function for all discovery.
2. **Retrieve**: Always fetch the `id` and `display_name` before suggesting modifications.
3. **Validate**: Cross-reference any extracted data (from Azure Document Intelligence) against existing records before posting.

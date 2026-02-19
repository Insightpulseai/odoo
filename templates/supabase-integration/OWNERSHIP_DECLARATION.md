# Ownership Declaration — Supabase Integration

## Summary
- integration_name:
- owner_system: supabase | odoo
- writeback_to_odoo: none | non_sor_only | (must justify)

## Data domains touched
- odoo_entities_referenced:
- supabase_schemas_touched:

## Sync mode
- mode: webhook | polling | manual | hybrid
- checkpoints_cursor_location:
- idempotency_key:

## Authorization model
- auth: supabase_auth | external_idp + supabase_rls
- rls_policies: (link/paths)
- service_role_usage: yes/no (why)

## Evidence outputs (required)
- ops.runs: yes
- ops.run_events: yes
- artifacts: yes (where stored)

## SSOT/SOR boundary acknowledgement
- No shadow ledger: yes/no
- Odoo wins conflicts for Odoo-owned domains: yes/no

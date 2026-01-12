Multi-tenant platform core for InsightPulse AI, providing tenant isolation and metadata management for shared Odoo + Supabase + Superset infrastructure.

This module implements **tenant-aware architecture** where:

* TBWA = tenant/client (not special codebase fork)
* Platform = shared infrastructure (Odoo CE + Supabase + Superset)
* Isolation = database-level (one Odoo DB per tenant + Supabase schema isolation)

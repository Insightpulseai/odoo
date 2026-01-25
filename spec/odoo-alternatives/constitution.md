# Constitution — Odoo Alternatives (EE → CE/OCA)

## 1. Non-Negotiables

1. **OCA-first**: Prefer OCA 18.0 modules over custom code whenever feasible.
2. **CE-compatible**: All recommendations must be compatible with **Odoo Community Edition** (target baseline: Odoo 18 CE; allow 19 as future milestone).
3. **Minimal custom**: Introduce custom modules only as a last resort; consolidate into a small set of `ipai_*` modules.
4. **Reproducible**: Every mapping must include install order, dependencies, and a verification command.
5. **No UI-only guidance**: All operational steps (install, configure, verify) must be expressed as CLI steps, scripts, or configuration-as-code.
6. **No proprietary dependency**: Avoid solutions requiring Odoo Enterprise/IAP/online upsells as prerequisites.

## 2. Decision Rules

1. If a CE core module exists, use it.
2. Else if an OCA module exists and is maintained, use it.
3. Else if community module exists but is low quality, mark as "risky" and provide fallback.
4. Else create minimal `ipai_*` glue:
   - No controllers/routes unless unavoidable.
   - Prefer model/view inheritance + server actions.
   - Include automated tests or at minimum install/upgrade smoke checks.

## 3. Output Contract for Each "Alternative"

Each mapped item must include:
- **EE feature name**
- **Replacement set**: CE module(s) + OCA module(s) + optional `ipai_*`
- **Install order**
- **Dependency notes / conflicts**
- **Verification** (CLI) and **Rollback** strategy

## 4. Data & Integrations

- Prefer **Supabase** for external state/queue/logging where needed (Edge Functions allowed).
- Prefer **n8n** for workflow automation and webhooks.
- Prefer **Superset** for BI; support connectors for Tableau/Power BI via standard DB connectivity or exports.

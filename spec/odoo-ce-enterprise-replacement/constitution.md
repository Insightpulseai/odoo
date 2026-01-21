# Constitution: Odoo CE Enterprise Replacement

## Non-Negotiables

1. **CE + OCA Only**: No Enterprise modules, no odoo.com IAP dependencies
2. **Self-Hosted**: All services must run on owned infrastructure (DigitalOcean, Azure, etc.)
3. **Programmatic Configuration**: All config via `odoo.conf`, env vars, XML/CSV seeds, or `ir.config_parameter`
4. **No UI-Only Setup**: Every configuration must have a CLI/CI equivalent
5. **Deterministic**: Same inputs produce same outputs; drift gates enforce consistency

## Scope

Replace all Enterprise Edition (EE) and IAP-backed features with:
- Odoo 18 CE core capabilities
- OCA community modules (18.0 branch)
- Custom `ipai_*` modules where gaps exist
- `ipai_enterprise_bridge` as the unified EE/IAP replacement layer

## Boundaries

### In Scope
- General Settings configuration (all sections)
- Email/SMTP without IAP (Mailgun, Postfix, etc.)
- OAuth without EE (Google, Azure AD, Keycloak)
- IoT without IoT Box subscription
- Multi-company without EE inter-company module
- Document digitization without IAP OCR

### Out of Scope
- Odoo.com hosting/SaaS features
- Enterprise-only UI components (Studio, Gantt, Map)
- Paid Odoo support contracts
- odoo.com partner portal integrations

## Success Criteria

1. Full General Settings functionality via CE+OCA+IPAI
2. Email send/receive without IAP
3. OAuth with Google + Azure AD without EE
4. IoT device registry + control without subscription
5. Multi-company with shared resources
6. All config reproducible via CI/CD
7. Zero EE module imports in `ir_module_module`

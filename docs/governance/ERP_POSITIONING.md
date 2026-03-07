# ERP Positioning Policy

**Canonical Name**: Odoo CE 19 (Community Edition)
**Hosting**: Self-hosted on DigitalOcean (178.128.112.214)
**Database**: PostgreSQL 16 (local to the droplet, NOT Supabase)

## Prohibited Terms

| Term | Why Prohibited |
|------|---------------|
| Odoo SaaS | We do not use Odoo's SaaS offering; we self-host |
| Odoo.sh | We do not use Odoo's PaaS; we build equivalent features ourselves |
| Odoo Enterprise | We do not license EE; we achieve parity via CE + OCA + ipai_* |
| Odoo Online | We do not use Odoo's managed hosting |
| odoo.com IAP | We do not consume Odoo's paid in-app services |

## Permitted Usage

- **EE Parity comparisons**: "Replaces Odoo Enterprise feature X" is allowed
- **Prohibition statements**: "No Odoo Enterprise modules" is allowed
- **Feature parity tables**: Referencing EE/Odoo.sh features we are replacing is allowed
- **Upstream Odoo documentation** (`docs/kb/odoo19/upstream/`): unmodified reference material

## Cross-References

- Root constitution: `constitution.md` (Section 1.3)
- Agent instructions: `CLAUDE.md` (Critical Rules, Section 4)
- Parity strategy: `docs/ai/EE_PARITY.md`

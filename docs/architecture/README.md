# Architecture Documentation

This directory contains the authoritative architecture documentation for InsightPulseAI.

## Documents

| Document | Description |
|----------|-------------|
| [INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md](INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md) | Master technical architecture specification |
| [IPAI_TARGET_ARCHITECTURE.md](IPAI_TARGET_ARCHITECTURE.md) | Target architecture and roadmap |
| [AUTH_MODEL.md](AUTH_MODEL.md) | Authentication and authorization model |
| [multi_tenant_architecture.md](multi_tenant_architecture.md) | Multi-tenancy design |

## Architecture Diagrams

### Source Files (Draw.io)

| Diagram | Description |
|---------|-------------|
| `ipai_idp_architecture.drawio` | IDP (Intelligent Document Processing) architecture |
| `ipai_idp_pdf_processing.drawio` | PDF processing pipeline |
| `ipai_idp_multi_agent_workflow.drawio` | Multi-agent workflow orchestration |
| `ipai_idp_build_deploy_custom_models.drawio` | Custom model build and deploy |

### Exports

Exported diagrams are stored in `exports/` directory:
- **SVG**: Vector format for documentation embedding (scalable)
- **PNG**: Raster at 2x resolution for presentations

### Regenerating Exports

```bash
# Export all diagrams
./scripts/export_architecture_diagrams.sh

# Export single diagram
./scripts/export_architecture_diagrams.sh --single ipai_idp_architecture.drawio

# Check for drift (CI mode)
./scripts/export_architecture_diagrams.sh --check
```

### CI Enforcement

The `architecture-diagrams.yml` workflow:
1. Triggers on changes to `.drawio` files or exports
2. Verifies exports match source diagrams
3. Fails if drift is detected

To update exports after editing a diagram:
```bash
./scripts/export_architecture_diagrams.sh
git add docs/architecture/exports/
git commit -m "chore(docs): update architecture diagram exports"
```

## Related Documentation

| Location | Description |
|----------|-------------|
| [db/DB_TARGET_ARCHITECTURE.md](../../db/DB_TARGET_ARCHITECTURE.md) | Database schema architecture and migration plan |
| [db/rls/RLS_ROLES.md](../../db/rls/RLS_ROLES.md) | Role definitions and RLS policies |
| [db/seeds/SEEDING_STRATEGY.md](../../db/seeds/SEEDING_STRATEGY.md) | Database seeding strategy |
| [odoo/ODOO_INTEGRATION_MAP.md](../../odoo/ODOO_INTEGRATION_MAP.md) | Odoo 18 CE integration mapping |
| [engines/](../../engines/) | Engine YAML specifications |

## Quick Links

- **Engine Specs:** [`engines/_template/engine.yaml`](../../engines/_template/engine.yaml)
- **Migration Scripts:** [`db/migrations/`](../../db/migrations/)
- **RLS Templates:** [`db/rls/RLS_BASE_TEMPLATE.sql`](../../db/rls/RLS_BASE_TEMPLATE.sql)
- **Seed Scripts:** [`tools/seed_*.ts`](../../tools/)

# InsightPulseAI Odoo 18 CE/OCA Implementation Handbook

This directory contains the stack-specific documentation for implementing and operating Odoo 18 Community Edition with OCA modules in the InsightPulseAI environment.

## Quick Start

- **Master Document**: [ODOO_18_CE_OCA_HANDBOOK.md](./ODOO_18_CE_OCA_HANDBOOK.md)
- **Spec Kit**: [spec/](./spec/)
- **Sample Pages**: [pages/](./pages/)

## Structure

```
docs/odoo-18-handbook/
├── ODOO_18_CE_OCA_HANDBOOK.md   # Master handbook document
├── README.md                     # This file
├── spec/                         # Spec Kit 4-file bundle
│   ├── constitution.md          # Documentation principles
│   ├── prd.md                   # Product requirements
│   ├── plan.md                  # Release roadmap
│   └── tasks.md                 # Task inventory
└── pages/                        # Sample documentation pages
    ├── 01-finance-accounting.md # Finance workspace (pilot)
    ├── 02-projects-ppm.md       # Projects & PPM workspace
    └── 03-retail-scout-integration.md # Retail & Scout workspace
```

## Key Features

### Odoo 18 Documentation Classification

Classifies official Odoo 18.0 documentation into:
- `CE_NATIVE` - Available in Community Edition
- `OCA_REPLACE` - Covered by OCA modules
- `REPLACE` - Use InsightPulseAI stack component
- `DROP` - Not in scope

### CE/OCA Mapping Tables

Maps Odoo features to:
- Odoo CE modules/models
- OCA addon alternatives
- Supabase schemas
- n8n workflows
- AI agent integrations

### Stack Integration Call-Outs

Every page includes:
```
InsightPulseAI Integration:
- Data flows to: [schemas]
- Used by engines: [engine names]
- Triggered automations: [n8n workflows]
- AI agents: [agent names]
```

### RAG-Ready Documentation

Designed for AI agent consumption:
- Chunking strategy defined
- Metadata schema for filtering
- Agent query patterns documented

## Related Documents

| Document | Location |
|----------|----------|
| CE/OCA Mapping | [../ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md](../ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md) |
| Technical Architecture | [../architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md](../architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md) |
| Enterprise Feature Gap | [../ENTERPRISE_FEATURE_GAP.yaml](../ENTERPRISE_FEATURE_GAP.yaml) |
| Project Constitution | [../../constitution.md](../../constitution.md) |

## Contributing

1. Follow the page template in [spec/prd.md](./spec/prd.md)
2. Include all required sections per documentation standards
3. Add RAG metadata tags
4. Get SME review before merging

## License

AGPL-3 (matches Odoo CE licensing)

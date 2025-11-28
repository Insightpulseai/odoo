# Architecture Diagrams

This directory contains cloud architecture diagrams for the fin-workspace / mybrick platform.

## Diagrams

| Name | Providers | Updated | Draw.io |
|------|-----------|---------|---------|
| fin-workspace Platform Overview | digitalocean, generic | 2025-11-26 | [Open](https://app.diagrams.net/?mode=github#Hjgtolentino/odoo-ce/main/docs/diagrams/architecture/fin-workspace-overview.drawio) |
| DO Advisor Agent Architecture | digitalocean, generic | 2025-11-26 | [Open](https://app.diagrams.net/?mode=github#Hjgtolentino/odoo-ce/main/docs/diagrams/architecture/do-advisor-architecture.drawio) |

## Usage

### Viewing Diagrams

1. Click "Open" in the table above to edit in draw.io with GitHub integration
2. Or open `.drawio` files directly in the draw.io desktop app

### Adding New Diagrams

```bash
# Add via script
python scripts/update_diagram_manifest.py --add-diagram my-diagram.drawio --provider azure

# Or use MCP skill
# "Create an architecture diagram for the Kubernetes cluster"
```

### Generating from Infrastructure

```bash
# Azure Resource Graph export
az graph query -q "resources | project name, type, location" -o json > infra_snapshots/azure/topology.json

# DigitalOcean export
doctl compute droplet list -o json > infra_snapshots/digitalocean/droplets.json

# Then generate diagram via MCP
```

## Directory Structure

```
architecture/
├── manifest.json           # Diagram metadata
├── README.md              # This file
├── *.drawio               # Source diagrams
└── previews/              # PNG/SVG exports
    └── *.png
```

## Icon Libraries

- [Azure Icons](https://github.com/jgraph/drawio-libs/tree/master/azure)
- [Kubernetes Icons](https://github.com/jgraph/drawio-libs/tree/master/kubernetes)
- [AWS Icons](https://github.com/jgraph/drawio-libs/tree/master/aws)
- [GCP Icons](https://github.com/jgraph/drawio-libs/tree/master/gcp)

## References

- [diagram-ai-generator](https://github.com/carlosmgv02/diagram-ai-generator)
- [draw.io Azure Diagrams](https://www.drawio.com/blog/azure-diagrams)
- [draw.io GitHub Integration](https://github.com/jgraph/drawio-github)

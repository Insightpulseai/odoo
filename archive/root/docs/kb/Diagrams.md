# Diagrams

Architecture and flow diagrams for the IPAI Platform.

## Overview

This page contains visual documentation of the IPAI platform architecture, data flows, and module relationships.

## Adding Diagrams

1. Create Mermaid diagrams in `docs/diagrams/*.mmd`
2. Export to PNG using the diagramflow tool or Mermaid CLI
3. Run `ipai-gen` to update this page

### Using diagramflow

```bash
# Convert all Mermaid files
diagramflow docs/diagrams/*.mmd -d docs/diagrams/

# Convert single file
diagramflow docs/diagrams/architecture.mmd
```

### Using Mermaid CLI

```bash
# Install
npm install -g @mermaid-js/mermaid-cli

# Convert to PNG
mmdc -i docs/diagrams/architecture.mmd -o docs/diagrams/architecture.png
```

## Diagram Types

### Architecture Diagrams

- System architecture overview
- Module dependency graphs
- Integration points

### Flow Diagrams

- Business process flows
- Data flow diagrams
- State machine diagrams

### Entity Relationship Diagrams

- Data model ERDs
- Module relationship maps

## Tools

| Tool | Purpose |
|------|---------|
| Mermaid | Source format for diagrams |
| diagramflow | Converts Mermaid to BPMN/draw.io |
| mermaid-cli | Renders Mermaid to PNG/SVG |
| ipai-gen | Auto-generates this wiki page |

## Contributing

1. Create diagram in Mermaid format
2. Place in `docs/diagrams/`
3. Run `ipai-gen` to regenerate wiki
4. Commit changes

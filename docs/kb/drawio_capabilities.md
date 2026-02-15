# Draw.io Capabilities & Integration

## Overview

Draw.io (diagrams.net) is a powerful diagramming tool that can be controlled via URL parameters and XML structure.

## Core Features

- **File Format:** XML-based (`mxGraphModel`). Compressed or uncompressed.
- **Layers & Metadata:** Supports layers, custom tags, and shape properties.
- **Automation:** Can generate diagrams from CSV, SQL, or Mermaid syntax.

## URL Control Patterns

Construct viewer URLs to control the user experience:

- **Light Mode:** `ui=kennedy` (standard), `ui=min` (minimal).
- **Dark Mode:** `ui=dark`.
- **Lightbox:** `lightbox=1` (removes editor UI, focuses on content).
- **Nav/Layers:** `nav=1` (folding), `layers=1` (layer control).
- **Edit Mode:** `edit=_blank` (opens editor in new window).

## Relevant Shapes for Odoo

- **Entity Relation:** `er` library for database schemas.
- **BPMN:** `bpmn` library for business process flows.
- **Flowchart:** Standard process mapping.
- **Mockups:** Wireframing UI components (`mockups` library).

## Advanced Techniques

- **CSV Import:** Define nodes/edges in CSV and paste into "Arrange > Insert > Advanced > CSV".
- **Mermaid:** Use "Arrange > Insert > Advanced > Mermaid" for text-to-diagram.
- **Waypoints:** Use waypoint shapes for circuit/logic routing.

## References

- [Features](https://www.drawio.com/features)
- [Example Diagrams](https://www.drawio.com/example-diagrams)
- [URL Parameters](https://desk.draw.io/support/solutions/articles/16000042546-what-url-parameters-are-supported)

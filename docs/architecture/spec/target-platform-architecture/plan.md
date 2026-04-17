# Plan — Target Platform Architecture

## Scope

Create the architecture docs and SSOT files that define:
- plane boundaries
- system context
- tenant model
- data flows
- truth-plane authorities
- diagram conventions
- domain workbench map

## Deliverables

- docs/architecture/target-platform-architecture.md
- docs/architecture/plane-boundaries.md
- docs/architecture/domain-workbench-map.md
- docs/architecture/diagram-conventions.md
- ssot/architecture/*.yaml

## Design decisions

### DD-1
Use six planes:
- governance/control
- identity/network/security
- business systems
- data intelligence
- agent/AI runtime
- experience/domain apps

### DD-2
Use shared control plane + selective data-plane isolation.

### DD-3
Make Foundry the agent runtime and governance plane for models/tools/evals.

### DD-4
Make Databricks the center of gravity for data engineering and ML engineering.

### DD-5
Treat Document Intelligence + Logic Apps + Functions as a distinct document automation subsystem.

### DD-6
Keep diagrams layered: overview, high-level, low-level.

## Risks

- shadow systems of record
- uncontrolled overlap between Odoo/Databricks/Foundry
- weak tenant context propagation
- implementation PRs ignoring plane boundaries

## Mitigations

- explicit SSOT files
- explicit runtime authority map
- explicit plane-boundary doc
- future release/control contracts to cite these files

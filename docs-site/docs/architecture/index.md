---
title: Architecture
description: System architecture, authority model, data flows, and target end state for InsightPulse AI.
---

# Architecture

InsightPulse AI integrates 12 systems around Odoo CE 19 as the transactional core. This section describes how those systems connect, which system owns which data, how data flows between them, and where the platform is heading.

<div class="grid cards" markdown>

-   :material-sitemap:{ .lg .middle } **System topology**

    ---

    The 12-system architecture and how they connect.

    [:octicons-arrow-right-24: System topology](system-topology.md)

-   :material-shield-lock:{ .lg .middle } **Authority model**

    ---

    Which system owns which data, and the hard rules that protect data integrity.

    [:octicons-arrow-right-24: Authority model](authority-model.md)

-   :material-transit-connection-variant:{ .lg .middle } **Data flows**

    ---

    ETL pipelines, medallion transforms, reverse ETL, and SAP integration flows.

    [:octicons-arrow-right-24: Data flows](data-flows.md)

-   :material-flag-checkered:{ .lg .middle } **Target end state**

    ---

    6-phase milestone roadmap from foundation to full enterprise parity.

    [:octicons-arrow-right-24: Target end state](target-end-state.md)

-   :material-map-marker-radius:{ .lg .middle } **SSOT boundaries**

    ---

    Domain-by-domain map of which system is the single source of truth.

    [:octicons-arrow-right-24: SSOT boundaries](ssot-boundaries.md)

-   :material-layers-triple:{ .lg .middle } **Module hierarchy**

    ---

    Target module structure: 60 modules across 8 layers.

    [:octicons-arrow-right-24: Module hierarchy](module-hierarchy.md)

</div>

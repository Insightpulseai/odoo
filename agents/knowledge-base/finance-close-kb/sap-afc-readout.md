# SAP AFC Documentation Readout & Architecture Map

This document contains a recursive readout of the SAP Advanced Financial Closing (AFC) documentation and how its platform features conceptually map to an orchestration engine.

## The Shortest Mental Model

The SAP AFC architecture is organized into six core lanes:

1. **What it is** → overview/guide/system landscape
2. **How to stand it up** → prerequisites/onboarding/automated setup
3. **How to secure it** → user management/security/roles
4. **How to connect systems** → connectivity/integration/business configuration/data sync
5. **How to run and support it** → monitoring/troubleshooting/system monitoring
6. **How to retire or preserve it** → archiving/migration/offboarding

## Core Capabilities to Mine for Odoo Copilot

For the Odoo Copilot / close-orchestration direction, the highest-value capabilities modeled by SAP AFC are:

* **Overview**: The architectural pattern of a central close-control plane (Cloud Foundry app on SAP BTP).
* **Connectivity**: The communication-system model, synchronization behavior (daily vs immediate), target-system navigation, and job execution bridging.
* **Security & User Management**: The static role-template model separating admin setup, task definition, processing, approvals, reporting, and API access.
* **Operations & Observability (Monitoring)**: Managing operational failure modes, handling degraded behavior, observing business logs, and resuming sync after downtime.
* **Lifecycle Management (Archiving & Offboarding)**: Long-term data handling, destructive offboarding grace periods, and audit-retention controls (Manage Archived Closing Task Lists).

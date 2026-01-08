# IPAI Platform Wiki

Welcome to the IPAI Platform documentation wiki for Odoo CE 18.

## Overview

IPAI (InsightPulse AI) provides enterprise-grade capabilities for Odoo CE, bridging the gap with SAP and Odoo Enterprise features.

## Capabilities

| SAP ID | Capability | Spec |
|--------|------------|------|
| AI-AGENTS | [AI Agents & RAG](cap-ai-agents) | [spec](../spec/kapa-plus/) |
| WF-APPROVALS | [Approval Workflows](cap-approvals) | [spec](../spec/approvals/) |
| FI-CLOSE-AFC | [Advanced Financial Closing](cap-fi-close-afc) | [spec](../spec/fi-close-afc/) |

## Quick Links

- [Architecture Overview](Architecture)
- [Installation Guide](Installation)
- [Configuration](Configuration)
- [Diagrams](Diagrams)

## Module Index

### IPAI Core Modules

Modules in `addons/ipai/` provide core platform functionality:

- `ipai_ai_agents` - AI agents with RAG and Supabase KB
- `ipai_approvals` - Generic approval workflows
- `ipai_finance_close_manager` - Month-end close orchestration
- `ipai_workspace_core` - Core workspace functionality

### Delta Modules

Modules in `addons/delta/` provide customization layers for specific deployments.

## Tools

- `ipai_module_gen` - Deterministic module generator from capability maps
- `diagramflow` - Mermaid to BPMN/draw.io converter

## Resources

- [GitHub Repository](https://github.com/jgtolentino/odoo-ce)
- [Odoo CE Documentation](https://www.odoo.com/documentation/18.0/)
- [OCA Modules](https://github.com/OCA)

## Contributing

See the contribution guidelines in the main repository.

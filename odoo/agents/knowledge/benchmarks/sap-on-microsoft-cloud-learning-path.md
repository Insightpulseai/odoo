# SAP on Microsoft Cloud — Learning Path Reference

> Source: [Run SAP on the Microsoft Cloud](https://learn.microsoft.com/en-us/training/paths/run-sap-microsoft-cloud/)
> Role: Benchmark curriculum for agent skill extraction
> Status: Reference only — not a mandatory implementation dependency

---

## Learning path modules

### Module 1: Microsoft and SAP partnership
- Partnership history and strategic alignment
- Joint customer value proposition
- Not an implementation requirement — framing context only

### Module 2: Introduction to SAP on Microsoft Cloud
- SAP BTP on Azure integration patterns
- Identity provider setup and SSO
- Integration scenarios (Teams, Power Platform, Azure services)
- BTP-on-Azure pattern mapping

### Module 3: Innovate using RISE with SAP
- RISE with SAP on Microsoft Cloud
- Workflow optimization and collaboration patterns
- Copilot/Teams process integration opportunities
- Innovation scenarios

### Module 4: Insights for SAP using unified analytics and AI platform
- Unified analytics patterns
- AI/Copilot Studio integration
- Power Platform benchmark extraction
- Data platform integration patterns

### Module 5: Explore Azure networking for SAP RISE
- VNet peering and VPN connectivity
- Internet exposure and ingress patterns
- Shared responsibility boundaries
- Network isolation patterns for ERP workloads

### Module 6: Secure SAP on Microsoft Cloud
- Microsoft Entra ID integration with SAP
- Microsoft Security Copilot for SAP
- Microsoft Sentinel for SAP monitoring
- SAP BTP security and monitoring
- SOAR response patterns
- Azure monitoring for SAP workloads

---

## How to use this reference

1. Extract architectural patterns from each module
2. Classify as benchmark (reference) vs integration (dependency)
3. Translate applicable patterns to Odoo on Azure target stack
4. Never assume SAP is the runtime — it is the quality reference

## Cross-references

- `docs/architecture/reference-benchmarks.md` — benchmark registry
- `agent-platform/ssot/learning/sap_agent_skill_map.yaml` — skill mapping
- `agents/skills/sap-*/` — individual skill implementations

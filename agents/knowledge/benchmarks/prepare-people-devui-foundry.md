# CAF Prepare People + DevUI + Foundry

## Sources

- [CAF: Prepare your people for the cloud](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/plan/prepare-people-for-cloud)
- [Agent Framework DevUI samples](https://learn.microsoft.com/en-us/agent-framework/devui/)
- [Microsoft Foundry overview](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

## Weight

0.90

## Interpretation

CAF defines the capability-building requirement: equip people with skills for Azure adoption.
DevUI is the learning/debug surface: visualize, trace, and test agents locally.
Foundry is the production runtime: host, scale, and manage agents on Azure.

These three combine into one capability ladder:
1. Learn Azure operating model (CAF)
2. Build and debug agents locally (DevUI)
3. Promote mature patterns to production (Foundry)

## Rule

Do not confuse local agent training (DevUI) with hosted agent production (Foundry).
DevUI is explicitly not for production use.

## Allowed influence

- agent-platform training paths and skill requirements
- developer enablement and onboarding docs
- readiness criteria for agent-lane roles

## Must not influence

- production runtime architecture (Foundry owns that)
- repo topology
- SSOT structure
- Odoo module boundaries

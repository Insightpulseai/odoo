# Examples — azd-template-selection

## Example 1: Python API on ACA

**Input**: Python FastAPI service, needs PostgreSQL, Entra auth, ACA deployment

**Template selected**: `azure-samples/todo-python-mongo-aca` (adapted)

**Reasoning**: Closest ACA + Python template. Requires adaptation:
- Replace Cosmos DB with Azure PostgreSQL
- Add Entra auth (template uses API key)
- Add VNet integration (template is public-only)

**Verdict**: Requires adaptation — use as scaffold, replace data tier and auth

---

## Example 2: Full-stack TypeScript app

**Input**: Next.js frontend + Node.js API, ACA, PostgreSQL, Entra auth

**Template selected**: `azure-samples/todo-nodejs-mongo-aca`

**Reasoning**: Full-stack ACA template with Node.js. Requires:
- Frontend adaptation to Next.js
- PostgreSQL instead of MongoDB
- Entra auth integration

**Verdict**: Requires adaptation — structural scaffold is reusable

---

## Example 3: Azure Functions timer job

**Input**: Python timer function, Flex Consumption, managed identity, VNet

**Template selected**: `azure-samples/functions-quickstart-python-azd`

**Reasoning**: Official Python Functions + azd template. Verify:
- Flex Consumption plan (not Classic)
- Managed identity configured
- VNet integration included

**Verdict**: Compatible with minor configuration — check plan type

---

## Anti-pattern: Using App Service template for ACA workload

**Input**: Container workload targeting ACA

**Wrong choice**: `azure-samples/python-web-azd` (targets App Service)

**Why wrong**: App Service templates use different IaC, scaling model, and networking. Adapting an App Service template to ACA is more work than starting from an ACA template.

**Correct approach**: Always filter for ACA-native templates first.

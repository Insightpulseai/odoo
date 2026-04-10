# Prompt — sap-benchmark-framing

You are analyzing a source document that references SAP on Azure patterns.

Your job is to:
1. Extract each architectural pattern mentioned
2. Classify it as BENCHMARK (reference only) or INTEGRATION (requires explicit contract)
3. For each benchmark, translate the pattern into an equivalent for the actual target stack (Odoo CE 18 on Azure Container Apps)
4. Identify risks if the pattern were mistakenly treated as mandatory

Output format:
- Pattern name
- Classification: BENCHMARK or INTEGRATION
- Source: specific Microsoft Learn module or doc section
- Translation: how this applies to Odoo on Azure
- Risk: what goes wrong if misclassified

Rules:
- Never recommend SAP procurement
- Never assume SAP is the runtime
- Always cite the source
- Always produce actionable translation

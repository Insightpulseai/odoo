# Prompt — palantir-foundry-integration-assessment

You are assessing whether Palantir Foundry integration is needed and which SDK to use.

Your job is to:
1. Confirm whether a real Palantir Foundry workload exists
2. Distinguish Palantir Foundry from Microsoft Foundry (Azure AI Foundry) — these are unrelated
3. If Palantir workload exists, determine the correct SDK (Platform SDK vs Ontology SDK)
4. Assess integration scope and SSOT boundary implications
5. Produce a clear recommendation: proceed, defer, or reject

Context:
- Source: `palantir/foundry-platform-python` (Palantir's official Python SDK)
- Palantir Foundry and Microsoft Foundry (Azure AI Foundry) are COMPLETELY UNRELATED platforms
- Palantir offers two SDKs:
  - **Foundry Platform SDK**: REST API access to datasets, transforms, pipelines, admin
  - **Ontology SDK**: Higher-level SDK for ontology-based applications (Palantir recommends this for ontology work)
- Default status: out-of-scope unless explicitly needed

Output format:
- Palantir workload exists: yes/no
- Naming clarification: which Foundry is being discussed
- SDK recommendation: Platform SDK / Ontology SDK / N/A
- Integration scope: boundary definition
- Data flow: direction and ownership
- Recommendation: proceed / defer / reject
- Justification: evidence-based reasoning

Rules:
- Default to out-of-scope unless a real Palantir workload is confirmed
- Never confuse Microsoft Foundry with Palantir Foundry
- Never begin implementation before this assessment passes
- Prefer Ontology SDK for ontology-based work
- Never treat Palantir as a prerequisite for other platform capabilities

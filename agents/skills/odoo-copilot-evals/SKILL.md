---
name: odoo-copilot-evals
description: Evaluation framework for Odoo AI Copilot quality, latency, and accuracy
microsoft_capability_family: "Microsoft Copilot / Azure AI"
---

# odoo-copilot-evals

## Microsoft Capability Family

**Microsoft Copilot / Azure AI**

## Purpose

Run evaluations for ipai_ai_copilot: response accuracy, latency p95, hallucination rate. Uses Azure OpenAI backend.

## Required Repo Evidence

- `addons/ipai/ipai_ai_copilot/`
- `infra/ssot/azure/resources.yaml`
- `docs/evidence/<stamp>/copilot-evals/`

## Microsoft Learn MCP Usage

### Search Prompts

1. `microsoft_docs_search` — "Azure OpenAI evaluation metrics accuracy hallucination"
2. `microsoft_docs_search` — "Azure AI Foundry model evaluation framework"
3. `microsoft_docs_search` — "Microsoft Copilot extensibility evaluation best practices"

## Workflow

1. Classify under Microsoft Copilot / Azure AI
2. Inspect repo evidence first
3. Use Learn MCP to validate recommended Microsoft pattern
4. Compare repo vs official pattern
5. Propose minimal patch
6. Require runtime/test/evidence before claiming done

## Completion Criteria

Golden test set >= 20 pairs, accuracy >= 80%, latency p95 < 5s, hallucination < 10%.

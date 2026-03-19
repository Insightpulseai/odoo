# Skill: Azure Foundry Models

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-models` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-from-partners |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, foundry |
| **tags** | models, llm, claude, gpt, llama, phi, mistral |

---

## Available Models by Provider

### Anthropic (Claude)

| Model | Context | Max Output | Tool Calling |
|-------|---------|------------|-------------|
| `claude-opus-4-6` (Preview) | 1,000,000 | 128,000 | Yes |
| `claude-opus-4-5` (Preview) | 200,000 | 64,000 | Yes |
| `claude-opus-4-1` (Preview) | 200,000 | 32,000 | Yes |
| `claude-sonnet-4-6` (Preview) | 1,000,000 | 128,000 | Yes |
| `claude-sonnet-4-5` (Preview) | 200,000 | 64,000 | Yes |
| `claude-haiku-4-5` (Preview) | 200,000 | 64,000 | Yes |

**Note**: Requires paid Azure subscription with billing account in supported country. Not available for Student/Free Trial/CSP subscriptions.

### Microsoft (Phi)

| Model | Context | Capabilities |
|-------|---------|-------------|
| `Phi-4-mini-instruct` | 131,072 | 23 languages |
| `Phi-4-multimodal-instruct` | 131,072 | Text + images + audio |
| `Phi-4` | 16,384 | 46 languages |
| `Phi-4-reasoning` | 32,768 | Reasoning with chain-of-thought |
| `Phi-4-mini-reasoning` | 128,000 | Reasoning (small) |

### Meta (Llama)

| Model | Context | Capabilities |
|-------|---------|-------------|
| `Llama-3.2-11B-Vision-Instruct` | 128,000 | Text + image |
| `Llama-3.2-90B-Vision-Instruct` | 128,000 | Text + image |
| `Meta-Llama-3.1-405B-Instruct` | 131,072 | 8 languages |
| `Llama-4-Scout-17B-16E-Instruct` | 128,000 | MoE architecture |

### Mistral AI

| Model | Context | Tool Calling |
|-------|---------|-------------|
| `Codestral-2501` | 262,144 | No |
| `Ministral-3B` | 131,072 | Yes |
| `Mistral-small-2503` | 32,768 | Yes |
| `Mistral-medium-2505` | 128,000 | No |

### Cohere

| Model | Type | Tool Calling |
|-------|------|-------------|
| `Cohere-command-r-plus-08-2024` | Chat | Yes |
| `Cohere-command-r-08-2024` | Chat | Yes |
| `Cohere-embed-v3-english` | Embeddings | No |
| `Cohere-embed-v3-multilingual` | Embeddings | No |

## IPAI Model Strategy

| Use Case | Primary | Fallback |
|----------|---------|----------|
| Agent reasoning | Claude Opus 4.6 | GPT-4o |
| Code generation | Claude Sonnet 4.6 | Codestral |
| Embeddings | Cohere embed-v3-multilingual | Azure OpenAI ada-002 |
| Evaluation judge | GPT-5-mini (recommended) | Claude Haiku 4.5 |
| Cost-sensitive | Phi-4-mini | Llama-3.2-11B |
| Foundry copilot | GPT-4.1 (current) | Claude Sonnet 4.5 |

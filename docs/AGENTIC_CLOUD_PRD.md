# InsightPulse Agentic Cloud — PRD v1.0

## 1. Purpose

InsightPulse Agentic Cloud provides a unified, production-grade platform for deploying, orchestrating, and monitoring AI agents, models, automations, and knowledge workflows across the InsightPulse AI ecosystem. It mirrors the functional architecture of DigitalOcean Gradient's Agentic Cloud while running entirely on our infrastructure.

The system standardizes model routing, tooling, environment orchestration, observability, and knowledge indexing across Odoo CE, Scout, CES, Ask CES, AppGenie, W9 Studio pipelines, and command-line operational automation.

---

## 2. High-Level Architecture Overview

| Plane | Role | Components |
|-------|------|------------|
| **Control Plane** | Coordination & agent runtime | Claude Code CLI, Codex runtime, MCP Hub, Pulser registry |
| **Model Plane** | Execution targets (LLMs/Modalities) | OpenAI/Anthropic/DeepSeek APIs + local inference (vLLM/Ollama on GPU droplet) |
| **Knowledge Plane** | Persistent indexed memory and embeddings | Supabase pgvector, n8n ingestion workflows, OCR pipelines |
| **Execution Plane** | Tools and Services invoked by agents | Odoo CE/Edge Functions/n8n/Mattermost automation/Atlas Crawler |
| **Observability Plane** | Monitoring, auditing, telemetry | Superset dashboards, Mattermost alerts, service logs, cron heartbeats |

---

## 3. Agent Types

### 3.1 System Agents
- **Odoo-OCA CI Fixer**
- **SchemaSync Agent**
- **ToolSync**
- **Migration & Repair Agent**
- **Health Monitor Agent**

### 3.2 Business Intelligence Agents
- **Scout GenieView**
- **CES AI Strategist**
- **Sari-Sari Expert Bot**
- **AutoSDR (Arkie)**

### 3.3 Creative & Content Agents
- **W9 Studio Creative Assistant**
- **AdsBot**
- **VoiceAqua Sync Agent**
- **Designer-Mentor**

---

## 4. Model Routing Strategy

| Model Type | Default Backend | Fallbacks | Notes |
|-----------|----------------|-----------|-------|
| General Reasoning | Claude 3.5/Opus | GPT-4.1 / DeepSeek-R1 | Always cache structured output |
| Code | Claude Code 3.7 | GPT-4.1 / DeepSeek-Coder / Local Code-Llama | Prefer MCP tool execution |
| Multimodal Vision | GPT-4o / Gemini Vision Pro | fal-3 (local) | Used for screenshot → UI → code workflows |
| Local First | GPU Droplet vLLM + Ollama | Cloud models only on degrade | Used for privacy & offline execution workflows |

---

## 5. Knowledge Base Strategy

### 5.1 Data Sources
- WARC case studies
- Notion exports
- GitHub READMEs & specs
- Internal docs (`schema`, `sops`, `prd`, `skills`, `modules`)
- OCR-processed receipts/invoices (for Odoo expense automation)

### 5.2 Pipeline
```
Source → n8n Worker → Parser → Chunker → Embeddings → pgvector Store → Agent Query
```

### 5.3 Embedding Format
```
{
"chunk_id": "uuid",
"content": "...",
"source": "ocr|web|github|notion|warc",
"semantic_tags": ["finance", "workflow", "branding"],
"embedding": vector(1536)
}
```

---

## 6. Observability & SLAs

| Metric | Target | Enforcement |
|--------|--------|-------------|
| Service Uptime | ≥ 99.5% | Cron heartbeat → n8n → Postgres → Superset |
| Backup Integrity | 100% verified nightly | Verify + restore test DB + Mattermost alert |
| Agent Failures | Logged + alert if > 3 retries | MCP telemetry → n8n webhook |
| Inference Response Latency | < 5 sec cloud / < 2 sec local | Logged + trend deviation alerts |

---

## 7. Deployment Requirements

- DigitalOcean Droplets (existing)
- Optional GPU droplet for local inferencing
- Supabase (pgvector + RLS)
- n8n (active)
- Mattermost (alerting)
- Claude Code CLI + MCP runtime enabled

---

## 8. Versioning

| Stage | Status | Tag |
|-------|--------|------|
| Baseline Infra | ✔ Complete | `v1.0` |
| Agent Hardening (health + backups) | ✔ Complete | `v1.1` |
| Observability + BI Integration | ✔ Complete | `v1.2` |
| Model Routing + Local GPU Inference | 🚧 Planned | `v1.3` |

---

## 9. Completion Definition

This platform is considered **operational** once:

- All agents use a unified runtime configuration.
- Data ingestion workflows update knowledge bases automatically.
- Monitoring dashboards track uptime, failures, inference latency, and backup health.
- MCP routing selects correct models and toolchains automatically.
- Agents can execute tasks across Odoo, Supabase, GitHub, n8n, OCR, and CLI.

---

**Status: Approved for rollout**

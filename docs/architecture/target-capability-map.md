# Target Capability Map

> Defines the benchmark capabilities, domain packs, and horizontal platform lanes
> that shape our target operating model.
> Updated: 2026-03-17

---

## Overview

The target capability map is built from three layers:

1. **Benchmark Capabilities** -- 5 external platforms that define what "good" looks like in specific domains
2. **Domain Packs** -- 4 vertical industry configurations that compose benchmarks for specific markets
3. **Horizontal Platform Lanes** -- 3 cross-cutting capability lanes that own implementation

Key rule: these benchmarks shape the target capability model. Actual implementation stays grounded in our Azure/Foundry/Databricks/Odoo stack.

---

## Benchmark Capabilities (5)

### Smartly.io -- Activation & Creative Media OS

Role: Cross-channel activation and creative media unification.

Capabilities:
- Cross-channel activation (social, CTV, open web)
- Creative media unification
- AI-driven personalization
- Automated creative testing
- Reporting, forecasting, and planning
- Social, CTV, and open web execution

### Quilt.AI -- Cultural & Consumer Intelligence OS

Role: Cultural and consumer intelligence platform.

Capabilities:
- Cultural intelligence and trend analysis
- Consumer segmentation
- Brand health measurement
- Discourse analysis
- Creative testing and validation
- LLM visibility analysis

### LIONS -- Creative Strategy & Effectiveness Benchmark

Role: Creative strategy and effectiveness benchmarking.

Capabilities:
- Creative strategy benchmark (what wins, why)
- Effectiveness benchmark (business outcome correlation)
- Leadership decision support (investment priorities)

### DataIntelligence.ro -- Marketing Data Hub & Measurement Benchmark

Role: Marketing data aggregation and measurement.

Capabilities:
- Real-time marketing data collection
- Research analytics
- Dashboarding and visualization
- Case studies and sample reports
- Data dictionary and taxonomy

### fal.ai -- Generative Media Creation OS

Role: Generative media creation platform for agencies, creators, brand teams, and content teams.

**Important**: fal.ai targets agencies/creators/brand teams -- it is NOT a developer platform lane. Its capabilities serve creative production, not engineering infrastructure.

Target users: agencies, creators, brand teams, content teams.

Capabilities:
- Image generation and editing
- Video generation
- Audio generation
- 3D generation
- Creative iteration at scale
- Campaign asset variation
- Branded visual consistency

---

## Domain Packs (4)

Domain packs compose benchmarks for specific industry verticals.

| Domain | Primary Benchmarks | Conditional |
|--------|-------------------|-------------|
| Marketing | Smartly.io, Quilt.AI, LIONS, DataIntelligence.ro, fal.ai | -- |
| Retail Media | Smartly.io, Quilt.AI, DataIntelligence.ro, fal.ai | -- |
| Entertainment | Smartly.io, Quilt.AI, LIONS, fal.ai | -- |
| Financial Services | Quilt.AI, LIONS | Smartly.io, DataIntelligence.ro, fal.ai |

Financial services has conditional benchmarks because activation/creative tooling adoption varies significantly by institution type and regulatory posture.

---

## Horizontal Platform Lanes (3)

These cross-cutting lanes own implementation regardless of which domain pack is active.

### Data Engineering

Owns: ingestion, normalization, identity resolution, semantic layers, feature/metrics stores, governed exports.

Implementation: Databricks (lakehouse, Unity Catalog, DLT pipelines), Azure Data Factory for orchestration where needed.

### App Development

Owns: analyst apps, operator apps, client-facing copilots, domain workbenches, internal control plane apps.

Implementation: Databricks Apps, Foundry agent apps, Odoo (ERP surface), Azure Container Apps.

### AI Agents

Owns: planning agents, research/insight agents, activation agents, QA/eval judges, domain advisors.

Implementation: Foundry (agent factory), Databricks (model serving), Azure AI services, Claude/OpenAI for LLM backends.

---

## Relationship to Existing Architecture

| This Map | Existing Doc | Relationship |
|----------|-------------|-------------|
| Benchmark targets | `ssot/capabilities/benchmark_targets.yaml` | SSOT definition |
| Domain packs | `ssot/capabilities/domain_packs.yaml` | SSOT definition |
| Horizontal lanes | `ssot/capabilities/horizontal_platform_lanes.yaml` | SSOT definition |
| Databricks skills | `agents/skills/databricks-*/` | Implementation of data engineering + AI agent lanes |
| Azure architecture | `ssot/azure/target-state.yaml` | Infrastructure layer under all lanes |
| Odoo ERP | `addons/ipai/` | App development lane (ERP surface) |
| Foundry agents | `agents/foundry/` | AI agents lane (agent factory) |

---

## SSOT Files

- `ssot/capabilities/benchmark_targets.yaml` -- canonical benchmark definitions
- `ssot/capabilities/domain_packs.yaml` -- domain pack compositions
- `ssot/capabilities/horizontal_platform_lanes.yaml` -- platform lane ownership

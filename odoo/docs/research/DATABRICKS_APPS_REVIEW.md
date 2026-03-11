# Databricks Apps -- Product Review & IPAI Stack Relevance

**Source URL**: `https://www.databricks.com/product/databricks-apps`
**Research Date**: 2026-03-07
**Branch**: `claude/review-signavio-url-HffM8`

> Databricks Apps lets teams build and deploy internal data/AI applications (Streamlit, Dash, Gradio, React) directly on the Databricks platform with serverless compute, Unity Catalog governance, and SSO. This review assesses relevance to our self-hosted stack.

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Supported Frameworks](#2-supported-frameworks)
3. [Key Features](#3-key-features)
4. [Architecture](#4-architecture)
5. [Use Cases](#5-use-cases)
6. [Pricing](#6-pricing)
7. [Competitive Landscape](#7-competitive-landscape)
8. [IPAI Stack Parity Analysis](#8-ipai-stack-parity-analysis)
9. [Verdict & Recommendations](#9-verdict--recommendations)

---

## 1. Product Overview

| Attribute | Value |
|-----------|-------|
| **Product** | Databricks Apps |
| **Status** | Generally Available (GA) |
| **Adoption** | 20,000+ apps across 2,500+ organizations (as of GA) |
| **Compute** | Serverless (auto-provisioned) |
| **Governance** | Unity Catalog, OAuth 2.0, SSO |
| **Languages** | Python, Node.js (JavaScript/TypeScript) |
| **Target** | Internal data/AI applications within Databricks ecosystem |

Databricks Apps is the fastest way for Data and AI teams to build and deploy internal applications directly on the Databricks Data Intelligence Platform. It eliminates the need for separate infrastructure -- apps run on automatically provisioned serverless compute.

---

## 2. Supported Frameworks

### Python Frameworks

| Framework | Best For | Key Strength |
|-----------|----------|-------------|
| **Streamlit** | Rapid ML demos, data profiling, form-based apps | Extremely fast builds; minimal code; built-in widgets |
| **Dash** (Plotly) | Analytical dashboards with rich interactivity | Production-grade; callback-driven; custom styling |
| **Gradio** | NLP/CV model demos, real-time predictions | Multi-modal (text, images, audio, video) |
| **Flask** | Custom web apps, APIs | Lightweight; full control |
| **Shiny** (Python) | R-style reactive apps | Familiar to R users |

### JavaScript/Node.js Frameworks

| Framework | Best For |
|-----------|----------|
| **React** | Complex SPAs, rich UIs |
| **Angular** | Enterprise apps |
| **Svelte** | Lightweight, fast apps |
| **Express** | API backends |

---

## 3. Key Features

| Feature | Description |
|---------|-------------|
| **Serverless Deployment** | No cluster provisioning; auto-scaled compute |
| **Unity Catalog Integration** | Data governance; access control on tables/models |
| **OAuth 2.0 + SSO** | Enterprise authentication; no custom auth code needed |
| **CI/CD Integration** | Git-based; works with standard CI/CD tools |
| **Audit Logging** | Track app usage and access patterns |
| **Isolated Environments** | Each app has its own dependency environment |
| **Native Data Access** | Direct access to Delta tables, ML models, notebooks |
| **Lakebase** | OLTP database (Postgres-based) for app state |

### App Structure

```
my-app/
├── app.yaml              # App config: run command, env vars, resources
├── requirements.txt      # Python dependencies
├── app.py                # Application code
└── ...
```

`app.yaml` defines the run command (e.g., `streamlit run app.py`), environment variables, and required Databricks resources.

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Databricks Workspace                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐   ┌──────────────┐  ┌─────────────┐  │
│  │ Databricks   │   │ Delta Lake   │  │ Mosaic AI   │  │
│  │ App          │──►│ Tables       │  │ Model       │  │
│  │ (Streamlit/  │   │ (governed)   │  │ Serving     │  │
│  │  Dash/React) │   └──────────────┘  └─────────────┘  │
│  └──────┬───────┘                                       │
│         │           ┌──────────────┐  ┌─────────────┐  │
│         │           │ Lakebase     │  │ SQL         │  │
│         └──────────►│ (OLTP/       │  │ Warehouses  │  │
│                     │  Postgres)   │  │ (analytics) │  │
│                     └──────────────┘  └─────────────┘  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Unity Catalog (Governance) + OAuth + SSO        │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  Compute: Serverless (auto-provisioned per app)         │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Use Cases

| Use Case | Description | Framework Fit |
|----------|------------|--------------|
| **Data Quality Dashboards** | Monitor data pipeline health, quality metrics | Streamlit, Dash |
| **LLM Copilots / RAG Apps** | Chat interfaces over enterprise data | Gradio, React |
| **Self-Service Analytics** | Business users query and visualize data | Streamlit, Dash |
| **Data Entry Forms** | Structured data collection into Delta tables | Flask, React |
| **ML Model Demos** | Interactive model inference UI | Gradio, Streamlit |
| **Custom Ops Interfaces** | Team-specific operational tools | React, Dash |
| **AI Agent Interfaces** | Agentic AI applications | React, Gradio |

---

## 6. Pricing

| Component | Rate | Notes |
|-----------|------|-------|
| **Compute** | $75/DBU (Premium, AWS) | Per-hour while app is running |
| **Cloud Infrastructure** | Additional | AWS/Azure/GCP charges on top |
| **Limit** | Limited apps per workspace | Workspace-level cap |

### Cost Example

| Scenario | Calculation | Monthly Cost |
|----------|-------------|-------------|
| Small app (0.5 DBU/hr, 8hr/day, 22 days) | 88 hrs × 0.5 DBU × $75 | ~$3,300 |
| Medium app (1 DBU/hr, 12hr/day, 30 days) | 360 hrs × 1 DBU × $75 | ~$27,000 |
| Always-on app (0.5 DBU/hr, 24/7) | 720 hrs × 0.5 DBU × $75 | ~$27,000 |

**Note**: These are Databricks fees only. Cloud infrastructure costs are additional (typically 50-200% more).

---

## 7. Competitive Landscape

| Platform | Type | Best For | Cost | Data Integration |
|----------|------|----------|------|-----------------|
| **Databricks Apps** | Managed (Databricks) | Teams in Databricks ecosystem | $75/DBU/hr + cloud | Native (Unity Catalog, Delta) |
| **Streamlit Cloud** | Managed (Snowflake) | Quick prototyping | Free tier + limits | Limited |
| **Vercel** | Managed hosting | Frontend/JS apps | $0-$20/mo + usage | None built-in |
| **DigitalOcean App Platform** | Managed PaaS | General web apps | $5-$25/mo | None built-in |
| **Self-hosted (Docker)** | Self-managed | Full control | $5-$50/mo infra | DIY |
| **Dash Enterprise** | Managed (Plotly) | Enterprise analytics | $$$ (quote-based) | Moderate |
| **Coolify / Dokploy** | Self-hosted PaaS | Cost-conscious self-hosting | $0 (infra only) | DIY |

### Key Trade-offs

| Criteria | Databricks Apps | Self-Hosted |
|----------|----------------|-------------|
| **Setup** | Minutes | Hours-days |
| **Governance** | Built-in (Unity Catalog) | DIY (Keycloak + RLS) |
| **Vendor Lock-in** | High (Databricks ecosystem) | None |
| **Cost** | $3K-$27K+/mo | $5-$50/mo |
| **Data Access** | Native Delta/ML | PostgreSQL direct |
| **Scalability** | Serverless auto-scale | Manual scaling |

---

## 8. IPAI Stack Parity Analysis

### What Databricks Apps Offers vs What We Have

| Databricks Apps Feature | IPAI Stack Equivalent | Parity |
|------------------------|----------------------|--------|
| **Serverless app hosting** | Vercel (Next.js) + DigitalOcean | 85% |
| **Data dashboards** | Apache Superset (self-hosted, free) | 95% |
| **ML model demos** | Hugging Face Spaces (free) or DO + Gradio | 80% |
| **SSO/Auth** | Keycloak (self-hosted, free) | 90% |
| **Audit logging** | `ipai_platform_audit` + Supabase logs | 80% |
| **Data governance** | Supabase RLS + PostgreSQL roles | 70% |
| **CI/CD** | GitHub Actions (self-hosted runners) | 95% |
| **Real-time apps** | Supabase Realtime + Next.js on Vercel | 85% |

### What We Already Have (Better)

| Capability | IPAI Advantage |
|-----------|---------------|
| **BI Dashboards** | Superset is more feature-rich than Streamlit for BI; free; self-hosted |
| **Web Apps** | Vercel (Next.js) is superior for production web apps; $0-$20/mo |
| **Cost** | Our entire infra is $50-100/mo vs $3K-27K+/mo for Databricks Apps |
| **Vendor Independence** | We own everything; no lock-in |
| **Odoo Integration** | Direct PostgreSQL access; no middleware needed |

### Gaps (Minor)

| Gap | Severity | Notes |
|-----|----------|-------|
| **Serverless data app hosting** | Low | Vercel + Supabase covers this |
| **Native ML model serving UI** | Low | Can use Gradio on DO or HF Spaces |
| **Unified governance for apps** | Low | Keycloak + Supabase RLS sufficient |

---

## 9. Verdict & Recommendations

### Verdict: **Do NOT adopt Databricks Apps**

| Criterion | Assessment |
|-----------|-----------|
| **Cost** | $3K-27K+/mo vs our $50-100/mo (30-270x our budget) |
| **Lock-in** | Requires Databricks ecosystem; proprietary |
| **Scale** | Designed for enterprises already on Databricks |
| **Self-Hosting** | Not self-hostable (managed SaaS only) |
| **Our Needs** | Superset + Vercel + Supabase already cover our app deployment needs |

### What's Worth Borrowing

| Concept | IPAI Implementation | Priority |
|---------|-------------------|----------|
| **`app.yaml` pattern** | Already use `docker-compose.yml` + `vercel.json` | N/A (done) |
| **Isolated app environments** | Docker containers per app | N/A (done) |
| **Lakebase (Postgres OLTP for apps)** | Already use PostgreSQL + Supabase | N/A (done) |
| **Gradio for ML demos** | Deploy Gradio on DO droplet or HF Spaces | P3 |

### Cost Comparison

| Solution | Monthly Cost | Annual Cost |
|----------|-------------|-------------|
| **IPAI Stack** (Superset + Vercel + DO) | $50-$120 | $600-$1,440 |
| **Databricks Apps** (single small app) | $3,300+ | $39,600+ |
| **Databricks Apps** (medium workload) | $27,000+ | $324,000+ |

---

## Sources

- [Databricks Apps Product Page](https://www.databricks.com/product/databricks-apps)
- [Databricks Apps Documentation (AWS)](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)
- [Databricks Apps Documentation (Azure)](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/)
- [Introducing Databricks Apps (Blog)](https://www.databricks.com/blog/introducing-databricks-apps)
- [Announcing GA of Databricks Apps](https://www.databricks.com/blog/announcing-general-availability-databricks-apps)
- [Key Concepts in Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/key-concepts)
- [Databricks Apps Pricing](https://www.databricks.com/product/pricing/databricks-apps)
- [Databricks Apps Guide (Tredence)](https://www.tredence.com/blog/mastering-databricks-apps-from-creation-to-deployment-of-interactive-data-applications)
- [Databricks Apps Pricing Discussion (Community)](https://community.databricks.com/t5/data-engineering/databricks-apps-pricing/td-p/138086)
- [Best Streamlit Alternatives (Plotly)](https://plotly.com/blog/best-streamlit-alternatives-production-data-apps/)
- [Vercel Alternatives (DigitalOcean)](https://www.digitalocean.com/resources/articles/vercel-alternatives)

---

*Review compiled: 2026-03-07*
*Branch: claude/review-signavio-url-HffM8*
*See also: [DATABRICKS_DATA_ENGINEERING_REVIEW.md](./DATABRICKS_DATA_ENGINEERING_REVIEW.md), [DATABRICKS_ARCHITECTURES_INDEX.md](./DATABRICKS_ARCHITECTURES_INDEX.md)*

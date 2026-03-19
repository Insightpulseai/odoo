# Knowledge: State of AI Agents 2026 — Databricks Report

## Source

- **Report**: Databricks State of AI Agents 2026
- **Data basis**: 20,000+ organizations, 60%+ of Fortune 500
- **Period**: November 2024 — October 2025
- **Extracted**: 2026-03-15

---

## Key Findings (5)

### 1. Multi-agent systems are the new enterprise operating model
- Supervisor Agent usage grew **327%** in 4 months (Jul–Oct 2025)
- 37% of Agent Bricks usage is Supervisor Agent (multi-agent orchestration)
- 31% is Information Extraction (structured data from unstructured docs)

### 2. AI agents drive core database activities
- **80%** of databases are now created by AI agents (up from 0.1% in 2023)
- **97%** of database branches created by AI agents
- Drives need for "Lakebase" — a new class of operational database

### 3. AI automates routine tasks across industries
- **40%** of top AI use cases focus on customer experience
- Top use cases: market intelligence, predictive maintenance, customer support, claim processing
- Use cases are pragmatic, not experimental

### 4. Model flexibility is the new strategy
- **78%** of companies use 2+ LLM model families
- **59%** use 3+ model families (up from 36% in 5 months)
- Multi-model prevents vendor lock-in

### 5. Governance and evaluations drive production
- Companies using **evaluation tools** get **6x** more AI into production
- Companies using **AI governance** put **12x** more AI into production
- AI governance investment grew **7x** in 9 months

---

## Enterprise AI Agent Types (Databricks Agent Bricks)

| Agent Type | Usage Share | Description |
|-----------|-----------|-------------|
| **Supervisor Agent** | 37% | Orchestrates multiple agents for complex tasks |
| **Information Extraction** | 31% | Converts unstructured text → structured tables |
| **Knowledge Assistant** | ~16% | Q&A chatbots on enterprise documents |
| **Custom LLMs** | ~16% | Domain-specific text generation |

### Supervisor Agent by Industry

| Industry | Adoption Level |
|----------|---------------|
| Technology | **Highest** (~4x more than any other) |
| Financial Services | High |
| Healthcare & Life Sciences | Medium |
| Manufacturing & Automotive | Medium |
| Retail & Consumer Goods | Medium |
| Communication, Media & Entertainment | Lower |
| Energy & Utilities | Lower |
| Public Sector & Education | Lower |

---

## Top AI Use Cases by Industry

| Industry | #1 Use Case | Category |
|----------|-------------|----------|
| **Technology** | Market Intelligence (16%) | Strategic Analytics |
| **Financial Services** | Market Intelligence (19%) | Strategic Analytics |
| **Healthcare & Life Sciences** | Medical Literature Synthesis (23%) | Knowledge Management |
| **Manufacturing & Automotive** | Predictive Maintenance (35%) | Business Operations |
| **Energy & Utilities** | Predictive Maintenance (33%) | Business Operations |
| **Retail & Consumer Goods** | Market Intelligence (14%) | Strategic Analytics |
| **Communication, Media & Entertainment** | Customer Advocacy (14%) | Customer Experience |

### Top 15 Use Cases (All Industries)

| Rank | Use Case | Category |
|------|----------|----------|
| 1 | Market Intelligence | Strategic Analytics |
| 2 | Predictive Maintenance | Business Operations |
| 3 | Customer Support | Customer Experience |
| 4 | Inquiry Classification & Routing | Customer Experience |
| 5 | Customer Advocacy | Customer Experience |
| 6 | Claim Processing | Risk & Compliance |
| 7 | Customer Onboarding | Customer Experience |
| 8 | Anti-Money Laundering | Risk & Compliance |
| 9 | Medical Literature Synthesis | Healthcare Knowledge |
| 10 | Personalized Marketing Content | Customer Experience |
| 11 | Order Process Automation | Business Operations |
| 12 | Regulatory Reporting | Risk & Compliance |
| 13 | Loan Origination | Risk & Compliance |
| 14 | Customer Interaction Summarization | Customer Experience |
| 15 | Clinical Note Summarization | Healthcare Knowledge |

---

## AI Agent Infrastructure Shift

### Database Operations by AI Agents

| Metric | Oct 2023 | Oct 2024 | Oct 2025 |
|--------|----------|----------|----------|
| Databases created by AI | 0.1% | 27% | **80%** |
| Database branches created by AI | 0.1% | 18% | **97%** |

### Why Traditional OLTP Fails for Agents

| Traditional OLTP | Agent-Era Requirements |
|-----------------|----------------------|
| Human workflows, predictable transactions | Continuous, high-frequency read/write |
| Infrequent schema changes | Rapid schema evolution |
| Manual provisioning | Programmatic create/teardown |
| Moderate concurrency | Massive concurrency |
| Minutes-scale provisioning | Millisecond-scale branching |

### Lakebase (New Category)

Operational database built for AI era:
- Combines OLTP performance with lakehouse elasticity
- Millisecond branching for agent test environments
- OLTP on same object store as analytics lakehouse
- Based on Neon (serverless Postgres, acquired by Databricks)

---

## Multi-Model Strategy

### LLM Family Usage (Oct 2025)

| # Model Families | % of Companies |
|-----------------|----------------|
| 1 model family | 22% |
| 2 model families | 19% |
| 3+ model families | **59%** |

### By Industry (2+ models)

| Industry | 2+ Model Families |
|----------|-------------------|
| Retail & Consumer Goods | **83%** (highest) |
| Technology | ~80% |
| Financial Services | ~75% |
| Healthcare & Life Sciences | ~70% |

### Inference Patterns

- **96%** of all requests are real-time (not batch)
- Tech: 32 real-time requests per 1 batch
- Healthcare: 13 real-time per 1 batch
- Real-time critical for copilots, support, personalization

---

## AI in Production: What Works

### The Production Gap

- 95% of GenAI pilots fail to reach production (MIT NANDA 2025)
- Only 2% of organizations rate AI delivery as "high" for measurable results
- Only 19% have deployed AI agents (mostly limited)

### What Drives Production Success

| Factor | Impact |
|--------|--------|
| **AI evaluation tools** | **6x** more projects in production |
| **AI governance** | **12x** more projects in production |
| **AI governance investment** | Grew **7x** in 9 months |

### Governance = Production Enabler

- Defines how data is used
- Sets guardrails and rate limits
- Establishes structured accountability
- Ensures alignment with ethical standards
- Enables compliance at scale

### Evaluations = Quality Catalyst

- Custom benchmarks on enterprise data (not generic benchmarks)
- Continuous testing: accuracy, safety, fairness, compliance
- Ties evaluation metrics to business KPIs (CSAT, handle time, revenue lift)
- Rapid feedback → early problem detection → iterative improvement
- Transforms agents from static tools to learning systems

---

## IPAI Relevance Map

| Report Finding | IPAI Current State | Action |
|---------------|-------------------|--------|
| Multi-agent (Supervisor Agent) | Single agents + n8n routing | **Adopt**: Build supervisor agent pattern |
| Information Extraction (31%) | ADE + Azure DI (planned) | **Validate**: Aligns with our OCR strategy |
| 78% use 2+ model families | Claude-first + Azure OpenAI fallback | **Aligned** — add Phi-4 for cost-sensitive |
| 80% DBs created by agents | Manual DB creation | **Consider**: Neon/Lakebase for agent dev DBs |
| 97% branches by agents | Manual test DB creation | **Adopt**: Agent-created `test_<module>` DBs |
| Governance → 12x production | Constitution + rules files (static) | **Gap**: Need enforceable governance layer |
| Evaluations → 6x production | `evals/odoo-copilot/` (manual) | **Adopt**: Cloud eval (Foundry SDK) |
| 40% use cases = customer exp | BIR/finance focus | **Expand**: Add customer-facing agents |
| Real-time > batch (96%) | Batch-oriented workflows | **Align**: Ensure agent responses are real-time |

### Key Takeaways for IPAI Strategy

1. **Governance is not optional** — it's the #1 driver of production deployment (12x). Our constitution + rules are a start. Need enforceable policies + monitoring.

2. **Evaluations are not optional** — 6x production impact. Migrate from manual rubric to Foundry cloud eval immediately.

3. **Multi-agent is the direction** — Supervisor Agent is the fastest-growing pattern. Our SDLC feedback loop (coding agent + SRE agent) aligns. Formalize as supervisor pattern.

4. **Information Extraction is the #2 use case** — Our ADE + Azure DI strategy is directly on trend. Priority: deploy invoice/receipt/BIR extraction pipeline.

5. **Agents creating databases** — Consider Neon-style branching for `test_<module>` databases. Agents should be able to spin up/tear down test environments.

6. **Multi-model is table stakes** — 78% use 2+ families. Our Claude + Azure OpenAI + Phi-4 strategy is aligned. Ensure easy model swapping in agent definitions.

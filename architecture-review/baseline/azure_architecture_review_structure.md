# Azure Architecture Review - Baseline Structure

**Source**: [Azure Architecture Review](https://learn.microsoft.com/en-us/assessments/azure-architecture-review/)
**Extracted**: <!-- TODO: Date -->
**Purpose**: Reference structure for our tailored review framework

---

## Azure Well-Architected Framework Pillars

The Azure Architecture Review is based on the Well-Architected Framework with these pillars:

### 1. Reliability
- **Focus**: Ability to recover from failures and continue to function
- **Key questions**: Failure mode analysis, health modeling, self-healing
- **Outcomes**: Defined SLOs, recovery procedures, chaos engineering

### 2. Security
- **Focus**: Protect data, systems, and assets
- **Key questions**: Identity, network, data protection, governance
- **Outcomes**: Zero trust implementation, defense in depth

### 3. Cost Optimization
- **Focus**: Manage costs while maximizing value
- **Key questions**: Resource optimization, pricing models, cost allocation
- **Outcomes**: Cost visibility, optimization recommendations

### 4. Operational Excellence
- **Focus**: Operations processes that keep production running
- **Key questions**: Monitoring, incident response, deployment practices
- **Outcomes**: Reduced MTTR, automated operations

### 5. Performance Efficiency
- **Focus**: Efficiently meet demands
- **Key questions**: Scaling, caching, data partitioning
- **Outcomes**: Performance baselines, capacity planning

---

## Question Structure (Azure Pattern)

Each Azure review question follows this pattern:

```yaml
question:
  text: "How do you [action] for [scope]?"
  intent: Why this matters for the pillar
  options:
    - score: 0
      text: "Not implemented"
    - score: 1
      text: "Ad-hoc / manual"
    - score: 2
      text: "Partially automated"
    - score: 3
      text: "Fully implemented"
    - score: 4
      text: "Continuously improving"
  recommendations:
    - action: What to do if score is low
      resources: Links to guidance
```

---

## Mapping to Our Framework

| Azure Pillar | Our Domains |
|--------------|-------------|
| Reliability | F. Reliability & DR, E. Integration & Automation |
| Security | A. Tenancy, B. Identity, H. Security Engineering |
| Cost Optimization | J. Cost & FinOps |
| Operational Excellence | G. Observability, L. SDLC |
| Performance Efficiency | I. Performance & Capacity |
| (Added) Data | C. Data Architecture |
| (Added) Application | D. App Architecture |
| (Added) Compliance | K. Compliance & Governance |

---

## Key Differences in Our Framework

1. **Multi-cloud focus**: Azure + Supabase + DigitalOcean + Vercel
2. **Postgres-first data**: RLS, Supabase Edge Functions
3. **Automation emphasis**: n8n, MCP agents, thin orchestration
4. **Evidence-driven**: Machine-verifiable artifacts preferred
5. **Blockers concept**: Hard fails regardless of score

---

## TODO: Full Extraction

- [ ] Extract complete question set from Azure review
- [ ] Map each question to our domains
- [ ] Adapt scoring to our scale (0-4)
- [ ] Add evidence requirements per question

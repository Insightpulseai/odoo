# Domain Intelligence Shells

> How Diva, Odoo, and Studio relate across domain verticals.
> Each vertical has an intelligence shell (Diva decides/routes/analyzes),
> an execution plane (Odoo governs/tracks), and optionally a creative plane (Studio creates/polishes).

---

## Doctrine

1. **Diva** owns the intelligence shell: routing, analysis, goal tracking, governance
2. **Odoo** owns downstream execution: transactional records, workflows, compliance tracking
3. **Studio** consumes downstream creative signals: finishing, export, publish — when creative activation is relevant

These are not three monoliths. Each domain vertical composes from the same three planes with domain-specific grounding.

---

## Domain Verticals

### Marketing Intelligence

| Plane | Role | Scope |
|-------|------|-------|
| Diva | Customer 360, campaign intelligence, brand intelligence | Composable CDP + governed lakehouse |
| Odoo | CRM records, campaign execution, partner management | Transactional SoR |
| Studio | Campaign creative, brand assets, social content | Finishing + publish |

Key capability: turn audience insights (Diva) into campaign actions (Odoo) and creative output (Studio).

### Media Intelligence

| Plane | Role | Scope |
|-------|------|-------|
| Diva | Audience analytics, content intelligence, monetization signals, QoE | Structured + unstructured + streaming |
| Odoo | Content scheduling, rights management, revenue tracking | Transactional SoR |
| Studio | Content production, post-production, platform export | Finishing + publish |

Key capability: turn content/audience signals (Diva) into scheduling/rights actions (Odoo) and finished media (Studio).

### Retail Intelligence

| Plane | Role | Scope |
|-------|------|-------|
| Diva | Inventory analytics, supply chain intelligence, demand forecasting, replenishment signals | Real-time + batch |
| Odoo | Purchase orders, inventory moves, sales orders, supplier management | Transactional SoR |
| Studio | Product visuals, catalog assets, POS displays | Finishing (when relevant) |

Key capability: turn supply/demand signals (Diva) into procurement/inventory actions (Odoo).

### Financial Operations Intelligence

| Plane | Role | Scope |
|-------|------|-------|
| Diva | Growth/protection/efficiency analytics, fraud/risk signals, compliance intelligence | Governed lakehouse |
| Odoo | Journal entries, invoices, payments, tax compliance, month-end close | Transactional SoR |
| Studio | Financial reports, investor decks (rare) | Finishing (rare) |

Key capability: turn risk/compliance/efficiency signals (Diva) into financial actions (Odoo).

---

## Composition Pattern

```
[Domain Signals]
       |
   Diva Shell (route, analyze, decide)
       |
   +---+---+
   |       |
 Odoo    Studio
 (execute) (create)
```

Each domain vertical is a **grounding configuration**, not a separate product. The same Diva modes, Odoo Copilot, and Studio Copilot serve all verticals with domain-specific KB segments and skill packs.

---

## What This Is Not

- Not four separate products per vertical
- Not a "mega-copilot" that knows all domains at once
- Not a reason to build domain-specific runtime infrastructure
- Not a replacement for Odoo's native module capabilities

---

## SSOT References

- Assistant surfaces: `ssot/agents/assistant_surfaces.yaml`
- Diva modes: `ssot/agents/diva_copilot.yaml#modes`
- Creative provider policy: `ssot/creative/provider_policy.yaml`

---

*Last updated: 2026-03-24*

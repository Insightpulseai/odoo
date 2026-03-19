# Strategy Layer

**Purpose**: Define enterprise direction, objectives, and value creation approach

**Layer Position**: Layer 1 of 7 (Strategy → Portfolio → Process → Execution → Control → Evidence → Integration)

---

## Purpose & Scope

This layer contains strategic artifacts that guide the entire organization's direction:

- **OKRs**: Quarterly and annual objectives and key results
- **Value Streams**: End-to-end value delivery workflows
- **Capabilities**: Core organizational competencies
- **Parity Analysis**: Strategic gap analysis (EE vs CE, SaaS vs Self-hosted)

---

## ID Convention

**Format**: `STRAT-<DOMAIN>-<NUMBER>`

**Examples**:
- `STRAT-OKR-2026Q1` - Q1 2026 OKRs
- `STRAT-PARITY-001` - Odoo.sh-grade parity strategy
- `STRAT-VALUE-ERP` - ERP value stream definition
- `STRAT-CAP-AI` - AI capabilities roadmap

---

## Directory Structure

```
strategy/
├── README.md                    # This file
├── okrs/                        # Quarterly objectives
│   ├── 2026-Q1.md
│   └── 2026-Q2.md
├── value-streams/               # End-to-end value flows
│   ├── erp-value-stream.md
│   └── analytics-value-stream.md
├── capabilities/                # Core competencies
│   ├── ai-capabilities.md
│   └── automation-capabilities.md
└── parity/                      # Strategic gap analysis
    ├── oca-parity/
    ├── best-of-breed/
    └── odoo-sh-grade/
```

---

## Connections to Other Layers

### Downstream (Strategy drives these layers)

- **Portfolio** (`docs/portfolio/`): Strategic objectives translate into portfolio initiatives
  - Example: `STRAT-PARITY-001` → `PORT-2026-007` (Odoo.sh-Grade Parity initiative)

- **Process** (`docs/process/`): Strategic capabilities require process definitions
  - Example: `STRAT-CAP-AI` → `PROC-AI-001` (AI model deployment process)

- **Control** (`docs/control/`): Strategic goals require control gates
  - Example: `STRAT-OKR-2026Q1` → `CTRL-GATE-001` (Architecture review gate)

### Upstream (These layers validate strategy)

- **Evidence** (`docs/evidence/`): Validates strategic outcomes achieved
  - Example: `STRAT-PARITY-001` validated by `EVID-20260212-001` (migration evidence)

---

## Document Format

All strategic documents must include frontmatter:

```yaml
---
id: STRAT-OKR-2026Q1
type: okr
name: Q1 2026 Enterprise OKRs
status: active
owner: leadership_team
period: 2026-Q1
portfolio_initiatives:
  - PORT-2026-007
  - PORT-2026-008
processes: [PROC-DEV-001, PROC-QA-002]
controls: [CTRL-GATE-001]
evidence: []
---
```

---

## How to Contribute

### Creating New Strategic Artifacts

1. **Choose appropriate subdirectory**: okrs/, value-streams/, capabilities/, parity/
2. **Generate unique ID**: Use `STRAT-<DOMAIN>-<NUMBER>` format
3. **Add frontmatter**: Include all required metadata
4. **Link to portfolio**: Reference downstream portfolio initiatives
5. **Update traceability index**: Add to `docs/TRACEABILITY_INDEX.yaml`

### Reviewing Strategic Artifacts

- **Alignment**: Does this align with enterprise mission/vision?
- **Measurability**: Can success be objectively measured?
- **Linkage**: Are downstream portfolio/process artifacts referenced?
- **Evidence**: Can we validate achievement through evidence layer?

---

## Key Strategic Documents

### Current OKRs
- **2026-Q1**: Focus on Odoo.sh-grade parity, AI automation, BIR compliance

### Active Value Streams
- **ERP Value Stream**: Order-to-Cash, Procure-to-Pay, Record-to-Report
- **Analytics Value Stream**: Data ingestion → transformation → visualization → decision

### Core Capabilities
- **AI/ML**: OCR, document intelligence, predictive analytics
- **Automation**: n8n workflows, MCP integration, Supabase bridges
- **Compliance**: BIR tax filing, audit trails, governance

### Parity Analysis
- **OCA Parity**: 80%+ Enterprise Edition feature coverage via CE + OCA
- **Best-of-Breed**: SaaS tool equivalents (Linear, Notion, Slack, etc.)
- **Odoo.sh-Grade**: Self-hosted deployment matching Odoo.sh reliability

---

## Success Metrics

Strategy layer effectiveness measured by:

1. **Cascade Clarity**: 100% of portfolio initiatives trace to strategic objectives
2. **Evidence Validation**: Strategic outcomes validated through evidence artifacts
3. **Alignment Score**: Team consensus on strategic priorities (quarterly survey)
4. **Execution Rate**: % of strategic initiatives delivered on time

---

## References

- **Traceability Index**: `docs/TRACEABILITY_INDEX.yaml`
- **Portfolio Layer**: `docs/portfolio/README.md`
- **Process Layer**: `docs/process/README.md`
- **Control Layer**: `docs/control/README.md`

---

*Last updated: 2026-02-12*

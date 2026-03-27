# Marketing Analytics Reference Model

> External accelerator patterns for the marketing measurement and activation lane.
> These are **reference implementations**, not canonical product architecture.
>
> **SSOT authority unchanged**:
> - Odoo = System of Record
> - platform = control plane / SSOT
> - data-intelligence = Databricks
> - agent-platform = Foundry
> - Azure Boards = execution coordination
>
> **Cross-references**:
> - `docs/architecture/enterprise_data_platform.md` § 8 (accelerator summary)
> - `ssot/governance/azdo-execution-hierarchy.yaml` (OBJ-004, OBJ-007)

---

## 1. Accelerator Inventory

### Media Mix Modeling (MMM)

**Source**: [Databricks MMM Accelerator](https://www.databricks.com/solutions/accelerators/media-mix-modeling)

**What it does**: Pre-built notebook-based accelerator for channel-level spend optimization.
Unifies TV, social, email, and other channel data; measures effectiveness; simulates
scenarios; optimizes media spend allocation.

**Fit for IPAI**: High — directly supports TBWA/SMP campaign measurement use case.

**Maps to**: FEAT-004-03 (Campaign measurement cloud)

---

### Multi-Touch Attribution (MTA)

**Source**: [Databricks MTA Accelerator](https://www.databricks.com/solutions/accelerators/multi-touch-attribution)

**What it does**: Journey/channel attribution with fine-grain dashboards.
Connects ad spend and marketing activities to sales, with easier integration
of new channels via lakehouse architecture.

**Fit for IPAI**: High — complements MMM with granular, journey-level attribution.

**Maps to**: FEAT-004-03 (Campaign measurement cloud)

---

### Customer Lifetime Value (CLV)

**Source**: [Databricks CLV Accelerator](https://www.databricks.com/solutions/accelerators/customer-lifetime-value)

**What it does**: Notebook-based accelerator using sample retail data plus ML to predict
future purchases. Supports retention modeling, acquisition prioritization, and
high-value customer identification.

**Fit for IPAI**: Medium-High — feeds Customer 360 gold layer with predictive scores.

**Maps to**: FEAT-004-02 (Customer 360 intelligence fabric)

---

### Sales Forecasting and Attribution

**Source**: [Databricks Sales Forecasting Accelerator](https://www.databricks.com/solutions/accelerators/sales-forecasting)

**What it does**: Reference architecture around batch/streaming ad metrics plus sales data.
Links advertising spend to sales outcomes with forecasting capabilities.

**Fit for IPAI**: Medium — useful for revenue pipeline modeling once sales volume justifies it.

**Maps to**: FEAT-004-03 (Campaign measurement cloud), FEAT-007-01 (Target solution portfolio)

---

### Meta Conversions API (CAPI)

**Source**: [Meta CAPI on Databricks](https://www.databricks.com/blog/activate-first-party-data-meta-conversions-api-databricks)

**What it does**: Bridges governed lakehouse data to Meta's ad platform. Supports
large-scale event processing in Databricks with server-side signal delivery
in a privacy-first measurement model.

**Fit for IPAI**: High for TBWA/SMP use case — first-party activation is a key differentiator.

**Maps to**: FEAT-007-03 (TBWA/SMP packaging)

---

## 2. Adoption Criteria

Before adopting any accelerator into the platform:

- [ ] Evaluate notebook code against current Databricks workspace version
- [ ] Map input data requirements to existing bronze/silver tables
- [ ] Confirm no Enterprise-only Databricks features are required (or document the dependency)
- [ ] Estimate DBU cost impact using cluster policies from § 5 of enterprise_data_platform.md
- [ ] Create Azure Boards Task under the mapped Issue with acceptance criteria
- [ ] Document any custom modifications in `spec/data-intelligence-pipeline/`
- [ ] Output artifacts land in gold layer, served via Unity Catalog + Databricks SQL

---

## 3. What These Do NOT Replace

These accelerators are starting points. They do not replace:

| What | Canonical Source |
|------|-----------------|
| Plane boundaries (Odoo/Databricks/Foundry) | `docs/architecture/UNIFIED_TARGET_ARCHITECTURE.md` |
| Azure landing zone / identity / network | `docs/architecture/identity_and_secrets.md`, infra/ |
| ERP integration contracts | `docs/contracts/DATA_AUTHORITY_CONTRACT.md` |
| SSOT and runtime authority | `ssot/governance/operating-model.yaml` |
| Delivery / DevSecOps / reliability | `docs/governance/devops_operating_model.md` |
| BIR tax compliance rules | `odoo/.claude/rules/bir-compliance.md` |

---

## 4. Azure Boards Issue Cross-Links

| Accelerator | Primary Issue | Secondary Issue |
|-------------|--------------|-----------------|
| MMM | FEAT-004-03 Campaign measurement cloud | FEAT-007-01 Target solution portfolio |
| MTA | FEAT-004-03 Campaign measurement cloud | — |
| CLV | FEAT-004-02 Customer 360 intelligence fabric | FEAT-007-01 Target solution portfolio |
| Sales Forecasting | FEAT-004-03 Campaign measurement cloud | FEAT-007-01 Target solution portfolio |
| Meta CAPI | FEAT-007-03 TBWA/SMP packaging | FEAT-004-03 Campaign measurement cloud |

---

*Last updated: 2026-03-17*

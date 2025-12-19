# ADR-0001: No Notion Integration — Clone SaaS UX Natively in Odoo CE/OCA

**Status**: Accepted  
**Date**: 2025-01-20  
**Authors**: Jake Tolentino, IPAI Control Center Team  
**Tags**: architecture, integration-strategy, parity-modules, saas-cloning

---

## Context

The IPAI Control Center project requires enterprise-grade capabilities for:
- Document management and wiki/knowledge base (Notion baseline)
- Travel & expense management (Concur baseline)
- Asset tracking and checkout workflows (Cheqroom baseline)
- Project portfolio management (Clarity PPM baseline)
- Supplier relationship management (SAP SRM baseline)

**Initial Consideration**: Build integrations/connectors to these SaaS products.

**Strategic Question**: Should we integrate with external SaaS tools, or clone their capabilities natively in Odoo CE + OCA modules?

---

## Decision

**We will NOT integrate with Notion, Concur, Cheqroom, Clarity PPM, or SAP SRM.**

Instead, we will **clone their SaaS user experience (UX) natively into Odoo CE 18.0 using OCA modules plus IPAI custom modules**.

**Parity Modules** (native Odoo apps, NOT external connectors):
- `ipai_workspace_core` — Shared knowledge primitives (wiki, docs, collaboration)
- `ipai_expense` — Concur travel & expense parity
- `ipai_assets` — Cheqroom asset management parity
- `ipai_ppm` — Clarity project portfolio management parity
- `ipai_srm` — SAP SRM supplier relationship management parity

**IPAI Stack Integration** (platform services, NOT SaaS parity targets):
- **Supabase** — PostgreSQL analytics + RLS + Edge Functions
- **n8n** — Workflow automation and orchestration
- **Mattermost** — Notifications and ops communications
- **Superset** — BI dashboards and analytics

---

## Rationale

### 1. Data Sovereignty & Compliance
**SaaS Risk**: Cloud-only data residency, unknown compliance guarantees  
**Odoo CE Advantage**: Self-hosted on DigitalOcean Singapore, full control for PH BIR compliance

### 2. Cost Predictability
**SaaS Risk**: Per-user SaaS fees ($10-20/user/month) = $3.6K-$7.2K/year for 30 users  
**Odoo CE Advantage**: AGPL license = $0 software cost, predictable infrastructure costs

### 3. Single System of Record
**SaaS Risk**: Two sources of truth, sync complexity, data divergence, conflict resolution  
**Odoo CE Advantage**: Single source of truth, no sync complexity, no data conflicts

### 4. Integration Complexity Avoidance
**SaaS Risk**: Unreliable webhooks, API rate limits, polling overhead, two-way sync nightmares  
**Odoo CE Advantage**: No integration needed, native Odoo workflows and automation

### 5. Long-Term Control & Flexibility
**SaaS Risk**: Vendor lock-in, feature deprecation, pricing changes, no exit strategy  
**Odoo CE Advantage**: Open-source, community-driven, full control, no vendor dependency

---

## Consequences

### Positive

1. **Full Control**: Complete ownership of data, features, and roadmap
2. **Cost Efficiency**: Predictable infrastructure costs vs per-user SaaS fees
3. **Compliance**: Self-hosted deployment ensures PH BIR data residency requirements
4. **Workflow Automation**: Native Odoo + n8n integration for advanced automation
5. **Customization**: Unlimited customization without SaaS API limitations
6. **Single Source of Truth**: No sync complexity or data divergence issues

### Negative

1. **Development Effort**: Must build parity modules vs "buy" SaaS integrations
2. **Feature Gap Risk**: May not match 100% of SaaS features initially
3. **Maintenance Burden**: Ongoing module maintenance and OCA upgrades required
4. **UI/UX Expectations**: Users familiar with SaaS UX may require adjustment period

### Mitigation Strategies

1. **Phased Rollout**: Start with minimal viable parity (MVP), iterate based on user feedback
2. **OCA Module Reuse**: Leverage existing OCA modules where possible (document_page, knowledge, project, hr_expense)
3. **Visual Parity Testing**: SSIM thresholds (≥0.97 mobile, ≥0.98 desktop) ensure UI quality
4. **User Training**: 3-day workshop on Odoo workflows and parity module usage
5. **Progressive Enhancement**: Continuous improvement based on real user workflows

---

## Implementation Strategy

### Module Architecture

**Layering Rule**: Odoo CE → OCA gap-fill → IPAI custom (minimal overrides, inherit/extend only)

**Standard Profile** (minimal production set):
- 14 OCA repositories
- 5 IPAI modules (workspace_core, ppm, advisor, workbooks, connectors)

**Parity Profile** (enterprise feature set):
- 32 OCA repositories
- All 27 IPAI modules (backward compatibility for existing deployments)

### Build Profiles

```bash
# Standard Profile (minimal production)
docker build --build-arg PROFILE=standard -t odoo-ce:prod .

# Parity Profile (enterprise features)
docker build --build-arg PROFILE=parity -t odoo-ce:enterprise-parity .
```

### Configuration Pattern

**Secrets** (env vars only, NEVER in ir.config_parameter):
```python
# In module code (models/*.py)
import os
supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
n8n_secret = os.getenv('N8N_WEBHOOK_SECRET')
```

**Non-Secrets** (ir.config_parameter or module settings):
```python
# URLs, toggles, feature flags
supabase_url = self.env['ir.config_parameter'].sudo().get_param('ipai.supabase.url')
enable_expense_parity = self.env['ir.config_parameter'].sudo().get_param('ipai.expense.enabled', default='true')
```

---

## Alternatives Considered

### Alternative 1: Integrate with SaaS Tools via Connectors
**Rejected Reason**: Data sovereignty risk, sync complexity, vendor lock-in, cost unpredictability

### Alternative 2: Hybrid Approach (Some SaaS, Some Native)
**Rejected Reason**: Introduces "two sources of truth" problem, increases architectural complexity

### Alternative 3: Enterprise Odoo (Proprietary Modules)
**Rejected Reason**: Per-user licensing cost (~$30/user/month), vendor dependency, limited customization

---

## Related Decisions

- **ADR-0002**: Unified Dockerfile with Build Profiles (standard/parity)
- **Constitution**: IPAI Control Center non-negotiables (idempotent migrations, CI green gates, operational-first)
- **PRD**: Product Requirements Document for parity modules
- **Plan**: Delivery plan and milestones for phased rollout

---

## References

- [Constitution — IPAI Control Center](../../spec/ipai-control-center/constitution.md)
- [Odoo CE Knowledge Management Strategy](../../apps/ipai-control-center-docs/pages/strategy/notion-vs-odoo.mdx)
- [OCA Knowledge Modules](https://github.com/OCA/knowledge)
- [OCA Project Modules](https://github.com/OCA/project)

---

## Acceptance Criteria

Before considering this ADR "implemented":

1. ✅ All Notion/Concur/Cheqroom/SAP SRM integration scaffolds removed from codebase
2. ✅ IPAI stack environment variables added to docker-compose.prod.yml
3. ✅ Parity modules (`ipai_expense`, `ipai_assets`, `ipai_ppm`, `ipai_srm`) scaffolded as native Odoo apps
4. ✅ Configuration pattern implemented (secrets via os.getenv(), non-secrets via ir.config_parameter)
5. ✅ Documentation updated to reflect "parity modules" terminology (not "integrations")
6. ✅ CI/CD pipeline validates module installation and visual parity (SSIM thresholds)

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-01-20 | Initial ADR created | Jake Tolentino |
| 2025-01-20 | Clarified "parity modules" vs "integrations" terminology | Jake Tolentino |

---

**Next Steps**:
1. Create ADR-0002 (Unified Dockerfile with Build Profiles)
2. Scaffold parity module skeletons (`ipai_expense`, `ipai_assets`, `ipai_ppm`, `ipai_srm`)
3. Update tech stack documentation to reflect IPAI stack integration
4. Create Docker architecture documentation with build profiles

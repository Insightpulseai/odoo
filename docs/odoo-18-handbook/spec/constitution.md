# Constitution – InsightPulseAI Odoo 18 CE/OCA Implementation Handbook

**Product:** Documentation product for Odoo 18 CE/OCA implementation
**Organization:** TBWA/InsightPulseAI
**Version:** 1.0.0
**Last Updated:** 2025-12-07

---

## 1. Purpose

This handbook serves as the **single source of truth** for implementing and operating Odoo 18 Community Edition with OCA modules in the InsightPulseAI stack. It provides:

- Configuration guides for every functional area
- Data mapping between Odoo and Supabase
- Automation blueprints for n8n workflows
- AI agent integration patterns
- Go-live and UAT checklists

---

## 2. Constraints

### 2.1 CE + OCA Only

- **No Enterprise modules**: Never document or suggest Enterprise, IAP, or SaaS features
- **OCA-first**: Always prefer OCA modules over custom development
- **Smart Delta**: Follow the `CE_CONFIG → OCA → GAP_DELTA → GAP_NEW_MODULE` decision tree

### 2.2 Supabase as Analytical Store

- **Odoo is operational**: Transactions, workflows, masters live in Odoo PostgreSQL
- **Supabase is analytical**: All reporting, AI, and external integrations use Supabase
- **Medallion architecture**: Bronze → Silver → Gold → Platinum data layers
- **RLS-enforced**: All Supabase tables use `tenant_id` for multi-tenancy

### 2.3 n8n as Workflow Engine

- **Event-driven**: Odoo events trigger n8n workflows
- **Approval workflows**: All multi-step approvals route through n8n + Mattermost
- **No Enterprise Approvals**: Never use Odoo Enterprise Approvals app

### 2.4 DigitalOcean Infrastructure

- **Droplets or DOKS**: All deployment on DigitalOcean
- **Docker-first**: All services containerized
- **Nginx reverse proxy**: SSL termination via Let's Encrypt

### 2.5 AI Integration Standards

- **Claude/OpenAI**: Primary AI providers
- **MCP servers**: Tool access for agents
- **RAG over docs**: Handbook is RAG-indexed for agent access
- **pgvector**: Embeddings stored in Supabase

---

## 3. Success Criteria

Every major business process must have:

| Deliverable | Description |
|-------------|-------------|
| **Odoo Config Guide** | Step-by-step setup instructions for CE/OCA |
| **Data Mapping** | Odoo model → Supabase schema mapping |
| **Automation Blueprint** | n8n workflow definitions |
| **UAT Checklist** | Acceptance test scenarios |
| **AI Integration** | Agent capabilities and prompts (if applicable) |

### 3.1 Documentation Quality Gates

- [ ] No Enterprise/IAP features documented without "Delta" notes
- [ ] All Supabase schema references verified against actual tables
- [ ] n8n workflow names match actual workflow IDs
- [ ] Code examples tested on Odoo 18 CE
- [ ] RAG metadata tags applied to all pages

### 3.2 Coverage Targets

| Domain | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| Finance | 100% | - | - |
| PPM | 80% | 100% | - |
| HR | 60% | 100% | - |
| Retail | 70% | 90% | 100% |
| Equipment | 50% | 100% | - |
| Sales/CRM | 30% | 70% | 100% |

---

## 4. Non-Goals

This handbook does **NOT**:

- Replace official Odoo documentation (links provided where applicable)
- Cover Enterprise, SaaS, or Odoo.sh features
- Document features not in the InsightPulseAI stack
- Provide end-user training (separate training materials exist)

---

## 5. Governance

### 5.1 Ownership

| Role | Responsibility |
|------|----------------|
| **Documentation Lead** | Overall handbook quality and completeness |
| **Domain SMEs** | Finance, PPM, HR, Retail content accuracy |
| **Platform Team** | Supabase, n8n, AI integration accuracy |
| **DevOps** | Deployment and infrastructure sections |

### 5.2 Change Process

1. Changes via Pull Request to `docs/odoo-18-handbook/`
2. Review by domain SME + Documentation Lead
3. CI validation of RAG metadata
4. Merge to main triggers handbook rebuild

### 5.3 Version Control

- Handbook versions match major Odoo releases (18.x)
- Breaking changes require major version bump
- Monthly review cycle for updates

---

## 6. Canonical References

| Reference | Location |
|-----------|----------|
| Odoo 18 CE/OCA Mapping | `docs/ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md` |
| Project Constitution | `constitution.md` |
| Technical Architecture | `docs/architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md` |
| Enterprise Feature Gap | `docs/ENTERPRISE_FEATURE_GAP.yaml` |

---

**This constitution governs all documentation in the InsightPulseAI Odoo 18 CE/OCA Implementation Handbook.**

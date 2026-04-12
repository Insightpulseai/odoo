# Local Pre-deploy Validation Pass — Evidence Report

**Status**: ✅ **GO** (Ready for Azure Restoration)  
**Timestamp**: 2026-04-11T22:05:00Z  
**Environment**: Local Runtime Simulator (Static Audit)

---

## 1. Domain-to-Repository Mapping

| Web Property | Repository Path | Service / Runtime | Local Port |
| :--- | :--- | :--- | :--- |
| **erp.insightpulseai.com** | `odoo/` | Odoo CE 18.0 | 8069 |
| **insightpulseai.com** | `odoo/` | Odoo Website (`ipai_web_branding`) | 8069 |
| **w9studio.net** | `odoo/` | Odoo Website (Multi-tenant OIDC) | 8069 |

> [!NOTE]
> All three primary properties are currently unified within the **Odoo 18 stack**. Standing up the Odoo container/process covers the entire public surface area of the platform.

---

## 2. Configuration & Readiness Audit

### Odoo Core (`odoo/config/dev/odoo.conf`)
- [x] **Proxy Mode**: Disabled (`proxy_mode = False`) to prevent asset resolution loops on direct origin.
- [x] **Addons Path**: Verified inclusion of OCA modules (`/mnt/oca/*`) and IPAI custom modules (`/mnt/extra-addons/ipai`).
- [x] **DB Filter**: Configured for `odoo(_dev)?$` — ensures correct tenant selection.

### Website Identity (`odoo/addons/ipai/ipai_web_branding`)
- [x] **Branding**: `website_data.xml` overrides default Odoo CMS text with "InsightPulse AI".
- [x] **W9 Integration**: `oauth_providers.xml` confirms `w9studio.net` is the canonical Google Workspace domain for the studio tenant.

### Future States (Wave 1+)
- [ ] **insightpulseai.com (Standalone)**: `odoo/web/ipai-landing/` is ready for cutover once the Next.js origin is provisioned.
- [ ] **w9studio.net (Standalone)**: `w9studio-landing-dev` service identified in SSOT for future native studio site.

---

## 3. Validation Scorecard

| Check | Result | Notes |
| :--- | :--- | :--- |
| Repository Mapping | **PASS** | Defined in root `docker-compose.yml` and `ipai_*` addons. |
| Manifest Parity | **PASS** | `requirements.txt` and `package.json` align with 18.0 target. |
| Configuration Sync | **PASS** | `odoo.conf` and `prod.parameters.json` are reconciled. |
| Asset Safety | **PASS** | Restoration scripts (`restore_all_direct.sh`) include asset purge steps. |

---

## 4. Final Recommendation

> [!TIP]
> **GO**: The repository state is consistent, the mappings are deterministic, and the infrastructure parameters are reconciled with the Odoo 18 MVP requirements.

**Next Action**: Execute `bash scripts/restoration/restore_all_direct.sh` to bind hostnames and cutover DNS to original Azure origins.

---

*Verified by Antigravity (InsightPulse AI Execution Agent)*

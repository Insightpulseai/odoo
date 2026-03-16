# PRD — Odoo 19 EE Surface Catalog & Goal-Based Parity

## 1) Background

Odoo Enterprise includes platform/service capabilities that are not simply “addons”, notably:

- **Odoo.sh hosting & lifecycle management**
- **Upgrades service**
- **Standard/Extended Support**
  Additionally, Odoo 19 introduces/expands AI-related features (e.g., AI Agents) that depend on external AI providers and configuration, and Odoo’s **In-App Purchase (IAP)** credit system.

We will implement parity as **goal-based outcomes**, using a catalog-driven approach.

## 2) Problem Statement

Current parity checks often:

- Misclassify implemented functionality as “missing” due to folder/module detection logic.
- Over-focus on modules and ignore the EE surfaces that matter operationally (hosting, upgrades, support).

## 3) Goals (What we care about)

### Tier-0 (Non-negotiable)

1. **Hosting/Lifecycle parity for Odoo.sh**
   - CI builds, environment separation, deploy pipelines, SSH/shell access, dependency handling.
2. **Upgrade safety**
   - Repeatable upgrade pipelines, test upgrades, neutralization + staging rehearsal.
3. **Support workflow**
   - Ticketing, SLAs, incident response, reproducible diagnostics, escalation paths.

### Tier-1 (Important, adjacent EE surfaces)

4. **AI Agents enablement**
   - Ability to run Odoo 19 AI Agents by configuring AI provider keys and enforcing policy guardrails.
5. **IAP operationalization**
   - Manage IAP credit usage/monitoring and ensure dependent features have a stable procurement and audit workflow.

## 4) Non-Goals (Explicitly not required for threshold)

- Perfect replication of Odoo Online constraints and hosting internals.
- Recreating proprietary vendor support internals; we only need a functional support process.
- Matching proprietary UI affordances where workflows suffice.

## 5) EE Surface Catalog (Source of Truth)

All EE surfaces are declared in:

- `docs/parity/EE_SURFACE_CATALOG.yaml`

This includes for each surface:

- Scope tier (Tier-0/Tier-1/Tier-2)
- Acceptance tests (machine-testable where possible)
- Implementation strategy (OCA modules, external services, glue scripts)
- Evidence artifacts required (logs, reports, runbooks)

## 6) Key Source Facts (Odoo 19)

- Odoo Enterprise positioning includes hosting, upgrades, and functional support as part of “all-in-one” enterprise package. :contentReference[oaicite:0]{index=0}
- Odoo.sh is documented as the official cloud platform for hosting/managing Odoo with features including web shell, module dependencies, CI, and SSH access. :contentReference[oaicite:1]{index=1}
- Odoo’s upgrade process includes an upgrade platform integrated with Odoo.sh, providing upgrade modes and database upgrade workflows. :contentReference[oaicite:2]{index=2}
- Odoo documents Standard vs Extended support as separate support levels and describes what each includes. :contentReference[oaicite:3]{index=3}
- Odoo 19 AI Agents require the AI application and configuration of external AI API keys (e.g., OpenAI / Gemini). :contentReference[oaicite:4]{index=4}
- IAP credits are used for certain services; credits can be purchased and are tied to a database. :contentReference[oaicite:5]{index=5}

## 7) Success Metrics

- Tier-0 goals: 100% pass rate (hard gate)
- Overall score threshold (configurable): default >= 0.80
- Zero false negatives due to folder/module detection
- CI produces machine-readable report + human summary

## 8) Stakeholders / Users

- DevOps: deploy, upgrades, backups, observability
- Finance/Ops: IAP procurement and audit
- Admin/IT: support workflows, runbooks
- Engineering: deterministic parity checks and evidence capture

## 9) Risks

- “Exact EE-only list” is not published as a single authoritative table by Odoo; we will treat the catalog as a living SSOT maintained via periodic review of Odoo docs & edition claims. :contentReference[oaicite:6]{index=6}

# Doctrine Precedence — Marketing Site Assistant

> Canonical conflict-resolution order for the 20 governance files governing the landing site and Ask Pulser.
> When two files conflict, the higher-precedence file wins for its concern area.
> Updated: 2026-03-25

---

## Precedence by Concern

| # | Concern | Winner | Scope |
|---|---------|--------|-------|
| 1 | Brand and public naming | `docs/brand/PULSER_NAMING_DOCTRINE.md` | Canonical names, deprecated names, brand rules. If a page, CTA, route label, or widget string conflicts, this wins. |
| 2 | Public assistant behavior | `docs/architecture/MARKETING_ASSISTANT_DOCTRINE.md` | Ask Pulser disclosure, source policy, CTA behavior. If UI copy or response behavior conflicts with implementation convenience, this wins. |
| 3 | Route and CTA execution | `platform/ssot/routes.yaml` | Executable route/CTA registry. The site implements what this file says, not whatever is hardcoded in a component. |
| 4 | Tool exposure (Pulser→Odoo) | `platform/ssot/tool_contracts.yaml` | Curated tools only. If the assistant can do it in UI but it is not allowed here, it must not ship. |
| 5 | Public vs authenticated boundaries | `docs/architecture/agents/ASSISTANT_SURFACES.md` + `ssot/agents/assistant_surfaces.yaml` + `ssot/architecture/tenancy_model.yaml` | Decides whether something belongs on public landing, authenticated surface, or different shell. |
| 6 | Runtime and infra constraints | `docs/architecture/PULSER_MINIMAL_RUNTIME.md` | Infrastructure, identity, runtime routing. If a surface idea violates runtime doctrine, runtime wins. |
| 7 | Ship/no-ship gate | `docs/audits/WEBSITE_BRANDING_ROUTE_AUDIT.md` | Publishability gate for route inventory, CTA audit, branding compliance. Last gate before deploy. |
| 8 | Cross-cutting contracts | `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` + `.claude/rules/ssot-platform.md` | Boundary, secret, DNS, or platform-rule conflicts not fully resolved by marketing docs. |
| 9 | Landing build/deploy | `web/ipai-landing/README.md` | Deployment/build authority for the landing surface itself. |

---

## 3 Mandatory Docs for Any Ask Pulser Change

Before shipping any landing-assistant change, these three must be green:

1. `docs/architecture/MARKETING_ASSISTANT_DOCTRINE.md`
2. `docs/brand/PULSER_NAMING_DOCTRINE.md`
3. `docs/audits/WEBSITE_BRANDING_ROUTE_AUDIT.md`

---

## Deploy Order

### Phase 1 — Doctrine and SSOT

Update in this order:

1. `PULSER_NAMING_DOCTRINE.md`
2. `MARKETING_ASSISTANT_DOCTRINE.md`
3. `platform/ssot/routes.yaml`
4. `platform/ssot/tool_contracts.yaml`
5. Surface/boundary docs:
   - `agents/ASSISTANT_SURFACES.md`
   - `assistant_surfaces.yaml`
   - `tenancy_model.yaml`
6. `WEBSITE_BRANDING_ROUTE_AUDIT.md`

Naming and behavior must be settled before route and tool execution are changed. The audit comes after implementation decisions, not before.

### Phase 2 — Landing Implementation

Update actual landing code and widget implementation under `web/ipai-landing/`.

### Phase 3 — Build and Publish

1. Build passes
2. Deploy succeeds
3. CDN purge completes
4. Route/CTA audit passes
5. Branding audit passes
6. Live smoke test passes

---

## Deploy Verification Checklist

After deploy, all must be true:

- [ ] Title: `InsightPulseAI — AI-native operations for marketing, media, retail, and financial services`
- [ ] Pulser API returns structured `ctas[]` per topic
- [ ] CSS served with correct MIME type (`text/css`)
- [ ] No `Get Started` (unless self-serve flow exists)
- [ ] No `Request a Demo` (canonical: `Book Demo`)
- [ ] No `Trust & Readiness` (canonical: `Trust Center`)
- [ ] No `Analytics` alone (canonical: `Analytics & Dashboards`)
- [ ] No `Odoo Copilot` remaining
- [ ] Marquee rail animates continuously
- [ ] All CTAs resolve to working destinations

---

## Repo-First Deployment Rule

Deploy only after these two truths match:

- **Doctrine truth** in docs/SSOT
- **Runtime truth** in landing implementation

If they diverge, do not ship. The audit doc and route/tool registries exist as separate authority surfaces specifically to catch this.

---

## Deploy Commands

```bash
# Build
cd web/ipai-landing && npm install && npx vite build

# Push to ACR (cloud build)
az acr build --registry acripaiodoo \
  --image ipai-website:latest \
  --image ipai-website:$(date +%Y%m%d-%H%M) \
  --file Dockerfile . --platform linux/amd64

# Deploy to ACA
az containerapp update \
  --name ipai-website-dev \
  --resource-group rg-ipai-dev-odoo-runtime \
  --image acripaiodoo.azurecr.io/ipai-website:latest

# Purge CDN
az afd endpoint purge \
  --resource-group rg-ipai-dev-platform \
  --profile-name ipai-fd-dev \
  --endpoint-name ipai-fd-dev-ep \
  --content-paths '/*' \
  --domains www.insightpulseai.com insightpulseai.com

# Verify
curl -s https://ipai-website-dev.salmontree-b7d27e19.southeastasia.azurecontainerapps.io/ \
  | grep -o '<title>[^<]*</title>'
```

---

*This document resolves conflicts between the 20 governance files. It does not replace them — each file remains the authority for its concern area.*

# Naming Policy — Pulser / Copilot / Odoo

> Prevent trademark leakage and naming drift across public UX, docs, APIs, and internal code.
> Updated: 2026-03-25

---

## Canonical Rules

### Public-facing surfaces

**Allowed:**
- Pulser
- AI assistant
- AI workspace
- agent
- assistant
- Microsoft Copilot integration
- Security Copilot integration
- Odoo integration
- built on Odoo
- Odoo on Cloud
- Pulser for Odoo

**Disallowed as first-party product naming:**
- Copilot
- Odoo Copilot
- InsightPulse Copilot
- IPAI Copilot
- Odoo AI

**Notes:**
- "Copilot" may only appear referentially for Microsoft-owned products or integrations.
- "Odoo" may only appear referentially for platform/runtime/integration context, not as a first-party branded product name.

### Internal code

**Allowed:**
- `copilot_*`
- `*_copilot`
- `agent_*`
- `assistant_*`

**Constraint:**
Internal `copilot` naming must not leak into:
- UI strings
- API names
- route names
- docs intended for external/public readers
- marketing/site copy
- OG metadata
- SEO metadata

### Boundary translation

| Internal | External |
|----------|----------|
| `copilot` | `pulser` |
| `assistant engine` | `Pulser` |
| `copilot panel` | `Pulser panel` |
| `copilot chat` | `Pulser chat` |
| `copilot workspace` | `Pulser workspace` |
| `/api/copilot/*` | `/api/pulser/*` |

---

## CI Enforcement

`scripts/ci/check_branding_policy.py` scans public-facing files and fails on forbidden first-party branding strings. See `.github/workflows/branding-policy-check.yml`.

---

## Migration Stages

### Stage 1 — Boundary containment (done)
- Preserve internal `copilot_*` symbols
- Rename public UI strings to Pulser
- Rename route labels / metadata / SEO / OG strings
- Add CI branding gate

### Stage 2 — External contract cleanup (future)
- Rename API operation names and exported SDK/public interfaces from `copilot` to `pulser`
- Keep compatibility aliases only where required

### Stage 3 — Internal convergence (future)
- Gradually rename internal modules/services from `copilot_*` to `pulser_*`
- Remove compatibility aliases after migration window

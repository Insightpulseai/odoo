# Web Presence & CMS Strategy
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Current State (as of 2026-02-07)

### Architecture

```
Customer-Facing (Vercel)           Admin (Self-Hosted)
+----------------------------+     +---------------------------+
| apps/web (Next.js 14)     |     | Odoo CE 19 backend        |
|  - Marketing / solutions   |     |  - ERP operations          |
|  - insightpulseai.com      |     |  - erp.insightpulseai.com  |
+----------------------------+     +---------------------------+
| apps/billing-site (Next.js)|     | Odoo website module        |
|  - Paddle billing          |     |  - Coming soon page only   |
|  - SaaS onboarding         |     |  - ipai_website_coming_soon|
+----------------------------+     +---------------------------+
| apps/odoo-frontend-shell   |
|  - Odoo UI extension       |
|  - sin1 region             |
+----------------------------+
```

### What Exists Today

| Layer | Technology | Status |
|-------|-----------|--------|
| Marketing site | Next.js + Vercel (`apps/web/`) | Active |
| Billing portal | Next.js + Paddle + Supabase Auth (`apps/billing-site/`) | Active |
| Odoo frontend shell | Next.js + Odoo XML-RPC (`apps/odoo-frontend-shell/`) | Active |
| Odoo CMS (website module) | `ipai_website_coming_soon` | Minimal — coming soon page only |
| Blog | None | Not implemented |
| E-commerce / Shop | None | Not planned |
| Knowledge base | None | Planned (spec: `insightpulse-docs-ai`) |
| Vendor portal | None | Planned (spec: `enterprise-parity`) |

### Active Odoo Website/Theme Modules

| Module | Purpose |
|--------|---------|
| `ipai_website_coming_soon` | Branded landing page with Pulser animation |
| `ipai_web_fluent2` | Frontend UI theme |
| `ipai_web_theme_tbwa` | TBWA branding theme |
| `ipai_web_icons_fluent` | Fluent icon set |
| `ipai_platform_theme` | Backend platform theme |
| `ipai_theme_copilot` | Backend theme variant |
| `ipai_theme_fluent2` | Backend theme variant |
| `ipai_theme_tbwa` | Backend theme variant |

### Not Yet Active

| Module | Location | Status |
|--------|----------|--------|
| `ipai_website_shell` | `sandbox/dev/addons/ipai/` | Sandbox — not promoted to production |
| `ipai_portal_fix` | Archived | Deprecated |

---

## CMS Adoption Strategy

### Decision: Hybrid (Odoo CMS for internal, Next.js for external)

```
+---------------------------------------------------------------+
|                    CMS Decision Matrix                         |
+---------------------------------------------------------------+
| Use Case              | Technology          | Why              |
|-----------------------|---------------------|------------------|
| Marketing site        | Next.js + Vercel    | SEO, speed, CDN  |
| Billing / SaaS portal| Next.js + Paddle    | Payment UX       |
| Internal knowledge    | Odoo website module | Integrated w/ ERP|
| Coming soon / landing | Odoo website module | Quick deploy     |
| Blog                  | TBD                 | Evaluate later   |
| E-commerce            | Not planned         | Not our business |
| Vendor self-service   | Next.js + Supabase  | Auth + API layer |
+---------------------------------------------------------------+
```

### Why NOT Full Odoo CMS?

1. **Performance**: Next.js on Vercel CDN (global edge) beats self-hosted Odoo for public pages
2. **SEO**: Next.js SSR/SSG gives better lighthouse scores than Odoo's QWeb rendering
3. **Cost**: Vercel free tier + Hobby plan ($0–20/mo) vs. scaling the DO droplet for public traffic
4. **Separation of concerns**: Customer-facing pages should not share compute with ERP operations
5. **Developer experience**: React/Next.js ecosystem has richer component libraries

### When TO Use Odoo CMS

1. **Internal-facing pages** that need ERP data (employee portal, internal wiki)
2. **Authenticated pages** where users are already logged into Odoo
3. **Quick landing pages** that don't need CDN distribution
4. **Forms** that write directly to Odoo models (contact us, support tickets)

---

## Recommended Adoption Path

### Phase 1: Current (Done)
- Marketing site on Vercel (`apps/web/`)
- Coming soon page via `ipai_website_coming_soon`
- Backend themes deployed

### Phase 2: Near-term
- Activate `ipai_website_shell` from sandbox → production addons
- Implement internal knowledge base using Odoo `website` + custom QWeb pages
- Connect vendor portal spec (Next.js + Supabase Auth + Odoo XML-RPC)

### Phase 3: Future
- Evaluate Odoo `website_blog` for internal-facing blog (company news, updates)
- Consider `website_helpdesk` integration with `ipai_helpdesk`
- Documentation portal (spec: `insightpulse-docs-ai`) — likely Next.js + MDX

---

## Deployment

### Next.js Apps (Vercel)

```
vercel.json (root):
  ipai-web              → apps/web
  ipai-control-center   → apps/ipai-control-center-docs
  ipai-control-room     → apps/control-room
```

### Odoo Website Module

```bash
# Install/update website module
docker compose exec -T web odoo -d odoo -i website --stop-after-init

# Install coming soon page
docker compose exec -T web odoo -d odoo -i ipai_website_coming_soon --stop-after-init

# Verify
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
```

### Scripts

```bash
scripts/odoo_coming_soon_install.sh    # Install coming soon page
scripts/odoo_coming_soon_rollback.sh   # Rollback coming soon page
scripts/odoo_coming_soon_verify.sh     # Verify deployment
```

---

## OCA Website Modules (Not Yet Adopted)

No OCA website modules are currently in use. Candidates for future evaluation:

| OCA Module | Purpose | Priority |
|------------|---------|----------|
| `website_blog_excerpt` | Blog excerpt management | P3 |
| `website_seo_redirection` | SEO redirect management | P2 |
| `website_cookie_notice` | GDPR cookie consent | P2 |
| `website_legal_page` | Legal/privacy pages | P2 |

Following the module philosophy: `Config → OCA → Delta (ipai_*)` — evaluate OCA options before building custom.

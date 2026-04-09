# Implementation Plan: W9 Studio Website

## Architecture Decision

**Native Odoo first.** Use built-in Odoo apps for the entire website surface:

| App | Purpose |
|-----|---------|
| `website` | CMS shell, page builder, menus, SEO, CDN, analytics |
| `website_blog` | Content publishing, SEO growth |
| `appointment` | Studio booking with calendar integration |
| `crm` | Inquiry and booking follow-up |
| `google_calendar` | Calendar sync to Google Calendar |
| `website_sale` | (Phase 2, optional) Online checkout for packages |
| `sale_subscription` | (Phase 2, optional) Recurring memberships |

## Repo Boundary

### Phase 1: No custom addon

Use native Odoo Website pages, templates, snippets, and apps. Content managed in Odoo UI. No files in `addons/`.

### Phase 2 (optional): Thin custom addon

Only if native pages/templates prove insufficient for the W9 Studio brand structure.

**Path:** `addons/local/w9_studio_website/` (NOT `addons/ipai/` — this is site-specific presentation, not a reusable bridge)

**Would contain:**
- Branded reusable snippets (hero, storyboard grid, gallery strip, testimonials)
- Deterministic homepage template (QWeb/XML)
- SCSS asset bundle (`$o-w9-gold`, `$o-w9-cyan`, `$o-w9-pink`, `$o-w9-dark`)
- Content seed fixtures (appointment types, demo pages)

## Content Authority

### Odoo runtime records (content authority)
- Website pages (composition, copy, images)
- Blog posts
- Appointment types and scheduling
- CRM leads/opportunities
- Optional eCommerce/subscription products

### Git (engineering authority)
- Template overrides (QWeb/XML)
- Snippet definitions (XML)
- Theme assets (SCSS/JS)
- Content seed fixtures (data XML)
- Migration hooks
- Specs, docs, architecture notes

## Security / Anti-Spam

- All public website forms must use **Cloudflare Turnstile** (Odoo recommends Turnstile over reCAPTCHA v3)
- Turnstile site key configured in Website Settings → Forms
- No unprotected public forms

## Template Strategy

Prefer native page templates first:
1. **Landing Pages** — homepage
2. **Gallery** — studio/work showcase
3. **Services** — service overview
4. **Pricing Plans** — rates/packages

Custom QWeb/XML templates only when native templates/snippets cannot achieve required structure.

## Wix-to-Odoo Section Mapping

| Wix Section | Odoo Target | Method |
|---|---|---|
| Hero / landing | `/` homepage | Website page + snippets |
| Services | `/services` | Website page (Services template) |
| Gallery | `/gallery` | Website page (Gallery template) |
| Rates / pricing | `/rates` | Website page (Pricing Plans template) |
| Contact / inquiry | `/contact` | Website form → `crm.lead` |
| Booking | `/book` | Appointments |
| Blog / updates | `/blog` | Blog app |
| Testimonials | Homepage section | Static snippet (no custom model) |
| Location / map | Homepage section or `/contact` | Google Maps embed snippet |

## Implementation Phases

### Phase 1 — Native Website Cutover

1. Install `website`, `website_blog`, `appointment`, `crm`, `google_calendar` on `odoo_dev`
2. Configure multi-website if needed (W9 Studio as separate website from InsightPulseAI)
3. Create 7 pages: `/`, `/services`, `/gallery`, `/rates`, `/contact`, `/book`, `/blog`
4. Build homepage using native Landing Page template + building blocks
5. Create appointment types: Studio Session, Discovery Call, Site Visit
6. Configure `/contact` form → `crm.lead` action
7. Enable Turnstile on all forms
8. Configure `google_calendar` with existing W9 Studio OAuth client
9. Migrate copy/assets from current React SPA into Odoo pages
10. Test full flow: visit → form → CRM lead, visit → book → appointment → CRM opportunity
11. Point `w9studio.net` DNS to Odoo instance
12. Decommission `w9studio-landing-dev` ACA container

### Phase 2 — Commercial Flows (if needed)

1. Install `website_sale` for one-time package purchase
2. Create service products with pricing tiers
3. Install `sale_subscription` for recurring memberships (if needed)
4. Decide: `/rates` stays informational or becomes transactional

### Phase 3 — Thin Custom Addon (if justified)

1. Create `addons/local/w9_studio_website/`
2. Add branded reusable snippets (hero, storyboard grid, gallery strip)
3. Add homepage template XML/QWeb
4. Add SCSS asset bundle
5. Add deterministic content fixtures

## Dependencies

- Odoo 18 CE running with Website module
- Google OAuth client for W9 Studio (`916601142061-f7j0...`, secret in Azure Key Vault `kv-ipai-dev`)
- Cloudflare Turnstile site key
- W9 Studio domain DNS control

## What Gets Retired

| Current | Action |
|---|---|
| `jgtolentino/studio-landing` GitHub repo | Archive after cutover |
| `w9studio-landing-dev` ACA container | Delete after DNS cutover |
| `acripaiodoo.azurecr.io/w9studio-landing:v3` | Delete from ACR |
| Express `/api/book` endpoint | Eliminated — native forms |
| Google Calendar API glue code in `server/index.ts` | Replaced by `google_calendar` module |

---

*Last updated: 2026-03-27*

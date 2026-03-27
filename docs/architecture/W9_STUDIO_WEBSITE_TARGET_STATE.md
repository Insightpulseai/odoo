# W9 Studio Website — Target State Architecture

## Target App Stack

| Odoo App | Purpose | Phase |
|----------|---------|-------|
| `website` | CMS shell, page builder, menus, SEO, CDN, analytics | 1 |
| `website_blog` | Content publishing, SEO growth | 1 |
| `appointment` | Studio booking with calendar integration | 1 |
| `crm` | Inquiry and booking follow-up | 1 |
| `google_calendar` | Calendar sync to Google Calendar | 1 |
| `website_sale` | Online checkout for packages | 2 (optional) |
| `sale_subscription` | Recurring memberships | 2 (optional) |

## Route Map

| Route | Type | Odoo Surface | Content Authority |
|-------|------|-------------|-------------------|
| `/` | Static page | Website (Landing Page template) | Odoo UI |
| `/services` | Static page | Website (Services template) | Odoo UI |
| `/gallery` | Static page | Website (Gallery template) | Odoo UI |
| `/rates` | Static page | Website (Pricing Plans template) | Odoo UI |
| `/book` | Dynamic | Appointments | Odoo UI + appointment.type records |
| `/contact` | Static page | Website form → `crm.lead` | Odoo UI |
| `/blog` | Dynamic | Blog app | Odoo UI + blog.post records |

## Wix-to-Odoo Section Mapping

| Current (Wix / React SPA) | Odoo Target |
|---|---|
| Hero / landing page | `/` — Website page + snippets/building blocks |
| Services grid (9 storyboard cards) | `/services` — Services template or custom snippet |
| Gallery / portfolio | `/gallery` — Gallery template |
| Rates / pricing | `/rates` — Pricing Plans template |
| Contact / inquiry form | `/contact` — Website form → CRM lead |
| Booking form | `/book` — Appointments (creates CRM opportunities) |
| Blog / updates | `/blog` — Blog app |
| Testimonials | Homepage section — static snippet |
| Location / map | Homepage or `/contact` — Google Maps embed |
| Footer | Website footer — standard building block |

## Native vs Custom Boundary

### Phase 1: Native Only (no custom addon)

All website content uses Odoo's built-in page builder, templates, and apps. No files in `addons/`.

**Native templates used:**
- Landing Pages (homepage)
- Gallery (showcase)
- Services (overview)
- Pricing Plans (rates)

### Phase 2 Optional: Thin Custom Addon

**Trigger:** Native templates/snippets demonstrably insufficient for W9 brand requirements.

**Path:** `addons/local/w9_studio_website/` (site-specific presentation, NOT `addons/ipai/`)

**Would contain:**
- Branded snippets (`s_w9_hero`, `s_w9_storyboard_grid`, `s_w9_gallery_strip`)
- Homepage template (QWeb/XML)
- SCSS tokens (`$o-w9-gold: #FFD700`, `$o-w9-cyan: #00FFFF`, `$o-w9-pink: #FF2E63`, `$o-w9-dark: #0F0F0F`)
- Content seed fixtures

## Runtime Authority Model

| Artifact | Authority | Location |
|----------|-----------|----------|
| Page content (copy, images, layout) | Odoo runtime | `website.page` records |
| Blog posts | Odoo runtime | `blog.post` records |
| Appointment types | Odoo runtime | `appointment.type` records |
| CRM leads/opportunities | Odoo runtime | `crm.lead` records |
| Products/subscriptions (if phase 2) | Odoo runtime | `product.template` records |
| Theme overrides (QWeb/XML) | Git | `addons/local/w9_studio_website/views/` |
| SCSS/JS assets | Git | `addons/local/w9_studio_website/static/` |
| Snippet definitions | Git | `addons/local/w9_studio_website/views/snippets/` |
| Content seed fixtures | Git | `addons/local/w9_studio_website/data/` |
| Specs and architecture docs | Git | `spec/w9-studio-website/`, `docs/architecture/` |

## Phase Gates

| Phase | Gate | Proceed When |
|-------|------|-------------|
| 1 → 2 | Commerce need | W9 Studio confirms online checkout is required |
| 1 → 3 | Template gap | Documented evidence that native templates cannot achieve required brand structure |

## Google Calendar Integration

- **Module:** `google_calendar` (Odoo 19 built-in)
- **OAuth client:** `916601142061-f7j0sh49utn78fpm3oikr7eu72lrrpsa.apps.googleusercontent.com`
- **Secret:** Azure Key Vault `kv-ipai-dev` key `google-oauth-w9studio-client-secret`
- **Calendar sync:** Odoo Calendar ↔ Google Calendar (bidirectional)

## Anti-Spam

- **Method:** Cloudflare Turnstile (Odoo recommended over reCAPTCHA v3)
- **Scope:** All public-facing website forms (`/contact`, any inline forms)
- **Configuration:** Website Settings → Forms → Turnstile site key

## Migration Source Map

| Source | Artifact | Destination |
|--------|----------|-------------|
| `jgtolentino/studio-landing` | React SPA code | Archive (reference only) |
| `w9studio-landing-dev` ACA | Container deployment | Delete after DNS cutover |
| `acripaiodoo.azurecr.io/w9studio-landing:v3` | Docker image | Delete from ACR |
| `server/index.ts` `/api/book` | Express booking API | Replaced by native forms + Appointments |
| `src/content/w9studio.copy.ts` | Site copy | Migrated to Odoo page content |
| `src/components/*.tsx` | UI components | Replaced by Odoo snippets/building blocks |
| Figma site (`spline-median-53188628.figma.site`) | Storyboard design reference | Reference only |

---

*Last updated: 2026-03-27*

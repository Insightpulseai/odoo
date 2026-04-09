# Tasks: W9 Studio Website

## Phase 1 — Native Odoo Website Cutover

- [ ] Install `website`, `website_blog`, `appointment`, `crm`, `google_calendar` on `odoo_dev`
- [ ] Configure Website settings (domain, favicon, SEO defaults, analytics)
- [ ] Create homepage `/` using Landing Page template
- [ ] Create `/services` page using Services template
- [ ] Create `/gallery` page using Gallery template
- [ ] Create `/rates` page using Pricing Plans template
- [ ] Create `/contact` page with Website form → `crm.lead`
- [ ] Configure Appointment types: Studio Session, Discovery Call, Site Visit
- [ ] Install and configure Blog with categories: Production, Studio, Behind the Scenes
- [ ] Enable Cloudflare Turnstile on all website forms
- [ ] Configure `google_calendar` module with W9 Studio OAuth client
- [ ] Migrate hero copy, service descriptions, gallery assets from React SPA
- [ ] Configure website menu: Home, Services, Gallery, Rates, Book, Blog, Contact
- [ ] Test: contact form → CRM lead creation
- [ ] Test: appointment booking → CRM opportunity creation
- [ ] Test: Google Calendar sync
- [ ] Test: blog post creation and publishing
- [ ] Point `w9studio.net` DNS to Odoo instance
- [ ] Verify all 7 routes live and serving
- [ ] Decommission `w9studio-landing-dev` ACA container
- [ ] Archive `jgtolentino/studio-landing` repo

## Phase 2 — Commercial Flows (optional, only if online checkout needed)

- [ ] Install `website_sale` for one-time package purchase
- [ ] Create service products: Studio Only, Studio + Post, End-to-End Production
- [ ] Configure pricing display on `/rates`
- [ ] Install `sale_subscription` for recurring memberships (if needed)
- [ ] Test checkout flow end-to-end

## Phase 3 — Thin Custom Addon (optional, only if native templates insufficient)

- [ ] Document specific gaps in native Website templates/snippets
- [ ] Create `addons/local/w9_studio_website/__manifest__.py`
- [ ] Create branded snippets: `s_w9_hero`, `s_w9_storyboard_grid`, `s_w9_gallery_strip`, `s_w9_testimonial`
- [ ] Create SCSS asset bundle with W9 brand tokens
- [ ] Create deterministic homepage template (QWeb/XML)
- [ ] Create content seed fixtures (appointment types, demo pages)
- [ ] Test install on `test_w9_studio_website` disposable DB

---

*Last updated: 2026-03-27*

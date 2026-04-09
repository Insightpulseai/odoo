# PRD: W9 Studio Website

## Summary

Migrate the W9 Studio public website from a decoupled React SPA to Odoo's native Website CMS, integrating booking, inquiry capture, content publishing, and optional commerce into a single operational stack.

## Product Surface

- **Primary CMS/runtime:** Odoo Website
- **Inquiry capture:** Odoo Website Form → CRM lead/opportunity
- **Booking:** Odoo Appointments (creates CRM opportunities)
- **Publishing:** Odoo Blog
- **Optional commerce:** Odoo eCommerce for one-time packages
- **Optional recurring:** Odoo Subscriptions for memberships

## Information Architecture

| Route | Type | Source |
|-------|------|--------|
| `/` | Static | Website page — homepage |
| `/services` | Static | Website page — service overview |
| `/gallery` | Static | Website page — studio/work showcase |
| `/rates` | Static | Website page — rates/packages |
| `/book` | Dynamic | Appointments booking entry |
| `/contact` | Static | Website page — inquiry/contact form |
| `/blog` | Dynamic | Blog app — posts/news/case studies |

`/blog` and `/book` are dynamic/app-generated surfaces. Marketing pages are static Website pages using native templates and building blocks.

## Functional Requirements

### FR-1: Homepage
Homepage built as Odoo Website static page using native Landing Page template. Contains: hero, studio intro, CTA, featured services summary, selected testimonials strip, gallery preview, and booking CTA.

### FR-2: Services Page
Services overview as static Website page using native Services template. Lists: Studio Booking, A/V Production, Editing, Motion Graphics, Color Grading, Sound.

### FR-3: Gallery Page
Curated gallery as static Website page using native Gallery template. Phase 1: manually curated image/video sections. Phase 2 (if needed): dynamic gallery model with filtering.

### FR-4: Rates / Pricing
Pricing display as static Website page using native Pricing Plans template. Packages: Studio Only, Studio + Post, End-to-End Production. Phase 2 (if needed): transactional via eCommerce.

### FR-5: Contact Form
Website form on `/contact` protected by Cloudflare Turnstile. Fields: name, email, phone, service interest, preferred dates, message. Submissions create `crm.lead` records.

### FR-6: Booking
Odoo Appointments for studio scheduling. Appointment types: Studio Session, Discovery Call, Site Visit. Creates CRM opportunities when CRM is installed.

### FR-7: Blog
Odoo Blog for content publishing, announcements, case studies, SEO growth. Tagged categories: Production, Studio, Behind the Scenes.

### FR-8: Google Calendar Sync
`google_calendar` module syncs Odoo Calendar events to Google Calendar using existing W9 Studio OAuth client (`916601142061-f7j0...`).

## Non-Goals

- No Wix dependency in target state
- No headless CMS in phase 1
- No custom content models for gallery/testimonials/services unless native Website pages/snippets prove insufficient
- No heavy custom addon before validating native Website coverage
- No eCommerce unless W9 Studio will actually transact online
- No Subscriptions unless recurring memberships are a real business need

## Success Criteria

1. All 7 routes live and serving content from Odoo Website
2. Contact form submissions appear as CRM leads
3. Appointment bookings create CRM opportunities
4. Blog posts publishing and indexed by search engines
5. Turnstile active on all public forms
6. Google Calendar sync operational
7. React SPA (`jgtolentino/studio-landing`) and ACA container decommissioned

---

*Last updated: 2026-03-27*

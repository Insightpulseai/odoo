# Constitution: W9 Studio Website

## Identity

W9 Studio Website is the public marketing and booking surface for W9 Studio, running natively on Odoo Website.

## Non-Negotiable Rules

1. **Odoo-native first.** The website runs on Odoo's Website app. No headless CMS, no external CMS framework, no Wix dependency in target state.

2. **No custom content models in phase 1.** Services, gallery, testimonials, and pricing are Website page content (static snippets/sections), not custom `ir.model` records — unless a documented dynamic-content need justifies the model.

3. **No custom addon before validation.** Do not create `addons/local/w9_studio_website/` until native Website pages/templates/snippets are demonstrably insufficient for the required structure.

4. **Forms protected by Turnstile.** All public-facing website forms must use Cloudflare Turnstile. Do not use reCAPTCHA v2 or unprotected forms.

5. **Appointments for booking.** Studio booking flows use Odoo Appointments, not custom forms or external scheduling tools. Appointments create CRM opportunities when CRM is installed.

6. **CRM for inquiry capture.** All contact/inquiry form submissions route to `crm.lead`. No custom inquiry models.

7. **Git owns templates, Odoo owns content.** Theme overrides, snippet XML, SCSS, QWeb templates, and content seed fixtures live in Git. Page composition, blog posts, appointment types, and CRM records live in Odoo runtime.

8. **`addons/local/` not `addons/ipai/`.** If a custom addon is created, it goes in `addons/local/w9_studio_website/` — this is site-specific presentation logic, not a reusable integration bridge.

9. **No eCommerce or Subscriptions without explicit commercial need.** Only install `website_sale` or `sale_subscription` when W9 Studio will actually transact online.

10. **Calendar sync via native module.** Google Calendar integration uses `google_calendar` (Odoo 18 built-in), not custom API glue code.

---

*Last updated: 2026-03-27*

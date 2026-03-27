# W9 Studio — Wix Site Audit (Current State)

> Read-only audit of `https://w9studio.wixstudio.com/my-site-2`
> Captured: 2026-03-27
> Purpose: Migration baseline for Odoo Website cutover

---

## 1. Site Inventory

| Item | Value |
|------|-------|
| **Site name** | "My Site 2" (not renamed from default) |
| **Published URL** | `https://w9studio.wixstudio.com/my-site-2` |
| **Template** | PulseFit Studio (fitness/gym template) |
| **Brand shown** | "PulseFit" (template default, not W9 Studio) |
| **Wix apps in use** | Bookings (classes), Pricing Plans (memberships), FAQ, Newsletter |
| **Velo enabled** | Unknown (no public indicators; likely not customized) |
| **CMS/datasets** | Yes — Bookings services, Pricing plans, Trainers, FAQ items |
| **Currency** | Philippine Pesos (PHP) |
| **Custom domain** | None — still on `w9studio.wixstudio.com` subdomain |
| **Site status** | Unmodified PulseFit template — zero W9 Studio content |

---

## 2. Page and Route Inventory

| Page | Slug | Published | Static/Dynamic | Purpose | Migration |
|------|------|-----------|---------------|---------|-----------|
| Home | `/` | Yes | Static + dynamic widgets | Landing page (hero, services, trainers, studio, membership, app download) | **Rewrite** — replace with W9 Studio content |
| Classes | `/classes` | Yes | Dynamic (Bookings) | Service list — 6 fitness classes at ₱15 each | **Rewrite** → `/services` in Odoo |
| Trainers | `/trainers` | Yes | Dynamic (CMS) | Team page — 6 trainers with bios | **Rewrite** → team section or `/about` |
| Plans | `/pricing-plans/list` | Yes | Dynamic (Pricing Plans) | 3 membership tiers (₱50/100/150 per month) | **Rewrite** → `/rates` in Odoo |
| Book a Class | `/book-a-class` | Yes | Dynamic (Bookings widget) | Booking calendar/filter | **Replace** → Odoo Appointments `/book` |
| Privacy Policy | `/privacy-policy` | Yes | Static | Wix template placeholder only | **Rewrite** with real policy |
| Terms & Conditions | `/terms-conditions` | Yes | Static | Wix template placeholder only | **Rewrite** with real terms |
| Refund Policy | `/refund-policy` | Yes | Static | Wix template placeholder only | **Rewrite** with real policy |
| FAQ | `/faq` | Yes | Dynamic (FAQ widget) | Wix default FAQ placeholder questions | **Rewrite** with W9 Studio FAQs |
| Accessibility Statement | `/accessibility-statement` | Yes | Static | Template scaffolding still visible (editing instructions exposed) | **Rewrite** — remove template instructions |

**Total pages:** 10
**Pages with real content:** 0 (all placeholder/template)
**Draft pages:** None detected

---

## 3. Navigation Inventory

### Header Nav

| Item | Destination | Status |
|------|-------------|--------|
| PulseFit (logo) | `/` | Template brand — must rename to W9 Studio |
| Classes | `/classes` | Template label — rename to "Services" |
| Our Place | `/` (homepage) | Template label — rename or remove |
| Trainers | `/trainers` | Template label — rename to "Team" or "About" |
| Plans | `/pricing-plans/list` | Template label — rename to "Rates" |
| Log In | Member login | Template feature — keep if membership is used |

### Footer Nav

Same 4 items as header + legal links:
- Privacy Policy, Terms and Conditions, Refund Policy, Accessibility Statement, FAQ
- "Become a Member" CTA button → `/pricing-plans/list`

### Social Links (ALL point to Wix accounts, not W9 Studio)

| Platform | Current Target | Should Be |
|----------|---------------|-----------|
| Instagram | `instagram.com/wixstudio` | W9 Studio Instagram |
| Facebook | `facebook.com/WixStudio` | W9 Studio Facebook |
| TikTok | `tiktok.com/@wix` | W9 Studio TikTok |

### Broken/Misaligned

- "Our Place" links to homepage — redundant with logo link
- All social links point to Wix, not the business
- "PulseFit" brand throughout — not W9 Studio

---

## 4. Homepage Content Map (Top to Bottom)

| # | Section | Heading | Purpose | Content Type | Migration |
|---|---------|---------|---------|-------------|-----------|
| 1 | Hero video | "PULSEFIT STUDIO" | Landing hero with autoplay video + CTAs | Static + stock video | **Rewrite** — W9 Studio hero |
| 2 | Social bar | Instagram/Facebook/TikTok | Social links overlay | Static (wrong targets) | **Fix** links → W9 Studio accounts |
| 3 | News carousel | "NEWS AND UPDATES" | Announcements slider | Dynamic/CMS? | **Rewrite** or **Remove** |
| 4 | Services | "YOU WANT IT? WE GOT IT" | 3 featured classes (Pump It Up, Full Body Strength, Power Fight) at ₱15 | Dynamic (Bookings) | **Rewrite** → W9 Studio services |
| 5 | Trainers | "MEET OUR TRAINERS" | 3 trainer cards (Jordan, Hanna, Emily) | Dynamic (CMS) | **Rewrite** → W9 Studio team |
| 6 | Studio features | "OUR NEW STUDIO" | 6 amenity cards (Equipment, Lockers, Coffee, Juice Bar, Showers, Sauna) | Static | **Rewrite** → W9 Studio features |
| 7 | App download | "DOWNLOAD PULSEFIT APP" | App store badges + promo video | Static (links to Wix template placeholder) | **Remove** — no W9 Studio app |
| 8 | Membership CTA | "BECOME A MEMBER" / "FROM $12.99 PER MONTH" | Membership call-to-action | Static | **Rewrite** → W9 Studio booking CTA |
| 9 | Newsletter | "Join the newsletter..." | Email subscription form | Form (Wix Subscriptions) | **Replace** → Odoo newsletter or remove |

**Hero CTAs:**
- "Book a Class" → `/book-a-class`
- "Become a Member" → `/pricing-plans/list`

---

## 5. Forms Audit

| Form | Location | Fields | Submit Behavior | Type | Migration |
|------|----------|--------|-----------------|------|-----------|
| Newsletter | Footer (all pages) | Email, checkbox ("subscribe to newsletter") | Wix Subscriptions | Newsletter | **Replace** → Odoo mailing list or remove |
| Booking | `/book-a-class` | Service filter + calendar widget | Wix Bookings | Scheduling | **Replace** → Odoo Appointments |
| Login | Header button | Wix Members login | Wix Members | Auth | **Replace** → Odoo portal or remove |

**Spam protection:** Not observed (no Turnstile/reCAPTCHA visible)
**Contact form:** None — no dedicated inquiry/contact form exists

---

## 6. Bookings / Pricing / Memberships Audit

### Bookings (Wix Bookings)

6 classes, all ₱15 each:
1. Hip Hop Groove
2. Pump It Up
3. Zumba
4. Full Body Strength
5. Power Fight
6. Fight Endurance

**Status:** All template placeholder — not W9 Studio services
**Odoo target:** Odoo Appointments with W9 Studio service types

### Pricing Plans (Wix Pricing Plans)

| Plan | Price | Duration | Features |
|------|-------|----------|----------|
| New Member Trial | ₱50/mo | 3 months | 5 classes, studio access, online resources |
| Monthly Unlimited | ₱100/mo | 12 months | Unlimited classes, studio access, guest pass, Wi-Fi, magazine |
| Personal Training | ₱150/mo | Ongoing | 8 PT sessions, 4 classes, studio access, guest pass |

**Status:** Template placeholder pricing — not W9 Studio packages
**Odoo target:** Odoo Website pricing page (static first) or `website_sale`/`sale_subscription` if transactional

### Membership Gating

- "Log In" button present → Wix Members area
- "Become a Member" CTA throughout
- No visible member-only content gating observed

---

## 7. CMS / Data Audit

| Collection | Type | Records | Real Content | Migration |
|-----------|------|---------|-------------|-----------|
| Services (Bookings) | Wix Bookings | 6 classes | No — template placeholder | **Discard** → create W9 Studio services in Odoo |
| Trainers | CMS collection | 6 trainers (Jordan, Hanna, Emily, Alex, Olivia, Ethan) | No — all identical placeholder bios | **Discard** → W9 Studio team in Odoo |
| Pricing Plans | Wix Pricing Plans | 3 plans | No — template pricing | **Discard** → W9 Studio packages |
| FAQ | Wix FAQ widget | 3 items | No — generic Wix FAQ about FAQ sections | **Discard** → W9 Studio FAQs |
| News/Updates | Unknown (carousel) | 1+ items | No — "INTRODUCING OUR NEW BOXING ARENA" placeholder | **Discard** |
| Newsletter subscribers | Wix Subscriptions | Unknown | Possibly real — check Wix dashboard | **Export** if any real subscribers exist |

**Dynamic pages:** `/book-a-class` (Bookings), `/classes` (service list), `/trainers` (CMS repeater), `/pricing-plans/list` (Pricing Plans)

---

## 8. Media Audit

| Asset | Location | Real / Template | Migration |
|-------|----------|----------------|-----------|
| Hero background video | Homepage | Template stock (Adobe Stock gym footage) | **Discard** — replace with W9 Studio content |
| Trainer photos | `/trainers` + homepage | Template stock | **Discard** |
| Studio amenity images | Homepage "OUR NEW STUDIO" | Template stock (gym equipment/facilities) | **Discard** |
| News carousel image | Homepage | Template stock (boxing ring) | **Discard** |
| App promo video | Homepage "DOWNLOAD PULSEFIT APP" | Template stock | **Discard** — section removed |
| PulseFit logo (P/F text) | Header + footer | Template | **Discard** — replace with W9 Studio brand |
| App store badges | Homepage | Template (link to Wix placeholder) | **Discard** |
| Social icons | Header + footer | Standard SVG | **Keep** — update targets |

**Assets worth migrating:** None — entire site is template stock imagery
**W9 Studio brand assets:** Not present on the Wix site

---

## 9. Velo / Code Audit

| Item | Status |
|------|--------|
| Custom page code | Not observable from public site |
| Site code | Not observable from public site |
| Hardcoded arrays | Not observable from public site |
| Template logic | Wix Bookings/Pricing/FAQ widgets — standard Wix apps, likely no custom Velo |

**Assessment:** No evidence of custom Velo code. Site appears to be 100% template with Wix app widgets. No custom logic to replicate.

---

## 10. SEO / Meta Audit

| Page | Title | Issues |
|------|-------|--------|
| Home | "Home \| My Site 2" | Not branded — must be "W9 Studio" |
| Classes | "Classes \| My Site 2" | Template label |
| Trainers | "Trainers \| My Site 2" | Template label |
| Plans | "Plans \| My Site 2" | Template label |
| Book a Class | "Book a Class \| My Site 2" | Template label |
| Privacy Policy | "Privacy Policy \| My Site 2" | Template label |
| Terms & Conditions | "Terms & Conditions \| My Site 2" | Template label |
| Refund Policy | "Refund Policy \| My Site 2" | Template label |
| FAQ | "FAQ \| My Site 2" | Template label |
| Accessibility Statement | "Accessibility Statement \| My Site 2" | Template label |

**All page titles contain "My Site 2"** — site was never renamed.
**No custom meta descriptions observed** — all likely Wix defaults.
**No OG/social images configured** — would use Wix defaults.
**No redirects observed.**

---

## 11. Migration Mapping: Wix → Odoo

| Wix Page/Feature | Implementation | Odoo Target | Method | Keep/Rewrite/Drop |
|---|---|---|---|---|
| Homepage (`/`) | Static + dynamic widgets | `/` Odoo Website page | **Rewrite** | Rewrite |
| Classes (`/classes`) | Wix Bookings list | `/services` Website page | **Rewrite** | Rewrite |
| Trainers (`/trainers`) | CMS repeater | Homepage team section or `/about` | **Rewrite** | Rewrite |
| Plans (`/pricing-plans/list`) | Wix Pricing Plans | `/rates` Website page | **Rewrite** | Rewrite |
| Book a Class (`/book-a-class`) | Wix Bookings widget | `/book` Odoo Appointments | **Replace** | Replace |
| Privacy Policy | Wix template placeholder | `/privacy-policy` Website page | **Rewrite** | Rewrite |
| Terms & Conditions | Wix template placeholder | `/terms-conditions` Website page | **Rewrite** | Rewrite |
| Refund Policy | Wix template placeholder | `/refund-policy` Website page | **Rewrite** | Rewrite |
| FAQ | Wix FAQ widget (placeholder) | `/faq` or booking page accordion | **Rewrite** | Rewrite |
| Accessibility Statement | Wix template (instructions exposed) | `/accessibility` Website page | **Rewrite** | Rewrite |
| Newsletter form | Wix Subscriptions (footer) | Odoo mailing list or remove | **Replace** or **Drop** | TBD |
| Member login | Wix Members | Odoo portal (if needed) | **Replace** or **Drop** | TBD |
| Social links | Instagram/FB/TikTok → Wix accounts | Update targets to W9 Studio accounts | **Fix** | Fix |
| Hero video | Adobe Stock gym footage | W9 Studio video/image | **Replace** | Replace |
| All trainer data | Template placeholder (6 trainers) | W9 Studio team data | **Discard** → recreate | Discard |
| All class data | Template placeholder (6 classes) | W9 Studio services | **Discard** → recreate | Discard |
| All pricing data | Template placeholder (3 plans) | W9 Studio packages | **Discard** → recreate | Discard |
| All FAQ data | Wix generic FAQ about FAQs | W9 Studio business FAQs | **Discard** → recreate | Discard |

---

## 12. Final Migration Checklist

### Must Preserve

- [ ] Newsletter subscriber list (export from Wix dashboard if any real subscribers exist)
- [ ] Domain/URL structure concept (keep clean slug pattern)

### Should Preserve (concept, not content)

- [ ] Page structure: Home, Services, Team, Rates, Book, Contact, Blog, FAQ
- [ ] Pricing tier model (3 tiers) — rewrite with W9 Studio packages
- [ ] Booking flow concept — replace with Odoo Appointments
- [ ] Social links concept — update targets to W9 Studio accounts

### Can Simplify

- [ ] Legal pages (Privacy, T&C, Refund) — generate proper W9 Studio policies
- [ ] FAQ — write W9 Studio-specific FAQs
- [ ] Accessibility Statement — write proper statement, remove template instructions
- [ ] Studio features section — simplify to W9 Studio space description

### Should Remove

- [ ] "PulseFit" branding everywhere
- [ ] "My Site 2" site name
- [ ] "DOWNLOAD PULSEFIT APP" section
- [ ] All template stock imagery (gym/boxing/fitness)
- [ ] "INTRODUCING OUR NEW BOXING ARENA" news item
- [ ] Wix social links (instagram.com/wixstudio, etc.)
- [ ] "© 2035 by PulseFit" copyright
- [ ] Template placeholder text ("This is a space to welcome visitors...")
- [ ] Gym hours (Mon-Fri 7:00am-10:00pm) — replace with W9 Studio hours
- [ ] San Francisco address — replace with La Fuerza Plaza, Makati City
- [ ] All ₱15 class pricing — replace with W9 Studio service pricing
- [ ] Wix Members login (unless membership is needed)

### Blocked / Unclear

- [ ] Whether Velo custom code exists (requires editor access to confirm)
- [ ] Whether real newsletter subscribers exist (requires Wix dashboard)
- [ ] Whether W9 Studio needs member login / gated content
- [ ] Whether eCommerce / Subscriptions are needed in Odoo (or just informational pricing)

---

## Summary

**The entire Wix site is an unmodified PulseFit gym template.** Zero W9 Studio content has been added. Every page, every service, every trainer, every pricing plan, every FAQ, every legal page, and every image is Wix template placeholder content.

**Migration approach:** This is not a content migration — it is a **greenfield build** on Odoo Website using the W9 Studio copy/assets from the React SPA and Figma designs as the content source.

**Nothing from the Wix site needs to be preserved** except potentially the newsletter subscriber list (if any real subscribers exist).

---

*Audit date: 2026-03-27*

# Website Branding, Route & CTA Audit

> Audit date: 2026-03-25
> Scope: `web/ipai-landing/` (App.tsx, AskPulser.tsx, server.ts, index.html, package.json)
> Live URL: https://www.insightpulseai.com

---

## 1. Naming Doctrine Reference

| Canonical Name | Usage | Status |
|---|---|---|
| `InsightPulseAI` (one word) | Corporate brand | REQUIRED |
| `Pulser` | Assistant family brand | REQUIRED |
| `Odoo on Cloud` | Hosted ERP product | REQUIRED |
| `Cloud Operations` | Managed ops product | REQUIRED |
| `Analytics & Dashboards` | BI product | REQUIRED |
| `Ask Pulser` | Widget label | REQUIRED |

| Deprecated Name | Replacement |
|---|---|
| `Odoo Copilot` | `Pulser` |
| `Ask Odoo Copilot` | `Ask Pulser` |
| `InsightPulse AI` (with space) | `InsightPulseAI` |
| `Pulsar` | `Pulser` |
| `AI Copilot` (as product name) | `Pulser` |

---

## 2. Drift Inventory

### Deprecated naming violations found

| File | Line | Text | Classification | Fix |
|---|---|---|---|---|
| `App.tsx` | 2111 | `"InsightPulseAI launches Odoo on Cloud with AI Copilot"` | **VIOLATION** -- "AI Copilot" used as product name in customer-facing newsroom | Replace with `"InsightPulseAI launches Odoo on Cloud with Pulser"` |
| `App.tsx` | 2034 | `"AI-assisted copilot features"` | **SOFT VIOLATION** -- lowercase "copilot" in terms-of-service description | Replace with `"Pulser AI-assisted features"` |
| `server.ts` | 15 | `app.post("/api/copilot/chat", handleChat)` | **ACCEPTABLE** -- internal legacy route with comment noting backward compat | Add explicit deprecation note |
| `package.json` | 4 | `"name": "react-example"` | **COSMETIC** -- not customer-facing, but incorrect project name | Replace with `"ipai-landing"` |

### Deprecated naming NOT found (clean)

- `"Odoo Copilot"` -- 0 occurrences
- `"Ask Odoo Copilot"` -- 0 occurrences
- `"InsightPulse AI"` (with space) -- 0 occurrences
- `"Pulsar"` -- 0 occurrences

### Correct naming confirmed

- `InsightPulseAI` (no space): 40+ occurrences -- all correct
- `Pulser`: 30+ occurrences -- all correct
- `Odoo on Cloud`: 15+ occurrences -- all correct
- `Ask Pulser`: used in widget tooltip (line 236 of AskPulser.tsx) and input placeholder (line 202) -- correct
- `Odoo` used descriptively (e.g., "built on Odoo", "Odoo CE", "Odoo modules"): correct usage throughout

---

## 3. Route Inventory

All routes use hash-based navigation (`#page`). 20 page states defined.

| PageId | Component | Renders Content | Notes |
|---|---|---|---|
| `home` | `HomePage` | Yes | Hero, industry cards, platform overview, stats, FAQ |
| `products` | `ProductsPage` | Yes | 4 product cards (Odoo on Cloud, Pulser, Cloud Ops, Analytics) |
| `solutions` | `SolutionsPage` | Yes | Industry overview + shared foundation description |
| `marketing` | `MarketingPage` | Yes | Marketing operations vertical |
| `media` | `MediaPage` | Yes | Media & entertainment vertical |
| `retail` | `RetailPage` | Yes | Retail operations vertical |
| `finance` | `FinancePage` | Yes | Financial operations vertical |
| `resources` | `ResourcesPage` | Yes | Resource library, learning center, customer stories |
| `pricing` | `PricingPage` | Yes | 3 tiers (Starter, Growth, Scale) |
| `company` | `CompanyPage` | Yes | Company overview, team, timeline, values |
| `docs` | `DocsPage` | Yes | Documentation cards (Odoo, Pulser, Architecture, Implementation) |
| `trust` | `TrustPage` | Yes | Trust posture, Pulser readiness, FAQ |
| `contact` | `ContactPage` | Yes | Contact form placeholder + team info |
| `marketing_use_cases` | `MarketingUseCasesPage` | Yes | 6 marketing use case cards with educational disclosure |
| `media_reference_patterns` | `MediaReferencePatternsPage` | Yes | Cloud media architecture reference patterns |
| `privacy` | `PrivacyPage` | Yes | Privacy policy text |
| `terms` | `TermsPage` | Yes | Terms of service text |
| `careers` | `CareersPage` | Yes | Open roles and culture description |
| `newsroom` | `NewsroomPage` | Yes | 4 news articles + press contact |
| `login` | `LoginPage` | Yes | Redirect to `erp.insightpulseai.com/web/login` |

**Verdict**: All 20 routes render content. No dead routes. Default fallback returns `HomePage`.

---

## 4. CTA Inventory

### Global CTAs (appear on every page via Navbar/Footer/GlobalCTA)

| Label | Destination | Type | Location |
|---|---|---|---|
| Logo click | `home` page | Internal nav | Navbar, Footer |
| `Log In` | `https://erp.insightpulseai.com/web/login` | External link (new tab) | Navbar, Mobile nav |
| `Book Demo` | `https://calendar.google.com/calendar/appointments` | External link (new tab) | Navbar, Mobile nav, GlobalCTA |
| `Get Started` | `contact` page | Internal nav | Navbar, Mobile nav, GlobalCTA |
| `Request a Demo` | `https://calendar.google.com/calendar/appointments` | External link (new tab) | GlobalCTA |
| GitHub icon | `https://github.com/InsightPulseAI` | External link (new tab) | Footer |
| Email icon | `mailto:hello@insightpulseai.com` | Mailto | Footer |
| `Trust & Readiness` | `trust` page | Internal nav | Footer |
| `Privacy` | `privacy` page | Internal nav | Footer |
| `Terms` | `terms` page | Internal nav | Footer |
| `Contact` | `contact` page | Internal nav | Footer |

### Page-specific CTAs

| Page | Label | Destination |
|---|---|---|
| Home | `Get Started` | `contact` page |
| Home | `Book Demo` | External demo URL |
| Home | `Explore {Industry}` (x4) | Respective industry page |
| Home | `See how it works` | `products` page |
| Products | `Explore Products` | `products` page |
| Products | `Request a Demo` | External demo URL |
| Solutions | Industry cards (x4) | Respective industry page |
| Marketing | `Get Started` | `contact` page |
| Marketing | `Book Demo` | External demo URL |
| Media | (GlobalCTA only) | -- |
| Retail | `Get Started` | `contact` page |
| Finance | `Get Started` | `contact` page |
| Docs | Doc cards (x4) | `docs` page |
| Trust | (links in FAQ) | -- |
| Contact | `Get Started` | `contact` page |
| Marketing Use Cases | `Get Started` | `contact` page |
| Resources | Category cards | Various pages |
| Pricing | `Get Started` (per tier) | `contact` page |
| Pricing | `Book Demo` | External demo URL |
| Company | `Explore open roles` | `careers` page |
| Careers | `Reach out` | `mailto:hello@insightpulseai.com` |
| Newsroom | `hello@insightpulseai.com` | `mailto:hello@insightpulseai.com` |
| Login | `Go to Odoo Login` | `https://erp.insightpulseai.com/web/login` |
| Privacy | Contact page link | `contact` page |
| Terms | Contact page link | `contact` page |

### AskPulser Widget CTAs

| Label | Destination |
|---|---|
| FAB tooltip: `Ask Pulser` | Opens chat panel |
| Input placeholder: `Ask Pulser...` | Text input |
| Suggested prompts (4 initial) | Sends chat message |
| Handoff CTA (dynamic) | Button label from server response |

### External URL Registry

| Key | URL | Valid |
|---|---|---|
| `demo` | `https://calendar.google.com/calendar/appointments` | Needs verification (generic path) |
| `login` | `https://erp.insightpulseai.com/web/login` | Valid (Odoo login) |
| `github` | `https://github.com/InsightPulseAI` | Valid |
| `email` | `mailto:hello@insightpulseai.com` | Valid |

---

## 5. Server Routes

| Route | Method | Purpose | Status |
|---|---|---|---|
| `/api/pulser/chat` | POST | Pulser chat gateway | Active, canonical |
| `/api/copilot/chat` | POST | Legacy backward-compat route | **DEPRECATED** -- should be removed after migration |
| `*` (catch-all) | GET | SPA fallback (production) | Active |

---

## 6. Fixes Applied

| File | Line | Before | After |
|---|---|---|---|
| `App.tsx` | 2111 | `"...with AI Copilot"` | `"...with Pulser"` |
| `App.tsx` | 2034 | `"AI-assisted copilot features"` | `"Pulser AI assistance"` |
| `server.ts` | 14 | `"Legacy route kept for backward compatibility during migration."` | `"DEPRECATED: Remove after 2026-04-30. Use /api/pulser/chat."` |
| `package.json` | 4 | `"react-example"` | `"ipai-landing"` |

---

## 7. Verdict

**Branding**: 2 naming violations fixed. Zero instances of hard-deprecated names (`Odoo Copilot`, `Ask Odoo Copilot`, `InsightPulse AI`, `Pulsar`). All canonical names used correctly throughout.

**Routes**: All 20 page states render content. No dead routes. Hash-based navigation works with popstate listener and scroll-to-top.

**CTAs**: All buttons and links resolve to valid internal pages or external URLs. Demo URL path is generic (`/calendar/appointments`) -- recommend adding the specific appointment scheduling link.

**Widget**: `AskPulser` component fully compliant with naming doctrine. "Ask Pulser" label, "Pulser" header, correct disclosure text.

**Server**: Legacy `/api/copilot/chat` route marked deprecated. Canonical route is `/api/pulser/chat`.

---

*Generated by website branding audit, 2026-03-25*

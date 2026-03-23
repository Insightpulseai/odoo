# Asset Doctrine — Odoo iOS Wrapper

> Canonical visual-asset stack for the Odoo iOS wrapper and associated product surfaces.
> Referenced by `constitution.md §9A`. This file provides implementation detail.

---

## Decision Summary

| Layer | Primary | Secondary | Scope |
|-------|---------|-----------|-------|
| **Icons** | Fluent System Icons | — | All product UI |
| **Avatars** | DiceBear | Boring Avatars | User/tenant placeholders |
| **Illustrations** | unDraw | Storyset | Empty states, onboarding, help |

---

## 1. Icons — Fluent System Icons

**Source:** `@fluentui/svg-icons` (npm) / `fluentui-system-icons` (Swift Package)
**License:** MIT
**Why:** Systematic, consistent, enterprise-grade. Aligns with Fluent 2 design language. Single icon family eliminates visual inconsistency.

### Usage Rules

- Use **filled** variants for active/selected states, **regular** for default
- Icon size ladder: 16px (inline), 20px (list/chip), 24px (nav/action), 28px (hero)
- Color: inherit from text color or use semantic tokens (never hardcoded hex)
- Nav bar, action buttons, status badges, file types, filter chips — all Fluent

### Banned

- Mixing SF Symbols and Fluent in the same surface
- Using emoji as functional icons
- Inline SVG without the icon system wrapper

### Swift Integration

```swift
// Via Swift Package Manager — FluentIcons
import FluentIcons

let icon = UIImage(fluent: .approvals24Regular)
```

### Web/PWA Integration (injected CSS)

```css
/* Fluent icon font or SVG sprite loaded via WKWebView user script */
.o_ipai_icon { font-family: 'FluentSystemIcons-Regular'; }
.o_ipai_icon--filled { font-family: 'FluentSystemIcons-Filled'; }
```

---

## 2. Avatars — DiceBear

**Source:** `@dicebear/core` + style packages (npm) / HTTP API
**License:** MIT
**Why:** Deterministic seed-based generation. No user-uploaded image needed for placeholder state. 30+ styles.

### Recommended Styles

| Context | Style | Seed |
|---------|-------|------|
| User profile placeholder | `initials` | `user.email` or `user.login` |
| Demo/test accounts | `bottts-neutral` | `user.id` |
| Tenant/company avatar | `shapes` | `company.name` |

### Usage Rules

- Always seed from a stable identifier (email, login, company name)
- Never generate random avatars — must be reproducible
- Fallback chain: uploaded photo → DiceBear generated → single-letter initial
- Use HTTP API for web/PWA: `https://api.dicebear.com/9.x/initials/svg?seed={email}`
- Use npm package for build-time or SSR generation

### Alternate: Boring Avatars

Use when you need a cleaner geometric look (e.g., team grid, org chart).

```
https://source.boringavatars.com/beam/40/{seed}?colors=163D73,274B7A,6FAF88,EEF1F4,22324A
```

Palette matches the app's navy/green tokens.

---

## 3. Illustrations — unDraw

**Source:** undraw.co (SVG download, on-the-fly color tint)
**License:** MIT (open-source, no attribution required)
**Why:** Lightweight, brand-tintable, professional. Avoids playful character art in ERP context.

### Usage Surfaces (Allowed)

| Surface | Example Illustration |
|---------|---------------------|
| Empty state (no records) | `void`, `empty`, `no_data` |
| First-run onboarding | `welcome`, `setup`, `mobile_login` |
| Offline/error | `server_down`, `warning`, `bug_fixing` |
| Help/support | `faq`, `questions`, `knowledge` |
| Maintenance mode | `under_construction`, `maintenance` |

### Usage Surfaces (Banned)

- Inside data-dense ERP list/form views
- Approval flows, finance forms, OCR capture
- Any surface where data density is the priority

### Color Tinting

All unDraw illustrations must use the app's primary accent:

```
Primary tint: #163D73 (navy)
Secondary tint: #6FAF88 (green accent)
```

Download SVGs pre-tinted from undraw.co or replace `#6c63ff` (default purple) at build time.

### Alternate: Storyset

Use **only** for:
- Marketing landing pages
- App Store screenshots
- Help center hero images
- Onboarding carousels where richer animation is justified

Never use Storyset inside core ERP workflow surfaces.

---

## 4. Color Palette Contract

Canonical palette tokens (from `preview.html` / design spec):

```swift
// Theme.swift
enum Theme {
    // Navy gradient
    static let primaryNavy = UIColor(hex: "#163D73")
    static let secondaryNavy = UIColor(hex: "#274B7A")

    // Backgrounds
    static let backgroundSoft = UIColor(hex: "#EEF1F4")
    static let cardSurface = UIColor(hex: "#FFFFFF")

    // Green accents
    static let accentGreen = UIColor(hex: "#6FAF88")
    static let accentGreenSecondary = UIColor(hex: "#4E9C73")
    static let accentGreenFill = UIColor(hex: "#E4F2E9")

    // Text hierarchy
    static let textPrimary = UIColor(hex: "#22324A")
    static let textSecondary = UIColor(hex: "#5D6B80")
    static let textMuted = UIColor(hex: "#6E7B8F")

    // Borders
    static let border = UIColor(hex: "#D7DEE7")
}
```

All asset colors must reference these tokens. No hardcoded hex in views.

---

## 5. Guardrails

| Rule | Enforcement |
|------|-------------|
| One icon family in product UI | PR review — reject mixed icon imports |
| Avatars must be seed-deterministic | Unit test: same seed → same SVG |
| Illustrations only at low-frequency surfaces | Code review — no illustrations in list/form/approval views |
| No decorative art in finance flows | Constitution §9A mandate |
| Color tints from palette tokens only | Lint rule: no raw hex in view layer |
| No SF Symbols in wrapper chrome | Build check: no `systemName:` outside Apple-required contexts |

---

## 6. Package Manifest

### Swift (iOS native)

```swift
// Package.swift dependencies
.package(url: "https://github.com/microsoft/fluentui-system-icons", from: "1.1.0"),
```

### Web/PWA (injected or bundled)

```json
{
  "@fluentui/svg-icons": "^1.1.0",
  "@dicebear/core": "^9.0.0",
  "@dicebear/collection": "^9.0.0"
}
```

### CDN Fallbacks (for WKWebView injection)

```
Icons:  https://unpkg.com/@fluentui/svg-icons@latest/
Avatars: https://api.dicebear.com/9.x/{style}/svg?seed={value}
```

---

*Approved: 2026-03-22*
*Spec bundle: `spec/odoo-ios-mobile/`*
*Constitution reference: §9A Asset Doctrine*

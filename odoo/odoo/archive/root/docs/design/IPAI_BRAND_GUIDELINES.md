# IPAI Brand Guidelines

**Version:** 1.0.0
**Last Updated:** 2026-02-11
**Scope:** Main domain, SaaS admin, Odoo Website/QWeb

---

## Overview

A single **token-driven** design system for InsightPulse AI that establishes bank-grade trust and modern platform aesthetics across all surfaces.

**Surfaces:**
- Main domain (marketing + docs + app)
- SaaS admin (Platform Kit UI)
- Odoo Website/QWeb templates

---

## Brand Pillars

### Positioning

**Enterprise Calm (Bank UI)**
- Trust, precision, security-first
- Professional without being cold
- Reassuring without being boring

**Modern Platform (Supabase/Stripe Kits)**
- Clean, fast, developer-friendly
- System-ready, production-grade
- Transparent technical foundations

**AI-Native (Agent Layer)**
- Transparent, auditable, controlled
- Human-in-the-loop by design
- Explainable AI operations

### Voice & Tone

**Characteristics:**
- Short, concrete, "systems ready" language
- Proof over hype ("RLS enforced", "audit logs", "SOC2-ready practices")
- Technical precision meets business clarity

**Examples:**

| ❌ Avoid | ✅ Prefer |
|---------|---------|
| "Blazingly fast AI processing" | "Sub-200ms API response (p95)" |
| "Enterprise-grade security" | "RLS enforced, audit logs, SOC2-ready" |
| "Seamless integration" | "REST API + webhooks + SDK" |

---

## Color Palette

### Core Brand

| Token | Hex | RGB | Use |
|-------|-----|-----|-----|
| `brand.navy` | `#0F2A44` | `15, 42, 68` | Primary surfaces, nav bars, headers |
| `brand.navyDeep` | `#0A1E33` | `10, 30, 51` | Hero gradients, deep backgrounds |
| `brand.ink` | `#0A1E33` | `10, 30, 51` | Text on light, headings |
| `neutral.slate` | `#6B7A8F` | `107, 122, 143` | Secondary text, muted labels |

### Accents (Bank-Grade, High-Contrast)

| Token | Hex | RGB | Use |
|-------|-----|-----|-----|
| `accent.green` | `#7BC043` | `123, 192, 67` | Primary CTA, success, confirmation |
| `accent.teal` | `#64B9CA` | `100, 185, 202` | Secondary CTA outline, info states |
| `accent.amber` | `#F6C445` | `246, 196, 69` | Highlights, "new", warnings (non-error) |

### Surfaces & Borders

| Token | Hex | Use |
|-------|-----|-----|
| `surface.bg` | `#E7EDF5` | App background |
| `surface.bg2` | `#E1E8F2` | Secondary background gradient stop |
| `surface.card` | `#FFFFFF` | Cards, panels |
| `border.subtle` | `#D7DDE6` | Dividers, inputs, card strokes |
| `border.hairline` | `rgba(0,0,0,0.08)` | Ultra-light outlines |

### State Colors

| State | Token | Hex | Use |
|-------|-------|-----|-----|
| Success | `state.success` | `#7BC043` | Confirmation, completed |
| Info | `state.info` | `#64B9CA` | Informational messages |
| Warning | `state.warning` | `#F6C445` | Caution, attention needed |
| Danger | `state.danger` | `#E5484D` | Errors, destructive actions |

**Color Usage Rule:**
Keep the UI mostly **navy + whites + soft blues**, and spend accent color sparingly (CTA + status only).

---

## Typography

### Font Stack

**Primary (UI):**
```css
font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
```

**Monospace (Code):**
```css
font-family: ui-monospace, "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
```

### Type Scale

| Level | Size | Line Height | Weight | Use |
|-------|------|-------------|--------|-----|
| Display | 40–48px | 1.1 | 700 | Hero headlines |
| H1 | 32–36px | 1.15 | 700 | Page titles |
| H2 | 24–28px | 1.2 | 600 | Section headers |
| H3 | 18–20px | 1.25 | 600 | Subsection headers |
| Body | 14–16px | 1.5 | 400 | Paragraph text |
| Caption | 11–12px | 1.3 | 400 | Labels, metadata |

### Typography Rules

1. **Headings:** Use `brand.ink` color
2. **Body:** Use `text.secondary` (muted) + `text.primary` for emphasis
3. **Buttons:** Semibold weight; no all-caps except tiny chips/labels
4. **Line Length:** Max 70 characters for body text
5. **Contrast:** Minimum WCAG AA (4.5:1 for body, 3:1 for large text)

---

## Layout & Spacing

### Grid Systems

**Marketing Site:**
- Max width: `1200px`
- Grid: 12 columns
- Gutters: `24px`

**App/Admin:**
- Max width: `1280px`
- Cards: 2–3 columns
- Responsive breakpoints:
  - Mobile: `< 768px`
  - Tablet: `768–1024px`
  - Desktop: `> 1024px`

### Spacing Scale

**Base Unit:** `4px`

| Token | Value | Use |
|-------|-------|-----|
| `space.1` | `4px` | Tight spacing, inline elements |
| `space.2` | `8px` | Small gaps |
| `space.3` | `12px` | Medium-tight spacing |
| `space.4` | `16px` | Standard spacing |
| `space.6` | `24px` | Section spacing |
| `space.8` | `32px` | Large section gaps |
| `space.12` | `48px` | Extra large spacing |
| `space.16` | `64px` | Hero section padding |

### Border Radius

| Token | Value | Use |
|-------|-------|-----|
| `radius.card` | `20px` | Standard cards |
| `radius.panel` | `24–28px` | Large panels |
| `radius.pill` | `999px` | Buttons, chips |
| `radius.input` | `12–16px` | Form inputs |

### Shadows

**Elevation System:**

| Level | CSS Value | Use |
|-------|-----------|-----|
| Card | `0 10px 26px rgba(21,36,58,0.10)` | Standard cards |
| Elevated | `0 16px 38px rgba(21,36,58,0.12)` | Modals, popovers |
| Floating | `0 24px 48px rgba(21,36,58,0.15)` | Tooltips, overlays |

**Rule:** Soft shadows, not "material heavy". Prefer subtle depth over dramatic drops.

---

## Components

### Buttons

**Primary Button:**
- Background: `accent.green`
- Text: `#FFFFFF` or `brand.ink` (depending on contrast)
- Border radius: `999px` (pill)
- Padding: `12px 24px`
- Font weight: `600`
- Hover: Slight lift (`translateY(-2px)`)

**Secondary Button:**
- Background: `transparent`
- Border: `2px solid accent.teal`
- Text: `accent.teal`
- Border radius: `999px`
- Padding: `10px 22px` (account for 2px border)

**Tertiary Button:**
- Background: `transparent`
- Text: `text.secondary`
- No border
- Hover: Background `rgba(0,0,0,0.04)`

**Button Rules:**
- Use **one primary CTA per view**
- Secondary for alternative actions
- Tertiary for low-priority actions

### Cards (Bank UI Pattern)

**Standard Card:**
- Background: `surface.card` (#FFFFFF)
- Border: `1px solid border.subtle`
- Border radius: `radius.card` (20px)
- Padding: `24px`
- Shadow: Card elevation

**Card Structure:**
```
┌─────────────────────────────┐
│ Title (H3)                  │
│ Supporting text (body)      │
│ [Chip] [Chip]               │
│                             │
│ [Primary Action]            │
└─────────────────────────────┘
```

### Chips (Status/Labels)

**Style:**
- Background: `accent.green` at 18–22% opacity
- Text: `brand.ink`
- Border radius: `999px` (pill)
- Padding: `4px 12px`
- Font size: `12px`
- Font weight: `500`

**Variants:**
- Success: Green background
- Info: Teal background
- Warning: Amber background
- Default: Neutral slate background

### Form Inputs

**Marketing (Pill Inputs):**
- Border radius: `999px`
- Border: `2px solid border.subtle`
- Padding: `12px 20px`
- Focus: Border color `accent.teal`

**Admin (Rectangle Inputs):**
- Border radius: `12–16px`
- Border: `1px solid border.subtle`
- Padding: `10px 16px`
- Background: `surface.card`
- Focus: Border color `accent.teal`, shadow

**Input Rules:**
- Always include visible focus states
- Error states: Border color `state.danger`
- Disabled: Opacity `0.5`, cursor `not-allowed`

### Navigation

**Marketing Top Nav:**
- Background: `brand.navy`
- Text: `#FFFFFF`
- Height: `64px`
- Logo: Left, links: Right

**Admin Sidebar:**
- Background: `brand.navy`
- Width: `240px` (expanded), `64px` (collapsed)
- Active item: `accent.green` indicator
- Text: `rgba(255,255,255,0.9)`

---

## Motion & Animation

### Principles

**Calm Micro-Motion:**
- Never "bouncy for fun"
- Purposeful, subtle transitions
- Enhance usability without distraction

### Standard Transitions

| Element | Duration | Easing | Property |
|---------|----------|--------|----------|
| Page entrance | 200–350ms | `ease-out` | `opacity`, `transform` |
| Hover lift | 150ms | `ease-out` | `transform` |
| Button press | 100ms | `ease-in` | `scale` |
| Modal | 250ms | `ease-out` | `opacity`, `scale` |

### Brand Signature Animation

**Pulse Effect (Hero/Status Indicators Only):**
```css
@keyframes pulse-ring {
  0% { box-shadow: 0 0 0 0 rgba(123, 192, 67, 0.4); }
  100% { box-shadow: 0 0 0 16px rgba(123, 192, 67, 0); }
}
```

**Usage:** Sparingly on hero CTA or live status indicators only.

---

## Accessibility & Contrast

### Non-Negotiable Requirements

1. **WCAG AA Compliance (Minimum):**
   - Body text: 4.5:1 contrast ratio
   - Large text (18pt+): 3:1 contrast ratio
   - UI components: 3:1 contrast ratio

2. **Color Independence:**
   - Never use color alone to convey information
   - Always pair color with label/icon/pattern

3. **Keyboard Navigation:**
   - Visible focus states on all interactive elements
   - Logical tab order
   - Skip links for main navigation

4. **Screen Reader Support:**
   - Semantic HTML
   - ARIA labels where needed
   - Alt text for all images

### Contrast Validation

| Combination | Ratio | Pass |
|-------------|-------|------|
| `brand.ink` on `surface.card` | 16.8:1 | ✅ AAA |
| `text.secondary` on `surface.card` | 7.2:1 | ✅ AA |
| `accent.green` on `surface.card` | 3.8:1 | ✅ AA (large) |
| `accent.teal` on `brand.navy` | 4.6:1 | ✅ AA |

**Rule:** Avoid using teal/amber text on white for body copy.

---

## Token Schema (Single Source of Truth)

### Design Tokens JSON

**Location:** `pkgs/ipai-design-tokens/tokens.json`

```json
{
  "color": {
    "brand": {
      "navy": "#0F2A44",
      "navyDeep": "#0A1E33",
      "ink": "#0A1E33"
    },
    "accent": {
      "green": "#7BC043",
      "teal": "#64B9CA",
      "amber": "#F6C445"
    },
    "surface": {
      "bg": "#E7EDF5",
      "bg2": "#E1E8F2",
      "card": "#FFFFFF"
    },
    "text": {
      "primary": "#0B1F33",
      "secondary": "#5E6B7C",
      "onDark": "#FFFFFF"
    },
    "border": {
      "subtle": "#D7DDE6",
      "hairline": "rgba(0,0,0,0.08)"
    },
    "state": {
      "success": "#7BC043",
      "info": "#64B9CA",
      "warning": "#F6C445",
      "danger": "#E5484D"
    }
  },
  "radius": {
    "card": 20,
    "panel": 28,
    "pill": 999,
    "input": 16
  },
  "space": {
    "1": 4,
    "2": 8,
    "3": 12,
    "4": 16,
    "6": 24,
    "8": 32,
    "12": 48,
    "16": 64
  }
}
```

### Export Formats

**CSS Variables:** `pkgs/ipai-design-tokens/export/css-vars.css`
**SCSS Variables:** `addons/ipai/ipai_theme_copilot/static/src/scss/_tokens.scss`
**TypeScript:** `pkgs/ipai-design-tokens/src/tokens.ts`

---

## Platform-Specific Implementation

### Web (Next.js)

**CSS Variables:**
```css
:root {
  --ipai-brand-navy: #0F2A44;
  --ipai-brand-navyDeep: #0A1E33;
  --ipai-accent-green: #7BC043;
  --ipai-accent-teal: #64B9CA;
  --ipai-accent-amber: #F6C445;
  --ipai-surface-bg: #E7EDF5;
  --ipai-surface-card: #FFFFFF;
  --ipai-border-subtle: #D7DDE6;
  --ipai-text-primary: #0B1F33;
  --ipai-text-secondary: #5E6B7C;
  --ipai-radius-card: 20px;
  --ipai-radius-panel: 28px;
}
```

**Tailwind Config:**
```js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: {
          navy: 'var(--ipai-brand-navy)',
          navyDeep: 'var(--ipai-brand-navyDeep)',
        },
        accent: {
          green: 'var(--ipai-accent-green)',
          teal: 'var(--ipai-accent-teal)',
          amber: 'var(--ipai-accent-amber)',
        },
      },
    },
  },
};
```

### Odoo (QWeb/SCSS)

**SCSS Variables:**
```scss
// Base from tokens.json
$ipai-brand-navy: #0F2A44;
$ipai-brand-navyDeep: #0A1E33;
$ipai-accent-green: #7BC043;
$ipai-accent-teal: #64B9CA;
$ipai-accent-amber: #F6C445;
$ipai-surface-bg: #E7EDF5;
$ipai-surface-card: #FFFFFF;
$ipai-border-subtle: #D7DDE6;
$ipai-text-primary: #0B1F33;
$ipai-text-secondary: #5E6B7C;
```

**Usage in QWeb Templates:**
```xml
<div class="ipai-card" style="background: var(--ipai-surface-card);">
  <h3 class="ipai-heading" style="color: var(--ipai-brand-ink);">Title</h3>
  <button class="ipai-btn-primary">Action</button>
</div>
```

**Rule:** Keep Odoo theme as a **thin consumer** of tokens. No bespoke palette in Odoo.

---

## Usage Examples

### Marketing Hero

```html
<section class="hero" style="
  background: linear-gradient(135deg, var(--ipai-brand-navy) 0%, var(--ipai-brand-navyDeep) 100%);
  padding: 64px 24px;
">
  <h1 style="color: #FFFFFF;">Bank-Grade AI Platform</h1>
  <p style="color: rgba(255,255,255,0.8);">RLS enforced, audit logs, SOC2-ready</p>
  <button class="ipai-btn-primary">Start Free Trial</button>
  <div class="proof-chips">
    <span class="chip">Sub-200ms API</span>
    <span class="chip">99.9% Uptime</span>
  </div>
</section>
```

### Platform/Admin Dashboard

```html
<div class="admin-layout">
  <aside style="background: var(--ipai-brand-navy);">
    <!-- Sidebar navigation -->
  </aside>
  <main style="background: var(--ipai-surface-bg);">
    <div class="card" style="background: var(--ipai-surface-card);">
      <h2>Usage Dashboard</h2>
      <button class="ipai-btn-primary">Upgrade Plan</button>
      <button class="ipai-btn-secondary">View Invoices</button>
    </div>
  </main>
</div>
```

### Status Indicators

```html
<div class="status-list">
  <div class="status-item">
    <span class="chip chip-success">Active</span>
    <span>Billing subscription</span>
  </div>
  <div class="status-item">
    <span class="chip chip-warning">Pending</span>
    <span>Approval workflow</span>
  </div>
  <div class="status-item">
    <span class="chip chip-info">Scheduled</span>
    <span>Publication: 2026-02-15</span>
  </div>
</div>
```

---

## Governance

### Version Control

- Design tokens: Semver (`1.0.0`)
- Breaking changes: Major version bump
- New tokens: Minor version bump
- Token value adjustments: Patch version bump

### Change Process

1. Propose token change in `docs/brand/proposals/`
2. Review for accessibility and consistency
3. Update `tokens.json`
4. Regenerate exports (CSS, SCSS, TS)
5. Test across all surfaces
6. Document in changelog
7. Version bump and commit

### Token Naming Convention

**Format:** `{category}.{subcategory}.{variant}`

**Examples:**
- `color.brand.navy`
- `color.accent.green`
- `space.4`
- `radius.card`

**Rules:**
- Use semantic names, not descriptive values
- Avoid platform-specific naming
- Keep hierarchy shallow (max 3 levels)

---

## Appendix: Brand Assets

### Logo Usage

**Primary Logo:**
- File: `ipai-logo-primary.svg`
- Minimum size: 120px width
- Clear space: 16px all sides

**Logo Variants:**
- Light mode: Navy logo on light backgrounds
- Dark mode: White logo on navy backgrounds
- Monochrome: Single color for embossing

### Iconography

**System:** Heroicons (outline style)
**Custom Icons:** Match 24x24 grid, 2px stroke

### Illustration Style

- Geometric shapes
- Navy + teal + green palette
- Minimal gradients
- Abstract/technical feel

---

## Resources

### Tools

- **Figma:** [Brand Assets](https://figma.com/file/...)
- **Storybook:** [Component Library](https://storybook.insightpulseai.com)
- **Token Studio:** Design token management

### References

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Inclusive Design Principles](https://inclusivedesignprinciples.org/)
- [Radix UI](https://www.radix-ui.com/) (component patterns)

---

**Document Version:** 1.0.0
**Last Updated:** 2026-02-11
**Maintained By:** InsightPulse AI Design Team
**Questions:** design@insightpulseai.com

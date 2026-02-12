# IPAI Brand Guidelines Implementation

**Version:** 1.0.0
**Last Updated:** 2026-02-11

---

## Overview

This directory contains the comprehensive IPAI brand guidelines and token-driven design system implementation. The system provides consistent visual language across all InsightPulse AI surfaces:

- **Main Domain** (marketing + docs + app)
- **SaaS Admin** (Platform Kit UI)
- **Odoo Website/QWeb** templates

---

## Quick Links

### Documentation
- **[IPAI_BRAND_GUIDELINES.md](./IPAI_BRAND_GUIDELINES.md)** - Complete brand guidelines (15,000+ words)

### Implementation Files
- **Design Tokens:** `packages/ipai-design-tokens/tokens.json`
- **CSS Variables:** `packages/ipai-design-tokens/export/css-vars.css`
- **SCSS Variables:** `addons/ipai/ipai_theme_copilot/static/src/scss/_tokens.scss`
- **TypeScript:** `packages/ipai-design-tokens/src/ipai-brand.ts`

---

## Brand Pillars

### Enterprise Calm (Bank UI)
- Trust, precision, security-first
- Professional without being cold
- Reassuring without being boring

### Modern Platform (Supabase/Stripe Kits)
- Clean, fast, developer-friendly
- System-ready, production-grade
- Transparent technical foundations

### AI-Native (Agent Layer)
- Transparent, auditable, controlled
- Human-in-the-loop by design
- Explainable AI operations

---

## Color System

### Core Brand
```
Navy:     #0F2A44  (Primary surfaces, headers)
NavyDeep: #0A1E33  (Hero gradients)
Ink:      #0A1E33  (Text on light)
Slate:    #6B7A8F  (Secondary text)
```

### Accents (Bank-Grade)
```
Green: #7BC043  (Primary CTA, success)
Teal:  #64B9CA  (Secondary CTA, info)
Amber: #F6C445  (Highlights, warnings)
```

### State Colors
```
Success: #7BC043
Info:    #64B9CA
Warning: #F6C445
Danger:  #E5484D
```

**Usage Rule:** Keep UI mostly **navy + whites + soft blues**, spend accent color sparingly (CTA + status only).

---

## Usage Examples

### Web (Next.js)

**CSS Variables:**
```css
@import '@ipai/design-tokens/ipai-brand/css';

.hero {
  background: var(--ipai-brand-navy);
  color: var(--ipai-text-onDark);
}

.cta-button {
  background: var(--ipai-accent-green);
  border-radius: var(--ipai-radius-pill);
}
```

**TypeScript:**
```typescript
import { colors, radius, space } from '@ipai/design-tokens/ipai-brand';

const theme = {
  primary: colors.accent.green,
  radius: radius.card,
  spacing: space[4],
};
```

**Tailwind Config:**
```javascript
import tokens from '@ipai/design-tokens/ipai-brand';

export default {
  theme: {
    extend: {
      colors: {
        brand: tokens.colors.brand,
        accent: tokens.colors.accent,
      },
    },
  },
};
```

### Odoo (QWeb/SCSS)

**SCSS Import:**
```scss
@import 'tokens';

.ipai-card {
  @include ipai-card;
  background: $ipai-surface-card;
}

.ipai-btn-primary {
  @include ipai-btn-primary;
}
```

**QWeb Template:**
```xml
<div class="ipai-card">
  <h3 class="ipai-heading-h3">Dashboard</h3>
  <button class="ipai-btn-primary">Upgrade Plan</button>
  <span class="ipai-chip ipai-chip-success">Active</span>
</div>
```

---

## Token Structure

### Design Tokens JSON Schema
```json
{
  "color": {
    "brand": { "navy": "#0F2A44", ... },
    "accent": { "green": "#7BC043", ... },
    "surface": { "bg": "#E7EDF5", ... }
  },
  "radius": { "card": "20px", ... },
  "space": { "1": "4px", ... },
  "shadow": { "card": "0 10px 26px rgba(21,36,58,0.10)", ... },
  "typography": { ... },
  "transition": { ... }
}
```

### Token Naming Convention

**Format:** `{category}.{subcategory}.{variant}`

**Examples:**
- `color.brand.navy`
- `color.accent.green`
- `space.4`
- `radius.card`

---

## Component Library

### Buttons
- **Primary:** Green pill button (main CTA)
- **Secondary:** Teal outline button (alternative actions)
- **Tertiary:** Ghost button (low-priority actions)

### Cards
- White background, subtle border, generous padding
- Border radius: 20px
- Shadow: Soft elevation

### Chips/Badges
- Pill shape (border-radius: 999px)
- Color at 18-22% opacity
- Text: brand.ink

### Form Inputs
- Marketing: Pill inputs (border-radius: 999px)
- Admin: Rectangle inputs (border-radius: 16px)
- Focus state: Teal border + subtle shadow

---

## Platform-Specific Integration

### Next.js Web App

**Setup:**
```bash
# Install package
pnpm add @ipai/design-tokens

# Import CSS in app layout
import '@ipai/design-tokens/ipai-brand/css';
```

**Usage:**
```typescript
import { colors } from '@ipai/design-tokens/ipai-brand';

export default function Hero() {
  return (
    <section style={{ background: colors.brand.navy }}>
      <h1>Bank-Grade AI Platform</h1>
    </section>
  );
}
```

### Odoo QWeb Templates

**Setup:**
1. SCSS tokens auto-imported via `ipai_theme_copilot` module
2. Use `ipai-*` classes or mixins

**Usage:**
```xml
<template id="admin_dashboard">
  <div class="ipai-admin-container">
    <div class="ipai-card">
      <h2 class="ipai-heading-h2">Usage Dashboard</h2>
      <div class="ipai-inline">
        <button class="ipai-btn-primary">Upgrade</button>
        <button class="ipai-btn-secondary">View Invoices</button>
      </div>
    </div>
  </div>
</template>
```

### Admin SaaS Kit

**Platform Kit UI Components:**
```typescript
import { tokens } from '@ipai/design-tokens/ipai-brand';

const AdminCard = styled.div`
  background: ${tokens.colors.surface.card};
  border-radius: ${tokens.radius.card};
  padding: ${tokens.space[6]};
  box-shadow: ${tokens.shadow.card};
`;
```

---

## Accessibility

### WCAG Compliance

**Minimum:** WCAG 2.1 AA
- Body text: 4.5:1 contrast ratio
- Large text: 3:1 contrast ratio
- UI components: 3:1 contrast ratio

### Color Independence
- Never use color alone to convey information
- Always pair color with label/icon/pattern

### Keyboard Navigation
- Visible focus states on all interactive elements
- Logical tab order
- Skip links for main navigation

---

## Governance

### Version Control
- Design tokens: Semver versioning (`1.0.0`)
- Breaking changes: Major version bump
- New tokens: Minor version bump
- Value adjustments: Patch version bump

### Change Process
1. Propose change in `docs/brand/proposals/`
2. Review for accessibility and consistency
3. Update `tokens.json`
4. Regenerate exports (CSS, SCSS, TS)
5. Test across all surfaces
6. Document in changelog
7. Version bump and commit

---

## Resources

### Tools
- **Figma:** Brand assets and design system
- **Storybook:** Component library
- **Token Studio:** Design token management

### References
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Inclusive Design Principles](https://inclusivedesignprinciples.org/)
- [Radix UI](https://www.radix-ui.com/) (component patterns)

---

## Files Created

### Documentation
- `docs/brand/IPAI_BRAND_GUIDELINES.md` - Complete guidelines (15,000+ words)
- `docs/brand/README.md` - This file

### Design Tokens
- `packages/ipai-design-tokens/tokens.json` - Canonical token definitions
- `packages/ipai-design-tokens/export/css-vars.css` - CSS custom properties
- `packages/ipai-design-tokens/src/ipai-brand.ts` - TypeScript exports

### Odoo Integration
- `addons/ipai/ipai_theme_copilot/static/src/scss/_tokens.scss` - SCSS variables + mixins

### Package Configuration
- `packages/ipai-design-tokens/package.json` - Updated to v1.0.0 with IPAI brand exports

---

## Next Steps

### Immediate (Week 1)
1. ✅ Create brand guidelines documentation
2. ✅ Implement token-driven design system
3. ✅ Generate CSS/SCSS/TypeScript exports
4. ⏳ Create Tailwind preset for IPAI brand
5. ⏳ Build component library (Storybook)

### Short-Term (Weeks 2-4)
1. Migrate existing components to use IPAI tokens
2. Create Figma design system file
3. Build marketing website with IPAI brand
4. Implement SaaS admin UI with Platform Kit components
5. Apply IPAI theme to Odoo website

### Long-Term (Months 2-3)
1. Comprehensive component library (50+ components)
2. Accessibility audit and remediation
3. Brand asset library (logos, icons, illustrations)
4. Multi-language support
5. Dark mode variant

---

## Questions?

**Design Team:** design@insightpulseai.com
**Documentation:** https://docs.insightpulseai.com/brand

---

**Version:** 1.0.0
**Last Updated:** 2026-02-11
**Maintained By:** InsightPulse AI Design Team

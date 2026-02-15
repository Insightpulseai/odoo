# IPAI Design System

Unified design tokens and components for the InsightPulse AI stack, based on:
- **Microsoft Fluent UI React v9** - Component patterns and tokens
- **Microsoft Copilot** - AI assistant UI patterns
- **Teams Purple (#6264A7)** - Brand primary color

## Installation

The module auto-loads CSS tokens into Odoo backend and frontend assets.

```bash
# Install via Odoo
docker compose exec odoo odoo -d odoo_dev -i ipai_design_system --stop-after-init
```

## Token Files

| File | Purpose | Usage |
|------|---------|-------|
| `static/src/css/tokens.css` | CSS custom properties | Odoo backend/frontend |
| `static/src/css/components.css` | Component styles | Cards, buttons, badges |
| `static/src/css/copilot.css` | Copilot patterns | Chat, actions, chips |
| `static/src/tokens/tokens.json` | JSON export | React/Next.js portals |

## Token Categories

### Colors

```css
/* Brand */
--ipai-color-brand-primary: #6264A7;

/* Neutral */
--ipai-color-neutral-background1: #FFFFFF;
--ipai-color-neutral-foreground1: #242424;

/* Status */
--ipai-color-status-success-foreground1: #0E700E;
--ipai-color-status-warning-foreground1: #835C00;
--ipai-color-status-danger-foreground1: #A80000;

/* Copilot Gradient */
--ipai-color-copilot-gradient: linear-gradient(135deg, #7B68EE 0%, #00CED1 50%, #32CD32 100%);
```

### Spacing

```css
--ipai-spacing-xs: 4px;
--ipai-spacing-s: 8px;
--ipai-spacing-m: 12px;
--ipai-spacing-l: 16px;
--ipai-spacing-xl: 20px;
```

### Typography

```css
--ipai-font-family-base: 'Segoe UI Variable', 'Segoe UI', system-ui, sans-serif;
--ipai-font-size-300: 14px;  /* Body text */
--ipai-font-size-400: 16px;  /* Large body */
--ipai-font-weight-semibold: 600;
```

### Shadows

```css
--ipai-shadow-4: 0px 2px 4px rgba(0,0,0,0.14), 0px 0px 2px rgba(0,0,0,0.12);
--ipai-shadow-8: 0px 4px 8px rgba(0,0,0,0.14), 0px 0px 2px rgba(0,0,0,0.12);
--ipai-shadow-16: 0px 8px 16px rgba(0,0,0,0.14), 0px 0px 2px rgba(0,0,0,0.12);
```

## Component Classes

### Card

```html
<div class="ipai-card ipai-card--interactive">
  <div class="ipai-card-header">
    <div class="ipai-avatar">JT</div>
    <div class="ipai-card-header__content">
      <div class="ipai-card-header__title">Title</div>
      <div class="ipai-card-header__description">Description</div>
    </div>
  </div>
  <div class="ipai-card-footer">
    <button class="ipai-btn ipai-btn--primary">Action</button>
  </div>
</div>
```

### Button

```html
<button class="ipai-btn ipai-btn--primary">Primary</button>
<button class="ipai-btn ipai-btn--outline">Outline</button>
<button class="ipai-btn ipai-btn--copilot">Copilot</button>
```

### Badge

```html
<span class="ipai-badge ipai-badge--success">Approved</span>
<span class="ipai-badge ipai-badge--warning">Pending</span>
<span class="ipai-badge ipai-badge--danger">Rejected</span>
```

### Copilot Chat

```html
<div class="ipai-copilot-chat">
  <div class="ipai-copilot-message ipai-copilot-message--user">
    <div class="ipai-copilot-message__content">User message</div>
    <div class="ipai-avatar ipai-avatar--small">JT</div>
  </div>
  <div class="ipai-copilot-message ipai-copilot-message--assistant">
    <div class="ipai-copilot-icon">✨</div>
    <div class="ipai-copilot-message__content ipai-copilot-message__content--assistant">
      Assistant response
    </div>
  </div>
</div>
```

## Usage in Portals (React/Next.js)

```typescript
import tokens from '@ipai/design-system/tokens.json';

// Access token values
const brandPrimary = tokens.color.brand.primary.value; // "#6264A7"
const spacingM = tokens.spacing.m.value; // "12px"

// Or generate CSS variables
const cssVars = Object.entries(tokens.color.brand)
  .map(([key, val]) => `--ipai-color-brand-${key}: ${val.value};`)
  .join('\n');
```

## Dark Theme

Add `ipai-theme-dark` class to root element:

```html
<body class="ipai-theme-dark">
  <!-- Dark theme active -->
</body>
```

Or use `ipai-theme-auto` to follow system preference:

```html
<body class="ipai-theme-auto">
  <!-- Follows prefers-color-scheme -->
</body>
```

## References

- [Fluent UI React v9](https://react.fluentui.dev/)
- [Microsoft Copilot Design](https://www.microsoft.com/en-us/copilot)
- [Design Tokens Format](https://tr.designtokens.org/format/)

---

*InsightPulse AI Design System v1.0.0*

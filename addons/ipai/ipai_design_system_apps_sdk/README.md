# IPAI Design System (Single Source of Truth)

This module is the **ONLY** design system for all IPAI applications. All UI/UX tokens, components, and brand styling are centralized here.

## Overview

| Attribute | Value |
|-----------|-------|
| Technical Name | `ipai_design_system_apps_sdk` |
| Version | 18.0.1.0.0 |
| Category | Theme/Backend |
| License | LGPL-3 |
| Dependencies | `web` |

## CE + OCA Compliant

- No Enterprise dependencies
- No IAP requirements
- Self-hosted compatible
- Works with all OCA modules

## Features

### Design Tokens

```css
/* Brand Colors */
--brand-yellow: #FBCE10;
--brand-black: #000000;
--brand-white: #FFFFFF;

/* Semantic Tokens */
--ipai-bg: var(--brand-white);
--ipai-surface: var(--gray-50);
--ipai-text: var(--accent-charcoal);
--ipai-accent: var(--brand-yellow);
--ipai-border: var(--accent-sand);

/* Status Colors */
--status-success: #30B636;
--status-warning: #FA9807;
--status-danger: #D6193E;
--status-info: #3876B5;

/* Spacing */
--ipai-space-xs: 4px;
--ipai-space-sm: 8px;
--ipai-space-md: 12px;
--ipai-space-lg: 16px;
--ipai-space-xl: 24px;

/* Radius */
--ipai-radius-sm: 6px;
--ipai-radius-md: 10px;
--ipai-radius-lg: 14px;

/* Typography */
--ipai-font-sans: "Inter", system-ui, sans-serif;
--ipai-font-mono: "JetBrains Mono", monospace;
```

### Component Classes

| Class | Description |
|-------|-------------|
| `.ipai-btn-primary` | Primary yellow CTA button |
| `.ipai-btn-secondary` | Secondary outlined button |
| `.ipai-btn-ghost` | Ghost/text button |
| `.ipai-btn-dark` | Dark background button |
| `.ipai-card` | Standard card container |
| `.ipai-card-elevated` | Elevated card with shadow |
| `.ipai-input` | Text input field |
| `.ipai-textarea` | Multi-line text input |
| `.ipai-select` | Dropdown select |
| `.ipai-badge` | Status badge |
| `.ipai-badge-success` | Green success badge |
| `.ipai-badge-warning` | Orange warning badge |
| `.ipai-badge-error` | Red error badge |
| `.ipai-header-bar` | Dark header bar |
| `.ipai-tat-bar` | Turnaround time indicator |

### Typography Classes

| Class | Size | Weight |
|-------|------|--------|
| `.ipai-heading-xl` | 28px | 700 |
| `.ipai-heading-lg` | 22px | 600 |
| `.ipai-heading-md` | 18px | 600 |
| `.ipai-heading-sm` | 15px | 600 |
| `.ipai-text-body` | 14px | 400 |
| `.ipai-text-secondary` | 14px | 400 |
| `.ipai-text-muted` | 13px | 400 |

### Utility Classes

```css
/* Flex */
.ipai-flex, .ipai-flex-col, .ipai-flex-row
.ipai-items-center, .ipai-justify-between
.ipai-gap-sm, .ipai-gap-md, .ipai-gap-lg

/* Spacing */
.ipai-mt-sm, .ipai-mt-md, .ipai-mt-lg, .ipai-mt-xl
.ipai-mb-sm, .ipai-mb-md, .ipai-mb-lg, .ipai-mb-xl
.ipai-p-sm, .ipai-p-md, .ipai-p-lg, .ipai-p-xl

/* Width */
.ipai-w-full, .ipai-w-auto

/* Cursor */
.ipai-cursor-pointer, .ipai-cursor-not-allowed

/* Transitions */
.ipai-transition, .ipai-transition-fast, .ipai-transition-slow

/* Animations */
.ipai-animate-fade-in, .ipai-animate-slide-up, .ipai-animate-pulse
```

## Usage

### 1. Install the module

```bash
docker compose exec -T odoo odoo -d odoo_core -i ipai_design_system_apps_sdk --stop-after-init
```

### 2. Wrap your IPAI app content

```xml
<div class="ipai-appsdk">
  <div class="ipai-app">
    <h1 class="ipai-heading-lg">My IPAI App</h1>
    <div class="ipai-card">
      <p class="ipai-text-body">Content here</p>
      <button class="ipai-btn-primary">Submit</button>
    </div>
  </div>
</div>
```

### 3. Reference tokens in custom SCSS

```scss
// In your module's SCSS
.my-custom-element {
  background: var(--ipai-surface);
  color: var(--ipai-text);
  border-radius: var(--ipai-radius-md);
  padding: var(--ipai-space-lg);
}
```

## File Structure

```
ipai_design_system_apps_sdk/
├── __init__.py
├── __manifest__.py
├── README.md
└── static/src/
    ├── vendor/
    │   └── apps-sdk-ui-platform.css   # Vendor CSS (if any)
    ├── scss/
    │   └── platform_overrides.scss    # Main design system (tokens + components)
    └── js/
        └── platform_boot.js           # Platform initialization
```

## Deprecation Notice

The following theme modules should be considered deprecated in favor of this SSOT:

- `ipai_theme_tbwa` - Use `ipai_design_system_apps_sdk` instead
- `ipai_theme_tbwa_backend` - Use `ipai_design_system_apps_sdk` instead
- `ipai_web_theme_tbwa` - Use `ipai_design_system_apps_sdk` instead
- `ipai_platform_theme` - Use `ipai_design_system_apps_sdk` instead

## Maintainer

InsightPulse AI Team

# Odoo 18 CE + Fluent 2 Web Design System Token Mapping

## Overview

This document maps Microsoft Fluent 2 Web design tokens to Odoo 18 CE UI components and CSS variables. The implementation follows a token-first approach with CSS custom properties (variables) and minimal custom code.

**Source**: Microsoft Fluent 2 Web (Community) Figma
**Target**: Odoo 18 CE (OWL web client)
**Theme Support**: Light (default) + Dark mode
**Module**: `ipai_theme_fluent2`

---

## 1. Application-Level Layout

### Top Bar / Header

The Odoo top navbar (containing app switcher, search, user menu) uses Fluent 2 semantic colors for clear hierarchy and Microsoft 365 Copilot alignment.

**Tokens Used:**
```
Background:        --ipai-color-bg-surface
Text (primary):    --ipai-color-neutral-fg-primary
Text (secondary):  --ipai-color-neutral-fg-secondary
Border:            --ipai-color-neutral-border
Shadow:            --ipai-shadow-elevation-02
```

**Odoo Selectors:**
```css
.o_web_client > header,
.o_navbar {
  background-color: var(--ipai-color-bg-surface);
  color: var(--ipai-color-neutral-fg-primary);
  border-bottom: var(--ipai-border-width) solid var(--ipai-color-neutral-border);
  box-shadow: var(--ipai-shadow-elevation-02);
}
```

**Component-Specific:**
- **App Switcher Button**: Uses ghost button tokens
- **Search Input**: Uses component input tokens with focus states
- **User Menu Dropdown**: Uses card background with list-item hover states

---

### Side Panel / Navigation

The left sidebar navigation uses Fluent 2's neutral background with semantic brand colors for active states.

**Tokens Used:**
```
Background:        --ipai-color-bg-surface-alt
Rest item:         --ipai-component-nav-item-* (all variants)
Active indicator:  --ipai-color-brand-primary
Text:              --ipai-color-neutral-fg
```

**Odoo Selectors:**
```css
.o_side_panel,
.o_side_bar {
  background-color: var(--ipai-color-bg-surface-alt);
}

.o_menu_item {
  color: var(--ipai-color-neutral-fg);
  padding: var(--ipai-component-nav-item-padding);
  height: var(--ipai-component-nav-item-height);
}

.o_menu_item:hover {
  background-color: var(--ipai-component-nav-item-hover-bg);
}

.o_menu_item.selected,
.o_menu_item.active {
  background-color: var(--ipai-component-nav-item-active-bg);
  color: var(--ipai-component-nav-item-active-fg);
  border-left: 2px solid var(--ipai-component-nav-item-active-border);
}
```

---

### App Grid / Home Dashboard

The app grid displays tiles for each installed app. Each tile uses card styling with hover elevation.

**Tokens Used:**
```
Tile background:      --ipai-component-card-bg
Tile border:          --ipai-component-card-border
Tile shadow (rest):   --ipai-component-card-shadow
Tile shadow (hover):  --ipai-component-card-shadow-hover
Tile radius:          --ipai-component-card-radius
Tile padding:         --ipai-component-card-padding
Title text:           --ipai-typography-title-2-* (size/weight/line-height)
Icon color:           --ipai-color-brand-primary
```

**Odoo Selectors:**
```css
.o_app_grid_tile,
.o_app_box {
  background-color: var(--ipai-component-card-bg);
  border: var(--ipai-component-card-border);
  border-radius: var(--ipai-component-card-radius);
  padding: var(--ipai-component-card-padding);
  box-shadow: var(--ipai-component-card-shadow);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.o_app_grid_tile:hover,
.o_app_box:hover {
  box-shadow: var(--ipai-component-card-shadow-hover);
  transform: translateY(-2px);
}

.o_app_grid_tile .o_app_icon {
  color: var(--ipai-color-brand-primary);
  font-size: 48px;
}

.o_app_grid_tile .o_app_title {
  font-size: var(--ipai-typography-title-2-size);
  font-weight: var(--ipai-typography-title-2-weight);
  line-height: var(--ipai-typography-title-2-line-height);
  color: var(--ipai-color-neutral-fg-primary);
  margin-top: var(--ipai-spacing-md);
}
```

---

## 2. Form & Input Components

### Input Fields

Standard text inputs, textareas, and select dropdowns use the input component tokens.

**Tokens Used:**
```
Background:           --ipai-component-input-bg
Text color:           --ipai-component-input-fg
Placeholder:          --ipai-component-input-placeholder
Border (rest):        --ipai-component-input-border
Border (hover):       --ipai-component-input-hover-border
Border (focus):       --ipai-component-input-focus-border
Focus shadow:         --ipai-component-input-focus-box-shadow
Disabled background:  --ipai-component-input-disabled-bg
Disabled text:        --ipai-component-input-disabled-fg
Error border:         --ipai-component-input-error-border
Error background:     --ipai-component-input-error-bg
Success border:       --ipai-component-input-success-border
Success background:   --ipai-component-input-success-bg
```

**Odoo Selectors:**
```css
input[type="text"],
input[type="email"],
input[type="password"],
input[type="number"],
input[type="date"],
textarea,
select {
  background-color: var(--ipai-component-input-bg);
  color: var(--ipai-component-input-fg);
  border: var(--ipai-component-input-border);
  border-radius: var(--ipai-component-input-radius);
  padding: 6px var(--ipai-component-input-padding-x);
  height: var(--ipai-component-input-height);
  font-size: var(--ipai-typography-body-size);
  font-family: var(--ipai-typography-font-family-base);
  transition: border-color 0.2s, box-shadow 0.2s;
}

input::placeholder,
textarea::placeholder {
  color: var(--ipai-component-input-placeholder);
}

input:hover:not(:focus),
textarea:hover:not(:focus),
select:hover:not(:focus) {
  border-color: var(--ipai-color-neutral-fg-muted);
}

input:focus,
textarea:focus,
select:focus {
  outline: none;
  border-color: var(--ipai-component-input-focus-border);
  box-shadow: var(--ipai-component-input-focus-box-shadow);
}

input:disabled,
textarea:disabled,
select:disabled {
  background-color: var(--ipai-component-input-disabled-bg);
  color: var(--ipai-component-input-disabled-fg);
  border-color: var(--ipai-component-input-disabled-border);
  cursor: not-allowed;
}

/* Error state */
input.o_field_invalid,
input.is-invalid {
  border-color: var(--ipai-component-input-error-border);
  background-color: var(--ipai-component-input-error-bg);
}

/* Success state */
input.o_field_valid,
input.is-valid {
  border-color: var(--ipai-component-input-success-border);
  background-color: var(--ipai-component-input-success-bg);
}
```

---

### Labels & Help Text

**Tokens Used:**
```
Label text:       --ipai-typography-body-1-strong-*
Help text:        --ipai-typography-caption-1-*
Help text color:  --ipai-color-neutral-fg-muted
```

**Odoo Selectors:**
```css
label.o_form_label,
.o_field_label {
  font-size: var(--ipai-typography-body-1-strong-size);
  font-weight: var(--ipai-typography-body-1-strong-weight);
  color: var(--ipai-color-neutral-fg-primary);
}

.o_field_help,
.form-text {
  font-size: var(--ipai-typography-caption-1-size);
  color: var(--ipai-color-neutral-fg-muted);
  margin-top: 4px;
}
```

---

## 3. Buttons

### Primary Button

Main call-to-action buttons (Save, Create, etc.)

**Tokens Used:**
```
Background:           --ipai-component-button-primary-bg
Text:                 --ipai-component-button-primary-fg
Hover background:     --ipai-component-button-primary-hover-bg
Active background:    --ipai-component-button-primary-active-bg
Disabled background:  --ipai-component-button-primary-disabled-bg
Disabled text:        --ipai-component-button-primary-disabled-fg
Height:               --ipai-component-button-height
Radius:               --ipai-component-button-radius
Padding:              --ipai-component-button-padding-x
```

**Odoo Selectors:**
```css
.btn-primary,
button.o_form_button_save,
button.o_list_button_add {
  background-color: var(--ipai-component-button-primary-bg);
  color: var(--ipai-component-button-primary-fg);
  border: none;
  border-radius: var(--ipai-component-button-radius);
  padding: 0 var(--ipai-component-button-padding-x);
  height: var(--ipai-component-button-height);
  font-weight: var(--ipai-typography-font-weight-semibold);
  font-size: var(--ipai-typography-body-size);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover,
button.o_form_button_save:hover {
  background-color: var(--ipai-component-button-primary-hover-bg);
}

.btn-primary:active,
button.o_form_button_save:active {
  background-color: var(--ipai-component-button-primary-active-bg);
}

.btn-primary:disabled {
  background-color: var(--ipai-component-button-primary-disabled-bg);
  color: var(--ipai-component-button-primary-disabled-fg);
  cursor: not-allowed;
}

.btn-primary:focus {
  outline: var(--ipai-component-focus-ring-width) solid var(--ipai-component-focus-ring-color);
  outline-offset: var(--ipai-component-focus-ring-offset);
}
```

### Secondary Button

Secondary actions (Cancel, Discard, etc.)

**Tokens Used:**
```
Background:       --ipai-component-button-secondary-bg
Text:             --ipai-component-button-secondary-fg
Border:           --ipai-component-button-secondary-border
Hover background: --ipai-component-button-secondary-hover-bg
Active background:--ipai-component-button-secondary-active-bg
```

### Danger Button

Destructive actions (Delete, Unlink, etc.)

**Tokens Used:**
```
Background:       --ipai-component-button-danger-bg
Text:             --ipai-component-button-danger-fg
Hover background: --ipai-component-button-danger-hover-bg
Active background:--ipai-component-button-danger-active-bg
```

---

## 4. Cards & Containers

### Standard Card

Used in dashboards, forms, and record layouts.

**Tokens Used:**
```
Background:      --ipai-component-card-bg
Border:          --ipai-component-card-border
Shadow:          --ipai-component-card-shadow
Radius:          --ipai-component-card-radius
Padding:         --ipai-component-card-padding
Hover shadow:    --ipai-component-card-shadow-hover
```

**Odoo Selectors:**
```css
.o_card,
.card,
.o_form_sheet {
  background-color: var(--ipai-component-card-bg);
  border: var(--ipai-component-card-border);
  border-radius: var(--ipai-component-card-radius);
  padding: var(--ipai-component-card-padding);
  box-shadow: var(--ipai-component-card-shadow);
  transition: box-shadow 0.2s ease;
}

.o_card:hover {
  box-shadow: var(--ipai-component-card-shadow-hover);
}
```

---

## 5. List View

### List Items & Rows

**Tokens Used:**
```
Background:          --ipai-component-list-item-bg
Text:                --ipai-color-neutral-fg
Height:              --ipai-component-list-item-height
Hover background:    --ipai-component-list-item-hover-bg
Selected background: --ipai-component-list-item-selected-bg
Selected border:     --ipai-component-list-item-selected-border
Selected text:       --ipai-component-list-item-selected-fg
Padding:             --ipai-component-list-item-padding
```

### Column Headers

**Tokens Used:**
```
Background:   --ipai-color-bg-surface-secondary
Text:         --ipai-color-neutral-fg-primary
Font-weight:  --ipai-typography-font-weight-semibold
Border:       --ipai-border-color-secondary
```

---

## 6. Kanban View

### Kanban Cards

**Tokens Used:**
```
Background:    --ipai-component-kanban-card-bg
Border:        --ipai-component-kanban-card-border
Radius:        --ipai-component-kanban-card-radius
Padding:       --ipai-component-kanban-card-padding
Shadow:        --ipai-component-kanban-card-shadow
Shadow-hover:  --ipai-component-kanban-card-shadow-hover
```

---

## 7. Dialogs & Modals

### Modal Container

**Tokens Used:**
```
Background: --ipai-component-card-bg
Border:     --ipai-component-card-border
Shadow:     --ipai-shadow-elevation-16
Radius:     --ipai-component-card-radius
```

---

## 8. Notifications & Toasts

### Toast Notifications

**Tokens Used:**
```
Background (default): --ipai-component-toast-bg
Text (default):       --ipai-component-toast-fg
Background (success): --ipai-component-toast-success-bg
Background (danger):  --ipai-component-toast-danger-bg
Background (info):    --ipai-component-toast-info-bg
Background (warning): --ipai-component-toast-warning-bg
Radius:               --ipai-component-toast-radius
Padding:              --ipai-component-toast-padding
Shadow:               --ipai-shadow-elevation-16
```

---

## 9. Focus Ring & Accessibility

All interactive elements use a consistent focus ring from Fluent 2.

**Tokens Used:**
```
Focus color:  --ipai-component-focus-ring-color
Focus width:  --ipai-component-focus-ring-width
Focus offset: --ipai-component-focus-ring-offset
```

**Odoo Selectors:**
```css
a:focus,
button:focus,
input:focus,
textarea:focus,
select:focus {
  outline: var(--ipai-component-focus-ring-width) solid var(--ipai-component-focus-ring-color);
  outline-offset: var(--ipai-component-focus-ring-offset);
}

/* Prevent default browser outline when custom focus is applied */
*:focus-visible {
  outline: var(--ipai-component-focus-ring-width) solid var(--ipai-component-focus-ring-color);
  outline-offset: var(--ipai-component-focus-ring-offset);
}
```

---

## 10. Badges

**Tokens Used:**
```
Background:       --ipai-component-badge-bg
Text:             --ipai-component-badge-fg
Radius:           --ipai-component-badge-radius
Padding:          --ipai-component-badge-padding-*
Font-size:        --ipai-component-badge-font-size
Font-weight:      --ipai-component-badge-font-weight
Danger variant:   --ipai-component-badge-danger-*
Success variant:  --ipai-component-badge-success-*
Warning variant:  --ipai-component-badge-warning-*
Info variant:     --ipai-component-badge-info-*
```

---

## Implementation Guide

### Module Structure

```
addons/ipai/ipai_theme_fluent2/
├── __init__.py
├── __manifest__.py
├── static/
│   └── src/
│       ├── css/
│       │   ├── fluent2.css     (Official @fluentui/tokens)
│       │   ├── tokens.css      (IPAI-prefixed tokens)
│       │   └── theme.css       (Odoo overrides)
│       └── js/
│           └── theme.js        (Dark mode toggle)
└── data/
    └── tokens.json             (Design tool import)
```

### Installation

1. Install the module:
   ```bash
   docker compose exec odoo-core odoo -d odoo_core -i ipai_theme_fluent2 --stop-after-init
   ```

2. Verify installation:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
   ```

### Dark Mode Support

Toggle dark mode via JavaScript:
```javascript
// Toggle between light/dark
IpaiThemeManager.toggleTheme();

// Set specific theme
IpaiThemeManager.applyTheme('dark');

// Get current theme
const theme = IpaiThemeManager.getCurrentTheme();

// Listen for theme changes
window.addEventListener('themechange', (e) => {
  console.log('Theme changed to:', e.detail.theme);
});
```

---

## Token Organization

All tokens follow the naming convention:
```
--ipai-{category}-{component}-{state}
```

**Examples:**
- `--ipai-color-brand-primary` - primary brand color
- `--ipai-component-button-primary-hover-bg` - primary button hover background
- `--ipai-typography-body-size` - body text size
- `--ipai-shadow-elevation-16` - elevation shadow level 16

---

## Known Limitations & Gaps

### Potential Overrides Needed

1. **Breadcrumbs**: Not explicitly in Fluent 2; use neutral colors
2. **Dropdowns**: Leverage input + card tokens
3. **Autocomplete**: Combine input + list-item tokens
4. **Tabs**: Use nav-item tokens with border variants
5. **Spinners/Loaders**: Use primary brand color with animations
6. **Popovers**: Use card tokens + shadow elevation

### Dark Mode Edge Cases

- Ensure sufficient contrast ratios (WCAG AA minimum 4.5:1)
- Test semantic color overlays on dark backgrounds
- Verify border visibility on dark surfaces

---

## References

- **Figma File**: Microsoft Fluent 2 Web (Community)
- **Fluent 2 Docs**: https://learn.microsoft.com/en-us/windows/apps/design/fluent2
- **CSS Variables MDN**: https://developer.mozilla.org/en-US/docs/Web/CSS/var()
- **Odoo 18 CE Docs**: https://www.odoo.com/documentation/18.0

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-01-13 | Initial token extraction from Figma |

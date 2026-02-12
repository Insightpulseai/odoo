# Google Antigravity Design System — Complete Design Tokens & Artifacts

**Extracted from**: `https://antigravity.google/`
**Date**: 2026-02-11
**Source**: Production CSS (`styles-7KLEMMT6.css`)

---

## 📐 Table of Contents

1. [Color Palette](#color-palette)
2. [Typography System](#typography-system)
3. [Spacing Scale](#spacing-scale)
4. [Border Radius (Shape Corners)](#border-radius-shape-corners)
5. [Grid System](#grid-system)
6. [Breakpoints](#breakpoints)
7. [Icon Sizes](#icon-sizes)
8. [Animation & Easing](#animation--easing)
9. [Theme Tokens (Semantic)](#theme-tokens-semantic)
10. [Component States](#component-states)
11. [Typography Classes](#typography-classes)
12. [Motion Principles](#motion-principles)

---

## 🎨 Color Palette

### Grey Scale

```css
--palette-grey-0: #FFFFFF;        /* Pure white */
--palette-grey-10: #F8F9FC;       /* Lightest grey */
--palette-grey-15: #F0F1F5;
--palette-grey-20: #EFF2F7;
--palette-grey-50: #E6EAF0;
--palette-grey-100: #E1E6EC;
--palette-grey-200: #CDD4DC;
--palette-grey-300: #B2BBC5;
--palette-grey-400: #B7BFD9;
--palette-grey-600: #AAB1CC4D;    /* With opacity */
--palette-grey-800: #45474D;
--palette-grey-900: #2F3034;
--palette-grey-1000: #212226;
--palette-grey-1100: #18191D;
--palette-grey-1200: #121317;     /* Darkest grey */
```

### Alpha Variants (RGB)

```css
--palette-grey-0-rgb: 255, 255, 255;
--palette-grey-50-rgb: 230, 234, 240;
--palette-grey-400-rgb: 183, 191, 217;
--palette-grey-600-rgb: 170, 177, 204;
--palette-grey-1000-rgb: 33, 34, 38;
--palette-grey-1200-rgb: 18, 19, 23;
```

### Accent Color

```css
--palette-blue-600: #3279F9;      /* Primary blue */
```

### Special States

```css
--palette-grey-1000-12: #dedfe2;  /* 12% opacity variant */
--palette-grey-50-20: #414347;    /* 20% opacity variant */
```

---

## 🔤 Typography System

### Font Families

**Primary**: `Google Sans Flex` (variable font)
- Weight range: 400-500
- Width range: 25%-150%
- Oblique range: 0deg-10deg
- Optical sizing: Auto

**Code/Monospace**: `Google Sans Code`
- Weight: 400
- Styles: Normal, Italic

**Icons**: `Google Symbols`
- Weight: 300
- Size: 24px base

### Typography Scale (Responsive)

| Scale | Size | Line Height | Letter Spacing | Optical Size |
|-------|------|-------------|----------------|--------------|
| **Landing Main** | 107px → 72px → 56px → 46px → 30px | 107px → 72.04px → 56.04px → 46.04px → 32.04px | -2.14px → -1.44px → -1.12px → -0.92px → -0.6px | 144 |
| **9XL** | 148px → 38px | 145.04px → 40.28px | -2.96px → -0.76px | 148 → 38 |
| **8XL** | 124px → 36px | 121.52px → 38.16px | -2.48px → -0.72px | 124 → 36 |
| **7XL** | 98px → 34px | 82.04px → 36.04px | -1.8px → -0.68px | 98 → 34 |
| **6XL** | 72px → 32px | 72px → 33.92px | -1.44px → -0.64px | 72 → 32 |
| **5XL** | 54px → 28px | 56.16px → 29.6px | -0.95px → -0.28px | 54 → 28 |
| **4XL** | 42px → 26px | 43.68px → 28.08px | -0.73px → -0.26px | 42 → 26 |
| **3XL** | 32px → 26px | 33.92px → 28.08px | -0.15px → -0.26px | 32 → 26 |
| **2XL** | 28px → 24px | 30.24px → 25.92px | -0.1px → -0.14px | 28 → 24 |
| **XL** | 24px → 22px | 25.92px → 24.64px | -0.07px → -0.13px | 24 → 22 |
| **LG** | 22px → 20px | 24.64px → 22.8px | -0.08px | 22 → 20 |
| **MD** | 20px → 18px | 26px → 23.4px | -0.05px → -0.07px | 20 → 18 |
| **Base** | 17.5px → 16px | 25.38px → 23px | 0.18px → 0.16px | 17.5 → 16 |
| **SM** | 14.5px → 16px | 21.02px → 23px | 0.16px | 14.5 → 16 |
| **XS** | 12.5px | 15.5px | 0.11px | 12.5 |

> **Note**: Typography scales are responsive with `→` showing breakpoint changes (Desktop → Tablet → Mobile)

### Font Variation Settings

```css
/* Headlines */
font-variation-settings: "wdth" 100, "opsz" 144;

/* Body text */
font-variation-settings: "wdth" 100, "opsz" 17.5;

/* Icons */
font-variation-settings: "FILL" 0, "wght" 300, "GRAD" 0, "ROND" 50, "opsz" 48;
```

---

## 📏 Spacing Scale

```css
--space-none: 0px;
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 36px;
--space-2xl: 48px;
--space-3xl: 60px;
--space-4xl: 80px;
--space-5xl: 88px;
--space-6xl: 120px;
--space-7xl: 180px;
```

### Spacing Ratio

- **XS → SM**: 2x jump (4px → 8px)
- **SM → MD**: 2x jump (8px → 16px)
- **MD → LG**: 1.5x jump (16px → 24px)
- **LG → XL**: 1.5x jump (24px → 36px)
- **XL → 2XL**: 1.33x jump (36px → 48px)
- **2XL → 3XL**: 1.25x jump (48px → 60px)
- **3XL → 4XL**: 1.33x jump (60px → 80px)
- **4XL → 5XL**: 1.1x jump (80px → 88px)
- **5XL → 6XL**: 1.36x jump (88px → 120px)
- **6XL → 7XL**: 1.5x jump (120px → 180px)

---

## ⭕ Border Radius (Shape Corners)

```css
--shape-corner-xs: 4px;
--shape-corner-sm: 8px;
--shape-corner-md: 16px;
--shape-corner-lg: 24px;
--shape-corner-xl: 36px;        /* 24px on mobile */
--shape-corner-2xl: 48px;
--shape-corner-rounded: 9999px; /* Fully rounded (pill) */
```

---

## 📱 Breakpoints

```css
--breakpoint-max: 1600px;   /* Container max width */
--breakpoint-xl: 1600px;
--breakpoint-lg: 1440px;
--breakpoint-md: 1024px;    /* Tablet */
--breakpoint-sm: 767px;     /* Mobile landscape */
--breakpoint-xs: 425px;     /* Mobile portrait */
```

### Responsive Behavior

| Breakpoint | Grid Columns | Grid Gutter | Page Margin |
|------------|--------------|-------------|-------------|
| **Desktop** (>1600px) | 12 | 64px | 72px |
| **Large** (≤1600px) | 12 | 48px | 72px |
| **Tablet** (≤1024px) | 8 | 40px | 40px |
| **Mobile** (≤767px) | 4 | 16px | 16px |

---

## 🔲 Grid System

```css
--grid-columns: 12;         /* 8 on tablet, 4 on mobile */
--grid-gutter: 64px;        /* 48px → 40px → 16px responsive */
--page-margin: 72px;        /* 40px on tablet, 16px on mobile */
```

### Grid Classes

- `.grid-container` — Max width container with page margins
- `.grid-row` — Flex container with negative gutter margins
- `.grid-col` — Column with gutter padding

**Column Sizing**:
- Mobile (XS): `.col-xs-1` to `.col-xs-4` (25%, 50%, 75%, 100%)
- Tablet (SM): `.col-sm-1` to `.col-sm-8` (12.5% increments)
- Desktop (MD): `.col-md-1` to `.col-md-12` (8.33% increments)

**Column Offsets** (Desktop only):
- `.col-md-offset-1` to `.col-md-offset-11`

---

## 🎯 Icon Sizes

```css
--icon-size-10xl: 120px;
--icon-size-9xl: 112px;
--icon-size-8xl: 104px;
--icon-size-7xl: 96px;
--icon-size-6xl: 88px;
--icon-size-5xl: 80px;
--icon-size-4xl: 72px;
--icon-size-3xl: 64px;
--icon-size-2xl: 56px;
--icon-size-xl: 48px;
--icon-size-lg: 36px;
--icon-size-md: 24px;
--icon-size-sm: 18px;
--icon-size-xs: 12px;
```

---

## ⚡ Animation & Easing

### Easing Curves

#### Ease-In (Accelerating)

```css
--ease-in-quad: cubic-bezier(.55, .085, .68, .53);
--ease-in-cubic: cubic-bezier(.55, .055, .675, .19);
--ease-in-quart: cubic-bezier(.895, .03, .685, .22);
--ease-in-quint: cubic-bezier(.755, .05, .855, .06);
--ease-in-expo: cubic-bezier(.95, .05, .795, .035);
--ease-in-circ: cubic-bezier(.6, .04, .98, .335);
```

#### Ease-Out (Decelerating)

```css
--ease-out-quad: cubic-bezier(.25, .46, .45, .94);
--ease-out-cubic: cubic-bezier(.215, .61, .355, 1);
--ease-out-quart: cubic-bezier(.165, .84, .44, 1);
--ease-out-quint: cubic-bezier(.23, 1, .32, 1);
--ease-out-expo: cubic-bezier(.19, 1, .22, 1);
--ease-out-circ: cubic-bezier(.075, .82, .165, 1);
```

#### Ease-In-Out (Smooth)

```css
--ease-in-out-quad: cubic-bezier(.455, .03, .515, .955);
--ease-in-out-cubic: cubic-bezier(.645, .045, .355, 1);
--ease-in-out-quart: cubic-bezier(.77, 0, .175, 1);
--ease-in-out-quint: cubic-bezier(.86, 0, .07, 1);
--ease-in-out-expo: cubic-bezier(1, 0, 0, 1);
--ease-in-out-circ: cubic-bezier(.785, .135, .15, .86);
```

#### Special Easing

```css
--ease-out-back: cubic-bezier(.34, 1.85, .64, 1); /* Overshoot effect */
```

### Recommended Usage

| Animation Type | Easing Curve | Use Case |
|----------------|--------------|----------|
| **Fade in** | `ease-out-quad` | Gentle appearance |
| **Slide in** | `ease-out-cubic` | Smooth entrance |
| **Bounce** | `ease-out-back` | Playful emphasis |
| **Modal open** | `ease-out-quart` | Dramatic reveal |
| **Scroll** | `ease-in-out-quad` | Smooth navigation |
| **Hover** | `ease-in-out-cubic` | Interactive feedback |
| **Exit** | `ease-in-quad` | Quick dismissal |

---

## 🎨 Theme Tokens (Semantic)

### Surface Colors

```css
--theme-surface-surface: var(--palette-grey-0);                  /* #FFFFFF */
--theme-surface-on-surface: var(--palette-grey-1200);            /* #121317 */
--theme-surface-on-surface-variant: var(--palette-grey-800);     /* #45474D */
--theme-surface-surface-container: var(--palette-grey-10);       /* #F8F9FC */
--theme-surface-surface-container-high: var(--palette-grey-20);  /* #EFF2F7 */
--theme-surface-surface-container-higher: var(--palette-grey-50);/* #E6EAF0 */
--theme-surface-surface-container-highest: var(--palette-grey-100);/* #E1E6EC */
```

### Inverse Surface Colors

```css
--theme-surface-inverse-surface: var(--palette-grey-1200);       /* #121317 */
--theme-surface-inverse-on-surface: var(--palette-grey-10);      /* #F8F9FC */
--theme-surface-inverse-on-surface-variant: var(--palette-grey-300);/* #B2BBC5 */
```

### Overlay Colors (Transparency)

```css
--theme-surface-overlay: rgba(var(--palette-grey-0-rgb), .95);          /* 95% white */
--theme-surface-overlay-low: rgba(var(--palette-grey-0-rgb), .12);      /* 12% white */
--theme-surface-overlay-high: rgba(var(--palette-grey-0-rgb), .24);     /* 24% white */
--theme-surface-overlay-higher: rgba(var(--palette-grey-0-rgb), .72);   /* 72% white */
--theme-surface-overlay-highest: rgba(var(--palette-grey-0-rgb), .95);  /* 95% white */
--theme-surface-transparent: rgba(var(--palette-grey-0-rgb), 0);        /* Fully transparent */
```

### Inverse Overlay Colors

```css
--theme-inverse-surface-overlay: rgba(var(--palette-grey-1200-rgb), .01);       /* 1% dark */
--theme-inverse-surface-overlay-high: rgba(var(--palette-grey-1200-rgb), .24);  /* 24% dark */
--theme-inverse-surface-overlay-higher: rgba(var(--palette-grey-1200-rgb), .72);/* 72% dark */
--theme-inverse-surface-overlay-highest: rgba(var(--palette-grey-1200-rgb), .95);/* 95% dark */
```

### Outline Colors

```css
--theme-outline: rgba(var(--palette-grey-1000-rgb), .12);        /* 12% opacity border */
--theme-outline-variant: rgba(var(--palette-grey-1000-rgb), .06);/* 6% opacity border */
--theme-inverse-outline: rgba(var(--palette-grey-50-rgb), .12);  /* Light mode outline */
--theme-inverse-outline-variant: rgba(var(--palette-grey-50-rgb), .06);
```

### Dividers

```css
--divider: var(--theme-outline-outline-variant);  /* 6% opacity */
```

---

## 🔘 Component States

### Button States — Primary

```css
--theme-button-states-primary-enabled: var(--theme-primary-primary);
--theme-button-states-primary-disabled: var(--palette-grey-10);
--theme-button-states-primary-hovered: var(--palette-grey-900);
--theme-button-states-primary-pressed: rgba(var(--palette-grey-50-rgb), .12);
--theme-button-states-primary-focused: rgba(var(--palette-grey-50-rgb), .2);
--theme-button-states-primary-on-disabled: rgba(var(--palette-grey-1000-rgb), .2);
```

### Button States — Secondary

```css
--theme-secondary-button: rgba(var(--palette-grey-400-rgb), .1);     /* 10% opacity */
--theme-button-secondary-hover: var(--palette-grey-15);
--theme-button-secondary-inverse-hover: rgba(var(--palette-grey-600-rgb), .3);
```

### Button States — Tonal

```css
--theme-button-states-tonal-enabled: var(--theme-tonal-tonal);
--theme-button-states-tonal-disabled: var(--palette-grey-10);
```

### Button States — Outlined

```css
--theme-button-states-outlined-enabled: var(--theme-outlined-outlined);
```

### Button States — Protected

```css
--theme-button-states-protected-enabled: var(--theme-protected-protected);
--theme-button-states-protected-hovered: var(--palette-grey-20);
--theme-button-states-protected-disabled: var(--palette-grey-100);
```

### Generic Interactive States

```css
--theme-button-states-disabled: var(--palette-grey-100);
--theme-button-states-on-disabled: #6A6A71;
--theme-button-states-hovered: rgba(var(--palette-grey-1000-rgb), .04);
--theme-button-states-pressed: rgba(var(--palette-grey-1000-rgb), .06);
--theme-button-states-focused: rgba(var(--palette-grey-1000-rgb), .12);
--theme-button-states-disabled-transparent: rgba(var(--palette-grey-50-rgb), 0);
```

### Navigation States

```css
--theme-nav-button: rgba(var(--palette-grey-400-rgb), .09);
--theme-nav-button-hover: rgba(var(--palette-grey-400-rgb), .2);
--nav-height: 52px;
```

### Text Link States

```css
--theme-text-link-states-enabled: var(--theme-surface-on-surface-variant);
--theme-text-link-states-hovered: var(--palette-grey-1000);
--theme-text-link-states-focused: var(--palette-grey-1100);
--theme-text-link-states-pressed: var(--palette-grey-1000);
--theme-text-link-states-disabled: #6A6A71;
```

---

## 📝 Typography Classes

### Heading Classes

```css
.landing-main {
  font-size: var(--landing-main-text-size);
  line-height: var(--landing-main-text-line-height);
  letter-spacing: var(--landing-main-text-letter-spacing);
  font-weight: 450;
  font-variation-settings: "wdth" 100, "opsz" 144;
}

.heading-00 { /* 9XL */ }
.heading-0  { /* 8XL */ }
.heading-1  { /* 7XL */ }
.heading-2  { /* 6XL */ }
.heading-3  { /* 5XL */ }
.heading-4  { /* 4XL */ }
.heading-5  { /* 3XL */ }
.heading-6  { /* 2XL */ }
.heading-7  { /* XL */ }
.heading-8  { /* LG */ }
.heading-9  { /* MD */ }
```

### Body & Utility Classes

```css
.body {
  font-size: var(--base-size);
  line-height: var(--base-line-height);
  letter-spacing: var(--base-letter-spacing);
  font-weight: 400;
  font-variation-settings: "wdth" 100, "opsz" 17.5;
}

.caption {
  font-size: var(--sm-size);
  line-height: var(--sm-line-height);
  letter-spacing: var(--sm-letter-spacing);
  font-weight: 400;
  font-variation-settings: "wdth" 100, "opsz" 15;
}

.small {
  font-size: var(--xs-size);
  line-height: var(--xs-line-height);
  letter-spacing: var(--xs-letter-spacing);
  font-weight: 450;
}

.call-to-action {
  font-size: var(--cta-size);
  line-height: var(--cta-line-height);
  letter-spacing: var(--cta-letter-spacing);
  font-weight: 450;
  font-variation-settings: "wdth" 100, "opsz" 17.5;
}

.call-to-action--nav {
  cursor: pointer;
  font-size: var(--cta-sm-size);
  line-height: var(--cta-sm-line-height);
  letter-spacing: var(--cta-sm-letter-spacing);
  font-weight: 450;
  font-variation-settings: "wdth" 100, "opsz" 14.5;
}
```

### Code & Monospace

```css
.special-text {
  color: var(--palette-grey-1200);
  font-family: Google Sans Code;
  font-size: 20px;
  font-style: normal;
  font-weight: 400;
  line-height: 28px;
  letter-spacing: -.08px;
}
```

---

## 🎬 Motion Principles

### Animation Patterns

#### Arrow Link Hover

```css
.arrow-link:not(.arrow-link-left):after {
  content: "keyboard_arrow_right";
  transition: .3s transform;
}

.arrow-link:not(.arrow-link-left):hover:after {
  transform: translate(50%);
}
```

#### Button Hover

```css
.carousel-nav button:hover {
  border-radius: var(--shape-corner-rounded);
  background: #eff0f3;
  backdrop-filter: blur(8px);
}
```

#### Backdrop Blur

```css
:root {
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.video-control-button {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
```

### Micro-Interaction Timings

| Interaction | Duration | Easing | Use Case |
|-------------|----------|--------|----------|
| **Link hover** | 0.3s | `transform` | Arrow slide animation |
| **Opacity** | 0.2s | Linear | Fade in/out |
| **Background** | 0.3s | `ease-out-cubic` | Color transitions |

---

## 🔧 Utility Classes

### Visibility

```css
.hidden-sm    /* Hidden on tablet (≤1024px) */
.hidden-xs    /* Hidden on mobile (≤767px) */
.no-scroll    /* overflow: hidden */
```

### Special Effects

```css
.smooth-scroll-wrapper {
  min-height: 100vh;
}

.second-line {
  color: var(--palette-grey-800);
}
```

---

## 📦 Design Token Export

### JSON Format

```json
{
  "colors": {
    "grey": {
      "0": "#FFFFFF",
      "10": "#F8F9FC",
      "1200": "#121317"
    },
    "blue": {
      "600": "#3279F9"
    }
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px"
  },
  "borderRadius": {
    "xs": "4px",
    "rounded": "9999px"
  },
  "typography": {
    "fontFamily": {
      "sans": "Google Sans Flex",
      "code": "Google Sans Code"
    },
    "fontSize": {
      "base": "17.5px",
      "xl": "24px"
    }
  },
  "animation": {
    "easeOutQuad": "cubic-bezier(.25, .46, .45, .94)",
    "easeOutBack": "cubic-bezier(.34, 1.85, .64, 1)"
  }
}
```

---

## 🎯 Key Design Principles

1. **Variable Fonts**: Google Sans Flex with optical sizing (`opsz`) and width (`wdth`) variation
2. **Responsive Typography**: Font sizes scale down across 5 breakpoints (Desktop → XL → MD → SM → XS)
3. **Semantic Tokens**: Theme tokens reference palette tokens for easy theming
4. **Layered Transparency**: Overlay system uses RGBA with varying opacity (1%, 12%, 24%, 72%, 95%)
5. **Rounded Corners**: 8px base unit with 2x scaling (8px → 16px → 24px → 36px → 48px)
6. **Icon System**: Google Symbols with variable fill, weight, grade, and rounding
7. **Easing Variety**: 22 easing curves for nuanced motion (quad, cubic, quart, quint, expo, circ, back)
8. **Grid Flexibility**: 12-column desktop, 8-column tablet, 4-column mobile
9. **Backdrop Blur**: 8px default, 16px for emphasis (video controls)
10. **State Management**: Comprehensive button states (enabled, hovered, pressed, focused, disabled)

---

## 📊 Usage Statistics

- **Color Palette**: 22 grey shades + 1 accent blue
- **Typography Scales**: 14 sizes (9XL → XS) with 5 responsive breakpoints
- **Spacing Tokens**: 11 values (0px → 180px)
- **Border Radius**: 7 values (4px → 9999px)
- **Easing Curves**: 22 cubic-bezier functions
- **Icon Sizes**: 14 sizes (12px → 120px)
- **Breakpoints**: 5 responsive tiers
- **Grid Columns**: 12 (desktop) → 8 (tablet) → 4 (mobile)

---

**End of Design System Documentation**
**Version**: 1.0.0
**Last Updated**: 2026-02-11

import {
  Theme,
  BrandVariants,
  createLightTheme,
  createDarkTheme,
} from "@fluentui/react-components";

/**
 * Unified Fluent 2 Theme System
 *
 * Three theme families synced with Odoo/IPAI design tokens:
 * - suqi: TBWA yellow brand (light mode default)
 * - system: Copilot-style blue (neutral enterprise)
 * - tbwa-dark: TBWA yellow + cyan on dark backgrounds
 */

export type UiTheme = "suqi" | "system" | "tbwa-dark";
export type Scheme = "light" | "dark";

/* ═══════════════════════════════════════════════════════════════════════════
   Brand Ramps - 16-step color scales for Fluent theming
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * SUQI / TBWA Yellow Brand
 * Primary: #FFCC00 (Suqi Gold)
 */
const SUQI_BRAND: BrandVariants = {
  10: "#221a00",
  20: "#3a2b00",
  30: "#554000",
  40: "#705500",
  50: "#8a6900",
  60: "#a57e00",
  70: "#bf9200",
  80: "#d9a700",
  90: "#f3bb00",
  100: "#ffcc00", // Primary
  110: "#ffd633",
  120: "#ffe066",
  130: "#ffea99",
  140: "#fff3cc",
  150: "#fff8e6",
  160: "#fffcf5",
};

/**
 * System / Copilot Blue Brand
 * Primary: #2563EB (Copilot Blue)
 */
const SYSTEM_BRAND: BrandVariants = {
  10: "#08142c",
  20: "#0b1c3a",
  30: "#0f2750",
  40: "#123166",
  50: "#153b7d",
  60: "#184493",
  70: "#1b4ea9",
  80: "#1e58c0",
  90: "#2061d6",
  100: "#2563eb", // Primary
  110: "#4a7df0",
  120: "#6f97f4",
  130: "#95b1f7",
  140: "#bacbf9",
  150: "#dfe5fc",
  160: "#f4f7fe",
};

/**
 * TBWA Dark uses the same yellow brand as Suqi
 * but with dark mode treatment + cyan accents
 */
const TBWA_DARK_BRAND: BrandVariants = SUQI_BRAND;

/* ═══════════════════════════════════════════════════════════════════════════
   Base Theme Generation
   ═══════════════════════════════════════════════════════════════════════════ */

const suqiLightBase = createLightTheme(SUQI_BRAND);
const suqiDarkBase = createDarkTheme(SUQI_BRAND);

const systemLightBase = createLightTheme(SYSTEM_BRAND);
const systemDarkBase = createDarkTheme(SYSTEM_BRAND);

const tbwaDarkLightBase = createLightTheme(TBWA_DARK_BRAND);
const tbwaDarkDarkBase = createDarkTheme(TBWA_DARK_BRAND);

/* ═══════════════════════════════════════════════════════════════════════════
   CSS Variable Alignment
   Sync Fluent tokens with IPAI/Odoo CSS custom properties
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Apply CSS variable alignment so Fluent + Tailwind + Odoo
 * all share the same visual language.
 */
function withCssVarAlignment(base: Theme): Theme {
  return {
    ...base,
    // Backgrounds
    colorNeutralBackground1: "var(--ipai-bg, #ffffff)",
    colorNeutralBackground2: "var(--ipai-surface, #f8fafc)",
    colorNeutralBackground3: "var(--ipai-surface-muted, #f1f5f9)",
    colorNeutralBackground4: "var(--ipai-surface-elevated, #ffffff)",
    colorSubtleBackground: "var(--ipai-surface-muted, #f1f5f9)",
    colorSubtleBackgroundHover: "var(--ipai-surface, #f8fafc)",
    colorSubtleBackgroundPressed: "var(--ipai-surface-muted, #f1f5f9)",

    // Borders
    colorNeutralStroke1: "var(--ipai-border, #e2e8f0)",
    colorNeutralStroke2: "var(--ipai-border-muted, #f1f5f9)",
    colorNeutralStrokeAccessible: "var(--ipai-border, #e2e8f0)",

    // Text
    colorNeutralForeground1: "var(--ipai-text-primary, #0f172a)",
    colorNeutralForeground2: "var(--ipai-text-muted, #64748b)",
    colorNeutralForeground3: "var(--ipai-text-subtle, #94a3b8)",
    colorNeutralForegroundDisabled: "var(--ipai-text-disabled, #cbd5e1)",

    // Brand colors
    colorBrandBackground: "var(--ipai-accent-primary)",
    colorBrandBackgroundHover: "var(--ipai-accent-hover)",
    colorBrandBackgroundPressed: "var(--ipai-accent-active)",
    colorBrandForeground1: "var(--ipai-accent-primary)",
    colorBrandForeground2: "var(--ipai-accent-hover)",
    colorBrandStroke1: "var(--ipai-accent-primary)",
    colorBrandStroke2: "var(--ipai-accent-hover)",

    // Subtle brand surfaces
    colorBrandBackground2:
      "color-mix(in srgb, var(--ipai-accent-primary) 8%, transparent)",
    colorBrandBackgroundInverted: "var(--ipai-nav-active-bg, #fff3cc)",

    // Compound brand (for buttons, etc.)
    colorCompoundBrandBackground: "var(--ipai-accent-primary)",
    colorCompoundBrandBackgroundHover: "var(--ipai-accent-hover)",
    colorCompoundBrandBackgroundPressed: "var(--ipai-accent-active)",
    colorCompoundBrandForeground1: "var(--ipai-accent-primary)",
    colorCompoundBrandForeground1Hover: "var(--ipai-accent-hover)",
    colorCompoundBrandForeground1Pressed: "var(--ipai-accent-active)",
    colorCompoundBrandStroke: "var(--ipai-accent-primary)",
    colorCompoundBrandStrokeHover: "var(--ipai-accent-hover)",
    colorCompoundBrandStrokePressed: "var(--ipai-accent-active)",
  } as Theme;
}

/* ═══════════════════════════════════════════════════════════════════════════
   Exported Themes
   ═══════════════════════════════════════════════════════════════════════════ */

export const fluentThemes: Record<UiTheme, Record<Scheme, Theme>> = {
  suqi: {
    light: withCssVarAlignment(suqiLightBase),
    dark: withCssVarAlignment(suqiDarkBase),
  },
  system: {
    light: withCssVarAlignment(systemLightBase),
    dark: withCssVarAlignment(systemDarkBase),
  },
  "tbwa-dark": {
    light: withCssVarAlignment(tbwaDarkLightBase),
    dark: withCssVarAlignment(tbwaDarkDarkBase),
  },
};

/**
 * Get the correct Fluent theme for a given UI theme and color scheme.
 */
export function getFluentTheme(theme: UiTheme, scheme: Scheme): Theme {
  return fluentThemes[theme][scheme];
}

/**
 * Determine the default color scheme for a given UI theme.
 * tbwa-dark defaults to dark scheme, others to light.
 */
export function getDefaultScheme(theme: UiTheme): Scheme {
  return theme === "tbwa-dark" ? "dark" : "light";
}

/**
 * Legacy export for backwards compatibility
 */
export { suqiLightBase as tbwaLightTheme, suqiDarkBase as tbwaDarkTheme };
export const tbwaTheme = withCssVarAlignment(suqiLightBase);

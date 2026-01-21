/**
 * Tableau UI Kit Design Tokens - Tailwind CSS Preset
 * ===================================================
 * Source: Figma Tableau UI Kit (Community)
 * Generated: 2026-01-21
 *
 * Usage in tailwind.config.ts:
 * ```ts
 * import tableauPreset from '@ipai/design-tokens/tailwind-tableau.preset';
 *
 * export default {
 *   presets: [tableauPreset],
 *   // ... your config
 * }
 * ```
 */

/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      colors: {
        // Tableau Classic 20 Palette
        "tableau-classic": {
          1: "#1F77B4",
          2: "#FF7F0E",
          3: "#2CA02C",
          4: "#D62728",
          5: "#9467BD",
          6: "#8C564B",
          7: "#E377C2",
          8: "#7F7F7F",
          9: "#BCBD22",
          10: "#17BECF",
        },

        // Color Blind Safe Palette
        "tableau-cb": {
          1: "#EDC948",
          2: "#79706E",
          3: "#D4A6C8",
          4: "#FFB67D",
          5: "#499894",
          6: "#BAB0AC",
          7: "#9D7660",
          8: "#59A14F",
          9: "#86BCB6",
          10: "#4E79A7",
          11: "#F28E2B",
          12: "#B07AA1",
          13: "#E15759",
          14: "#FF9DA7",
          15: "#76B7B2",
          16: "#9C755F",
        },

        // Chart Series (alias to Classic 20)
        "chart-series": {
          1: "#1F77B4",
          2: "#FF7F0E",
          3: "#2CA02C",
          4: "#D62728",
          5: "#9467BD",
          6: "#8C564B",
          7: "#E377C2",
          8: "#7F7F7F",
          9: "#BCBD22",
          10: "#17BECF",
        },

        // Semantic Status Colors
        "tableau-success": "#59A14F",
        "tableau-warning": "#F28E2B",
        "tableau-error": "#E15759",
        "tableau-info": "#4E79A7",
        "tableau-neutral": "#79706E",

        // Background Colors
        "tableau-bg": {
          DEFAULT: "#FFFFFF",
          elevated: "#F8F8F8",
        },

        // Surface Colors
        "tableau-surface": {
          DEFAULT: "#FFFFFF",
          alt: "#F8F8F8",
        },

        // Text Colors
        "tableau-text": {
          DEFAULT: "#000000",
          primary: "#000000",
          secondary: "#666666",
          disabled: "#CCCCCC",
          inverse: "#FFFFFF",
        },

        // Border Colors
        "tableau-border": {
          DEFAULT: "#D0D0D0",
          light: "#E8E8E8",
          dark: "#999999",
        },

        // Chart Diverging
        "chart-negative": "#1F77B4",
        "chart-neutral": "#FFFFFF",
        "chart-positive": "#8C564B",
      },

      fontSize: {
        "tableau-xs": ["12px", { lineHeight: "1.4" }],
        "tableau-sm": ["14px", { lineHeight: "1.5" }],
        "tableau-base": ["16px", { lineHeight: "1.5" }],
        "tableau-lg": ["18px", { lineHeight: "1.5" }],
        "tableau-xl": ["20px", { lineHeight: "1.4" }],
        "tableau-2xl": ["24px", { lineHeight: "1.3" }],
        "tableau-3xl": ["32px", { lineHeight: "1.2" }],
      },

      fontFamily: {
        "tableau-primary": ["Roboto", "system-ui", "-apple-system", "sans-serif"],
        "tableau-mono": ["Roboto Mono", "monospace"],
      },

      fontWeight: {
        "tableau-light": "300",
        "tableau-regular": "400",
        "tableau-medium": "500",
        "tableau-semibold": "600",
        "tableau-bold": "700",
      },

      lineHeight: {
        "tableau-tight": "1.2",
        "tableau-normal": "1.5",
        "tableau-relaxed": "1.75",
        "tableau-loose": "2",
      },

      letterSpacing: {
        "tableau-tight": "-0.02em",
        "tableau-normal": "0",
        "tableau-wide": "0.02em",
        "tableau-wider": "0.04em",
      },

      spacing: {
        "tableau-xs": "4px",
        "tableau-sm": "8px",
        "tableau-md": "16px",
        "tableau-lg": "24px",
        "tableau-xl": "32px",
        "tableau-2xl": "48px",
      },

      borderRadius: {
        "tableau-none": "0",
        "tableau-sm": "2px",
        "tableau-md": "4px",
        "tableau-lg": "8px",
        "tableau-xl": "12px",
        "tableau-full": "9999px",
      },

      boxShadow: {
        "tableau-sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
        "tableau-md": "0 4px 6px rgba(0, 0, 0, 0.1)",
        "tableau-lg": "0 10px 15px rgba(0, 0, 0, 0.1)",
        "tableau-xl": "0 20px 25px rgba(0, 0, 0, 0.1)",
      },

      opacity: {
        "tableau-disabled": "0.5",
        "tableau-hover": "0.8",
        "tableau-focus": "0.9",
      },

      screens: {
        "tableau-sm": "640px",
        "tableau-md": "768px",
        "tableau-lg": "1024px",
        "tableau-xl": "1280px",
        "tableau-2xl": "1536px",
      },

      transitionDuration: {
        "tableau-fast": "100ms",
        "tableau-base": "200ms",
        "tableau-slow": "300ms",
        "tableau-slower": "500ms",
      },

      transitionTimingFunction: {
        "tableau-ease-in": "cubic-bezier(0.4, 0, 1, 1)",
        "tableau-ease-out": "cubic-bezier(0, 0, 0.2, 1)",
        "tableau-ease-in-out": "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
};

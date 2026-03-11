/**
 * IPAI Design Tokens - Tailwind CSS Preset
 *
 * Usage in tailwind.config.js:
 *   import preset from "@ipai/design-tokens/tailwind.preset";
 *   export default { presets: [preset], ... }
 */

export default {
  theme: {
    extend: {
      colors: {
        ipai: {
          bg: "var(--ipai-bg)",
          surface: "var(--ipai-surface)",
          surface2: "var(--ipai-surface-2)",
          border: "var(--ipai-border)",
          "border-strong": "var(--ipai-border-strong)",
          text: "var(--ipai-text)",
          muted: "var(--ipai-text-muted)",
          faint: "var(--ipai-text-faint)",
          primary: "var(--ipai-primary)",
          primary2: "var(--ipai-primary-2)",
          "primary-dark": "var(--ipai-primary-dark)",
          danger: "var(--ipai-danger)",
          success: "var(--ipai-success)",
          info: "var(--ipai-info)",
          warning: "var(--ipai-warning)"
        }
      },
      borderRadius: {
        ipai: "var(--ipai-radius)",
        "ipai-sm": "var(--ipai-radius-sm)",
        "ipai-lg": "var(--ipai-radius-lg)",
        "ipai-full": "var(--ipai-radius-full)"
      },
      boxShadow: {
        ipai: "var(--ipai-shadow)",
        "ipai-soft": "var(--ipai-shadow-soft)",
        "ipai-lg": "var(--ipai-shadow-lg)",
        "ipai-ring": "var(--ipai-ring)"
      },
      spacing: {
        "ipai-gap": "var(--ipai-gap)",
        "ipai-gap-sm": "var(--ipai-gap-sm)",
        "ipai-gap-lg": "var(--ipai-gap-lg)"
      },
      fontFamily: {
        ipai: ["var(--ipai-font)"],
        "ipai-mono": ["var(--ipai-font-mono)"]
      },
      backgroundColor: {
        "ipai-input": "var(--ipai-input-bg)",
        "ipai-input-2": "var(--ipai-input-bg-2)"
      }
    }
  }
};

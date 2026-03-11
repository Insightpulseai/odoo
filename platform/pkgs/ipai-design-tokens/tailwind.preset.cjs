/**
 * IPAI Design Tokens - Tailwind CSS Preset
 * Auto-generated from tokens/source/tokens.json
 * DO NOT EDIT MANUALLY - Run 'pnpm generate:tokens' to regenerate
 */
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: "#E7EDF5",
        surface: "#FFFFFF",
        canvas: "#F5F8FA",
        primary: "#0F2A44",
        "primary-deep": "#0A1E33",
        "primary-hover": "#1A3A5A",
        accent: {
          green: "#7BC043",
          "green-hover": "#6AA638",
          teal: "#64B9CA",
          "teal-hover": "#52A7B8",
          amber: "#F6C445",
          "amber-hover": "#E5B334",
        },
        semantic: {
          success: "#7BC043",
          warning: "#F6C445",
          error: "#E74C3C",
          info: "#64B9CA",
        },
        border: "#D1DCE5",
        "border-light": "#E7EDF5",
        "border-dark": "#B8C7D6",
        text: {
          primary: "#0B1F33",
          secondary: "#4A5F7A",
          tertiary: "#7A8FA5",
          "on-accent": "#FFFFFF",
        },
      },
      spacing: {
        gap: "16px",
        "gap-sm": "12px",
        "gap-lg": "24px",
      },
      borderRadius: {
        DEFAULT: "8px",
        sm: "4px",
        lg: "12px",
        full: "9999px",
      },
      boxShadow: {
        DEFAULT: "0 4px 12px rgba(11, 31, 51, 0.08)",
        soft: "0 2px 8px rgba(11, 31, 51, 0.06)",
        lg: "0 8px 24px rgba(11, 31, 51, 0.12)",
        inner: "inset 0 2px 4px rgba(11, 31, 51, 0.06)",
      },
      fontFamily: {
        sans: ["-apple-system","BlinkMacSystemFont","'Segoe UI'","Roboto","'Helvetica Neue'","Arial","sans-serif"],
        mono: ["'SF Mono'","Monaco","'Cascadia Code'","'Roboto Mono'","Consolas","'Courier New'","monospace"],
      },
    },
  },
};

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
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
        },
      },
      borderRadius: {
        ipai: "var(--ipai-radius)",
        "ipai-sm": "var(--ipai-radius-sm)",
      },
      boxShadow: {
        ipai: "var(--ipai-shadow)",
        "ipai-soft": "var(--ipai-shadow-soft)",
      },
    },
  },
  plugins: [],
};

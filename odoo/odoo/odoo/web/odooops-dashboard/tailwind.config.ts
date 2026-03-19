import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Sync with Odoo CSS vars
        primary: "#3b82f6",
        odooops: {
          bg: "#ffffff",
          text: "#1f2937",
          border: "#e5e7eb",
        },
      },
    },
  },
  plugins: [],
};
export default config;

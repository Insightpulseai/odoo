import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Vite configuration for building the React + Fluent UI panel as an IIFE bundle.
 *
 * The output is a single IIFE file that:
 * - Exposes window.IPAI_AI_UI.mount(element, options)
 * - Can be loaded via Odoo's web.assets_backend
 * - Contains all dependencies (React, Fluent UI) bundled together
 */
export default defineConfig({
  plugins: [react()],
  build: {
    lib: {
      entry: "src/main.tsx",
      name: "IPAI_AI_UI",
      formats: ["iife"],
      fileName: () => "ipai_ai_ui.iife.js",
    },
    outDir: "dist",
    sourcemap: false,
    cssCodeSplit: false,
    // Inline all dependencies
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
  },
  define: {
    "process.env.NODE_ENV": JSON.stringify("production"),
  },
});

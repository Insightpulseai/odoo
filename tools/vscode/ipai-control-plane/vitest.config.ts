import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
    exclude: ["src/test/**", "node_modules/**"],
    setupFiles: ["src/test/setup.ts"],
    reporters: ["default", "junit"],
    outputFile: {
      junit: "./test-results/junit.xml"
    },
    coverage: {
      reporter: ["text", "json", "html"],
      exclude: [
        "node_modules/**",
        "dist/**",
        "src/test/**",
        "**/*.test.ts",
        "**/*.config.ts"
      ]
    }
  }
});

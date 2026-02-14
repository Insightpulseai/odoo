"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const config_1 = require("vitest/config");
exports.default = (0, config_1.defineConfig)({
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
//# sourceMappingURL=vitest.config.js.map
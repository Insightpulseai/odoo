/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * IPAI Design System Boot Service
 *
 * Initializes the platform-wide design system by adding stable root classes
 * that allow all Apps SDK UI styles to be properly scoped.
 */
export const ipaiDesignSystemBoot = {
    dependencies: [],

    start(env) {
        // Add stable root class for design system scoping
        document.documentElement.classList.add("ipai-appsdk");

        // Add platform identifier for analytics/debugging
        document.documentElement.dataset.ipaiPlatform = "apps-sdk-ui";
        document.documentElement.dataset.ipaiVersion = "18.0.1.0.0";

        // Log initialization in development mode
        if (env.debug) {
            console.log(
                "%c[IPAI Design System] Apps SDK UI initialized",
                "color: #f7d046; font-weight: bold;"
            );
        }
    },
};

registry
    .category("services")
    .add("ipai_design_system_apps_sdk.boot", ipaiDesignSystemBoot);

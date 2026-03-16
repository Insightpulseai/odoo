{
    "name": "IPAI Design System (SSOT)",
    "version": "19.0.1.0.0",
    "category": "Theme/Backend",
    "summary": "Single Source of Truth for all IPAI UI/UX: tokens, components, and brand styling",
    "description": """
IPAI Design System (Single Source of Truth)
============================================

This is the **ONLY** design system module for IPAI. All other theme/styling
modules should depend on this or be deprecated.

CE + OCA Compliant:
-------------------
* No Enterprise dependencies
* No IAP requirements
* Self-hosted compatible

Features:
---------
* Complete design token system (colors, spacing, typography, radius, shadows)
* TBWA brand color palette (light theme)
* Reusable component classes (buttons, cards, inputs, badges, etc.)
* Utility classes (flex, spacing, visibility, cursor)
* Animation helpers
* Scoped styling via .ipai-appsdk root class (safe for legacy screens)
* Backend and frontend asset bundles

Design Token Categories:
------------------------
* Brand: --brand-yellow, --brand-black, --brand-white
* Accents: --accent-brown-gold, --accent-charcoal, --accent-sand
* Status: --status-success, --status-info, --status-warning, --status-danger
* Semantic: --ipai-bg, --ipai-surface, --ipai-text, --ipai-accent, --ipai-border
* Spacing: --ipai-space-xs through --ipai-space-2xl
* Radius: --ipai-radius-sm through --ipai-radius-full
* Typography: --ipai-font-sans, --ipai-font-mono

Component Classes:
------------------
* .ipai-btn-primary, .ipai-btn-secondary, .ipai-btn-ghost, .ipai-btn-dark
* .ipai-card, .ipai-card-elevated
* .ipai-input, .ipai-textarea, .ipai-select
* .ipai-badge, .ipai-badge-success, .ipai-badge-warning, .ipai-badge-error
* .ipai-header-bar, .ipai-tat-bar
* .ipai-heading-xl through .ipai-heading-sm
* .ipai-text-body, .ipai-text-secondary, .ipai-text-muted

Usage:
------
1. Install this module (auto_install=False for explicit control)
2. Wrap IPAI app content with <div class="ipai-appsdk"><div class="ipai-app">
3. Use component classes for consistent styling across all IPAI apps
4. Reference design tokens via CSS custom properties (var(--ipai-*))
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "ipai_design_system_apps_sdk/static/src/vendor/apps-sdk-ui-platform.css",
            "ipai_design_system_apps_sdk/static/src/scss/platform_overrides.scss",
            "ipai_design_system_apps_sdk/static/src/js/platform_boot.js",
        ],
        "web.assets_frontend": [
            "ipai_design_system_apps_sdk/static/src/vendor/apps-sdk-ui-platform.css",
            "ipai_design_system_apps_sdk/static/src/scss/platform_overrides.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}

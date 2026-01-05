# Odoo Developer Tools (Debug Mode) — How we use it in IPAI

## 1. Official Odoo Docs Map (The "Catalogue")

* **[Developer mode (Debug mode)](https://www.odoo.com/documentation/19.0/applications/general/developer_mode.html)**: What it unlocks + how to enable via UI or URL.
* **[Developer Docs Hub](https://www.odoo.com/documentation/18.0/th/developer.html)**: Top-level index for backend/frontend/reference/tutorials.
* **[Frontend Assets](https://www.odoo.com/documentation/18.0/th/developer/reference/frontend/assets.html)**: What `debug=assets` actually does (no minify/concat).
* **[Backend Actions](https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html)**: Server Actions reference.
* **[Unit Tests](https://www.odoo.com/documentation/18.0/th/developer/tutorials/unit_tests.html)**: Modular testing structure.

## 2. Modes & Activation

### Enablement
* **UI**: Settings → Developer Tools → Click "Activate...".
* **URL**: Append `?debug=...` or `?debug=assets` to your web URL (e.g., `/web?debug=1`).

### The 3 Key Modes

#### A) `debug=1` (Standard Developer Mode)
**Use when**: You need technical menus + model/view introspection.
* **Unlocks**: Technical Menu, View/Field/Menu inspection, record rules debugging.
* **URL**: `https://erp.insightpulseai.net/odoo/web?debug=1`

#### B) `debug=assets` (Developer Mode with Assets)
**Use when**: Debugging **frontend/OWL/JS/SCSS**.
* **Behavior**: Serves assets unminified and unbundled. Crucial for tracing console errors to the exact file/line in custom modules (`ipai_platform_theme`, `chatgpt_ipai_ai_studio`, etc.).
* **URL**: `https://erp.insightpulseai.net/odoo/web?debug=assets`

#### C) `debug=tests` (Developer Mode with Tests Assets)
**Use when**: Loading test bundles for dev+test scenarios.
* **Behavior**: Includes JS test assets (QUnit tests, test helpers).
* **URL**: `https://erp.insightpulseai.net/odoo/web?debug=tests`

## 3. IPAI Implementation Playbook

### 3.1 Verify Installation/Upgrades
Use **Developer Mode (`debug=1`)** to inspect runtime objects:
1.  **Settings → Technical → User Interface**: Confirm XML views loaded without errors.
2.  **Settings → Technical → Database Structure**: Confirm Models/Fields exist in the registry.
*   *Tip*: Always use the CLI install runner for strictly safe `-i` / `-u` operations.

### 3.2 Debug UI (WorkOS / Theme / Ask AI)
Use **Assets Mode (`debug=assets`)**:
*   For OWL components (AI Studio widget, Copilot panel).
*   For SCSS token issues (Theme colors).
*   **Workflow**: Enable assets mode -> Hard Refresh -> Open Console -> Trace error.

### 3.3 Test Verification
Use **Tests Mode (`debug=tests`)**:
*   For running frontend test tours.
*   For validating module-specific JS test logic.

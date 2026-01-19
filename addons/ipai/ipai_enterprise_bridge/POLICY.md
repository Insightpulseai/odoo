# IPAI Enterprise Bridge Policy

**Status:** Active
**Enforcement:** CI/CD + Architect Review

## 1. Core Mandate
This repository Strictly adheres to the **"CE -> OCA -> Bridge"** hierarchy for all feature implementations. We do NOT replicate Odoo Enterprise (EE) features unless absolutely necessary, and when we do, we do it in this specific order:

1.  **Odoo 18 CE Native**: Use what exists (e.g., standard unique constraints, basic views).
2.  **OCA Modules**: Verify if an OCA port exists for v18.0.
3.  **Bridge (Overlay)**: If gaps remain, implement the *minimum viable glue* in `ipai_enterprise_bridge`.

**Prohibited**: Creating new standalone custom module directories for EE replacement features (e.g., `ipai_studio_replacement`, `ipai_approvals_custom`) is forbidden.

## 2. What belongs in `ipai_enterprise_bridge`?
This module is a "monolith of glue". It is designed to be messy but consolidated.

*   **Allowed**:
    *   Mixins that bridge two OCA modules (e.g., `base_tier_validation` on `hr.expense`).
    *   View inheritance (`inherit_id`) to expose OCA menus.
    *   Simple fields added to standard models (`res.partner`, `product.template`) that don't warrant a separate module.
    *   AI Integration points (Bridge -> AI SDK).
*   **Forbidden**:
    *   Redefining complex business logic already in OCA.
    *   Code duplication from EE.
    *   Hardcoded secrets.

## 3. Workflow for Requesting Replacements
To request a new feature that matches an EE capability:

1.  Run `./scripts/ee_replace_request.sh EE_AREA="MyFeature"`
2.  Review the output recommendation.
3.  Update `spec/ipai_enterprise_bridge/ee-replacement-matrix.yaml` if the area is new.
4.  Implement in `addons/ipai/ipai_enterprise_bridge` ONLY if matrix says `bridge_required: true`.
5.  Submit PR.

## 4. CI Enforcement
*   **`scripts/validate_ee_replacements.py`**: Ensures the matrix is valid.
*   **`scripts/check_addon_allowlist.py`**: Ensures no unauthorized directories appear in `addons/ipai/`.

## 5. View Conventions
Odoo 18 CE uses `<list>` instead of `<tree>`. Ensure all new XML views follow this standard.

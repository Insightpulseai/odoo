# Prototype Modules

These modules are in development/alpha state and not ready for production.

## Modules

- `ipai_fluent_web_365_copilot`: SAP Joule / Microsoft 365 Copilot-style AI assistant (Alpha)
- `ipai_aiux_chat`: AI chat widget scaffold
- `ipai_theme_aiux`: AI UX theme scaffold

## Usage

These modules are NOT loaded in production images. To develop on them:

```bash
# Add to addons path during development
docker run ... -v $(pwd)/prototypes:/mnt/prototypes \
  -e ODOO_ADDONS_PATH=/mnt/addons/ipai,/mnt/addons/oca,/mnt/prototypes
```

## Promotion to Production

When a prototype is ready:

1. Move to `addons/ipai/`
2. Update manifest: remove `development_status: Alpha`
3. Add tests
4. Update dependencies

---

*Created: 2026-01-28*
*Deprecation Plan: docs/DEPRECATION_PLAN.md*

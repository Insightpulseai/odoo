# Architecture Diagram Exports

This directory contains exported architecture diagrams in SVG and PNG formats.

## Regenerating Exports

```bash
./scripts/export_architecture_diagrams.sh
```

## Expected Files

| Source | SVG | PNG |
|--------|-----|-----|
| `ipai_idp_architecture.drawio` | `ipai_idp_architecture.svg` | `ipai_idp_architecture.png` |
| `ipai_idp_pdf_processing.drawio` | `ipai_idp_pdf_processing.svg` | `ipai_idp_pdf_processing.png` |
| `ipai_idp_multi_agent_workflow.drawio` | `ipai_idp_multi_agent_workflow.svg` | `ipai_idp_multi_agent_workflow.png` |
| `ipai_idp_build_deploy_custom_models.drawio` | `ipai_idp_build_deploy_custom_models.svg` | `ipai_idp_build_deploy_custom_models.png` |

## Export Settings

- **SVG**: Default Draw.io export settings
- **PNG**: 2x scale for high-resolution output

## CI Enforcement

Exports are verified on every push/PR via `.github/workflows/architecture-diagrams.yml`.
If exports drift from source diagrams, CI will fail.

## Manifest

`MANIFEST.json` contains SHA256 hashes of all exports for integrity verification.

### feat: add ipai_finance_ppm + ipai_ops_connector and parity docs

This PR introduces two new Odoo modules and supporting documentation:

- **ipai_finance_ppm**: Adds finance project portfolio management features.
- **ipai_ops_connector**: Adds operational connector logic.
- Adds new documentation under `docs/parity`, `docs/policy`, and `docs/stack` for module parity, policy, and stack baseline.

**Summary of changes:**
- New module directories and manifests
- Python and XML files for models, views, wizards, and security
- Documentation for platform components, bridge matrix, module completeness, and stack baseline

**Motivation:**
- Enhance finance and operations integration
- Improve documentation and compliance

**Testing:**
- Modules pass manifest, Python, and XML syntax checks
- All referenced data files exist

---

Please review and merge. This PR is required to unblock further integration and deployment steps.
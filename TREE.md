# 📁 Repository Structure

> Auto-generated on every commit via GitHub Actions

```
odoo-ce/
├── .github/
│   └── workflows/
│       ├── auto-sitemap-tree.yml    # Auto-update this file
│       ├── ci.yml                   # Build & test
│       └── deploy.yml               # Production deploy
│
├── config/
│   └── odoo.conf                    # Odoo configuration
│
├── deploy/
│   ├── nginx.conf                   # Nginx reverse proxy
│   └── entrypoint.sh                # Custom entrypoint
│
├── docs/
│   ├── CLAUDE.md                    # AI coding guidelines
│   ├── PRD_TARGET_IMAGE.md          # Product requirements
│   └── AI_AGENT_TROUBLESHOOTING.md  # Troubleshooting guide
│
├── ipai_addons/                     # Our 5 custom modules
│   ├── ipai_dev_studio_base/        # Foundation
│   │   ├── __manifest__.py
│   │   ├── __init__.py
│   │   ├── models/
│   │   ├── views/
│   │   └── data/
│   │
│   ├── ipai_workspace_core/         # Notion-style workspaces
│   │   ├── __manifest__.py
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   └── workspace.py
│   │   ├── views/
│   │   │   ├── workspace_views.xml
│   │   │   └── workspace_menus.xml
│   │   ├── security/
│   │   │   ├── ir.model.access.csv
│   │   │   └── workspace_security.xml
│   │   └── demo/
│   │
│   ├── ipai_industry_accounting_firm/  # Delta: accounting
│   │   ├── __manifest__.py
│   │   ├── __init__.py
│   │   ├── models/
│   │   └── views/
│   │
│   ├── ipai_industry_marketing_agency/ # Delta: marketing
│   │   ├── __manifest__.py
│   │   ├── __init__.py
│   │   ├── models/
│   │   └── views/
│   │
│   └── ipai_ce_branding/            # CE branding
│       ├── __manifest__.py
│       ├── __init__.py
│       ├── models/
│       ├── views/
│       ├── data/
│       └── static/
│           └── src/
│               ├── js/
│               └── css/
│
├── oca_addons/                      # Vendored OCA modules
│   └── web/                         # OCA web enhancements
│
├── docker-compose.yml               # Development
├── docker-compose.prod.yml          # Production
├── Dockerfile                       # Baked image build
├── requirements.txt                 # Python deps
│
├── SITEMAP.md                       # Navigation map
├── TREE.md                          # This file
└── README.md                        # Project overview
```

## 📊 Stats

| Metric | Count |
|--------|-------|
| Custom Modules | 5 |
| OCA Modules | 1+ (web) |
| Workflows | 3 |

## 📝 Module Summary

| Module | Files | Lines (approx) |
|--------|-------|----------------|
| ipai_dev_studio_base | ~5 | ~100 |
| ipai_workspace_core | ~8 | ~300 |
| ipai_industry_accounting_firm | ~4 | ~100 |
| ipai_industry_marketing_agency | ~4 | ~100 |
| ipai_ce_branding | ~8 | ~400 |
| **Total** | **~29** | **~1000** |

---

*This tree auto-updates on every commit via [GitHub Actions](.github/workflows/auto-sitemap-tree.yml)*

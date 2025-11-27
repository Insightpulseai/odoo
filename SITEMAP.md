# 🗺️ Sitemap - InsightPulse ERP

> Auto-generated on every commit via GitHub Actions

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Project overview |
| [CLAUDE.md](CLAUDE.md) | AI coding guidelines |
| [PRD_TARGET_IMAGE.md](docs/PRD_TARGET_IMAGE.md) | Product requirements |

## 📦 Custom Modules (5 Total)

| # | Module | Type | Description |
|---|--------|------|-------------|
| 1 | [ipai_dev_studio_base](ipai_addons/ipai_dev_studio_base) | Foundation | CE dependencies + disable IAP |
| 2 | [ipai_workspace_core](ipai_addons/ipai_workspace_core) | New Concept | Notion-style workspaces |
| 3 | [ipai_industry_accounting_firm](ipai_addons/ipai_industry_accounting_firm) | Delta | Accounting client workspaces |
| 4 | [ipai_industry_marketing_agency](ipai_addons/ipai_industry_marketing_agency) | Delta | Brand/campaign workspaces |
| 5 | [ipai_ce_branding](ipai_addons/ipai_ce_branding) | Delta | Hide Enterprise, InsightPulse branding |

## 🔧 Configuration

| File | Purpose |
|------|---------|
| [docker-compose.yml](docker-compose.yml) | Docker orchestration |
| [Dockerfile](Dockerfile) | Container build |
| [config/odoo.conf](config/odoo.conf) | Odoo configuration |
| [.github/workflows/](https://github.com/jgtolentino/odoo-ce/tree/main/.github/workflows) | CI/CD pipelines |

## 🏗️ Infrastructure

| Component | URL/Location |
|-----------|--------------|
| Production | https://erp.insightpulseai.net |
| Server | 159.223.75.148 (odoo-erp-prod) |
| Registry | ghcr.io/jgtolentino/odoo-ce |
| Superset | https://superset.insightpulseai.net |

## 📊 Module Dependency Graph

```
ipai_dev_studio_base (foundation)
         │
         ▼
ipai_workspace_core (new concept)
         │
    ┌────┴────┐
    ▼         ▼
ipai_industry_  ipai_industry_
accounting_firm marketing_agency
    (delta)        (delta)

ipai_ce_branding (standalone)
```

## 🔗 Quick Links

- **GitHub**: https://github.com/jgtolentino/odoo-ce
- **OCA**: https://github.com/OCA
- **Odoo Docs**: https://www.odoo.com/documentation/18.0/

---

*This sitemap auto-updates on every commit via [GitHub Actions](.github/workflows/auto-sitemap-tree.yml)*

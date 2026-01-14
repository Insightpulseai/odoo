# Odoo 18 CE Docker Development Environment

A standalone, production-ready Docker setup for Odoo 18 Community Edition with the Finance PPM module and OCA integrations.

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 2. Build and start
docker compose up -d --build

# 3. Access Odoo
open http://localhost:8069
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐       ┌─────────────────┐              │
│  │   odoo:18.0     │       │  postgres:16    │              │
│  │   (web)         │──────▶│  (db)           │              │
│  │   Port 8069     │       │  Port 5432      │              │
│  └─────────────────┘       └─────────────────┘              │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Mounted Volumes                     │    │
│  │  • ./config/odoo.conf → /etc/odoo/odoo.conf         │    │
│  │  • odoo-filestore → /var/lib/odoo                   │    │
│  │  • odoo-logs → /var/log/odoo                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Included Components

### OCA Repositories (5 repos, 18.0 branch)
| Repository | Purpose |
|------------|---------|
| `reporting-engine` | MIS Builder, report_xlsx for Excel exports |
| `account-financial-reporting` | Trial Balance, General Ledger, Aged Partner |
| `project` | Task dependencies, WBS, Gantt views |
| `web` | web_responsive for mobile workflows |
| `server-tools` | Base utilities and extensions |

### Custom Module: `ipai_finance_ppm` v18.0.1.0.0
- **FinancePPMTask**: Hierarchical WBS with Preparer/Reviewer/Approver workflow
- **FinancePPMCanvas**: Dashboard widgets with ECharts (bar, pie, line, ring)
- **FinanceTeam**: Team directory with role codes
- **BIR Tax Calendar**: 2026 Philippine tax deadline tracking

### Debranding (Section 4.5)
The Dockerfile includes `sed` patches that remove:
- "My Odoo.com Account" and "Support" links
- Enterprise upgrade/upsell banners
- IAP (In-App Purchase) credit prompts
- "Powered by Odoo" footer text

## Configuration

### Environment Variables (`.env`)
```bash
POSTGRES_DB=postgres
POSTGRES_USER=odoo
POSTGRES_PASSWORD=your_secure_password

HOST=db
USER=odoo
PASSWORD=your_secure_password
```

### Odoo Configuration (`config/odoo.conf`)
Key settings:
- `workers = 0` - Threaded mode (set to `(2 * CPU) + 1` for production)
- `without_demo = all` - No demo data
- `log_level = info` - Production logging

## Development

### Install a Module
```bash
docker compose exec web odoo -d your_db -i module_name --stop-after-init
```

### Update a Module
```bash
docker compose exec web odoo -d your_db -u module_name --stop-after-init
```

### Run Tests
```bash
docker compose exec web odoo -d test_db -i ipai_finance_ppm --test-enable --stop-after-init
```

### Access Shell
```bash
docker compose exec web odoo shell -d your_db
```

### View Logs
```bash
docker compose logs -f web
```

## Contributing to OCA

If you want to contribute improvements back to the OCA repositories:

### 1. Fork & Clone
```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/reporting-engine.git
cd reporting-engine
git remote add upstream https://github.com/OCA/reporting-engine.git
```

### 2. Create Feature Branch
```bash
git checkout -b 18.0-add-my-feature
```

### 3. Follow OCA Guidelines
- Use [Pylint-Odoo](https://github.com/OCA/pylint-odoo) for linting
- Follow [OCA Technical Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Ede/CONTRIBUTING.rst)
- Include tests with >80% coverage

### 4. Create Pull Request
- Target: `OCA/<repo>` base branch `18.0`
- Include test scenario in description
- Wait for CI checks (CLA Bot, Travis, Coveralls, Codacy)

### 5. Review Process
- **3 positive reviews** within 5 days (or 2 after 5+ days)
- At least 1 review from PSC member or OCA Core Maintainer

## References

- [Official Odoo Docker Image](https://github.com/docker-library/docs/tree/master/odoo)
- [OCA Contribution Guide](https://odoo-community.org/page/Contribute)
- [OCA GitHub Organization](https://github.com/OCA)
- [Odoo 18 Documentation](https://www.odoo.com/documentation/18.0/)

## License

- Odoo CE: LGPL-3
- OCA Modules: AGPL-3
- Custom Module (ipai_finance_ppm): LGPL-3

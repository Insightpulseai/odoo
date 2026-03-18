# Odoo.sh Persona Model — Benchmark Reference

## Source

Odoo.sh features page: four built-in roles that govern the Odoo.sh delivery lifecycle. These roles serve as the **benchmark taxonomy** for InsightPulse AI delivery personas. The actual implementation binds to the Azure-first stack (Azure Container Apps, Azure Front Door, Azure managed PostgreSQL), not to Odoo.sh runtime.

## Four Benchmark Roles

### 1. Developers

Odoo.sh provides developers with:
- **GitHub integration**: Direct repository linking, branch-per-environment model
- **Clear logs**: Structured Odoo server logs with filtering and search
- **Web shell**: Browser-based terminal access to running containers
- **Emails**: Outbound mail configuration and delivery monitoring
- **CI/testing**: Automated test execution on branch push

**Azure equivalent**: GitHub Actions CI, Azure Log Analytics, `az containerapp exec`, Zoho SMTP, GitHub Actions test gates.

### 2. Testers

Odoo.sh provides testers with:
- **Automated tests**: `--test-enable` execution with structured results
- **Staging branches**: Dedicated staging environments with production-like data
- **Track developments**: Branch monitoring for test impact assessment
- **Manual tests**: Access to running instances for exploratory testing
- **Community modules**: OCA module compatibility testing surface

**Azure equivalent**: `test_<module>` disposable databases, `odoo_staging` on Azure managed PG, GitHub branch tracking, Azure Container App staging revisions, OCA 19.0 branch verification.

### 3. Project Managers

Odoo.sh provides project managers with:
- **Dev to staging**: Branch promotion from development to staging environment
- **Staging to production**: Controlled production deployment with safety checks
- **Share test builds**: Build artifact distribution for stakeholder review

**Azure equivalent**: GitHub PR merge flow, Azure Container App revision promotion, container image tagging and registry management (`cripaidev`, `ipaiodoodevacr`).

### 4. System Administrators

Odoo.sh provides system administrators with:
- **High availability**: Multi-worker architecture with automatic failover
- **Incremental backups**: Daily backups with 3-datacenter replication
- **Mail servers**: SMTP configuration and deliverability management
- **Performance**: Resource monitoring and optimization tools
- **Monitoring**: Server status dashboards, uptime tracking
- **Instant recovery**: Point-in-time restore from backup snapshots
- **DNS**: Custom domain management with automatic TLS
- **Security**: Access control, firewall rules, vulnerability scanning

**Azure equivalent**: ACA scaling + revision traffic splitting, Azure PG backup + geo-redundancy, Zoho SMTP + SPF/DKIM/DMARC, Azure Monitor + Application Insights, ACA revision rollback + PG point-in-time restore, Cloudflare DNS + Azure Front Door TLS, managed identity + Key Vault + WAF.

## Taxonomy Mapping

| Odoo.sh Role | InsightPulse AI Persona | Implementation Plane |
|--------------|------------------------|---------------------|
| Developers | `odoo-developer` | GitHub + Azure Container Apps + Azure Log Analytics |
| Testers | `odoo-tester` | Azure managed PG + ACA staging revisions + GitHub Actions |
| Project Managers | `odoo-release-manager` | GitHub PR flow + ACA revision promotion + ACR |
| System Administrators | `odoo-platform-admin` | Azure Monitor + Azure PG + Cloudflare + Azure Front Door |
| (no equivalent) | `odoo-delivery-judge` | Cross-persona validation gate (meta-persona) |

## Key Principle

Odoo.sh defines **what** delivery personas need. Azure defines **how** those needs are met. The persona model is portable; the skill implementations are Azure-native.

## Cross-References

- `agents/personas/odoo-developer.md`
- `agents/personas/odoo-tester.md`
- `agents/personas/odoo-release-manager.md`
- `agents/personas/odoo-platform-admin.md`
- `agents/personas/odoo-delivery-judge.md`
- `agent-platform/ssot/learning/odoo_sh_skill_persona_map.yaml`
- `docs/architecture/reference-benchmarks.md`

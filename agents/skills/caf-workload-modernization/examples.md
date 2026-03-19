# Examples — caf-workload-modernization

## Example 1: Keycloak to Entra ID modernization

**Input**: Modernize identity from self-hosted Keycloak to Microsoft Entra ID.

**Output**:
- Current state: Keycloak Container App (`ipai-auth-dev`), self-managed, OIDC/SAML
- Opportunity: Replace self-hosted IdP with managed Entra ID — eliminate container, reduce ops burden
- Target: Microsoft Entra ID with Conditional Access, PIM, SSO for all platform services
- Modernization plan:
  - Phase 1: Entra ID tenant setup, user provisioning
  - Phase 2: OIDC/SAML parity testing (Odoo, Superset, Plane, n8n)
  - Phase 3: Per-app cutover with parallel auth (Keycloak + Entra)
  - Phase 4: Keycloak decommission after all apps migrated
- Cost: Keycloak ACA ($25/mo saved) vs Entra ID Free/P1 tier
- Performance: Auth latency expected to improve (managed global infrastructure)
- Risks: [group/role mapping gaps, service-account replacement, break-glass admin access]

## Example 2: Database performance modernization

**Input**: PostgreSQL performance issues with Odoo under load.

**Output**:
- Current state: Azure PG Flexible Server, Burstable B2ms, single server
- Opportunity: Right-size compute, add read replica, optimize connection pooling
- Target: General Purpose D4s_v3, PgBouncer connection pooling, read replica for reporting
- Modernization plan:
  - Phase 1: Enable PgBouncer (built-in on Flex Server)
  - Phase 2: Scale to General Purpose tier during maintenance window
  - Phase 3: Add read replica for Superset/reporting queries
- Cost: $25/mo → $150/mo (offset by eliminating Superset query impact on primary)
- Performance: Expected 3x improvement in concurrent connection handling
- Risks: [scaling requires brief restart, read replica lag for reporting]

## Example 3: Monolith to microservices assessment (not recommended)

**Input**: Assess whether Odoo monolith should be decomposed into microservices.

**Output**:
- Current state: Odoo CE 19 monolith on ACA (web + worker + cron containers)
- Assessment: NOT RECOMMENDED for modernization
- Justification: Odoo is architecturally a monolith with module system. Decomposing into microservices would break the ORM, module dependency graph, and upgrade path. The current 3-container split (web, worker, cron) is the correct Odoo deployment pattern.
- Recommendation: Keep Odoo as monolith, modernize satellite services instead
- Alternative: Use ipai_* bridge modules to connect Odoo to Azure-native microservices

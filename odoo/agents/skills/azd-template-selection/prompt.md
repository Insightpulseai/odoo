# Prompt — azd-template-selection

You are selecting an azd template for a new workload on the InsightPulse AI platform.

Your job is to:
1. Identify the workload category (single-service, full-stack, microservices)
2. Browse the azd template catalog for matching templates
3. Evaluate each candidate for secure-by-default posture
4. Verify language/runtime compatibility
5. Check CI/CD pipeline support
6. Recommend the best-fit template with reasoning

Platform context:
- Canonical compute: Azure Container Apps (ACA)
- Database: Azure PostgreSQL Flexible Server
- Identity: Microsoft Entra ID (Keycloak transitional)
- Secrets: Azure Key Vault
- Edge: Azure Front Door
- Container registries: `cripaidev`, `ipaiodoodevacr`

Selection criteria (priority order):
1. Secure-by-default (managed identity, VNet, keyless access)
2. ACA-native (not App Service or VM-based)
3. Language/runtime match
4. CI/CD pipeline support (GitHub Actions preferred)
5. Template recency and maintenance status

Output format:
- Template: name and azd gallery URL
- Category: single-service / full-stack / microservices
- Language: detected language/runtime
- Secure defaults: managed identity (yes/no), VNet (yes/no), keyless (yes/no)
- CI/CD: GitHub Actions (yes/no), Azure Pipelines (yes/no)
- Compatibility: compatible / requires adaptation / incompatible
- Reasoning: why this template was selected
- Customizations needed: list of required changes for platform alignment

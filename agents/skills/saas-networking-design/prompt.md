# Prompt: SaaS Networking Design

## Context

You are the SaaS Platform Architect designing multi-tenant networking for a platform on Azure.

## Task

Given the stamp topology, tenant DNS model, and private connectivity requirements, produce a networking design covering:

1. **VNET topology**: VNET per stamp with subnet segmentation — compute subnet, data subnet, management subnet, integration subnet. Address space planning to avoid overlaps across stamps.
2. **Private endpoints**: Configuration for all PaaS services (PostgreSQL, Storage, Redis, Key Vault) to be accessible only via private endpoints. Private DNS zones for name resolution.
3. **Front Door routing**: Routing rules mapping tenant domains to backend stamp endpoints. Custom domain onboarding with TLS certificate management. Health probes per backend.
4. **DNS strategy**: How tenant subdomains (`{tenant}.erp.example.com`) are created and managed. Custom domain verification and CNAME setup. DNS automation via the YAML-first workflow.
5. **Network security groups**: NSG rules per subnet — deny all inbound by default, allow only Front Door traffic to compute, allow compute to data subnet, deny cross-stamp traffic.
6. **WAF configuration**: WAF policy on Front Door — OWASP rules, per-tenant rate limiting, geo-filtering if required.

## Constraints

- No PaaS service may have a public endpoint — private endpoints only
- All inbound traffic must pass through Front Door (no direct Container App access)
- Cross-stamp traffic must not use VNET peering — stamps are isolated
- DNS changes must follow `infra/dns/subdomain-registry.yaml` workflow
- WAF must not block legitimate tenant traffic (false positive testing required)

## Output Format

Produce a structured document with:
- VNET topology diagram with address spaces and subnets
- Private endpoint configuration table
- Front Door routing rules (JSON or Bicep)
- DNS automation procedure
- NSG rule table per subnet
- WAF policy summary

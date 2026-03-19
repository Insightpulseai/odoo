# Checklist: SaaS Networking Design

## Pre-flight

- [ ] Stamp topology finalized (count, regions)
- [ ] Tenant DNS model selected (shared subdomain, per-tenant, custom domain)
- [ ] Private connectivity requirements documented per tenant tier
- [ ] WAF requirements defined (compliance, rate limiting)
- [ ] Address space planning completed (no CIDR overlaps across stamps)

## VNET Topology

- [ ] One VNET per stamp with non-overlapping address spaces
- [ ] Subnets segmented: compute, data, management, integration
- [ ] Subnet delegation configured for Container Apps
- [ ] No VNET peering between stamps (isolation boundary)
- [ ] VNET flow logs enabled for traffic analysis

## Private Endpoints

- [ ] Private endpoints created for PostgreSQL, Storage, Redis, Key Vault
- [ ] Public access disabled on all PaaS services
- [ ] Private DNS zones configured for private endpoint resolution
- [ ] DNS zone linked to stamp VNET
- [ ] Connectivity verified from compute subnet to PaaS via private endpoint

## Front Door Routing

- [ ] Front Door configured as sole ingress point
- [ ] Backend pools created per stamp
- [ ] Routing rules map tenant domains to correct backend pool
- [ ] Health probes configured per backend
- [ ] Custom domain TLS certificates managed (Front Door managed or Key Vault)
- [ ] Origin host header set correctly for each backend

## DNS Management

- [ ] Tenant subdomain creation automated
- [ ] Custom domain verification (CNAME or TXT record) procedure documented
- [ ] DNS changes follow YAML-first workflow
- [ ] Wildcard certificate or per-domain certificate strategy decided
- [ ] DNS TTL appropriate for failover scenarios

## Network Security

- [ ] NSG on each subnet with deny-all default inbound
- [ ] Allow rule: Front Door service tag to compute subnet
- [ ] Allow rule: compute subnet to data subnet
- [ ] Deny rule: cross-stamp traffic (if VNETs peered for any reason)
- [ ] NSG flow logs enabled and retained for audit period

## WAF

- [ ] WAF policy associated with Front Door
- [ ] OWASP core rule set enabled
- [ ] Per-tenant rate limiting configured
- [ ] False positive testing completed
- [ ] WAF in detection mode initially, switched to prevention after validation

## Post-flight

- [ ] Port scan: no PaaS services accessible on public IP
- [ ] Front Door bypass test: direct Container App access blocked
- [ ] Custom domain TLS: certificate valid and auto-renewing
- [ ] Cross-stamp isolation: no network path between stamps
- [ ] WAF: legitimate traffic passes, attack traffic blocked

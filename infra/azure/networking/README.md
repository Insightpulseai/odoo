# Azure Networking

Azure networking configuration: VNets, NSGs, private endpoints, and DNS zones.

## Architecture

- Azure Container Apps use managed VNet integration
- Private endpoints for PostgreSQL and Key Vault
- Azure Front Door provides public ingress with WAF
- Azure DNS is the authoritative DNS provider

## Convention

- No public IPs on backend services (ACA ingress only)
- Private endpoints for all data services
- NSG rules follow least-privilege principle

<!-- TODO: Add Bicep/ARM templates for networking resources -->

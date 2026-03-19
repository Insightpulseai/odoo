# Checklist: SaaS Deployment Stamp Design

## Pre-flight

- [ ] Tenant growth projection documented (12-month, 24-month)
- [ ] Geo requirements mapped (regions, data residency)
- [ ] SLA targets defined per tier (availability, latency)
- [ ] Azure subscription limits reviewed for stamp count
- [ ] Budget per stamp estimated

## Stamp Composition

- [ ] Resources per stamp defined (compute, database, cache, storage, networking)
- [ ] Bicep/ARM template created and parameterized
- [ ] Template deploys a complete stamp in a single operation
- [ ] Stamp resources tagged for identification and cost attribution
- [ ] Stamp naming convention follows organization standard

## Capacity Model

- [ ] Max tenants per stamp calculated per resource bottleneck
- [ ] CPU, memory, connection, and storage limits documented
- [ ] Safety margin defined (e.g., 80% capacity triggers new stamp)
- [ ] Capacity model validated against real workload patterns
- [ ] Stamp sizing documented per tenant tier (small tenants vs enterprise)

## Tenant-to-Stamp Assignment

- [ ] Assignment algorithm selected and documented
- [ ] Tenant catalog stores stamp assignment (central database or control plane)
- [ ] Assignment API available for provisioning workflow
- [ ] Reassignment (migration) procedure defined
- [ ] No hardcoded tenant-to-stamp mapping in routing configuration

## Stamp Lifecycle

- [ ] New stamp creation automated via IaC pipeline
- [ ] Stamp creation time measured and within SLA
- [ ] Stamp scaling (vertical) procedure documented
- [ ] Stamp draining procedure: migrate all tenants, then decommission
- [ ] Stamp decommission: resource cleanup verified, no orphaned resources

## Geo-Distribution

- [ ] Stamps mapped to Azure regions based on tenant geo requirements
- [ ] Front Door routing configured with region-aware backend pools
- [ ] Data residency compliance verified per region
- [ ] Cross-region failover strategy documented (if applicable)
- [ ] Latency tested from target regions to nearest stamp

## Post-flight

- [ ] New stamp deployed from template — verified operational
- [ ] Tenant provisioned on new stamp — verified accessible
- [ ] Stamp failure simulated — other stamps unaffected
- [ ] Tenant migrated between stamps — zero downtime verified
- [ ] Capacity alerts fire at configured thresholds

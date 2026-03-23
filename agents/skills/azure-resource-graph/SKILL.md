# Skill: Azure Resource Graph Exploration

This skill enables an agent to perform advanced cloud governance, resource discovery, and cost optimization using Azure Resource Graph (ARG) and Kusto Query Language (KQL).

## Objective
To provide a high-performance interface for querying Azure resources at scale, identifying governance gaps, and optimizing cloud spend through Advisor insights.

## Core Rules
1. **Always use KQL**: All discovery must be performed via Azure Resource Graph queries using Kusto syntax.
2. **Adhere to Scopes**: Restrict queries to the provided subscription, management group, or tenant scope.
3. **Handle Limits**: Be aware of the 1,000-record default limit; use pagination if result sets are large.
4. **Security First**: Never include secrets in queries. Use system-assigned managed identities for execution.
5. **No Ad-hoc Filters**: Use existing Resource Graph tables (`resources`, `advisorresources`, `healthresources`) instead of slow individual API calls.

## Key Procedures

### 1. Perform Fleet Inventory
When asked to list or count resources, use `summarize count() by type` or `project` specific fields.
- **Table**: `resources`
- **Pattern**: `resources | project name, type, location | order by name asc`

### 2. Identify Governance Gaps
Detect unassociated or non-compliant resources (e.g., NSGs without subnets, orphan disks).
- **Pattern**: `resources | where type =~ "microsoft.network/networksecuritygroups" | where isnull(properties.networkInterfaces) and isnull(properties.subnets)`

### 3. Retrieve Cost & Optimization Insights
Extract recommendations from Azure Advisor to identify potential savings.
- **Table**: `advisorresources`
- **Pattern**: `advisorresources | where properties.category == 'Cost' | extend savings = todouble(properties.extendedProperties.savingsAmount)`

### 4. Monitor Resource Health
Check availability and health signals for critical infrastructure.
- **Table**: `healthresources`
- **Pattern**: `healthresources | where properties.availabilityState == 'Unavailable'`

## Troubleshooting
- **Throttling**: If `x-ms-user-quota-remaining` is low, wait for the reset interval.
- **Null Properties**: Ensure property casing is correct; property access in KQL is case-sensitive (e.g., `properties.storageProfile` not `properties.storageprofile`).

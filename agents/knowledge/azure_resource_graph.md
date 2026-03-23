# Knowledge Item: Azure Resource Graph (ARG)

Azure Resource Graph (ARG) is an Azure service designed to extend Azure Resource Management by providing efficient and performant resource exploration. It uses the **Kusto Query Language (KQL)** to query at scale across subscriptions, management groups, and tenants.

## Core Capabilities
- **Query at Scale**: Complex filtering, grouping, and sorting across thousands of resources.
- **Iterative Exploration**: Discover resources based on governance requirements.
- **Change Tracking**: View the last 14 days of resource configuration changes.
- **Policy Assessment**: Assess the impact of applying policies in large environments.

## Logical Tables
| Table | Description |
|-------|-------------|
| `resources` | Primary table for Azure resources (VMs, storage, networking). |
| `resourcecontainers` | Details for subscriptions and resource groups. |
| `advisorresources` | Azure Advisor recommendations (Cost, Security, High Availability). |
| `healthresources` | Resource health status and availability events. |
| `alertsmanagementresources` | Azure Monitor alerts and management metadata. |

## Canonical Query Patterns (KQL)

### 1. Resource Inventory
```kusto
resources
| project name, type, location, subscriptionId
| order by name asc
```

### 2. Summarize by Type
```kusto
resources
| summarize count() by type
| order by count_ desc
```

### 3. VM OS Distribution
```kusto
resources
| where type =~ 'Microsoft.Compute/virtualMachines'
| summarize count() by tostring(properties.storageProfile.osDisk.osType)
```

### 4. Unassociated NSGs (Governance)
```kusto
resources
| where type =~ "microsoft.network/networksecuritygroups" 
| where isnull(properties.networkInterfaces) and isnull(properties.subnets)
| project name, resourceGroup
```

### 5. Advisor Cost Savings
```kusto
advisorresources
| where type == 'microsoft.advisor/recommendations'
| where properties.category == 'Cost'
| extend savings = todouble(properties.extendedProperties.savingsAmount)
| summarize sum(savings) by tostring(properties.shortDescription.solution)
```

## Constraints & Limits
- **Throttling**: ARG is a free service and throttles at the user level. Response headers `x-ms-user-quota-remaining` and `x-ms-user-quota-resets-after` indicate quota status.
- **Pagination**: Default limit is 1,000 records. Use `skipToken` (Search-AzGraph cmdlet) or `$skipToken` (REST API) for pagination.
- **Permissions**: Minimum `Reader` access is required for the target scope.

## Integration Path
- **Azure CLI**: `az graph query -q "..."`
- **PowerShell**: `Search-AzGraph -Query "..."`
- **REST API**: `POST https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2021-03-01`
- **Power BI**: Native connector for tenant-level reporting.

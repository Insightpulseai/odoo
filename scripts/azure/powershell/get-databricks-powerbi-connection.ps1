<#
.SYNOPSIS
    Prepare Databricks SQL warehouse connection values for Power BI.

.DESCRIPTION
    Automates the Databricks prerequisite for Power BI Desktop:
    - Finds or validates the target SQL warehouse
    - Starts the warehouse if stopped
    - Optionally validates catalog/schema existence via SQL Statement Execution API
    - Emits powerbi-databricks-connection.json with exact paste values

    The actual Power BI Desktop connector step is still interactive
    (Azure Databricks connector -> paste hostname + HTTP path).

    Databricks recommends SQL warehouses for Power BI DirectQuery.
    Metric views require BI Compatibility Mode enabled in the connector.

.PARAMETER WorkspaceHost
    Full Databricks workspace URL (with https://).
    Default: https://adb-7405610347978231.11.azuredatabricks.net

.PARAMETER ServerHostname
    Databricks workspace hostname (without https://).
    Default: adb-7405610347978231.11.azuredatabricks.net

.PARAMETER WarehouseName
    Preferred SQL warehouse name.
    Default: ipai-dev-warehouse

.PARAMETER Catalog
    Unity Catalog name.
    Default: ipai_lakehouse_dev

.PARAMETER SchemaCandidates
    Target schema(s) to validate. String array.
    Default: serving, gold

.PARAMETER DatabricksProfile
    Databricks CLI profile name.
    Default: DEFAULT

.PARAMETER OutFile
    Output path for connection JSON.
    Default: ./powerbi-databricks-connection.json

.PARAMETER SmokeTest
    Run SQL catalog/schema validation via Statement Execution API.

.EXAMPLE
    pwsh -NoProfile -File get-databricks-powerbi-connection.ps1

.EXAMPLE
    pwsh -NoProfile -File get-databricks-powerbi-connection.ps1 -SmokeTest

.EXAMPLE
    pwsh -NoProfile -File get-databricks-powerbi-connection.ps1 `
      -WarehouseName "prod-warehouse" -Catalog "ipai_lakehouse_prod" -SmokeTest
#>

param(
    [string]$WorkspaceHost = "https://adb-7405610347978231.11.azuredatabricks.net",
    [string]$ServerHostname = "adb-7405610347978231.11.azuredatabricks.net",
    [string]$WarehouseName = "ipai-dev-warehouse",
    [string]$Catalog = "ipai_lakehouse_dev",
    [string[]]$SchemaCandidates = @("serving", "gold"),
    [string]$DatabricksProfile = "DEFAULT",
    [string]$OutFile = ".\powerbi-databricks-connection.json",
    [switch]$SmokeTest
)

$ErrorActionPreference = "Stop"

function Assert-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $Name"
    }
}

function Invoke-DatabricksJson {
    param(
        [Parameter(Mandatory = $true)][string[]]$Args
    )

    $raw = & databricks @Args 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Databricks CLI failed:`n$raw"
    }

    if (-not $raw) {
        return $null
    }

    return ($raw | ConvertFrom-Json)
}

function Wait-WarehouseRunning {
    param(
        [Parameter(Mandatory = $true)][string]$WarehouseId,
        [int]$TimeoutSeconds = 300,
        [int]$PollSeconds = 5
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $deadline) {
        $details = Invoke-DatabricksJson -Args @(
            "--profile", $DatabricksProfile,
            "warehouses", "get", $WarehouseId,
            "--output", "json"
        )

        $state = $details.state
        if ($state -eq "RUNNING") {
            return $details
        }

        Start-Sleep -Seconds $PollSeconds
    }

    throw "Warehouse $WarehouseId did not reach RUNNING state within ${TimeoutSeconds}s"
}

function Test-CatalogAndSchemas {
    param(
        [Parameter(Mandatory = $true)][string]$WarehouseId,
        [Parameter(Mandatory = $true)][string]$CatalogName,
        [Parameter(Mandatory = $true)][string[]]$Schemas
    )

    $results = [ordered]@{
        catalog_exists = $false
        schemas = @{}
        raw = @{}
    }

    $catalogStmt = @"
SHOW CATALOGS LIKE '$CatalogName'
"@

    $catalogResp = Invoke-DatabricksJson -Args @(
        "--profile", $DatabricksProfile,
        "api", "post", "/api/2.0/sql/statements/",
        "--json", (@{
            warehouse_id = $WarehouseId
            catalog      = $CatalogName
            schema       = "default"
            disposition  = "INLINE"
            statement    = $catalogStmt
        } | ConvertTo-Json -Compress)
    )

    $results.raw.catalog = $catalogResp
    if ($catalogResp.status.state -eq "SUCCEEDED" -and $catalogResp.result.data_array) {
        if ($catalogResp.result.data_array.Count -gt 0) {
            $results.catalog_exists = $true
        }
    }

    foreach ($schema in $Schemas) {
        $schemaStmt = @"
SHOW SCHEMAS IN $CatalogName LIKE '$schema'
"@

        $schemaResp = Invoke-DatabricksJson -Args @(
            "--profile", $DatabricksProfile,
            "api", "post", "/api/2.0/sql/statements/",
            "--json", (@{
                warehouse_id = $WarehouseId
                catalog      = $CatalogName
                schema       = "default"
                disposition  = "INLINE"
                statement    = $schemaStmt
            } | ConvertTo-Json -Compress)
        )

        $results.raw[$schema] = $schemaResp

        $exists = $false
        if ($schemaResp.status.state -eq "SUCCEEDED" -and $schemaResp.result.data_array) {
            if ($schemaResp.result.data_array.Count -gt 0) {
                $exists = $true
            }
        }

        $results.schemas[$schema] = $exists
    }

    return $results
}

# --- Main ---

Assert-Command -Name "databricks"

Write-Host "Checking Databricks warehouse..." -ForegroundColor Cyan

$warehouses = Invoke-DatabricksJson -Args @(
    "--profile", $DatabricksProfile,
    "warehouses", "list",
    "--output", "json"
)

if (-not $warehouses) {
    throw "No warehouses returned by Databricks CLI"
}

$warehouse = $warehouses | Where-Object { $_.name -eq $WarehouseName } | Select-Object -First 1
if (-not $warehouse) {
    Write-Host "Available warehouses:" -ForegroundColor Yellow
    $warehouses | Select-Object id, name, state | Format-Table -AutoSize
    throw "Warehouse '$WarehouseName' not found"
}

Write-Host "Selected warehouse: $($warehouse.name) [$($warehouse.id)] state=$($warehouse.state)" -ForegroundColor Green

if ($warehouse.state -ne "RUNNING") {
    Write-Host "Starting warehouse..." -ForegroundColor Cyan
    & databricks --profile $DatabricksProfile warehouses start $warehouse.id
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to start warehouse $($warehouse.id)"
    }
    $warehouse = Wait-WarehouseRunning -WarehouseId $warehouse.id
} else {
    $warehouse = Invoke-DatabricksJson -Args @(
        "--profile", $DatabricksProfile,
        "warehouses", "get", $warehouse.id,
        "--output", "json"
    )
}

$httpPath = "/sql/1.0/warehouses/$($warehouse.id)"

$payload = [ordered]@{
    generated_at = (Get-Date).ToString("o")
    workspace = [ordered]@{
        host = $WorkspaceHost
        server_hostname = $ServerHostname
        databricks_profile = $DatabricksProfile
    }
    warehouse = [ordered]@{
        id = $warehouse.id
        name = $warehouse.name
        state = $warehouse.state
        http_path = $httpPath
    }
    power_bi = [ordered]@{
        connector = "Azure Databricks"
        recommended_connectivity_mode = "DirectQuery"
        metric_view_bi_compatibility_mode = $true
        catalog = $Catalog
        schema_candidates = $SchemaCandidates
        recommended_auth = @(
            "Microsoft Entra ID",
            "Client credentials",
            "Personal Access Token (fallback)"
        )
    }
}

if ($SmokeTest) {
    Write-Host "Running SQL smoke test for catalog/schema existence..." -ForegroundColor Cyan
    $smoke = Test-CatalogAndSchemas -WarehouseId $warehouse.id -CatalogName $Catalog -Schemas $SchemaCandidates
    $payload["smoke_test"] = $smoke
}

$payload | ConvertTo-Json -Depth 8 | Set-Content -Path $OutFile -Encoding UTF8

Write-Host ""
Write-Host "Power BI connection details written to: $OutFile" -ForegroundColor Green
Write-Host ""
Write-Host "Server Hostname: $ServerHostname"
Write-Host "HTTP Path:       $httpPath"
Write-Host "Catalog:         $Catalog"
Write-Host "Schemas:         $($SchemaCandidates -join ', ')"
Write-Host "Mode:            DirectQuery"
Write-Host "Metric Views:    Enable BI Compatibility Mode in Power BI if using metric views"

# Databricks notebook source
# MAGIC %md
# MAGIC # Azure Resource Graph Ingestion
# MAGIC
# MAGIC Ingests Azure Advisor recommendations and Resource Graph data.

# COMMAND ----------

import os
import json
from datetime import datetime
from azure.identity import ClientSecretCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest
from pyspark.sql.functions import current_timestamp, lit

# COMMAND ----------

# Configuration
SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID")
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET")
TENANT_ID = os.environ.get("AZURE_TENANT_ID")
CATALOG = os.environ.get("DATABRICKS_CATALOG", "ppm")
SCHEMA = "bronze"

# COMMAND ----------

# Initialize Azure credentials
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

rg_client = ResourceGraphClient(credential)

# COMMAND ----------

# Azure Advisor recommendations query
ADVISOR_QUERY = """
advisorresources
| where type == 'microsoft.advisor/recommendations'
| where properties.category in ('Cost', 'Security', 'Reliability', 'OperationalExcellence', 'Performance')
| project
    id,
    subscriptionId,
    resourceGroup,
    category = properties.category,
    impact = properties.impact,
    impactedField = properties.impactedField,
    impactedValue = properties.impactedValue,
    shortDescription = properties.shortDescription.problem,
    extendedProperties = properties.extendedProperties,
    lastUpdated = properties.lastUpdated
| order by category, impact
"""

# COMMAND ----------

def query_resource_graph(query: str, subscriptions: list[str]):
    """Execute an Azure Resource Graph query."""
    request = QueryRequest(
        subscriptions=subscriptions,
        query=query
    )

    response = rg_client.resources(request)

    # Handle pagination
    all_data = list(response.data)

    while response.skip_token:
        request.options = {"$skipToken": response.skip_token}
        response = rg_client.resources(request)
        all_data.extend(response.data)

    return all_data

# COMMAND ----------

def ingest_advisor_recommendations():
    """Ingest Azure Advisor recommendations to bronze."""
    print("Querying Azure Advisor recommendations...")

    results = query_resource_graph(ADVISOR_QUERY, [SUBSCRIPTION_ID])
    print(f"Found {len(results)} recommendations")

    if not results:
        return 0

    # Convert to records
    records = []
    for rec in results:
        records.append({
            "recommendation_id": rec.get("id"),
            "subscription_id": rec.get("subscriptionId"),
            "resource_group": rec.get("resourceGroup"),
            "category": rec.get("category"),
            "impact": rec.get("impact"),
            "impacted_field": rec.get("impactedField"),
            "impacted_value": rec.get("impactedValue"),
            "short_description": rec.get("shortDescription"),
            "extended_properties": json.dumps(rec.get("extendedProperties", {})),
            "last_updated": rec.get("lastUpdated"),
            "raw_payload": json.dumps(rec)
        })

    # Create DataFrame
    df = spark.createDataFrame(records)
    df = df.withColumn("synced_at", current_timestamp())

    # Write to bronze
    df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SCHEMA}.azure_advisor_raw")

    print(f"Ingested {len(records)} recommendations")
    return len(records)

# COMMAND ----------

# Resource cost query (if cost management is enabled)
COST_QUERY = """
resources
| where type =~ 'microsoft.compute/virtualmachines'
    or type =~ 'microsoft.storage/storageaccounts'
    or type =~ 'microsoft.sql/servers/databases'
    or type =~ 'microsoft.databricks/workspaces'
| project
    id,
    name,
    type,
    location,
    resourceGroup,
    subscriptionId,
    sku = sku,
    properties
| limit 1000
"""

def ingest_resources():
    """Ingest resource inventory for cost analysis."""
    print("Querying Azure resources...")

    results = query_resource_graph(COST_QUERY, [SUBSCRIPTION_ID])
    print(f"Found {len(results)} resources")

    if not results:
        return 0

    records = []
    for res in results:
        records.append({
            "resource_id": res.get("id"),
            "name": res.get("name"),
            "type": res.get("type"),
            "location": res.get("location"),
            "resource_group": res.get("resourceGroup"),
            "subscription_id": res.get("subscriptionId"),
            "sku": json.dumps(res.get("sku", {})),
            "properties": json.dumps(res.get("properties", {})),
            "raw_payload": json.dumps(res)
        })

    df = spark.createDataFrame(records)
    df = df.withColumn("synced_at", current_timestamp())

    df.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(f"{CATALOG}.{SCHEMA}.azure_resources_raw")

    print(f"Ingested {len(records)} resources")
    return len(records)

# COMMAND ----------

# Run ingestion
advisor_count = ingest_advisor_recommendations()
resource_count = ingest_resources()

print(f"\nTotal: {advisor_count} recommendations, {resource_count} resources")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "success",
    "advisor_recommendations": advisor_count,
    "resources": resource_count,
    "timestamp": datetime.utcnow().isoformat()
}))

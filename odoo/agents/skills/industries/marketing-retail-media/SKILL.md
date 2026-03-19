# Skill: Databricks — Marketing, Retail, Media Use Cases

source: databricks.com/solutions/industries/marketing + retail + media-and-entertainment
extracted: 2026-03-15
applies-to: lakehouse, agents

## Marketing — Data Intelligence for Marketing
Core capability: unified customer + campaign data on lakehouse.
Key pattern: Composable CDP (warehouse-native activation, no data movement).
- Identity resolution (Amperity: 45min login to completed ID resolution)
- Delta Sharing → martech tools (Salesforce, Adobe, Braze, Hightouch, Census)
- Unity Catalog enforces GDPR/CCPA governance on all marketing data

## Retail
Core pattern: unified commerce data (POS + e-commerce + supply chain).
- Real-time personalization (product recommendations)
- Inventory optimization (demand forecasting with DLT + MLflow)
- Loyalty program orchestration

IPAI relevance: Project Scout (sari-sari store analytics) fits retail medallion pattern.

## Media & Entertainment
- Audience segmentation (first + third party data unification)
- Content performance analytics
- Ad traffic + performance intelligence (Agent Bricks accelerator)

## Shared medallion pattern across verticals

```
Bronze: raw events (clickstream, transactions, interactions)
Silver: cleansed + identity-resolved
Gold: audience segments, campaign KPIs, attribution models
AI layer: embeddings + recommendations + churn prediction
Activation: Delta Sharing → downstream martech/adtech tools
```

# ML & Serving Policy

## Model Registry Rules

- Models must be registered in Unity Catalog (catalog.schema.model naming)
- Model versions are immutable — create new versions, do not overwrite
- Production aliases should be managed through model version aliases
- Deleting a registered model is destructive and irreversible — confirm no active serving endpoints reference it

## Serving Endpoint Rules

- Enable scale-to-zero for non-production endpoints to control costs
- Traffic routing changes should be gradual (canary/blue-green)
- Endpoint specs must be version-controlled as JSON files
- Monitor endpoint latency and error rates after deployment
- Query endpoints with structured input (dataframe_records format)

## Experiment Rules

- Experiments organize MLflow runs — create per project/use case
- Deleted experiments are soft-deleted (can be restored)
- Experiment names should follow convention: `/ipai/<domain>/<experiment>`

## Secret Handling

- Model serving endpoints may need API keys for external services
- Use Databricks secrets for endpoint environment variables
- Never pass API keys as model input features

## Cost Controls

- Scale-to-zero for development endpoints
- Monitor serving endpoint compute hours
- Use appropriate workload sizes (Small/Medium/Large)

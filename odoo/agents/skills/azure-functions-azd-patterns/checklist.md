# Checklist — azure-functions-azd-patterns

## Plan and configuration

- [ ] Flex Consumption plan selected (not Classic Consumption)
- [ ] Instance memory configured appropriately
- [ ] Concurrency settings defined
- [ ] Application Insights connected

## Security

- [ ] Managed identity assigned (system-assigned)
- [ ] Downstream services accessed via managed identity (not connection strings)
- [ ] VNet integration configured for private resource access
- [ ] HTTP trigger auth level appropriate (not anonymous for internal APIs)
- [ ] No secrets in application settings (use Key Vault references)

## Trigger configuration

- [ ] Trigger type correctly defined in function.json / decorators
- [ ] Timer CRON expression validated and in UTC
- [ ] Event-driven triggers have dead-letter configuration
- [ ] Batch size and concurrency tuned for workload

## Deployment

- [ ] azd template selected and initialized
- [ ] azure.yaml declares Functions service with correct host
- [ ] azd up completes successfully
- [ ] Function execution verified post-deployment
- [ ] Cold start latency measured and documented

## Monitoring

- [ ] Application Insights configured
- [ ] Alerts set for function failures
- [ ] Log queries available for troubleshooting

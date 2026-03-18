# Examples — azure-load-testing-cli-patterns

## Example 1: Odoo health endpoint baseline

```bash
# Create load test resource
az load create \
  --name lt-ipai-dev \
  --resource-group rg-ipai-dev \
  --location southeastasia

# Create quick test (no JMeter file needed)
az load test create \
  --load-test-resource lt-ipai-dev \
  --test-id odoo-health-baseline \
  --display-name "Odoo Health Endpoint Baseline" \
  --test-type URL \
  --url "https://ipai-odoo-dev-web.thankfulbush-191bdcb0.southeastasia.azurecontainerapps.io/web/health"

# Configure: 10 users, 2 min ramp, 5 min sustain
az load test update \
  --load-test-resource lt-ipai-dev \
  --test-id odoo-health-baseline \
  --engine-instances 1

# Execute
az load test-run create \
  --load-test-resource lt-ipai-dev \
  --test-id odoo-health-baseline \
  --test-run-id baseline-run-001 \
  --display-name "Baseline Run 2026-03-17"

# Get results
az load test-run metrics list \
  --load-test-resource lt-ipai-dev \
  --test-run-id baseline-run-001 \
  --output table
```

---

## Example 2: JMeter test plan for API endpoints

```xml
<!-- test-plan.jmx (simplified) -->
<jmeterTestPlan>
  <ThreadGroup>
    <stringProp name="ThreadGroup.num_threads">50</stringProp>
    <stringProp name="ThreadGroup.ramp_time">60</stringProp>
    <stringProp name="ThreadGroup.duration">300</stringProp>
    <HTTPSamplerProxy>
      <stringProp name="HTTPSampler.domain">erp.insightpulseai.com</stringProp>
      <stringProp name="HTTPSampler.path">/web/health</stringProp>
    </HTTPSamplerProxy>
  </ThreadGroup>
</jmeterTestPlan>
```

```bash
az load test create \
  --load-test-resource lt-ipai-dev \
  --test-id api-load-test \
  --test-plan test-plan.jmx
```

---

## Example 3: CI/CD integration (GitHub Actions)

```yaml
# .github/workflows/load-test.yml
- name: Run load test
  uses: azure/load-testing-run-test@v2
  with:
    loadTestConfigFile: 'load-test-config.yaml'
    resourceGroup: 'rg-ipai-dev'
    loadTestResource: 'lt-ipai-dev'
```

---

## Anti-pattern: Unbounded production test

```bash
# WRONG — no duration limit, targeting production
az load test-run create \
  --load-test-resource lt-ipai-prod \
  --test-id stress-test \
  # Missing: bounded duration, approval, traffic controls

# CORRECT — bounded, dev environment, explicit limits
az load test update --engine-instances 1  # Limit engines
# JMX has: duration=300s, threads=50, ramp=60s
```

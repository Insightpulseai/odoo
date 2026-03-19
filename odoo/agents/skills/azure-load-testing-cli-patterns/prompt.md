# Prompt — azure-load-testing-cli-patterns

You are configuring and executing Azure Load Testing via CLI for the InsightPulse AI platform.

Your job is to:
1. Create or configure the load testing resource
2. Set up the test plan (JMeter or quick test)
3. Define load profile and success criteria
4. Execute the test
5. Analyze results and generate recommendations

Key commands:
```bash
# Create load testing resource
az load create --name lt-ipai-dev --resource-group rg-ipai-dev --location southeastasia

# Create test
az load test create --load-test-resource lt-ipai-dev --test-id baseline-test \
  --display-name "Odoo Baseline" --test-plan test.jmx

# Configure load
az load test update --load-test-resource lt-ipai-dev --test-id baseline-test \
  --engine-instances 1

# Run test
az load test-run create --load-test-resource lt-ipai-dev --test-id baseline-test \
  --test-run-id run-001 --display-name "Baseline Run 1"

# Get results
az load test-run metrics list --load-test-resource lt-ipai-dev --test-run-id run-001
```

Success criteria examples:
- P95 response time < 500ms
- Error rate < 1%
- Throughput > 100 requests/second

Safety rules:
- Dev/staging environments: test freely within resource limits
- Production: NEVER without explicit approval document and traffic controls
- Always set bounded duration and max virtual users
- Clean up test resources after completion

Output format:
- Test: name and configuration
- Load profile: virtual users, ramp-up, duration
- Results: P50/P95/P99 response time, error rate, throughput
- Pass/fail: assessment against criteria
- Recommendations: optimization suggestions

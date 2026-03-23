# Agent Deployments Operational Runbook
## Scale Policy By Service Class
- stateless_judge: safely scales to 3 replicas max based on resource quotas.
- single_writer_supervisor: scale blocked at 1. Scaling triggers split-brain loop without Redis clustering. DO NOT BYPASS.
## Crashloop / Probe failure
If probes map outside of `timeout_seconds: 5`, check node latency issues.

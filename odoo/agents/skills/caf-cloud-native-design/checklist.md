# Checklist — caf-cloud-native-design

- [ ] Workload requirements defined (functional and non-functional)
- [ ] Scalability targets specified (requests/sec, concurrent users)
- [ ] Availability target defined (SLA/SLO)
- [ ] Architecture pattern selected with justification
- [ ] Compute platform selected (ACA default, AKS only if justified)
- [ ] Data services selected with isolation and consistency requirements
- [ ] Event-driven flows designed with message semantics documented
- [ ] API design follows consistent patterns (REST, gRPC, or GraphQL)
- [ ] Service communication patterns defined (sync vs async)
- [ ] DevOps pipeline designed (build, test, deploy, promote)
- [ ] Deployment strategy selected (blue-green, canary, rolling)
- [ ] Observability designed (distributed tracing, metrics, structured logs)
- [ ] Health checks and readiness probes defined
- [ ] Well-Architected Framework validation completed (5 pillars)
- [ ] Architecture decision records created for key choices
- [ ] Operational complexity assessed against team capacity
- [ ] Evidence captured in `docs/evidence/{stamp}/caf/cloud-native/`

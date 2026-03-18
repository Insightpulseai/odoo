# Checklist — agent-framework-core

- [ ] Workflow defined as a directed graph with named nodes and typed edges
- [ ] Conditional branching logic is explicit on edge definitions (no implicit routing)
- [ ] Parallel execution paths have defined convergence points
- [ ] Middleware pipeline configured in correct order (auth before business logic)
- [ ] OpenTelemetry traces enabled with `agent.<workflow>.<step>` span naming
- [ ] Telemetry sampling policy defined (100% for dev, configurable for production)
- [ ] Checkpoint strategy defined for workflows running longer than 30 seconds
- [ ] Checkpoint storage backend configured (not in-memory for production)
- [ ] Human-in-the-loop gates block execution until approval received
- [ ] Escalation rules defined for unresolved gates (timeout, fallback)
- [ ] LLM provider selection uses abstraction layer (not hardcoded)
- [ ] Multi-provider failover configured if applicable
- [ ] End-to-end test executed with DevUI visualization
- [ ] Evidence captured in `docs/evidence/{stamp}/agent-framework/workflow/`

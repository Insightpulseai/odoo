# Agent Deployments Hardening Architecture
## Doctrine
Execution correctness decays without infrastructure bounds. Deployments strictly bind to their `runtime_profiles.yaml` definition preventing silent scaling that exceeds software architectural limits.

## Topology Compatibility
`single_writer_supervisor` guarantees exactly-once processing solely because of `replicas_max: 1` combined with `shared_persistent_required` limits.

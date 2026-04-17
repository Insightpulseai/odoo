# Agent Deployments Hardening Constitution

## Purpose
Define runtime deployment doctrine for all Agent Factory services.

## Authority model
* `spec/agent-deployments-hardening/*` = specification truth
* `ssot/deployments/agents/*.yaml` = intended-state truth
* deployment manifests / IaC = implementation truth
* evidence pack = operational proof

## Execution invariants
* every deployable agent has one declared runtime profile
* storage assumptions must be explicit
* health/readiness contracts must be explicit
* scale topology must not exceed coordination assumptions
* secrets/config surfaces must be declared, not implicit

## Failure contract
* missing required storage class / volume / secret / probe => fail closed
* unsupported scale shape => not production-approved

## Drift policy
* reject undeclared manifest fields that materially alter runtime semantics
* reject promotion to production without environment contract evidence

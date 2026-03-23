# Agent Deployments Hardening PRD

## Problem
code-level guarantees degrade if runtime manifests violate lock, storage, or health assumptions

## Goal
make agent deployment topology explicit, testable, and promotion-gated

## Non-goals
* not a full platform rewrite
* not universal multi-region correctness
* not a substitute for app-level fail-closed logic

## Personas
* deployable agent
* operator
* release pipeline
* platform maintainer

## Functional requirements
* runtime profile per agent
* storage contract per agent
* liveness/readiness/startup probe contract
* scale limits / topology contract
* secrets/config contract
* promotion gate by environment

## Acceptance criteria
* every deployable agent has a frozen runtime contract
* manifests cannot claim unsupported topology
* health probes align with service behavior
* storage-dependent services declare persistent/shared storage assumptions
* CI rejects production promotion without contract/evidence match

## Risks
* false green from bad probes
* ephemeral storage drift
* scale-out invalidating single-writer assumptions
* secret/config skew across environments
* rollout policy mismatch

# Eval Gate Contract

## Purpose

Define the mandatory evaluation gate for AI-enabled releases before production promotion and marketplace claims.

## Applies when

This contract is required if any release contains:

- agent behavior
- LLM/model output exposed to users
- automated reasoning/action recommendations
- tool use or orchestration
- retrieval or grounding logic
- AI-marketed capabilities in release notes or marketplace listing

## Source and target

**Source:** Staging deployment or pre-production build
**Target:** Production promotion decision

## Required artifacts

For each AI-enabled release:

- threshold file in `foundry/evals/<slug>/thresholds.yaml`
- evaluator configuration
- dataset or test case definition
- trace availability
- monitoring plan
- linked work item/spec

## Required dimensions

Every eval gate must explicitly define thresholds for relevant dimensions:

- quality / correctness
- groundedness
- tool-use success
- latency
- safety / policy adherence
- failure rate
- fallback behavior

## Pass/fail policy

Production promotion is blocked if:

- any blocking threshold fails
- trace collection is unavailable
- monitoring path is not configured
- evaluator version is missing
- release claims exceed measured evidence

## Marketplace claim rule

No marketplace claim may be made unless the underlying AI behavior was evaluated, thresholds passed, and claim language does not exceed measured capability.

## Continuous evaluation rule

For high-risk AI paths, production release is not the end of evaluation. These releases must define: post-release monitoring, trigger conditions for reevaluation, follow-up Issue creation path if quality/safety drifts.

## Evidence outputs

The eval gate must publish or link: summary result, threshold comparison, trace link, evaluator version, dataset version, decision outcome.

## Failure conditions

This contract fails if: AI-enabled functionality bypasses evaluation, eval exists but thresholds are undefined, pass/fail decision is manual with no artifact, or marketing claim is broader than evaluated behavior.

---

*Last updated: 2026-03-17*

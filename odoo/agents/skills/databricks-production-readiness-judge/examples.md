# Examples — databricks-production-readiness-judge

## Example 1: Spark Declarative Pipelines (Adopt)

**Input**: Pipeline readiness skill assessment: PRODUCTION-READY. Feature maturity: GA (released 2024, stable API). All four pillars pass.

**Output**:
- Feature: Spark Declarative Pipelines (formerly DLT)
- Release maturity: GA
- Source: Databricks release notes, GA announcement
- Production-grade classification: Production-ready
- Four-pillar assessment:
  - Deployment: Codified (YAML + Jobs workflow)
  - Observability: Complete (event log, metrics, alerting)
  - Rollback: Defined (checkpoints, versioned tables)
  - Lane assessment: PASS (pipeline readiness skill)
- Recommendation: **Adopt**
- Conditions: None
- Risk: Low

## Example 2: Databricks Apps with new autoscaling feature in Public Preview (Adopt-with-conditions)

**Input**: App readiness skill assessment: CONDITIONALLY-READY (autoscaling feature in Public Preview). Core Databricks Apps is GA. Autoscaling feature has stable interface and documented SLA. Deployment codified. Monitoring partial — no autoscaling-specific metrics yet.

**Output**:
- Feature: Databricks Apps autoscaling
- Release maturity: Public Preview
- Source: Databricks docs, feature status page
- Production-grade classification: Preview-acceptable
- Four-pillar assessment:
  - Deployment: Codified (CI/CD bundle deploy)
  - Observability: Partial (app monitoring exists, autoscaling metrics not yet available)
  - Rollback: Defined (version pinning, fixed instance count fallback)
  - Lane assessment: CONDITIONALLY-READY (app readiness skill)
- Recommendation: **Adopt-with-conditions**
- Conditions:
  - Monitor autoscaling behavior in staging for 2 weeks before production
  - Configure fixed instance count as fallback if autoscaling misbehaves
  - Re-assess when autoscaling metrics become available
- Risk: Medium — Public Preview feature with stable interface but limited observability

## Example 3: Agent framework tool with Beta status (Reject)

**Input**: Agent readiness skill assessment: NOT-READY. New tool execution feature in Beta. No SLA. API may change. No monitoring integration yet.

**Output**:
- Feature: Agent Framework tool execution (Beta)
- Release maturity: Beta
- Source: Databricks changelog, Beta label in docs
- Production-grade classification: Not-production-grade
- Four-pillar assessment:
  - Deployment: Manual (no bundle support yet)
  - Observability: Absent (no monitoring integration)
  - Rollback: Undefined (no versioning for tool configs)
  - Lane assessment: NOT-READY (agent readiness skill)
- Recommendation: **Reject**
- Conditions: N/A
- Risk: High — Beta feature with unstable API, no SLA, no observability
- Next review: When feature reaches Public Preview or GA. Check Databricks release notes monthly.

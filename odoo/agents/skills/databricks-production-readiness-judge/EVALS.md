# Evals — databricks-production-readiness-judge

| Dimension | Pass criteria |
|-----------|--------------|
| Maturity classification | Correctly identifies GA / Public Preview / Beta / Private Preview / Experimental |
| Maturity source citation | Cites specific release notes, docs page, or changelog — not generic |
| Beta/Preview rejection | Never classifies Beta/Private Preview/Experimental as production-ready |
| Four-pillar completeness | Assesses all four pillars: deployment, observability, rollback, lane assessment |
| Lane skill integration | References at least one lane-specific skill assessment |
| Classification accuracy | Production-grade determination matches evidence |
| Recommendation coherence | Recommendation logically follows from classification and evidence |
| Condition specificity | Conditions (if any) are actionable and measurable |
| Risk assessment | Identifies concrete risks, not generic warnings |
| Guardrail compliance | Respects all guardrails — no false production-ready claims |
| Output completeness | All required fields present in judgment output |
| Evidence quality | Judgment backed by specific artifacts and lane skill outputs |

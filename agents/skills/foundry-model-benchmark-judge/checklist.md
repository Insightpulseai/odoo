# Checklist — foundry-model-benchmark-judge

- [ ] Leaderboard data freshness verified (within 30 days)
- [ ] Quality dimension covered in selection
- [ ] Safety dimension covered in selection
- [ ] Cost dimension covered in selection
- [ ] Throughput dimension covered in selection
- [ ] Selection is workload-specific (not generic "best model")
- [ ] Safety thresholds defined and checked per candidate
- [ ] Cost within budget per candidate
- [ ] Over-budget candidates flagged
- [ ] Rejected models have documented exclusion reasons
- [ ] Rejection reasons are verifiable against leaderboard data
- [ ] No "best model everywhere" language present
- [ ] Verdict issued: APPROVE, REJECT, or CONDITIONAL
- [ ] Findings documented with specific issues
- [ ] Evidence captured in `docs/evidence/{stamp}/foundry/model-benchmark-judge/`

# Bank Reconciliation — Production Soak Window Runbook (BR-08)

## Objective
Observe 3–5 controlled production reconciliation cycles to capture real-world operational variance, validate fail-closed stability, and identify edge cases before widening heuristics or expanding scope.

## Scope
- Applies to all production batches following the first controlled import.
- **NO HEURISTIC WIDENING**: Use currently approved matching rules only.
- 3–5 stable cycles required for exit criteria.

## Cycle Requirements
For each cycle, the following must be captured and verified:
1.  **Cycle Log**: Trace of all matching decisions and tool calls.
2.  **Outcome Report**: JSON summary of state transitions (matched, ambiguous, unmatched).
3.  **Operator Review**: Human signoff on the cycle's correctness and any anomalies.
4.  **Acceptance Record**: JSON object validated against `bank_recon_soak_cycle.schema.json`.

## Stop Conditions
Abort the soak and return to assessment if:
- **Illegal Post**: Any line reaches `posted` without satisfying the evidence gate.
- **Duplicate Post**: Multiple entries posted for the same bank statement line or source document.
- **Unexplained Ambiguity Spike**: Sudden increase in ambiguity rates due to unexpected format drift.
- **Evidence Gaps**: Missing agent evidence packs for posted transactions.

## Execution Steps
1.  Load the production statement batch.
2.  Execute the Bank Reconciliation Agent under `monitored-production` status.
3.  Monitor logs for any `exception` or `fail-closed` events.
4.  Verify outcomes in the Odoo General Ledger.
5.  Perform operator review and generate the evidence pack.
6.  Update the `soak-rollup.json` with the latest cycle results.

## Exit Criteria
- 3–5 consecutive cycles completed without stop-condition violations.
- Residual risks updated based on production variance.
- Candidate heuristic refinements identified (but not yet enabled).
- Operational status remains `monitored-production`.

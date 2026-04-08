# Task Router Operations Runbook
- **Drain queue**: Inspect `RouterState` cache and delete active keys via metrics interface bounds.
- **Inspect quarantined tasks**: Query metrics output to detect malformed syntax envelopes.
- **Replay dead-lettered tasks**: Drop JSON from `/agents/dead-letters/` back to enqueue target.
- **Recover stale claims**: Automatic lease expiry logic cleans ghost handles without intervention.
- **Poison-message handling**: Handled actively via Retry exhaustion DLQ immutable writes preventing eternal loops.

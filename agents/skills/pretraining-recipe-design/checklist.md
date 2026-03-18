# Pretraining Recipe Design — Checklist

- [ ] Task classified: full pretraining vs continued pretraining
- [ ] Architecture selected (family, size, context length)
- [ ] Learning rate set with justification
- [ ] Batch size configured (effective via gradient accumulation if needed)
- [ ] Warmup steps defined (1-5% of total)
- [ ] Learning rate scheduler selected
- [ ] Max steps / epochs calculated from data size
- [ ] Weight decay configured
- [ ] Optimizer betas set appropriately
- [ ] Checkpoint save frequency defined
- [ ] Evaluation frequency defined
- [ ] Checkpoint retention policy set
- [ ] Best model selection criteria defined
- [ ] Loss monitoring configured (train loss, val loss, grad norm, lr)
- [ ] Divergence detection threshold set
- [ ] Logging target specified
- [ ] Compute budget estimated

# Training Readiness Judge — Checklist

## Data Quality Gate
- [ ] Data card exists with provenance and licensing
- [ ] Deduplication evidence provided
- [ ] Quality filtering evidence provided
- [ ] Train/validation/test splits documented
- [ ] Validation set strictly held out (not used for training decisions)

## Eval Completeness Gate
- [ ] Task-specific metrics reported
- [ ] General benchmarks reported
- [ ] Comparison to base model or previous checkpoint
- [ ] Post-training comparison to SFT baseline (if applicable)
- [ ] All required benchmarks present (none missing)

## Training Health Gate
- [ ] Loss converged (decreasing trend, stabilized)
- [ ] No loss divergence (no spikes > 2x moving average)
- [ ] No NaN or Inf values in loss
- [ ] Gradient norms within expected range
- [ ] Learning rate schedule executed correctly

## Reproducibility Gate
- [ ] Full training config saved (all hyperparameters)
- [ ] Random seed documented
- [ ] Data version or hash documented
- [ ] Software versions documented (transformers, torch, trl)
- [ ] Hardware configuration documented

## Decision
- [ ] All four gates assessed
- [ ] Decision reached: promote / reject / needs_more_eval
- [ ] Justification documented
- [ ] Gaps listed (if any)

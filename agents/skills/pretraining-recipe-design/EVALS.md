# Pretraining Recipe Design — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Task classification | 20% | Correct full vs continued pretraining decision |
| Training args quality | 25% | Appropriate lr, batch size, warmup, scheduler |
| Checkpoint strategy | 20% | Balanced frequency, retention, evaluation |
| Monitoring plan | 20% | Loss tracking, divergence detection configured |
| Compute estimation | 15% | Realistic resource estimate |

## Test Cases

### TC-1: Full pretraining request
- Input: "Train a 1B parameter model from scratch on 20B tokens"
- Expected: Full pretraining classification, lr ~1e-4 to 3e-4, cosine scheduler, warmup, checkpoint plan
- Fail if: Uses continued pretraining lr (too low) or missing warmup

### TC-2: Continued pretraining request
- Input: "Adapt Llama-3 to medical domain with 2B tokens of clinical notes"
- Expected: Continued pretraining, lr ~1e-5 to 5e-5, lower than base training, domain eval metrics
- Fail if: Uses full pretraining lr (too high) or ignores catastrophic forgetting monitoring

### TC-3: Insufficient data
- Input: "Pretrain from scratch with 100M tokens"
- Expected: Warning that data is insufficient for full pretraining, suggest continued pretraining instead
- Fail if: Proceeds with full pretraining without flagging data insufficiency

## Pass threshold: Correct task classification, appropriate lr range, monitoring configured

# Fine-Tuning Recipe Design — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Approach selection | 20% | Correct full FT vs PEFT decision for constraints |
| Training args quality | 25% | Appropriate lr, epochs, scheduler for fine-tuning |
| Forgetting monitoring | 20% | General benchmark baseline tracked |
| Task-specific eval | 20% | Meaningful metrics for the target task |
| Schedule design | 15% | Early stopping, best model, evaluation frequency |

## Test Cases

### TC-1: Domain adaptation with limited compute
- Input: "Fine-tune 7B model for medical QA, 1 GPU available"
- Expected: QLoRA or LoRA recommendation, appropriate rank/alpha, lr ~1e-4 to 3e-4 for PEFT
- Fail if: Recommends full fine-tuning on 1 GPU for 7B model

### TC-2: Instruction tuning with ample compute
- Input: "Instruction-tune 360M model, 8 GPUs available, 200K examples"
- Expected: Full fine-tuning viable, lr ~1e-5 to 5e-5, 2-5 epochs, early stopping
- Fail if: Uses pretraining learning rates or too many epochs (overfitting risk)

### TC-3: Catastrophic forgetting awareness
- Input: "Fine-tune on narrow domain data"
- Expected: General benchmark baseline recorded, forgetting threshold defined
- Fail if: No mention of catastrophic forgetting or general eval

## Pass threshold: Correct approach for constraints, lr in fine-tuning range, forgetting check present

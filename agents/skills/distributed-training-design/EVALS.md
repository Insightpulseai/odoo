# Distributed Training Design — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Memory analysis | 25% | Correct memory estimation |
| Strategy selection | 25% | Appropriate parallelism for model/hardware |
| Optimization choices | 20% | Mixed precision, gradient checkpointing applied correctly |
| Simplicity | 15% | Simplest strategy that meets requirements |
| Validation plan | 15% | Small-scale test planned |

## Test Cases

### TC-1: Small model, single GPU
- Input: "Train 360M model on 1x A100 80GB"
- Expected: Single GPU, no distribution, bf16, no gradient checkpointing needed
- Fail if: Recommends unnecessary distribution or FSDP

### TC-2: Model doesn't fit on one GPU
- Input: "Train 13B model on 2x A100 80GB"
- Expected: FSDP, bf16, gradient checkpointing, memory analysis showing >80GB needed
- Fail if: Recommends DDP (model won't fit on single GPU) or omits FSDP

### TC-3: Speed optimization
- Input: "Train 1.7B model on 8x A100s, need maximum throughput"
- Expected: DDP (model fits on 1 GPU), bf16, optimized batch size, throughput estimate
- Fail if: Uses FSDP unnecessarily (adds communication overhead when DDP suffices)

## Pass threshold: Correct fit analysis, appropriate strategy, mixed precision enabled

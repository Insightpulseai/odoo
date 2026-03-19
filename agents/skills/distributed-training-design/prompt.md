# Distributed Training Design — Prompt

You are designing a distributed training strategy. Your goal is to find the simplest configuration that fits the model in memory and meets the training time budget.

## Process

### 1. Memory Analysis
Estimate memory per GPU for training:
```
Model parameters:      params * bytes_per_param (bf16=2, fp32=4)
Optimizer states:      params * 8 (Adam: 2 fp32 copies + 2 momentum states)
Gradients:             params * bytes_per_param
Activations:           Varies by batch size, seq length, model depth
                       Rule of thumb: 2-4x model size for typical batch sizes

Total (fp32 Adam):     ~16-20 bytes per parameter
Total (bf16 + fp32 Adam): ~12-16 bytes per parameter
```

### 2. Fit Check
- **Fits on 1 GPU**: Use single GPU. No distribution needed.
- **Fits on 1 GPU with optimization**: Apply gradient checkpointing and/or mixed precision first.
- **Does NOT fit on 1 GPU**: Choose parallelism strategy.

### 3. Parallelism Selection

| Strategy | When to use | Complexity |
|----------|-------------|------------|
| **DDP** (Data Parallel) | Model fits on 1 GPU, want speed from multiple GPUs | Low |
| **FSDP** (Fully Sharded) | Model doesn't fit on 1 GPU, shard across GPUs | Medium |
| **Tensor Parallel** | Very large models, need to split individual layers | High |
| **Pipeline Parallel** | Very large models, split layers across GPUs sequentially | High |
| **DDP + FSDP** | Large model + many GPUs | Medium-High |

Decision tree:
1. Model fits on 1 GPU? -> DDP for speedup
2. Model fits with gradient checkpointing? -> DDP + gradient checkpointing
3. Model doesn't fit at all? -> FSDP (shard model across GPUs)
4. Model too large even for FSDP across available GPUs? -> Tensor/Pipeline parallel

### 4. Memory Optimizations
Apply in order of least to most invasive:
1. **Mixed precision** (bf16/fp16): ~2x memory reduction, minimal quality impact
2. **Gradient checkpointing**: ~50% activation memory reduction, ~30% slower
3. **Gradient accumulation**: Simulate larger batch without more memory
4. **CPU offloading**: Move optimizer states to CPU, significant speed penalty
5. **Activation offloading**: Move activations to CPU, significant speed penalty

### 5. Validate
- Run a small-scale test (100 steps) to verify:
  - No OOM errors
  - Loss is decreasing
  - Throughput meets expectations
  - All GPUs are utilized

## Output
```
Model size: [parameters]
Memory per GPU: [estimated GB]
Hardware: [GPU type x count]
Strategy: [DDP | FSDP | TP | PP | combination]
Optimizations: [list applied]
Estimated throughput: [tokens/sec or samples/sec]
Validation: [small-scale test plan]
```

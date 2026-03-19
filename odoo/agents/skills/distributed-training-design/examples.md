# Distributed Training Design — Examples

## Example 1: Single-GPU Fine-Tuning (no distribution needed)

```
Model size: 360M parameters
Memory estimate: 360M * 16 bytes = ~5.8 GB (bf16 + Adam)
Hardware: 1x A100 80GB

Strategy: Single GPU (no distribution)
Optimizations:
  - bf16 mixed precision (default)
  - No gradient checkpointing needed (ample memory)
  - Batch size 32 fits comfortably

Estimated throughput: ~8000 tokens/sec
Validation: Not needed — straightforward single-GPU setup
```

## Example 2: Multi-GPU Pretraining with DDP

```
Model size: 1.7B parameters
Memory estimate: 1.7B * 16 bytes = ~27 GB (bf16 + Adam)
Hardware: 4x A100 80GB

Fit check: 27 GB fits on single A100 80GB
Strategy: DDP (Data Parallel) — model fits, use multiple GPUs for speed
Optimizations:
  - bf16 mixed precision
  - Gradient checkpointing (reduce activation memory for large batch)
  - Gradient accumulation: 4 steps (effective batch = 4 GPUs * 32 micro * 4 accum = 512)

Estimated throughput: ~25000 tokens/sec (4x near-linear scaling)
Validation: 100-step test confirming all 4 GPUs >95% utilized
```

## Example 3: Large Model with FSDP

```
Model size: 7B parameters
Memory estimate: 7B * 16 bytes = ~112 GB (bf16 + Adam)
Hardware: 4x A100 80GB (320 GB total)

Fit check: 112 GB does NOT fit on single 80GB GPU
Strategy: FSDP (Fully Sharded Data Parallel) — shard across 4 GPUs
  - Sharding strategy: FULL_SHARD
  - Auto wrap policy: transformer_layer
Optimizations:
  - bf16 mixed precision
  - Gradient checkpointing (mandatory at this scale)
  - CPU offloading: NOT needed (4 GPUs * 80GB = 320GB > 112GB requirement)

Estimated throughput: ~12000 tokens/sec
Validation: 100-step test verifying:
  - No OOM on any GPU
  - Memory usage ~60-70% per GPU
  - Loss decreasing normally
  - Communication overhead acceptable
```

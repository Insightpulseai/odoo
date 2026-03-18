# Pretraining Recipe Design — Examples

## Example 1: Full Pretraining (1.7B parameter model)

```
Task type: Full pretraining
Base model: From scratch
Architecture: Llama-style decoder-only, 1.7B parameters, 2048 context length

Training args:
  learning_rate: 2e-4
  batch_size: 512 (via 4 GPUs x 32 micro-batch x 4 gradient accumulation)
  warmup_steps: 2000 (2% of 100K total steps)
  scheduler: cosine with warmup
  max_steps: 100000
  weight_decay: 0.1
  adam_beta1: 0.9
  adam_beta2: 0.95
  max_grad_norm: 1.0

Checkpoint plan:
  save_steps: 1000
  eval_steps: 500
  save_total_limit: 5
  best_model: lowest validation loss

Monitoring:
  metrics: train_loss, eval_loss, grad_norm, learning_rate, tokens_per_second
  divergence_threshold: 10% increase over 100 steps
  logging: Weights & Biases

Estimated compute: ~2000 A100 GPU-hours
Data: 35B tokens (20x parameter count)
```

## Example 2: Continued Pretraining (domain adaptation)

```
Task type: Continued pretraining
Base model: SmolLM2-1.7B
Architecture: Inherited from base (decoder-only, 1.7B params)

Training args:
  learning_rate: 2e-5 (10x lower than full pretraining)
  batch_size: 256
  warmup_steps: 500 (5% of 10K total steps)
  scheduler: cosine with warmup
  max_steps: 10000
  weight_decay: 0.01
  adam_beta1: 0.9
  adam_beta2: 0.95

Checkpoint plan:
  save_steps: 500
  eval_steps: 250
  save_total_limit: 3
  best_model: lowest validation loss

Monitoring:
  metrics: train_loss, eval_loss, domain_perplexity, general_perplexity
  divergence_threshold: 15% increase over 50 steps
  logging: TensorBoard

Estimated compute: ~100 A100 GPU-hours
Data: 5B tokens of domain-specific text
```

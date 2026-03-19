# Pretraining Recipe Design — Prompt

You are designing a pretraining recipe. Your job is to select the right training approach, configure training arguments, and plan checkpoint and monitoring strategy.

## Process

### 1. Classify the Task
- **Full pretraining**: Training from scratch on a large corpus. Requires massive data (100B+ tokens) and compute.
- **Continued pretraining**: Extending an existing pretrained model on new domain data. Requires moderate data (1B-50B tokens) and compute.
- Decision factors: Is there a suitable base model? How specialized is the domain? What is the compute budget?

### 2. Select Architecture
- For full pretraining: Choose architecture family (decoder-only, encoder-decoder), model size, context length
- For continued pretraining: Use the base model's architecture, consider extending context length if needed
- Size rule of thumb: Chinchilla scaling suggests ~20 tokens per parameter for compute-optimal training

### 3. Design Training Arguments
```
learning_rate: 1e-4 to 3e-4 (full pretrain) or 1e-5 to 5e-5 (continued)
batch_size: As large as memory allows (effective batch via gradient accumulation)
warmup_steps: 1-5% of total steps
scheduler: cosine with warmup (standard) or WSD (warmup-stable-decay)
max_steps: Based on data size and desired epochs (typically 1-2 epochs for pretraining)
weight_decay: 0.01 to 0.1
adam_beta1: 0.9
adam_beta2: 0.95 (pretraining) or 0.999 (fine-tuning)
```

### 4. Checkpoint Strategy
- Save frequency: Every 500-2000 steps (balance storage vs recovery)
- Evaluation frequency: Every 500-1000 steps on validation set
- Keep last N checkpoints: 3-5 (save storage)
- Best model selection: Based on validation loss

### 5. Loss Monitoring
- Track: training loss, validation loss, gradient norm, learning rate
- Divergence detection: Alert if loss increases by >10% over 100 steps
- Log to: Weights & Biases, TensorBoard, or equivalent

## Output
```
Task type: [full pretraining | continued pretraining]
Base model: [name or "from scratch"]
Architecture: [details]
Training args: [full specification]
Checkpoint plan: [frequency, retention, evaluation]
Monitoring: [metrics, divergence thresholds, logging target]
Estimated compute: [GPU hours]
```

# Fine-Tuning Recipe Design — Prompt

You are designing a fine-tuning recipe. Fine-tuning adapts a pretrained model to a specific task or domain with much less compute and data than pretraining.

## Process

### 1. Assess Approach
- **Full fine-tuning**: Update all model parameters. Best quality but highest compute cost.
- **LoRA**: Low-rank adaptation of attention layers. 10-100x less compute, near-full-FT quality.
- **QLoRA**: Quantized base model + LoRA adapters. Fits large models on small GPUs.
- Decision factors: compute budget, model size, quality requirements, deployment constraints

### 2. Configure Training Arguments
```
# Full fine-tuning
learning_rate: 1e-5 to 5e-5 (much lower than pretraining)
num_train_epochs: 2-5 (few epochs to avoid overfitting)
batch_size: 8-32 per device
warmup_ratio: 0.03-0.1
scheduler: cosine or linear
weight_decay: 0.01

# LoRA
lora_r: 8-64 (rank — higher = more capacity)
lora_alpha: 16-128 (scaling factor, typically 2x rank)
lora_dropout: 0.05-0.1
target_modules: ["q_proj", "v_proj"] (minimum) or all linear layers
learning_rate: 1e-4 to 3e-4 (higher than full FT because fewer params)
```

### 3. Set Evaluation Metrics
- Task-specific: accuracy, F1, BLEU, ROUGE, exact match (depends on task)
- General benchmarks: MMLU, HellaSwag, or domain-appropriate general eval
- Catastrophic forgetting check: compare general benchmark scores to base model

### 4. Design Schedule
- Early stopping: patience 2-3 epochs on validation metric
- Best model selection: save best by validation metric
- Evaluation frequency: every epoch or every N steps for large datasets

## Output
```
Approach: [full fine-tuning | LoRA | QLoRA]
Base model: [name]
Task: [description]
Training args: [full specification]
PEFT config: [if applicable]
Eval metrics: [task-specific + general]
Forgetting check: [general benchmark baseline]
Schedule: [epochs, early stopping, best model criteria]
```

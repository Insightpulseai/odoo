# Fine-Tuning Recipe Design — Examples

## Example 1: Domain Adaptation Fine-Tuning

```
Approach: LoRA
Base model: SmolLM2-1.7B
Task: Adapt to legal document analysis

PEFT config:
  lora_r: 32
  lora_alpha: 64
  lora_dropout: 0.05
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

Training args:
  learning_rate: 2e-4
  num_train_epochs: 3
  per_device_train_batch_size: 8
  gradient_accumulation_steps: 4
  warmup_ratio: 0.05
  scheduler: cosine
  weight_decay: 0.01
  bf16: true

Eval metrics:
  task_specific: document_classification_accuracy, entity_extraction_f1
  general: MMLU (baseline 45.2 on base model)
  forgetting_threshold: >5% MMLU drop triggers review

Schedule:
  eval_strategy: epoch
  early_stopping_patience: 2
  best_model: highest entity_extraction_f1
  save_total_limit: 3

Estimated compute: ~8 A100 GPU-hours
Data: 50K legal documents with annotations
```

## Example 2: Instruction Tuning

```
Approach: Full fine-tuning
Base model: SmolLM2-360M (small enough for full FT)
Task: Instruction-following assistant

Training args:
  learning_rate: 2e-5
  num_train_epochs: 3
  per_device_train_batch_size: 16
  warmup_ratio: 0.1
  scheduler: cosine
  weight_decay: 0.01
  bf16: true
  max_seq_length: 2048

Eval metrics:
  task_specific: instruction_following_score (GPT-4 judge), response_quality
  general: MMLU, HellaSwag
  forgetting_threshold: >3% drop on general benchmarks

Schedule:
  eval_steps: 500
  early_stopping_patience: 3
  best_model: highest instruction_following_score
  save_total_limit: 3

Estimated compute: ~4 A100 GPU-hours
Data: 100K instruction-response pairs (curated)
```

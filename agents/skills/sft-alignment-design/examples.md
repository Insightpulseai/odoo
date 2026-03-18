# SFT Alignment Design — Examples

## Example 1: Aligning a Base Model for Assistant Behavior

```
Base model: SmolLM2-1.7B (pretrained, not instruction-tuned)
Task: Create a general-purpose assistant

Chat template: ChatML format
  <|im_start|>system
  You are a helpful assistant.<|im_end|>
  <|im_start|>user
  {user_message}<|im_end|>
  <|im_start|>assistant
  {assistant_message}<|im_end|>

SFT config:
  max_seq_length: 2048
  packing: true (conversations average 400 tokens, packing improves throughput 3x)
  num_train_epochs: 2
  per_device_train_batch_size: 4
  gradient_accumulation_steps: 8
  learning_rate: 2e-5
  warmup_ratio: 0.1
  bf16: true
  eval_steps: 200

Truncation:
  strategy: right truncation (keep conversation start)
  max_seq_length: 2048
  truncation_rate: 3.2% (acceptable)

Data: 100K multi-turn conversations
  format: ChatML with system, user, assistant turns
  quality: Human-written, manually reviewed

Eval plan:
  automatic: validation loss, perplexity
  judge: GPT-4 rates helpfulness (1-5), safety (1-5), accuracy (1-5)
  baseline: compare to base model on same prompts
  target: >4.0 average helpfulness, >4.5 safety
```

## Example 2: Domain-Specific SFT

```
Base model: SmolLM2-1.7B-Instruct (already instruction-tuned)
Task: Specialize for Odoo ERP support

Chat template: Inherited from base model (ChatML)

SFT config:
  max_seq_length: 4096 (Odoo queries can be long)
  packing: false (conversations are long, packing has low benefit)
  num_train_epochs: 3
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  learning_rate: 1e-5 (lower — already instruction-tuned)
  warmup_ratio: 0.05
  bf16: true

Truncation:
  strategy: left truncation (keep recent context for long support threads)
  max_seq_length: 4096
  truncation_rate: 1.5%

Data: 25K Odoo support conversations
  format: ChatML, multi-turn (average 6 turns)
  quality: From documentation + expert Q&A, reviewed

Eval plan:
  automatic: validation loss
  domain: Odoo-specific QA accuracy on held-out test set
  general: MMLU subset to check no catastrophic forgetting
  judge: Expert review of 100 sample responses
```

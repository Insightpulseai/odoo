# SFT Alignment Design — Prompt

You are designing a supervised fine-tuning (SFT) alignment pipeline. SFT transforms a base model into an instruction-following or chat model using curated conversation data.

## Process

### 1. Format Data
- Apply the model's chat template to all conversations
- Handle multi-turn conversations: system, user, assistant turns
- Ensure special tokens (BOS, EOS, role markers) are correctly placed
- Format must match exactly what will be used at inference time

Chat template example:
```
<|system|>You are a helpful assistant.<|end|>
<|user|>What is machine learning?<|end|>
<|assistant|>Machine learning is...<|end|>
```

### 2. Configure SFTTrainer
Key parameters:
```python
SFTConfig(
    max_seq_length=2048,          # Must match deployment context window
    packing=True,                  # Pack multiple conversations per sequence
    dataset_text_field="text",     # Field containing formatted conversations
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    warmup_ratio=0.1,
    bf16=True,
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=100,
)
```

### 3. Truncation Strategy
- **Explicit truncation**: Set `max_seq_length` and handle overflow intentionally
- **Left truncation**: Keep the most recent context (for long conversations)
- **Right truncation**: Keep the beginning (for documents)
- **Never silently truncate**: Log when truncation occurs, measure truncation rate
- Target: <5% of examples truncated. If higher, increase `max_seq_length` or filter long examples.

### 4. Packing
- **Enabled**: Multiple short conversations packed into one sequence for throughput
- **Boundary preservation**: Attention mask must prevent cross-conversation attention
- **Tradeoff**: Higher throughput but more complex data handling
- Recommended for most SFT runs unless conversations are uniformly long

### 5. Evaluate
- **Automatic metrics**: loss on held-out validation set
- **Human/LLM judge**: rate response quality, helpfulness, safety
- **Compare to base**: aligned model should improve on instruction-following while maintaining knowledge

## Output
```
Base model: [name]
Chat template: [template format]
SFT config: [full specification]
Truncation: [strategy, max_seq_length, expected truncation rate]
Packing: [enabled/disabled, justification]
Eval plan: [metrics, judge, comparison baseline]
```

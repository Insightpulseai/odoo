# Preference Optimization Design — Prompt

You are designing a preference optimization stage. This refines an SFT-aligned model using preference signals to better match desired behavior.

## Process

### 1. Select Method

| Method | Data requirement | Compute | Best for |
|--------|-----------------|---------|----------|
| **DPO** | Offline preference pairs (chosen/rejected) | Lower | Static, high-quality preference data available |
| **GRPO** | Online generation + reward signal | Higher | Iterative improvement, no static preference data |

Decision factors:
- Have high-quality preference pairs? -> DPO
- Want iterative improvement from model's own outputs? -> GRPO
- Limited compute? -> DPO (offline, no generation needed)

### 2. Prepare Data

**DPO format:**
```json
{
  "prompt": "What is the capital of France?",
  "chosen": "The capital of France is Paris.",
  "rejected": "France is a country in Europe with many cities."
}
```
- Each example has: prompt, chosen response, rejected response
- Quality of preference pairs is critical -- noisy labels degrade results
- Minimum ~5K-10K pairs for meaningful signal

**GRPO format:**
- Prompts only (model generates responses)
- Reward function or reward model scores generations
- Groups of generations are ranked and optimized

### 3. Configure Trainer

**DPO:**
```python
DPOConfig(
    beta=0.1,                     # Preference strength (0.05-0.5)
    loss_type="sigmoid",          # sigmoid (standard) or hinge
    learning_rate=5e-7,           # Very low -- small updates
    num_train_epochs=1,           # Usually 1 epoch
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    bf16=True,
    max_length=2048,
    max_prompt_length=1024,
)
```

**GRPO:**
```python
GRPOConfig(
    num_generations=4,            # Generations per prompt
    learning_rate=1e-6,
    num_train_epochs=1,
    per_device_train_batch_size=2,
    bf16=True,
)
```

### 4. Beta Tuning
- **Too low** (< 0.05): Weak preference signal, minimal change from SFT
- **Sweet spot** (0.1-0.2): Meaningful preference alignment without over-optimization
- **Too high** (> 0.5): Over-optimization, repetitive/degenerate outputs, reward hacking

Monitor for over-optimization:
- Increasing reward but decreasing quality (judge scores)
- Decreased response diversity
- Repetitive patterns in outputs

### 5. Evaluate
- Compare to SFT baseline on same prompts
- Check win rate: what % of responses are preferred over SFT?
- Run general benchmarks to check no quality regression
- Monitor for reward hacking (high reward, low quality)

## Output
```
Method: [DPO | GRPO]
SFT baseline: [checkpoint name]
Data: [size, source, format]
Config: [full specification]
Beta: [value with justification]
Eval plan: [win rate vs SFT, general benchmarks, reward hacking checks]
```

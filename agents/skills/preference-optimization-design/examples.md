# Preference Optimization Design — Examples

## Example 1: DPO with Human Preference Data

```
Method: DPO
SFT baseline: SmolLM2-1.7B-SFT-v1
Task: Improve helpfulness and reduce verbosity

Data:
  source: Human annotators compared pairs of model responses
  size: 15K preference pairs
  format: prompt + chosen + rejected
  quality: Inter-annotator agreement > 80%

Config:
  beta: 0.1 (standard starting point)
  loss_type: sigmoid
  learning_rate: 5e-7
  num_train_epochs: 1
  per_device_train_batch_size: 4
  gradient_accumulation_steps: 4
  bf16: true
  max_length: 2048
  max_prompt_length: 1024

Eval plan:
  win_rate: Human judges compare DPO vs SFT on 200 prompts
  target: >60% win rate for DPO
  general: MMLU, HellaSwag (must not regress >2%)
  reward_hacking: Check response length distribution (verbosity reduction target)
  diversity: Measure unique n-gram ratio across 1000 responses
```

## Example 2: GRPO for Iterative Improvement

```
Method: GRPO
SFT baseline: SmolLM2-1.7B-SFT-v1
Task: Improve code generation accuracy

Data:
  source: Model generates 4 solutions per coding prompt
  reward: Unit test pass rate (0 or 1 per solution)
  prompts: 10K coding problems with test suites

Config:
  num_generations: 4
  learning_rate: 1e-6
  num_train_epochs: 1
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  bf16: true
  max_length: 4096

Eval plan:
  accuracy: HumanEval pass@1 (SFT baseline: 32%, target: >40%)
  general: MMLU subset (must not regress)
  reward_hacking: Manual review of 50 "passing" solutions for test gaming
  diversity: Check solution variety (not converging to single pattern)
  iterations: Run 3 GRPO iterations, measure improvement per iteration
```

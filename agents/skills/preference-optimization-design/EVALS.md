# Preference Optimization Design — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Method selection | 20% | Correct DPO vs GRPO choice for available data/compute |
| Beta tuning | 20% | Appropriate beta with justification |
| Data quality | 20% | Preference data verified, correct format |
| Over-optimization detection | 20% | Reward hacking and diversity monitoring planned |
| Baseline comparison | 20% | SFT comparison with win rate metric |

## Test Cases

### TC-1: DPO with preference data available
- Input: "Have 20K human preference pairs, want to improve helpfulness"
- Expected: DPO selected, beta ~0.1, lr ~5e-7, win rate eval vs SFT
- Fail if: Selects GRPO when static preference data is available and sufficient

### TC-2: No preference data, want iterative improvement
- Input: "No preference annotations, but have reward model for code quality"
- Expected: GRPO selected, generation config, reward function integration
- Fail if: Selects DPO without preference pairs

### TC-3: Over-optimization awareness
- Input: "Previous DPO run showed high reward but repetitive outputs"
- Expected: Lower beta, diversity monitoring, reward hacking detection plan
- Fail if: Increases beta or ignores over-optimization signals

## Pass threshold: Correct method for data availability, beta justified, over-optimization monitoring present

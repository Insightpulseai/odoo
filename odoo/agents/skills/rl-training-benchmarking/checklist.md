# Checklist: RL Training Benchmarking

## Protocol Definition

- [ ] Environment(s) selected
- [ ] Algorithm(s) selected
- [ ] Total timesteps per run defined
- [ ] Number of seeds defined (minimum 3, prefer 5)
- [ ] Evaluation frequency defined
- [ ] Number of evaluation episodes per checkpoint defined
- [ ] Random baseline included

## Fair Comparison

- [ ] Same environment version across all algorithms
- [ ] Same total timesteps budget
- [ ] Same evaluation protocol (frequency, episodes, deterministic flag)
- [ ] Same random seeds across algorithms (for paired comparison)
- [ ] Same hardware and environment normalization settings
- [ ] Algorithm-specific hyperparameters documented

## Metrics Collection

- [ ] Episode return (primary metric)
- [ ] Evaluation return at checkpoints
- [ ] Timesteps to threshold (sample efficiency)
- [ ] Wall-clock training time
- [ ] Algorithm-specific diagnostics (loss, KL, entropy)

## Statistical Analysis

- [ ] Mean and standard deviation computed across seeds
- [ ] Confidence intervals computed (bootstrap or t-distribution)
- [ ] Learning curves plotted with confidence bands
- [ ] No conclusions drawn from single runs
- [ ] Statistical significance assessed for performance differences

## Reporting

- [ ] Comparison table with mean, std, seeds, timesteps
- [ ] Learning curve plot with error bands
- [ ] Winner declared with metric and confidence level
- [ ] Caveats and limitations noted
- [ ] Hyperparameters for all algorithms documented
- [ ] Compute cost noted (GPU hours or wall-clock time)

## Common Pitfalls

- [ ] Not cherry-picking best seed
- [ ] Not comparing apples to apples (different timestep budgets)
- [ ] Not accounting for algorithm overhead (per-step compute cost)
- [ ] Not checking if differences are statistically significant
- [ ] Not including random baseline for context

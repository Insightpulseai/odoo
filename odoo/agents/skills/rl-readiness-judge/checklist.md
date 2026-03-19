# Checklist: RL Readiness Judge

## Convergence Assessment

- [ ] Training returns have stabilized (last 100 episodes vs previous 100)
- [ ] Relative change < 5% between windows
- [ ] No upward trend (training budget may be insufficient)
- [ ] No catastrophic drops in late training
- [ ] Diagnostic metrics stable (value loss, policy loss, entropy)

## Performance Assessment

- [ ] Mean eval return computed over 100+ episodes
- [ ] Standard deviation computed and reported
- [ ] Exceeds random baseline by significant margin
- [ ] Meets environment-specific threshold (if defined)
- [ ] Performance consistent across evaluation runs

## Generalization Assessment

- [ ] Tested with different environment seeds
- [ ] Tested with perturbed parameters (if applicable)
- [ ] Performance drop < 20% on unseen variations
- [ ] No catastrophic failure on any variation
- [ ] Edge cases tested (boundary conditions, unusual states)

## Safety Assessment

- [ ] 100+ evaluation episodes completed
- [ ] Zero constraint violations
- [ ] Joint/action limits respected
- [ ] No unsafe behaviors observed
- [ ] Adversarial/edge-case testing completed (if applicable)

## Reproducibility Assessment

- [ ] Minimum 3 seeds tested (5 for production)
- [ ] Results consistent across seeds
- [ ] No single seed is a major outlier
- [ ] Standard deviation reasonable for the environment

## Documentation Assessment

- [ ] Training configuration fully documented
- [ ] Hyperparameters listed with rationale
- [ ] Environment version and configuration recorded
- [ ] Training curve and eval results saved
- [ ] Known limitations documented

## Promotion Decision Matrix

| Tier | Convergence | Performance | Generalization | Safety | Reproducibility | Documentation |
|------|------------|-------------|----------------|--------|-----------------|---------------|
| Experiment | Optional | Optional | Optional | Optional | Optional | Optional |
| Staging | Required | Required | Recommended | Required | Recommended | Required |
| Production | Required | Required | Required | Required | Required | Required |

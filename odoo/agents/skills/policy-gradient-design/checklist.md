# Checklist: Policy Gradient Design

## Prerequisites

- [ ] Environment observation and action spaces characterized
- [ ] Action space type determines policy head (Categorical or Gaussian)
- [ ] Monte Carlo returns feasible (episodes terminate in reasonable time)

## Policy Network

- [ ] Input matches observation space
- [ ] Output matches action distribution parameters
- [ ] Discrete: output logits (n_actions)
- [ ] Continuous: output mean (action_dim), separate log_std parameter
- [ ] Hidden layers sized appropriately (64-256 typical)

## Episode Collection

- [ ] Run complete episodes before updating
- [ ] Store: states, actions, log_probs, rewards per timestep
- [ ] Multiple episodes per update batch (reduces variance)

## Return Computation

- [ ] Discounted returns computed correctly (backwards from episode end)
- [ ] Returns normalized across batch (optional but helps)
- [ ] Terminal states have no future reward

## Baseline

- [ ] Baseline type selected (none, mean return, or learned value)
- [ ] If mean return: subtract mean of batch returns
- [ ] If learned value: separate value network trained on returns
- [ ] Advantage = return - baseline

## Loss and Update

- [ ] Policy loss = -mean(log_prob * advantage)
- [ ] Entropy bonus added (encourages exploration)
- [ ] Optimizer: Adam with appropriate learning rate
- [ ] Gradient clipping applied (max_grad_norm ~0.5)

## Evaluation

- [ ] Periodic evaluation with deterministic policy (argmax for discrete, mean for continuous)
- [ ] Learning curve tracked
- [ ] Variance of returns monitored (high variance is expected for REINFORCE)
- [ ] Compared to random baseline

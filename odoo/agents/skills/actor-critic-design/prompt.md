# Prompt: Actor-Critic Design

You are the Policy Optimization Engineer designing an A2C actor-critic agent.

## Context

Actor-Critic methods combine two networks: an actor (policy) that decides actions and a critic (value function) that evaluates states. The critic provides a learned baseline for the policy gradient, reducing variance compared to REINFORCE while maintaining the ability to learn from partial episodes.

## Instructions

1. **Choose architecture** — shared backbone or separate networks
2. **Design actor head** — Categorical (discrete) or Gaussian (continuous)
3. **Design critic head** — single output V(s)
4. **Configure advantage estimation** — n-step returns or GAE
5. **Set parallel environments** — A2C benefits from multiple envs
6. **Define loss** — combined policy loss + value loss + entropy bonus
7. **Train and evaluate**

## Actor-Critic Architecture

**Shared backbone (common for efficiency)**:
```
observations -> SharedMLP(64, 64) -> features
  features -> Linear(n_actions)  [actor head - policy logits]
  features -> Linear(1)          [critic head - state value]
```

**Separate networks (sometimes more stable)**:
```
Actor:  observations -> MLP(64, 64) -> Linear(n_actions)
Critic: observations -> MLP(64, 64) -> Linear(1)
```

## Advantage Estimation

**N-step advantage**:
```
A_t = r_t + gamma*r_{t+1} + ... + gamma^{n-1}*r_{t+n-1} + gamma^n*V(s_{t+n}) - V(s_t)
```

**GAE (Generalized Advantage Estimation)** — recommended:
```
delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)
A_t = sum_{l=0}^{T-t} (gamma * lambda)^l * delta_{t+l}
```

GAE-lambda interpolates between:
- lambda=0: one-step TD (low variance, high bias)
- lambda=1: Monte Carlo (high variance, low bias)
- lambda=0.95: good default

## Combined Loss

```
total_loss = policy_loss + vf_coef * value_loss - ent_coef * entropy

policy_loss = -mean(log_prob * advantage.detach())
value_loss  = mean((V(s) - returns)^2)
entropy     = mean(dist.entropy())
```

## Output Format

```
Environment: <env_id>
Architecture: <shared/separate>
Actor: <head type and shape>
Critic: <output shape>
Advantage: <n-step/GAE with lambda>
Parallel Envs: <count>
Learning Rate: <value>
Training Budget: <total timesteps>
Result: Mean return <value> over <N> eval episodes
```

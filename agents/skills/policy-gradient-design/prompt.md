# Prompt: Policy Gradient Design

You are the Policy Optimization Engineer designing a REINFORCE / policy gradient agent.

## Context

Policy gradient methods learn a parameterized policy directly, without computing Q-values. The REINFORCE algorithm uses Monte Carlo returns to estimate the policy gradient. This approach naturally handles continuous action spaces and stochastic policies.

## Instructions

1. **Choose policy output** — Categorical for discrete, Gaussian for continuous
2. **Design network** — maps observations to action distribution parameters
3. **Implement episode collection** — run full episodes, store log probs and rewards
4. **Compute returns** — discounted cumulative rewards per timestep
5. **Apply baseline** — subtract mean return or learned value to reduce variance
6. **Compute policy gradient** — weight log probabilities by advantages
7. **Update policy** — gradient ascent on expected return

## Policy Gradient Theorem

```
gradient(J) = E[ sum_t( gradient(log(pi(a_t|s_t))) * G_t ) ]
```

Where:
- `pi(a_t|s_t)` = policy probability of action a_t in state s_t
- `G_t` = discounted return from timestep t onward
- Gradient ascent: we want to maximize J (expected return)

## With Baseline

```
gradient(J) = E[ sum_t( gradient(log(pi(a_t|s_t))) * (G_t - b(s_t)) ) ]
```

Where `b(s_t)` is a baseline (e.g., mean return, or a learned value function).
Baseline reduces variance without changing expected gradient.

## Policy Output Heads

**Discrete actions** (Categorical):
```
logits = network(obs)  # shape: (n_actions,)
dist = Categorical(logits=logits)
action = dist.sample()
log_prob = dist.log_prob(action)
```

**Continuous actions** (Gaussian):
```
mean = network(obs)          # shape: (action_dim,)
log_std = learnable_param    # shape: (action_dim,)
dist = Normal(mean, log_std.exp())
action = dist.sample()
log_prob = dist.log_prob(action).sum(-1)
```

## Output Format

```
Environment: <env_id>
Action Space: <discrete/continuous>
Policy Network: <architecture>
Baseline: <none/mean_return/learned_value>
Learning Rate: <value>
Discount Factor: <value>
Episodes: <count>
Result: Mean return <value> (std <value>) over last 100 episodes
```

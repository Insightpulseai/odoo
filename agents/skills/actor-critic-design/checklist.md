# Checklist: Actor-Critic Design

## Prerequisites

- [ ] Environment observation and action spaces characterized
- [ ] REINFORCE baseline attempted (or reason to skip documented)
- [ ] Compute resources assessed (A2C benefits from parallel envs)

## Architecture

- [ ] Shared vs separate backbone decision made and justified
- [ ] Actor head matches action space (Categorical or Gaussian)
- [ ] Critic head outputs single scalar V(s)
- [ ] Hidden layer sizes appropriate
- [ ] Activation functions chosen

## Advantage Estimation

- [ ] GAE or n-step returns selected
- [ ] GAE lambda set (0.95 default)
- [ ] Discount factor gamma set (0.99 default)
- [ ] Advantages normalized before policy update (optional but recommended)

## Parallel Environments

- [ ] Number of parallel envs chosen (4-16 typical for A2C)
- [ ] Vectorized environment wrapper used (SubprocVecEnv or DummyVecEnv)
- [ ] Observation normalization applied across envs

## Loss Function

- [ ] Policy loss uses log_prob * advantage (advantage detached from critic graph)
- [ ] Value loss uses MSE between V(s) and computed returns
- [ ] Entropy bonus included to prevent premature convergence
- [ ] Loss coefficients set: vf_coef (~0.5), ent_coef (~0.01)

## Training

- [ ] N-steps per update set (5-128 typical)
- [ ] Optimizer: Adam or RMSprop
- [ ] Learning rate appropriate (~7e-4 for A2C)
- [ ] Gradient clipping enabled (max_grad_norm ~0.5)
- [ ] Total timesteps set

## Evaluation

- [ ] Periodic evaluation during training
- [ ] Separate eval environment (not training envs)
- [ ] Mean and std over 10+ episodes
- [ ] Learning curve shows improvement
- [ ] Compared to REINFORCE baseline (should be lower variance)

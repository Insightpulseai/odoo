# Checklist: Q-Learning Baseline Design

## Prerequisites

- [ ] Environment has discrete state space (Discrete or can be discretized)
- [ ] Environment has discrete action space
- [ ] State space is small enough for a table (< 10,000 states)
- [ ] Reward structure understood (dense vs sparse)

## Q-Table Setup

- [ ] Q-table shape matches (n_states, n_actions)
- [ ] Initialization strategy chosen (zeros, small random, optimistic)
- [ ] Q-table data type appropriate (float32 or float64)

## Hyperparameters

- [ ] Learning rate set and decay schedule defined
- [ ] Discount factor chosen (0.95 is a common default)
- [ ] Epsilon start, end, and decay rate defined
- [ ] Number of training episodes set
- [ ] Max steps per episode set (if not environment-limited)

## Training Loop

- [ ] Epsilon-greedy action selection implemented
- [ ] Q-value update uses Bellman equation correctly
- [ ] Terminal states handled (no future value for terminal)
- [ ] Epsilon decays after each episode (not each step)
- [ ] Episode return tracked for monitoring

## Evaluation

- [ ] Greedy policy evaluated (epsilon=0) over 100+ episodes
- [ ] Mean and std of evaluation returns reported
- [ ] Learning curve plotted (episode return vs episode number)
- [ ] Q-values inspected for reasonableness
- [ ] Compared to random policy baseline

## Common Pitfalls

- [ ] Not confusing terminated vs truncated (Gymnasium v26+)
- [ ] Not updating Q-values for terminal transitions with future value
- [ ] Learning rate not too high (causes oscillation) or too low (too slow)
- [ ] Epsilon not decaying too fast (insufficient exploration)

# Checklist: Deep Q-Learning Design

## Prerequisites

- [ ] Environment has discrete action space
- [ ] Observation space characterized (vector dim or image shape)
- [ ] Compute budget established (GPU availability, training time)
- [ ] Baseline performance known (random policy, tabular Q-learning if applicable)

## Network Architecture

- [ ] Input layer matches observation shape
- [ ] Output layer has one unit per action
- [ ] CNN used for image inputs, MLP for vector inputs
- [ ] Hidden layer sizes appropriate (not too small, not too large)
- [ ] Activation functions chosen (ReLU standard)

## Experience Replay

- [ ] Buffer size set (100K-1M typical)
- [ ] Buffer stores (state, action, reward, next_state, done) tuples
- [ ] Uniform random sampling implemented
- [ ] Learning starts after buffer has minimum samples (learning_starts parameter)

## Target Network

- [ ] Target network initialized as copy of online network
- [ ] Update frequency set (hard: every 1000-10000 steps)
- [ ] Or soft update tau set (0.001-0.01 typical)

## Epsilon Schedule

- [ ] Start epsilon = 1.0
- [ ] End epsilon set (0.01-0.1 typical)
- [ ] Decay schedule defined (linear over N steps)
- [ ] Exploration fraction appropriate for training budget

## Training

- [ ] Optimizer chosen (Adam standard, lr ~1e-4)
- [ ] Loss function = MSE or Huber loss on TD error
- [ ] Gradient clipping enabled (max_grad_norm ~10)
- [ ] Batch size set (32-256)
- [ ] Training frequency set (train every N steps)

## DQN Variant

- [ ] Vanilla DQN, Double DQN, or Dueling DQN selected
- [ ] If Double: online net selects action, target net evaluates
- [ ] If Dueling: value and advantage streams separated

## Evaluation

- [ ] Periodic evaluation during training (every N timesteps)
- [ ] Evaluation uses greedy policy (epsilon=0)
- [ ] Mean and std over 10+ evaluation episodes
- [ ] Learning curve tracked
- [ ] Compared to random and/or tabular baseline

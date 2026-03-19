# Examples: Multi-Agent RL Design

## Example 1: Cooperative Navigation (PettingZoo)

**Problem**: 3 agents must spread out to cover 3 landmarks.

**Design**:
```
Environment: pettingzoo.mpe.simple_spread_v3
N Agents: 3
Interaction: Cooperative
Paradigm: Shared policy (agents are homogeneous)
Per-Agent Observation: (18-dim) own position/velocity + relative positions of other agents and landmarks
Per-Agent Action: Continuous (2-dim) — x/y velocity
Reward: Team reward — negative sum of distances from each agent to nearest landmark
Communication: None (agents observe each other's positions)
Algorithm: PPO with shared policy
Training Budget: 1,000,000 timesteps
```

**Training**:
```python
from pettingzoo.mpe import simple_spread_v3
import supersuit as ss

env = simple_spread_v3.parallel_env()
env = ss.pettingzoo_env_to_vec_env_v1(env)
env = ss.concat_vec_envs_v1(env, 8, base_class="stable_baselines3")

from stable_baselines3 import PPO
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=1_000_000)
```

**Result**: Agents learn to spread to cover all landmarks, minimizing total distance.

---

## Example 2: Competitive Self-Play (Tag)

**Problem**: One agent (predator) chases another agent (prey).

**Design**:
```
Environment: pettingzoo.mpe.simple_tag_v3
N Agents: 4 (3 predators + 1 prey)
Interaction: Competitive (predators vs prey)
Paradigm: Independent learners (different roles)
  Predator policy: PPO trained to minimize distance to prey
  Prey policy: PPO trained to maximize distance to predators
Per-Agent Observation: Positions and velocities of all agents
Per-Agent Action: Continuous (2-dim) movement
Reward:
  Predators: +10 when any predator catches prey, -0.1 per step
  Prey: -10 when caught, +0.1 per step survived
Communication: None
Algorithm: PPO per role
```

**Key insight**: Independent training creates an arms race — predators improve, prey adapts, predators improve further. This auto-curriculum makes both sides stronger over time.

---

## Example 3: Self-Play with Sample Factory

**Problem**: Train a competitive game agent using self-play.

**Design**:
```
Environment: Custom 1v1 game (PettingZoo API)
N Agents: 2
Interaction: Competitive (zero-sum)
Paradigm: Self-play
  Current policy vs sampled past policies
  Opponent sampling: 80% latest, 20% uniform from history
Per-Agent Observation: Local game state
Per-Agent Action: Discrete (game-specific)
Reward: +1 for win, -1 for loss, 0 for draw
Algorithm: PPO via Sample Factory (high throughput)
Policy History: Save checkpoint every 100K steps
```

**Training with Sample Factory**:
```python
from sample_factory.cfg.arguments import parse_full_cfg
from sample_factory.train import run

cfg = parse_full_cfg(argv=[
    "--algo=APPO",
    "--env=my_game_env",
    "--experiment=self_play_v1",
    "--num_workers=16",
    "--num_envs_per_worker=4",
    "--self_play=True",
    "--self_play_opponent_sample_range=100",
])
run(cfg)
```

**Key insight**: Sample Factory provides high-throughput training essential for self-play, where millions of games are needed for learning.

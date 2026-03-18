# Benchmark: Hugging Face Deep RL Course

> Source: Hugging Face Deep Reinforcement Learning Course
>
> Role: RL skill taxonomy benchmark — NOT a default platform lane
>
> Status: Course is in LOW-MAINTENANCE mode. AI vs AI unit is non-functional.
> Leaderboard is no longer operational. Use as curriculum reference only.

---

## Canonical Fit

```
HF Deep RL Course  = benchmark curriculum for RL skill taxonomy
SB3/CleanRL/etc.   = implementation source of truth
Repo evals         = promotion gate
```

---

## Course Syllabus to Skill Mapping

| Course Unit | Skill Family | Library Surface |
|-------------|-------------|-----------------|
| Intro to Deep RL | `rl-environment-selection` | Gymnasium |
| Q-Learning | `q-learning-baseline-design` | Custom / SB3 |
| Deep Q-Learning (Atari) | `deep-q-learning-design` | SB3, CleanRL |
| Policy Gradient (Reinforce) | `policy-gradient-design` | SB3, CleanRL |
| Actor-Critic (A2C) | `actor-critic-design` | SB3 |
| PPO | `ppo-design` | SB3, CleanRL |
| Actor-Critic with Robotics | `robotics-rl-design` | SB3, PyBullet/MuJoCo |
| Multi-Agents and AI vs AI | `multi-agent-rl-design` | Sample Factory, PettingZoo |

---

## Algorithm Families

### Value-Based Methods

- **Q-Learning**: Tabular, model-free, off-policy. Learns Q(s,a) directly.
- **Deep Q-Learning (DQN)**: Neural network approximation of Q-function. Experience replay, target networks.
- Best for: discrete action spaces, game-like environments.

### Policy-Based Methods

- **REINFORCE**: Monte Carlo policy gradient. Simple but high variance.
- Best for: continuous action spaces, stochastic policies.

### Actor-Critic Methods

- **A2C/A3C**: Combines value function (critic) with policy (actor). Lower variance than pure policy gradient.
- **PPO**: Clipped surrogate objective. Most widely used RL algorithm. Stable, general-purpose.
- Best for: most RL problems. PPO is the default starting point.

### Multi-Agent

- **Independent learners**: Each agent learns independently.
- **Centralized training, decentralized execution (CTDE)**: Train together, act independently.
- **Communication-based**: Agents share information during execution.

---

## Key Libraries

| Library | Purpose | Status |
|---------|---------|--------|
| Stable Baselines3 | Reliable RL algorithm implementations | Active, maintained |
| CleanRL | Single-file RL implementations for research | Active |
| Sample Factory | High-throughput multi-agent RL | Active |
| RL Baselines3 Zoo | Training configs and pretrained agents for SB3 | Active |
| Gymnasium | Standard environment API | Active (successor to OpenAI Gym) |
| PettingZoo | Multi-agent environment API | Active |

---

## Important Guardrails

1. **Course = benchmark curriculum only** — do not use as production-readiness standard
2. **Official library docs = implementation source of truth** — course may be outdated
3. **Repo evals = promotion gate** — no agent deploys without eval evidence
4. **AI vs AI unit is non-functional** — do not depend on it
5. **Leaderboard is no longer operational** — do not reference it as a live benchmark

---

## Use Cases (Benchmark Only)

| Use Case | Relevance to Platform |
|----------|----------------------|
| Game agents | Low — not core platform |
| Robotics control | Low — not core platform |
| Multi-agent coordination | Medium — relevant for agent orchestration patterns |
| Simulation-based training | Medium — relevant for agent testing |
| Reward design | High — applicable to agent evaluation |

---

## Sources

- [HF Deep RL Course](https://huggingface.co/learn/deep-rl-course/en/unit0/introduction)
- [Stable Baselines3](https://stable-baselines3.readthedocs.io/)
- [CleanRL](https://docs.cleanrl.dev/)
- [Sample Factory](https://www.samplefactory.dev/)

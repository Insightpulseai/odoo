# Checklist: Multi-Agent RL Design

## Problem Classification

- [ ] Number of agents defined
- [ ] Interaction type classified (cooperative, competitive, mixed)
- [ ] Agent homogeneity assessed (same capabilities or different)
- [ ] Observation type: local only, or global state available during training

## Paradigm Selection

- [ ] Paradigm chosen and justified (independent, CTDE, self-play, shared)
- [ ] If independent: non-stationarity acknowledged and mitigated
- [ ] If CTDE: global state access during training confirmed
- [ ] If self-play: opponent sampling strategy defined
- [ ] If shared policy: agent homogeneity verified

## Environment Design

- [ ] PettingZoo API used for standard environments
- [ ] Per-agent observation space defined
- [ ] Per-agent action space defined
- [ ] Episode termination conditions defined
- [ ] Agent ordering or simultaneity specified (turn-based vs parallel)

## Reward Design

- [ ] Individual rewards defined (if applicable)
- [ ] Team reward defined (if cooperative)
- [ ] Reward credit assignment considered
- [ ] No incentive for agents to sabotage teammates (if cooperative)
- [ ] Competitive reward is zero-sum or appropriate

## Training Configuration

- [ ] Algorithm selected per agent (PPO default)
- [ ] Policy sharing configured (if applicable)
- [ ] Communication mechanism designed (if applicable)
- [ ] Opponent sampling strategy set (if self-play)
- [ ] Curriculum or difficulty progression planned

## Evaluation

- [ ] Agents evaluated against fixed baselines (random, heuristic)
- [ ] Agents evaluated against each other
- [ ] Cooperation metrics tracked (if cooperative)
- [ ] Elo or ranking system (if competitive)
- [ ] Robustness to new opponents tested

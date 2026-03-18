# Evals: Multi-Agent RL Design

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Agents learn | Required | Performance improves over training |
| Coordination emerges (cooperative) | Required | Team outperforms independent baselines |
| Robust to opponents (competitive) | High | Beats fixed heuristic opponents |
| Paradigm justified | High | Choice of independent/CTDE/self-play explained |
| Non-stationarity addressed | Medium | Acknowledged and mitigated |
| Reward credit assignment | Medium | Individual contributions tracked |

## Automated Checks

```python
# Cooperative: team performance
def eval_cooperative(policies, env, n_episodes=100):
    team_returns = []
    for _ in range(n_episodes):
        observations, _ = env.reset()
        total = 0
        while env.agents:
            actions = {a: policies[a].predict(observations[a])[0] for a in env.agents}
            observations, rewards, terms, truncs, infos = env.step(actions)
            total += sum(rewards.values())
        team_returns.append(total)
    return np.mean(team_returns), np.std(team_returns)

# Competitive: win rate
def eval_competitive(policy, opponent, env, n_episodes=100):
    wins = 0
    for _ in range(n_episodes):
        # Run episode, track winner
        winner = run_episode(policy, opponent, env)
        if winner == "policy":
            wins += 1
    return wins / n_episodes
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Agents do not coordinate | No incentive for cooperation | Add team reward component |
| Strategy cycling (self-play) | Opponent sampling too narrow | Sample from wider history |
| One agent dominates | Asymmetric capabilities/rewards | Rebalance reward or handicap |
| Training instability | Non-stationarity | Use CTDE, slow opponent updates |
| All agents converge to same behavior | Shared policy too constraining | Use independent policies |
| Poor generalization | Overfit to specific opponents | Diversify training opponents |

## Promotion Gate

Multi-agent RL design passes when:
1. Cooperative: team performance exceeds independent agent baseline
2. Competitive: trained agent beats heuristic opponents > 60% of the time
3. Self-play: Elo rating increases over training checkpoints
4. No catastrophic strategy cycling observed
5. Paradigm choice is documented and justified
6. Non-stationarity concerns are addressed

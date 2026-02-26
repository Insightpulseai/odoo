# GitHub Docs Skill

This skill answers GitHub-related questions using only official GitHub documentation (`docs.github.com`) as the authoritative source.

## What it covers

- REST API concepts, endpoints, pagination, auth, and rate limiting
- GraphQL schema usage, costs, and limits
- Webhooks event types, payloads, delivery validation patterns
- GitHub Actions events & workflow triggers (when relevant)

## Non-goals

- "Best tool" opinions not grounded in docs
- Unverified third-party blog patterns unless explicitly requested

## Reproducible Index

The index is built deterministically via `scripts/ingest_docs.py`, converting official docs to a version-controlled semantic snapshot. Evaualations in `evals/eval_cases.yaml` guarantee the skill grounds rate limits and event definitions correctly before usage.

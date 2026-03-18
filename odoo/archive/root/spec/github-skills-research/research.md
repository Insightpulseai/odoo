# Deep Research: GitHub Developer Ecosystem for Agentic Skills

## Overview

This research catalogs the primary GitHub surfaces—REST API, GraphQL API, GitHub Apps, and GitHub Actions—to determine how they can be indexed and utilized as atomic blocks for building agentic skills.

## Core Capabilities Found

### 1. REST & GraphQL APIs (`https://docs.github.com/en/rest`, `https://docs.github.com/en/graphql`)

- **Capabilities**: Repository management, code scanning, issue/PR management, releases, dependency graphs, secret scanning, code security settings.
- **Agentic Value**: The REST API is the primary execution layer for agent skills. Agents can fetch PR diffs, dispatch workflow runs, list artifacts, and comment on reviews using standard HTTP/JSON contracts.
- **Auth Patterns**: Personal Access Tokens (PATs Classic/Fine-grained) and GitHub App installation tokens.

### 2. GitHub Apps (`https://docs.github.com/en/apps`)

- **Capabilities**: Responding to webhooks, acting on behalf of users or as a bot, issuing short-lived server-to-server installation tokens, integrating deeply into the GitHub UI (e.g., checks API, deployment API).
- **Agentic Value**: Building autonomous agents that listen to repository events (e.g., `issue_comment` for slash commands, `pull_request` for auto-reviews). Apps provide the strictest security boundary (fine-grained repo permissions) compared to PATs.

### 3. GitHub Actions (`https://docs.github.com/en/actions`)

- **Capabilities**: CI/CD workflows, custom workflow templates, composite actions, container actions.
- **Agentic Value**: Actions can serve as the execution environments or "tools" themselves. An agent can dispatch an action (via `workflow_dispatch`), monitor its status via REST API, and retrieve the logs to form a feedback loop.

## Architectural Recommendations for Agent Skills

1. **GitHub App-First**: Prefer GitHub Apps over PATs for agent integrations. Generate short-lived tokens scoped strictly to the repositories needed.
2. **Webhooks as Triggers**: Use GitHub App webhooks to wake up the agent orchestration server rather than polling APIs.
3. **Actions as Compute**: Use GitHub Actions for heavy, prolonged computational tasks (like compiling code or running test suites), passing control asynchronously back to the agent via REST callbacks.

## Assumptions & Open Questions

- **Assumption**: GitHub Enterprise Server parity is not strictly required initially (cloud GitHub.com is the assumed target).
- **Open Question**: What is the strict token budget available for agent-initiated requests before triggering GitHub API Rate Limits?
- **Open Question**: Should agents construct their own GitHub Actions (YAML generation) dynamically, or should they only invoke pre-approved workflows?

## Recommended Next Actions

- [ ] Scaffold a new `ipai_github_agent` or MCP server utilizing Octokit.
- [ ] Implement a webhook ingress controller to parse GitHub App events.
- [ ] Map explicit REST API scopes required for core PR review tasks.

# Agent Operating Contract (SSOT)

## Canonical Workflow
1) Read Spec Kit (spec/<slug>/*) + spec/platforms/*
2) Implement scripts + config deterministically
3) Add tests + drift checks
4) Update runbooks
5) CI must reproduce locally with scripts/ci/run_all.sh

## Required outputs for any platform change
- Apply commands
- Test/verify commands
- Deploy/rollback commands
- Production validation commands

## Where to write things
- specs: spec/
- runbooks: docs/runbooks/
- scripts: scripts/
- workflows: .github/workflows/

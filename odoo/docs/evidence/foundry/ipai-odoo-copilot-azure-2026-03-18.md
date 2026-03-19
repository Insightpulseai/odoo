# Microsoft Foundry evidence for Odoo Copilot

## Evidence date

2026-03-18

## Workspace

data-intel-ph

## Agent

ipai-odoo-copilot-azure

## Confirmed

- Foundry workspace reachable
- agent exists
- Build/Preview surface visible
- model shown: gpt-4.1
- instructions present: IPAI Odoo Copilot — System Instructions v5
- tools present: File search, Code interpreter
- knowledge attached: ipai-odoo-knowledge-base
- saved revision shown: v7

## Classification

- evidence class: foundry agent configuration proof
- result: PASS

## Not yet proven

- publish state
- live endpoint usage from Odoo
- Odoo runtime auth/config binding
- production end-to-end invocation

## Verification matrix

| Control | Status | Notes |
|---------|--------|-------|
| Foundry workspace exists | PASS | data-intel-ph visible |
| Copilot agent exists | PASS | ipai-odoo-copilot-azure in Build |
| Agent has instructions | PASS | System Instructions v5 |
| Agent has tools | PASS | File search + Code interpreter |
| Agent has knowledge | PASS | ipai-odoo-knowledge-base |
| Preview surface exists | PASS | Interactive testing available |
| Publication state proven | PARTIAL | Not evidenced as completed |
| Odoo-to-Foundry invocation | FAIL | No runtime call evidence |
| Full copilot chain complete | FAIL | 3 bridge modules missing |

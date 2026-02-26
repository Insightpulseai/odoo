# Sub-Agent Registry

This directory contains the SSOT definitions for our 3 specialist sub-agents: `git-expert`, `devops-expert`, and `repo-expert`.
These agents function cooperatively under a unified coordinator orchestrator.

## How to add future sub-agents

1. Add a new block to `registry.yaml` with the agent's `id`, `name`, `scope`, `ssot` paths, `tools`, and `output_contract`.
2. Add a clear routing trigger block for the agent to `router.md` so the main orchestrator knows when to invoke it.
3. Ensure the agent adheres strictly to the layout defined in `output_contract.md` (mandating minimal diffs, a relay prompt, and verification checklists).
4. Do not recreate overlapping boundaries; if scope blurs, prefer expanding an existing expert's `ssot` over inventing a new persona.

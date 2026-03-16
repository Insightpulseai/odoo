# Local LLM Routing Policy

## Procedural Skills + Routing

Procedural skills MUST be executed deterministically. Local SLMs may be used ONLY for:

- manifest parsing / validation summaries
- dependency graph toposort
- log classification (traceback detection, known failure signatures)
  All state-changing actions (deploy/restart/install) are executed by the runtime executor and audited.
  Agents may not override router decisions.

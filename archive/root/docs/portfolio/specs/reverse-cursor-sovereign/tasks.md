# Tasks — Cursor Sovereign

## Spec Kit
- [ ] Validate Spec Kit structure exists and is linked from repo index
- [ ] Add "Docs as product" outline to docs nav

## Context Snapshot
- [ ] Implement merkle snapshot generator CLI
- [ ] Implement ignore rules: .gitignore + .cursorignore + custom ignore
- [ ] Emit context.json + ignore_report.json
- [ ] Add verify command (CI-safe)

## Gates
- [ ] Create gate catalog schema (YAML/JSON)
- [ ] Implement preflight gate runner
- [ ] Implement full gate runner
- [ ] Add forbidden enterprise module gate
- [ ] Add secret scanning gate
- [ ] Add lint gate
- [ ] Add unit test gate
- [ ] Add docs drift gate
- [ ] Add seed drift gate

## Prompt Builder (Self-hostable)
- [ ] Scaffold service (Docker)
- [ ] Add enterprise LLM connector interface
- [ ] Add Azure/OpenAI/Anthropic implementations
- [ ] Add policy enforcement (allowlists)
- [ ] Add run manifest emitter

## Agent Integration
- [ ] Implement run loop: snapshot -> plan -> execute -> gate -> emit artifacts
- [ ] Add PR bundle output format (diff + manifests + proofs)

## Docs
- [ ] Add docs pages: Architecture, Security, Data Flow, Gate Catalog, Runbooks
- [ ] Add Primer tokens stylesheet
- [ ] Add examples: "Agent refactor PR" walkthrough (CLI-only)

## Release
- [ ] Tag v0.1.0 (spec + snapshot + gates)
- [ ] Tag v0.2.0 (prompt builder + direct-route)

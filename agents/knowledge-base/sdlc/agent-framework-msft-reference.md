# Microsoft Agent Framework — Reference Architecture

source: https://github.com/microsoft/agent-framework
extracted: 2026-03-15

## Overview
MIT-licensed, 7.2k stars. Python + .NET. Official replacement for both Semantic Kernel and AutoGen for agent orchestration.

## Capability comparison with IPAI stack

| Capability | Agent Framework | IPAI current stack |
|---|---|---|
| Graph-based workflows | Native | n8n (linear/branching) |
| Multi-agent orchestration | Native | Manual via n8n + Claude |
| Streaming + checkpointing | Built-in | Custom Supabase queues |
| Human-in-the-loop | Built-in | Custom review tables |
| Time-travel / replay | Built-in | ops.run_events (DIY) |
| OpenTelemetry observability | Built-in | DIY via OTLP |
| Self-hosted / portable | MIT, no Foundry required | Yes |
| Provider-agnostic (Claude, etc.) | Multi-provider | Claude-first |

## SSOT/SOR integration pattern

```
Agent Framework (orchestration layer)
        ↓ emits run events / artifacts
Supabase ops.* (SSOT / control plane)
        ↓ posts accounting artifacts
Odoo (SOR / ledger)
```

Use `ops.runs` + `ops.run_events` as backing store for AF checkpointing.
AF stays stateless executor; Supabase canonical for orchestration state.

## Adoption posture
- 589 open issues — pre-1.0, pin versions
- Use as reference architecture for agent sequencing and observability patterns
- Not wholesale adoption — targeted replacement for agentic layer only
- Keep n8n for pure integration/webhook routing where simpler

# PRD: MAF Orchestration Layer

## Problem
Single-agent architecture limits the platform's ability to handle complex multi-step workflows (close orchestration, compliance, planning) with proper delegation, checkpointing, and observability.

## Solution
Introduce a multi-agent orchestration layer using Microsoft Agent Framework, with a coordinator/specialist decomposition pattern inspired by Google ADK.

## Target Users
- Internal operators managing monthly close
- Compliance teams tracking BIR deadlines
- Platform administrators monitoring agent health

## Requirements
1. Coordinator agent routes requests to appropriate specialists
2. Specialist agents handle domain-specific reasoning
3. Graph-based workflow execution with checkpointing
4. OpenTelemetry tracing for all orchestrated flows
5. Human-in-the-loop gates for mutations
6. Shared state model across agent boundaries
7. Graceful degradation to single-agent Foundry mode

## Non-Goals
- Replacing the public landing-page chat (stays on Foundry)
- Building a general-purpose agent framework
- Supporting non-Azure runtimes in Phase 1

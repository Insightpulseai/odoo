---
name: pulser-run-trace
description: Managed Agents "Session" harness for Pulser. Interrogates ops.run_events for persistent context, recovery, and replay. Features Brain-Hands decoupling for cattle-not-pets resilient execution.
disable-model-invocation: true
user-invocable: true
allowed-tools: Bash(python3 scripts/get_events.py), Read
---

# pulser-run-trace

This skill implements the IPAI "Session" layer, providing durable context and recovery paths for long-horizon agentic tasks.

## Managed Agent Recovery (wake(sessionId) pattern)
When a task harness fails or a container is replaced (cattle), this skill provides the \`resume_from_session(session_id)\` logic.
- **Recovery**: Fetches the last 5 events from \`ops.run_events\` for a specific session.
- **Resumption**: Re-initializes the harness state to the last successful checkpoint.

## Brain-Hands Decoupling
This skill virtualizes the event log:
- **Brain Interrogation**: Brain calls \`getEvents(id, limit, offset)\` to interrogate positional slices of history without bloating the context window.
- **Hands Logging**: Hands emit append-only events to the session log via this skill.

## Usage
- "resume from session smp-2026-04-12"
- "get history for run tbwa-ga-01"

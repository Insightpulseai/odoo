# State Checkpointing

State checkpointing for long-running agent sessions.

## Responsibilities

- Persist session state at defined checkpoints
- Restore session state on resume
- Enforce stateless-agent contract (state stored externally, never in-process)
- Support Azure-native storage backends (Blob Storage, Table Storage)

## Status

Stub implementation. See `index.ts` for interface definitions.

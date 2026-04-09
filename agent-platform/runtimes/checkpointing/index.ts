// State Checkpointing — persist and restore agent session state
// TODO: Implement Azure Blob/Table Storage backend for checkpoint persistence

export interface Checkpoint {
  sessionId: string;
  agentId: string;
  step: number;
  state: unknown;
  createdAt: string;
}

export class CheckpointStore {
  async save(checkpoint: Checkpoint): Promise<void> {
    // TODO: Persist to Azure Blob Storage or Table Storage
    throw new Error("NotImplemented: checkpoint save");
  }

  async restore(sessionId: string): Promise<Checkpoint | null> {
    // TODO: Restore latest checkpoint for session
    throw new Error("NotImplemented: checkpoint restore");
  }
}

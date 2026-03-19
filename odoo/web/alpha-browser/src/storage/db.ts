import Dexie, { type Table } from 'dexie';
import type { Mission, Checkpoint, MemoryEntry } from '@/shared/types';
import { loggers } from '@/shared/logger';

const logger = loggers.storage;

/**
 * IndexedDB schema for Alpha Browser
 * Stores missions, checkpoints, and long-term memory
 */
export class AlphaDB extends Dexie {
  missions!: Table<Mission, string>;
  checkpoints!: Table<Checkpoint, string>;
  memory!: Table<MemoryEntry, string>;

  constructor() {
    super('AlphaBrowserDB');

    this.version(1).stores({
      missions: 'id, status, createdAt, updatedAt',
      checkpoints: 'id, missionId, timestamp',
      memory: 'id, missionId, timestamp, tags'
    });
  }
}

// Singleton instance
export const db = new AlphaDB();

/**
 * Initialize database and run migrations
 */
export async function initDB(): Promise<void> {
  try {
    await db.open();
    logger.info('Database initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize database:', error);
    throw error;
  }
}

/**
 * Clear all data (for testing)
 */
export async function clearDB(): Promise<void> {
  await db.missions.clear();
  await db.checkpoints.clear();
  await db.memory.clear();
  logger.info('Database cleared');
}

/**
 * Get database statistics
 */
export async function getDBStats(): Promise<{
  missions: number;
  checkpoints: number;
  memory: number;
}> {
  return {
    missions: await db.missions.count(),
    checkpoints: await db.checkpoints.count(),
    memory: await db.memory.count()
  };
}

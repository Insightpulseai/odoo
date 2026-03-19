import { db } from './db';
import type { MemoryEntry } from '@/shared/types';
import { loggers } from '@/shared/logger';
import { generateId } from '@/shared/utils';

const logger = loggers.storage;

/**
 * Store memory entry (for RAG future enhancement)
 */
export async function storeMemory(
  missionId: string,
  content: string,
  tags: string[] = []
): Promise<MemoryEntry> {
  const entry: MemoryEntry = {
    id: generateId(),
    missionId,
    content,
    tags,
    timestamp: Date.now()
  };

  await db.memory.add(entry);
  logger.debug(`Memory stored for mission ${missionId}`);
  return entry;
}

/**
 * Search memory by tags
 */
export async function searchMemoryByTags(
  tags: string[],
  limit: number = 10
): Promise<MemoryEntry[]> {
  return db.memory
    .filter(entry => tags.some(tag => entry.tags.includes(tag)))
    .limit(limit)
    .reverse()
    .toArray();
}

/**
 * Get memory for mission
 */
export async function getMissionMemory(
  missionId: string
): Promise<MemoryEntry[]> {
  return db.memory
    .where('missionId')
    .equals(missionId)
    .toArray();
}

/**
 * Delete old memory entries
 */
export async function pruneMemory(days: number = 90): Promise<number> {
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;

  const toDelete = await db.memory
    .where('timestamp')
    .below(cutoff)
    .primaryKeys();

  await db.memory.bulkDelete(toDelete as string[]);
  logger.info(`Pruned ${toDelete.length} memory entries`);
  return toDelete.length;
}

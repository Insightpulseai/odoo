import { db } from './db';
import type { Checkpoint } from '@/shared/types';
import { loggers } from '@/shared/logger';
import { generateId } from '@/shared/utils';

const logger = loggers.storage;

/**
 * Save checkpoint (service worker state before suspension)
 */
export async function saveCheckpoint(
  missionId: string,
  state: unknown
): Promise<Checkpoint> {
  const checkpoint: Checkpoint = {
    id: generateId(),
    missionId,
    state,
    timestamp: Date.now()
  };

  await db.checkpoints.add(checkpoint);
  logger.debug(`Checkpoint saved for mission ${missionId}`);
  return checkpoint;
}

/**
 * Get latest checkpoint for mission
 */
export async function getLatestCheckpoint(
  missionId: string
): Promise<Checkpoint | undefined> {
  const checkpoints = await db.checkpoints
    .where('missionId')
    .equals(missionId)
    .sortBy('timestamp');

  return checkpoints.length > 0 ? checkpoints[checkpoints.length - 1] : undefined;
}

/**
 * List all checkpoints for mission
 */
export async function listCheckpoints(
  missionId: string
): Promise<Checkpoint[]> {
  return db.checkpoints
    .where('missionId')
    .equals(missionId)
    .reverse()
    .toArray();
}

/**
 * Delete old checkpoints (keep last N per mission)
 */
export async function pruneCheckpoints(
  missionId: string,
  keepLast: number = 5
): Promise<number> {
  const checkpoints = await listCheckpoints(missionId);

  if (checkpoints.length <= keepLast) {
    return 0;
  }

  const toDelete = checkpoints.slice(keepLast);
  const ids = toDelete.map(c => c.id);

  await db.checkpoints.bulkDelete(ids);
  logger.debug(`Pruned ${ids.length} checkpoints for mission ${missionId}`);
  return ids.length;
}

/**
 * Delete all checkpoints for mission
 */
export async function deleteCheckpoints(missionId: string): Promise<void> {
  await db.checkpoints.where('missionId').equals(missionId).delete();
  logger.debug(`Deleted all checkpoints for mission ${missionId}`);
}

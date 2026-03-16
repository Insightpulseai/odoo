import { db } from './db';
import type { Mission, MissionStatus } from '@/shared/types';
import { loggers } from '@/shared/logger';
import { generateId } from '@/shared/utils';

const logger = loggers.storage;

/**
 * Create a new mission
 */
export async function createMission(goal: string): Promise<Mission> {
  const mission: Mission = {
    id: generateId(),
    goal,
    status: 'pending',
    steps: [],
    createdAt: Date.now(),
    updatedAt: Date.now()
  };

  await db.missions.add(mission);
  logger.info(`Mission created: ${mission.id}`);
  return mission;
}

/**
 * Get mission by ID
 */
export async function getMission(id: string): Promise<Mission | undefined> {
  return db.missions.get(id);
}

/**
 * Update mission status
 */
export async function updateMissionStatus(
  id: string,
  status: MissionStatus
): Promise<void> {
  const updates: Partial<Mission> = {
    status,
    updatedAt: Date.now()
  };

  if (status === 'completed' || status === 'failed') {
    updates.completedAt = Date.now();
  }

  await db.missions.update(id, updates);
  logger.info(`Mission ${id} status updated to ${status}`);
}

/**
 * Update mission with new data
 */
export async function updateMission(
  id: string,
  updates: Partial<Mission>
): Promise<void> {
  await db.missions.update(id, {
    ...updates,
    updatedAt: Date.now()
  });
  logger.debug(`Mission ${id} updated`);
}

/**
 * List all missions
 */
export async function listMissions(
  filter?: {
    status?: MissionStatus;
    limit?: number;
  }
): Promise<Mission[]> {
  let query = db.missions.orderBy('createdAt').reverse();

  if (filter?.status) {
    query = query.filter(m => m.status === filter.status);
  }

  if (filter?.limit) {
    query = query.limit(filter.limit);
  }

  return query.toArray();
}

/**
 * Get active mission (if any)
 */
export async function getActiveMission(): Promise<Mission | undefined> {
  const active = await db.missions
    .where('status')
    .equals('active')
    .first();
  return active;
}

/**
 * Delete mission and associated checkpoints
 */
export async function deleteMission(id: string): Promise<void> {
  await db.transaction('rw', [db.missions, db.checkpoints], async () => {
    await db.missions.delete(id);
    await db.checkpoints.where('missionId').equals(id).delete();
  });
  logger.info(`Mission ${id} deleted`);
}

/**
 * Clean up completed missions older than specified days
 */
export async function cleanupOldMissions(days: number = 30): Promise<number> {
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;

  const toDelete = await db.missions
    .where('completedAt')
    .below(cutoff)
    .primaryKeys();

  await db.transaction('rw', [db.missions, db.checkpoints], async () => {
    for (const id of toDelete) {
      await db.missions.delete(id as string);
      await db.checkpoints.where('missionId').equals(id as string).delete();
    }
  });

  logger.info(`Cleaned up ${toDelete.length} old missions`);
  return toDelete.length;
}

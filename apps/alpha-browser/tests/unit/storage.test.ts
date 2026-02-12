import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { db, initDB, clearDB, getDBStats } from '@/storage/db';
import { createMission, getMission, updateMissionStatus, listMissions } from '@/storage/missions';
import { saveCheckpoint, getLatestCheckpoint } from '@/storage/checkpoints';

describe('Storage Layer', () => {
  beforeEach(async () => {
    await initDB();
    await clearDB();
  });

  afterEach(async () => {
    await clearDB();
  });

  describe('Database', () => {
    it('should initialize database', async () => {
      const stats = await getDBStats();
      expect(stats.missions).toBe(0);
      expect(stats.checkpoints).toBe(0);
      expect(stats.memory).toBe(0);
    });
  });

  describe('Missions', () => {
    it('should create a mission', async () => {
      const mission = await createMission('Fill out contact form');
      expect(mission.goal).toBe('Fill out contact form');
      expect(mission.status).toBe('pending');
      expect(mission.steps).toEqual([]);
    });

    it('should get mission by ID', async () => {
      const created = await createMission('Test goal');
      const retrieved = await getMission(created.id);
      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe(created.id);
      expect(retrieved?.goal).toBe('Test goal');
    });

    it('should update mission status', async () => {
      const mission = await createMission('Test goal');
      await updateMissionStatus(mission.id, 'active');

      const updated = await getMission(mission.id);
      expect(updated?.status).toBe('active');
    });

    it('should list missions', async () => {
      await createMission('Mission 1');
      await createMission('Mission 2');
      await createMission('Mission 3');

      const missions = await listMissions({ limit: 10 });
      expect(missions).toHaveLength(3);
    });

    it('should filter missions by status', async () => {
      const m1 = await createMission('Mission 1');
      const m2 = await createMission('Mission 2');
      await updateMissionStatus(m1.id, 'completed');

      const active = await listMissions({ status: 'pending' });
      expect(active).toHaveLength(1);
      expect(active[0].id).toBe(m2.id);
    });
  });

  describe('Checkpoints', () => {
    it('should save checkpoint', async () => {
      const mission = await createMission('Test goal');
      const state = { step: 1, data: 'test' };

      const checkpoint = await saveCheckpoint(mission.id, state);
      expect(checkpoint.missionId).toBe(mission.id);
      expect(checkpoint.state).toEqual(state);
    });

    it('should get latest checkpoint', async () => {
      const mission = await createMission('Test goal');

      await saveCheckpoint(mission.id, { step: 1 });
      await new Promise(resolve => setTimeout(resolve, 10)); // Ensure different timestamps
      await saveCheckpoint(mission.id, { step: 2 });

      const latest = await getLatestCheckpoint(mission.id);
      expect(latest).toBeDefined();
      expect((latest?.state as { step: number }).step).toBe(2);
    });
  });
});

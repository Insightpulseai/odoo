import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listMissions, createMission, updateMissionStatus } from '@/storage/missions';
import type { Mission } from '@/shared/types';

export function App() {
  const [newMissionGoal, setNewMissionGoal] = useState('');
  const queryClient = useQueryClient();

  // Fetch missions
  const { data: missions = [], isLoading } = useQuery({
    queryKey: ['missions'],
    queryFn: () => listMissions({ limit: 10 })
  });

  // Create mission mutation
  const createMissionMutation = useMutation({
    mutationFn: (goal: string) => createMission(goal),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['missions'] });
      setNewMissionGoal('');
    }
  });

  // Update mission status mutation
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: Mission['status'] }) =>
      updateMissionStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['missions'] });
    }
  });

  const handleCreateMission = (e: React.FormEvent) => {
    e.preventDefault();
    if (newMissionGoal.trim()) {
      createMissionMutation.mutate(newMissionGoal.trim());
    }
  };

  return (
    <div className="popup-container">
      <header className="popup-header">
        <h1>Alpha Browser</h1>
        <p className="subtitle">Vision-First Browser Automation</p>
      </header>

      <section className="mission-form">
        <form onSubmit={handleCreateMission}>
          <input
            type="text"
            value={newMissionGoal}
            onChange={(e) => setNewMissionGoal(e.target.value)}
            placeholder="Describe what you want to do..."
            className="mission-input"
            disabled={createMissionMutation.isPending}
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={createMissionMutation.isPending || !newMissionGoal.trim()}
          >
            {createMissionMutation.isPending ? 'Creating...' : 'Create Mission'}
          </button>
        </form>
      </section>

      <section className="missions-list">
        <h2>Recent Missions</h2>

        {isLoading && <p className="loading">Loading missions...</p>}

        {!isLoading && missions.length === 0 && (
          <p className="empty-state">No missions yet. Create your first mission above!</p>
        )}

        {!isLoading && missions.length > 0 && (
          <div className="mission-items">
            {missions.map((mission) => (
              <div key={mission.id} className={`mission-item status-${mission.status}`}>
                <div className="mission-header">
                  <h3 className="mission-goal">{mission.goal}</h3>
                  <span className={`status-badge ${mission.status}`}>
                    {mission.status}
                  </span>
                </div>

                <div className="mission-meta">
                  <span className="mission-date">
                    {new Date(mission.createdAt).toLocaleString()}
                  </span>
                  {mission.steps.length > 0 && (
                    <span className="mission-steps">
                      {mission.steps.filter(s => s.status === 'completed').length}/{mission.steps.length} steps
                    </span>
                  )}
                </div>

                {mission.status === 'pending' && (
                  <button
                    onClick={() =>
                      updateStatusMutation.mutate({ id: mission.id, status: 'active' })
                    }
                    className="btn-secondary"
                    disabled={updateStatusMutation.isPending}
                  >
                    Start
                  </button>
                )}

                {mission.status === 'active' && (
                  <button
                    onClick={() =>
                      updateStatusMutation.mutate({ id: mission.id, status: 'paused' })
                    }
                    className="btn-secondary"
                    disabled={updateStatusMutation.isPending}
                  >
                    Pause
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      <footer className="popup-footer">
        <p className="version">v0.1.0 - Phase 1 Foundation</p>
      </footer>
    </div>
  );
}

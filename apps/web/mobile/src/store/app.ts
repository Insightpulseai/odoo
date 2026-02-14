/**
 * App Store - Global State Management
 * Using Zustand for React Native
 */

import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import AsyncStorage from '@react-native-async-storage/async-storage'
import { Job, ApprovalRequest, Employee, JobStats, ApprovalStats } from '../types/database'

interface AppState {
  // Auth
  user: Employee | null
  isAuthenticated: boolean
  setUser: (user: Employee | null) => void

  // Jobs
  jobs: Job[]
  jobStats: JobStats | null
  setJobs: (jobs: Job[]) => void
  updateJob: (job: Job) => void
  setJobStats: (stats: JobStats) => void

  // Approvals
  approvals: ApprovalRequest[]
  approvalStats: ApprovalStats | null
  setApprovals: (approvals: ApprovalRequest[]) => void
  updateApproval: (approval: ApprovalRequest) => void
  setApprovalStats: (stats: ApprovalStats) => void

  // Offline queue
  offlineQueue: OfflineAction[]
  addToOfflineQueue: (action: OfflineAction) => void
  removeFromOfflineQueue: (id: string) => void
  clearOfflineQueue: () => void

  // Network
  isOnline: boolean
  setIsOnline: (online: boolean) => void
  lastSyncAt: string | null
  setLastSyncAt: (timestamp: string) => void

  // UI
  isDarkMode: boolean
  toggleDarkMode: () => void
}

interface OfflineAction {
  id: string
  type: 'approve' | 'reject' | 'update' | 'create'
  entity: 'approval' | 'expense' | 'task'
  entityId: string
  payload: Record<string, unknown>
  createdAt: string
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // Auth
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),

      // Jobs
      jobs: [],
      jobStats: null,
      setJobs: (jobs) => set({ jobs }),
      updateJob: (job) => set((state) => ({
        jobs: state.jobs.map((j) => j.id === job.id ? job : j)
      })),
      setJobStats: (stats) => set({ jobStats: stats }),

      // Approvals
      approvals: [],
      approvalStats: null,
      setApprovals: (approvals) => set({ approvals }),
      updateApproval: (approval) => set((state) => ({
        approvals: state.approvals.map((a) => a.id === approval.id ? approval : a)
      })),
      setApprovalStats: (stats) => set({ approvalStats: stats }),

      // Offline queue
      offlineQueue: [],
      addToOfflineQueue: (action) => set((state) => ({
        offlineQueue: [...state.offlineQueue, action]
      })),
      removeFromOfflineQueue: (id) => set((state) => ({
        offlineQueue: state.offlineQueue.filter((a) => a.id !== id)
      })),
      clearOfflineQueue: () => set({ offlineQueue: [] }),

      // Network
      isOnline: true,
      setIsOnline: (online) => set({ isOnline: online }),
      lastSyncAt: null,
      setLastSyncAt: (timestamp) => set({ lastSyncAt: timestamp }),

      // UI
      isDarkMode: true,
      toggleDarkMode: () => set((state) => ({ isDarkMode: !state.isDarkMode })),
    }),
    {
      name: 'insightpulse-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({
        user: state.user,
        isDarkMode: state.isDarkMode,
        offlineQueue: state.offlineQueue,
        lastSyncAt: state.lastSyncAt,
      }),
    }
  )
)

// Selectors
export const selectPendingApprovals = (state: AppState) =>
  state.approvals.filter((a) => a.status === 'pending')

export const selectRecentJobs = (state: AppState) =>
  state.jobs.slice(0, 20)

export const selectOfflineQueueCount = (state: AppState) =>
  state.offlineQueue.length

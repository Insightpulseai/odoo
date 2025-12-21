/**
 * Real-time Subscription Hooks
 * Manages Supabase Realtime subscriptions
 */

import { useEffect, useCallback } from 'react'
import { supabase, subscribeToJobs, subscribeToApprovals } from '../lib/supabase'
import { useAppStore } from '../store/app'
import { Job, ApprovalRequest } from '../types/database'

// Hook for real-time job updates
export function useRealtimeJobs() {
  const { setJobs, updateJob } = useAppStore()

  useEffect(() => {
    // Initial fetch
    fetchJobs()

    // Subscribe to changes
    const subscription = subscribeToJobs((payload) => {
      if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
        updateJob(payload.new as Job)
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  const fetchJobs = useCallback(async () => {
    const { data, error } = await supabase
      .from('control_room_jobs')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(100)

    if (!error && data) {
      setJobs(data as Job[])
    }
  }, [setJobs])

  return { refetch: fetchJobs }
}

// Hook for real-time approval updates
export function useRealtimeApprovals() {
  const { setApprovals, updateApproval, user } = useAppStore()

  useEffect(() => {
    if (!user) return

    // Initial fetch
    fetchApprovals()

    // Subscribe to changes
    const subscription = subscribeToApprovals((payload) => {
      if (payload.eventType === 'INSERT' || payload.eventType === 'UPDATE') {
        const approval = payload.new as ApprovalRequest
        // Only update if assigned to current user
        if (approval.assigned_to === user.id) {
          updateApproval(approval)
        }
      }
    })

    return () => {
      subscription.unsubscribe()
    }
  }, [user?.id])

  const fetchApprovals = useCallback(async () => {
    if (!user) return

    const { data, error } = await supabase
      .from('approval_requests')
      .select('*')
      .eq('assigned_to', user.id)
      .order('created_at', { ascending: false })
      .limit(50)

    if (!error && data) {
      setApprovals(data as ApprovalRequest[])
    }
  }, [user, setApprovals])

  return { refetch: fetchApprovals }
}

// Hook for job statistics
export function useJobStats() {
  const { setJobStats, jobStats } = useAppStore()

  const fetchStats = useCallback(async () => {
    const today = new Date().toISOString().split('T')[0]

    const { data, error } = await supabase
      .from('control_room_jobs')
      .select('status')
      .gte('created_at', today)

    if (!error && data) {
      const stats = {
        running: data.filter(j => j.status === 'running').length,
        succeeded: data.filter(j => j.status === 'success').length,
        failed: data.filter(j => j.status === 'failed').length,
        queued: data.filter(j => j.status === 'pending').length,
        total_today: data.length,
        success_rate: data.length > 0
          ? (data.filter(j => j.status === 'success').length / data.length) * 100
          : 0
      }
      setJobStats(stats)
    }
  }, [setJobStats])

  useEffect(() => {
    fetchStats()
    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [fetchStats])

  return { stats: jobStats, refetch: fetchStats }
}

// Hook for approval statistics
export function useApprovalStats() {
  const { setApprovalStats, approvalStats, user } = useAppStore()

  const fetchStats = useCallback(async () => {
    if (!user) return

    const today = new Date().toISOString().split('T')[0]

    const [pending, approved, rejected] = await Promise.all([
      supabase
        .from('approval_requests')
        .select('id', { count: 'exact', head: true })
        .eq('assigned_to', user.id)
        .eq('status', 'pending'),
      supabase
        .from('approval_requests')
        .select('id', { count: 'exact', head: true })
        .eq('approved_by', user.id)
        .gte('updated_at', today),
      supabase
        .from('approval_requests')
        .select('id', { count: 'exact', head: true })
        .eq('rejected_by', user.id)
        .gte('updated_at', today),
    ])

    const stats = {
      pending: pending.count || 0,
      approved_today: approved.count || 0,
      rejected_today: rejected.count || 0,
      avg_approval_time_hours: 4.2 // TODO: Calculate from actual data
    }
    setApprovalStats(stats)
  }, [user, setApprovalStats])

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 60000)
    return () => clearInterval(interval)
  }, [fetchStats])

  return { stats: approvalStats, refetch: fetchStats }
}

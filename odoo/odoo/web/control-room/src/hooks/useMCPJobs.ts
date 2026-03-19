'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { supabase, type MCPJob, type MCPJobStats } from '@/lib/supabase';

interface UseJobsOptions {
  source?: string;
  status?: string;
  jobType?: string;
  limit?: number;
  enableRealtime?: boolean;
}

export function useMCPJobs(options: UseJobsOptions = {}) {
  const queryClient = useQueryClient();
  const { source, status, jobType, limit = 50, enableRealtime = true } = options;

  const query = useQuery({
    queryKey: ['mcp-jobs', { source, status, jobType, limit }],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (source) params.set('source', source);
      if (status) params.set('status', status);
      if (jobType) params.set('jobType', jobType);
      params.set('limit', String(limit));

      const res = await fetch(`/api/mcp-jobs?${params}`);
      if (!res.ok) throw new Error('Failed to fetch jobs');
      return res.json() as Promise<MCPJob[]>;
    },
    refetchInterval: enableRealtime ? false : 30000,
  });

  // Realtime subscription for job updates
  useEffect(() => {
    if (!enableRealtime) return;

    const channel = supabase
      .channel('mcp_jobs_changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'mcp_jobs',
          table: 'jobs',
        },
        () => {
          queryClient.invalidateQueries({ queryKey: ['mcp-jobs'] });
          queryClient.invalidateQueries({ queryKey: ['mcp-jobs-stats'] });
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [queryClient, enableRealtime]);

  return query;
}

export function useMCPJobStats() {
  return useQuery({
    queryKey: ['mcp-jobs-stats'],
    queryFn: async () => {
      const res = await fetch('/api/mcp-jobs/stats');
      if (!res.ok) throw new Error('Failed to fetch job stats');
      return res.json() as Promise<MCPJobStats>;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });
}

interface EnqueueJobInput {
  source: string;
  jobType: string;
  payload?: Record<string, unknown>;
  priority?: number;
}

export function useEnqueueJob() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: EnqueueJobInput) => {
      const res = await fetch('/api/mcp-jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.message || 'Failed to enqueue job');
      }

      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mcp-jobs'] });
      queryClient.invalidateQueries({ queryKey: ['mcp-jobs-stats'] });
    },
  });
}

// Helper to get job by ID
export function useMCPJob(jobId: string | null) {
  return useQuery({
    queryKey: ['mcp-job', jobId],
    queryFn: async () => {
      if (!jobId) return null;

      const res = await fetch(`/api/mcp-jobs/${jobId}`);
      if (!res.ok) throw new Error('Failed to fetch job');
      return res.json() as Promise<MCPJob>;
    },
    enabled: !!jobId,
  });
}

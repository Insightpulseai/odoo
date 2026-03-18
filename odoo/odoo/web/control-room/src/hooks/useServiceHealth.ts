'use client';

import { useQuery } from '@tanstack/react-query';
import type { ServiceHealth } from '@/lib/supabase';

interface HealthResponse {
  status: 'healthy' | 'degraded' | 'down' | 'error';
  healthy: number;
  total: number;
  services: ServiceHealth[];
  timestamp: string;
  error?: string;
}

export function useServiceHealth(options?: { refetchInterval?: number }) {
  return useQuery({
    queryKey: ['service-health'],
    queryFn: async () => {
      const res = await fetch('/api/health');
      if (!res.ok) throw new Error('Failed to fetch health status');
      return res.json() as Promise<HealthResponse>;
    },
    refetchInterval: options?.refetchInterval ?? 15000, // Default 15s
    staleTime: 10000, // Consider data stale after 10s
  });
}

// Get health for a specific service
export function useServiceHealthByName(serviceName: string) {
  const { data, ...rest } = useServiceHealth();

  const service = data?.services.find((s) => s.name === serviceName);

  return {
    ...rest,
    data: service,
    overallStatus: data?.status,
  };
}

// Helper to determine status color
export function getStatusColor(
  status: 'healthy' | 'unhealthy' | 'unreachable' | 'degraded' | 'down' | 'error'
): string {
  switch (status) {
    case 'healthy':
      return 'text-green-500';
    case 'degraded':
    case 'unhealthy':
      return 'text-yellow-500';
    case 'unreachable':
    case 'down':
    case 'error':
      return 'text-red-500';
    default:
      return 'text-gray-500';
  }
}

// Helper to determine status badge variant
export function getStatusBadgeVariant(
  status: 'healthy' | 'unhealthy' | 'unreachable' | 'degraded' | 'down' | 'error'
): 'success' | 'warning' | 'error' | 'default' {
  switch (status) {
    case 'healthy':
      return 'success';
    case 'degraded':
    case 'unhealthy':
      return 'warning';
    case 'unreachable':
    case 'down':
    case 'error':
      return 'error';
    default:
      return 'default';
  }
}

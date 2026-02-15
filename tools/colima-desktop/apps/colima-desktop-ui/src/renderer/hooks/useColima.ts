import { useState, useEffect, useCallback } from 'react';
import type {
  StatusResponse,
  ColimaConfig,
  ConfigUpdateRequest,
  ConfigUpdateResponse,
  LogsRequest,
  LogsResponse,
} from '../../../../../src/shared/contracts/index.js';

interface UseStatusResult {
  status: StatusResponse | null;
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
}

interface UseConfigResult {
  config: ColimaConfig | null;
  loading: boolean;
  error: Error | null;
  updateConfig: (updates: ConfigUpdateRequest) => Promise<ConfigUpdateResponse>;
  refresh: () => Promise<void>;
}

interface UseLogsResult {
  logs: string[];
  loading: boolean;
  error: Error | null;
  refresh: (request?: LogsRequest) => Promise<void>;
  totalLines: number;
  truncated: boolean;
}

export function useStatus(autoRefresh = true, intervalMs = 5000): UseStatusResult {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchStatus = useCallback(async () => {
    try {
      setError(null);
      const result = await window.colima.getStatus();
      setStatus(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch status'));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();

    if (autoRefresh) {
      const interval = setInterval(fetchStatus, intervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchStatus, autoRefresh, intervalMs]);

  return {
    status,
    loading,
    error,
    refresh: fetchStatus,
  };
}

export function useConfig(): UseConfigResult {
  const [config, setConfig] = useState<ColimaConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchConfig = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await window.colima.getConfig();
      setConfig(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch config'));
    } finally {
      setLoading(false);
    }
  }, []);

  const updateConfig = useCallback(async (updates: ConfigUpdateRequest): Promise<ConfigUpdateResponse> => {
    try {
      setError(null);
      const result = await window.colima.setConfig(updates);
      await fetchConfig();
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to update config');
      setError(error);
      throw error;
    }
  }, [fetchConfig]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  return {
    config,
    loading,
    error,
    updateConfig,
    refresh: fetchConfig,
  };
}

export function useLogs(
  request: LogsRequest = { tail: 200, source: 'colima' },
  autoRefresh = false,
  intervalMs = 2000
): UseLogsResult {
  const [logs, setLogs] = useState<string[]>([]);
  const [totalLines, setTotalLines] = useState(0);
  const [truncated, setTruncated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchLogs = useCallback(async (customRequest?: LogsRequest) => {
    const finalRequest = customRequest || request;

    try {
      if (logs.length === 0) {
        setLoading(true);
      }
      setError(null);
      const result: LogsResponse = await window.colima.tailLogs(finalRequest);
      setLogs(result.lines);
      setTotalLines(result.total_lines);
      setTruncated(result.truncated);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch logs'));
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [request, logs.length]);

  useEffect(() => {
    fetchLogs();

    if (autoRefresh) {
      const interval = setInterval(() => fetchLogs(), intervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchLogs, autoRefresh, intervalMs]);

  return {
    logs,
    loading,
    error,
    refresh: fetchLogs,
    totalLines,
    truncated,
  };
}

export function useLifecycle() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const start = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await window.colima.start();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to start Colima');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const stop = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await window.colima.stop();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to stop Colima');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const restart = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      await window.colima.restart();
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to restart Colima');
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    start,
    stop,
    restart,
    loading,
    error,
  };
}

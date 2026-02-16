import { useState, useEffect } from 'react';
import type { StatusResponse, ColimaConfig } from '../../shared/types';

export function useStatus() {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await window.colima.status();
        setStatus(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return { status, loading, error };
}

export function useConfig() {
  const [config, setConfig] = useState<ColimaConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchConfig = async () => {
    try {
      const data = await window.colima.getConfig();
      setConfig(data);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  const updateConfig = async (newConfig: Partial<ColimaConfig>) => {
    try {
      const result = await window.colima.setConfig(newConfig);
      await fetchConfig();
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  return { config, loading, error, updateConfig, refetch: fetchConfig };
}

export function useLogs(source: 'colima' | 'lima' | 'daemon', tail = 200) {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const data = await window.colima.tailLogs({ tail, source });
        setLogs(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 2000);
    return () => clearInterval(interval);
  }, [source, tail]);

  return { logs, loading, error };
}

export function useLifecycle() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const start = async (opts?: any) => {
    setLoading(true);
    setError(null);
    try {
      await window.colima.start(opts);
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const stop = async () => {
    setLoading(true);
    setError(null);
    try {
      await window.colima.stop();
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const restart = async (opts?: any) => {
    setLoading(true);
    setError(null);
    try {
      await window.colima.restart(opts);
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { start, stop, restart, loading, error };
}

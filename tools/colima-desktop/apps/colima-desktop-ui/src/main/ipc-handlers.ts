import { ipcMain, BrowserWindow } from 'electron';
import type {
  StatusResponse,
  ConfigResponse,
  ConfigUpdateRequest,
  ConfigUpdateResponse,
  LogsRequest,
  LogsResponse,
  DiagnosticsResponse,
  LifecycleRequest,
  LifecycleResponse,
} from '../../../../src/shared/contracts/index.js';
import { IPCChannel } from '../../../../src/shared/contracts/index.js';

/**
 * Daemon REST API Configuration
 */
const DAEMON_BASE_URL = 'http://localhost:35100';
const API_VERSION = 'v1';

/**
 * Status change polling interval (5 seconds)
 */
const STATUS_POLL_INTERVAL = 5000;

/**
 * Make REST API call to daemon
 */
async function daemonRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${DAEMON_BASE_URL}/${API_VERSION}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: response.statusText }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Daemon request failed: ${error.message}`);
    }
    throw new Error('Daemon request failed: Unknown error');
  }
}

/**
 * Status Handler
 * GET /v1/status
 */
ipcMain.handle(IPCChannel.STATUS, async (): Promise<StatusResponse> => {
  return daemonRequest<StatusResponse>('/status');
});

/**
 * Start Handler
 * POST /v1/lifecycle/start
 */
ipcMain.handle(
  IPCChannel.START,
  async (_event, opts?: LifecycleRequest): Promise<LifecycleResponse> => {
    return daemonRequest<LifecycleResponse>('/lifecycle/start', {
      method: 'POST',
      body: opts ? JSON.stringify(opts) : undefined,
    });
  }
);

/**
 * Stop Handler
 * POST /v1/lifecycle/stop
 */
ipcMain.handle(IPCChannel.STOP, async (): Promise<LifecycleResponse> => {
  return daemonRequest<LifecycleResponse>('/lifecycle/stop', {
    method: 'POST',
  });
});

/**
 * Restart Handler
 * POST /v1/lifecycle/restart
 */
ipcMain.handle(
  IPCChannel.RESTART,
  async (_event, opts?: LifecycleRequest): Promise<LifecycleResponse> => {
    return daemonRequest<LifecycleResponse>('/lifecycle/restart', {
      method: 'POST',
      body: opts ? JSON.stringify(opts) : undefined,
    });
  }
);

/**
 * Get Config Handler
 * GET /v1/config
 */
ipcMain.handle(IPCChannel.GET_CONFIG, async (): Promise<ConfigResponse> => {
  return daemonRequest<ConfigResponse>('/config');
});

/**
 * Set Config Handler
 * PUT /v1/config
 */
ipcMain.handle(
  IPCChannel.SET_CONFIG,
  async (_event, cfg: ConfigUpdateRequest): Promise<ConfigUpdateResponse> => {
    // Validate payload
    if (!cfg || typeof cfg !== 'object') {
      throw new Error('Invalid config payload');
    }

    return daemonRequest<ConfigUpdateResponse>('/config', {
      method: 'PUT',
      body: JSON.stringify(cfg),
    });
  }
);

/**
 * Tail Logs Handler
 * GET /v1/logs?tail=N&source=colima
 */
ipcMain.handle(
  IPCChannel.TAIL_LOGS,
  async (_event, opts?: LogsRequest): Promise<LogsResponse> => {
    const params = new URLSearchParams();

    if (opts?.tail !== undefined) {
      params.set('tail', String(opts.tail));
    }

    if (opts?.source) {
      params.set('source', opts.source);
    }

    const query = params.toString();
    const endpoint = query ? `/logs?${query}` : '/logs';

    return daemonRequest<LogsResponse>(endpoint);
  }
);

/**
 * Diagnostics Handler
 * POST /v1/diagnostics
 */
ipcMain.handle(IPCChannel.DIAGNOSTICS, async (): Promise<DiagnosticsResponse> => {
  return daemonRequest<DiagnosticsResponse>('/diagnostics', {
    method: 'POST',
  });
});

/**
 * Status Change Polling
 * Polls daemon every 5s and emits status changes to renderer
 */
let statusPollTimer: NodeJS.Timeout | null = null;
let lastStatus: StatusResponse | null = null;

function startStatusPolling(window: BrowserWindow | null) {
  if (!window || statusPollTimer) {
    return;
  }

  statusPollTimer = setInterval(async () => {
    if (!window || window.isDestroyed()) {
      stopStatusPolling();
      return;
    }

    try {
      const status = await daemonRequest<StatusResponse>('/status');

      // Only emit if status changed
      if (!lastStatus || JSON.stringify(status) !== JSON.stringify(lastStatus)) {
        lastStatus = status;
        window.webContents.send(IPCChannel.STATUS_CHANGED, status);
      }
    } catch (error) {
      // Ignore errors (daemon may be stopped)
      console.error('Status poll error:', error);
    }
  }, STATUS_POLL_INTERVAL);
}

function stopStatusPolling() {
  if (statusPollTimer) {
    clearInterval(statusPollTimer);
    statusPollTimer = null;
    lastStatus = null;
  }
}

/**
 * Initialize IPC handlers
 */
export function setupIPCHandlers(window: BrowserWindow | null) {
  startStatusPolling(window);
}

/**
 * Cleanup IPC handlers
 */
export function cleanupIPCHandlers() {
  stopStatusPolling();
}

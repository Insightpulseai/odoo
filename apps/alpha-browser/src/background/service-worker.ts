import { loggers } from '@/shared/logger';
import { initDB } from '@/storage/db';
import { getActiveMission } from '@/storage/missions';
import { saveCheckpoint, getLatestCheckpoint } from '@/storage/checkpoints';
import type { AgentMessage } from '@/shared/types';

const logger = loggers.serviceWorker;

/**
 * Service Worker Lifecycle Management
 * MV3 service workers terminate after 30s-5min, requiring aggressive state persistence
 */

// Keep-alive interval (ping every 20s to prevent termination)
const KEEPALIVE_INTERVAL = 20000;
const CHECKPOINT_INTERVAL = 30000;

let keepaliveInterval: ReturnType<typeof setInterval>;
let checkpointInterval: ReturnType<typeof setInterval>;

/**
 * Initialize service worker on startup
 */
chrome.runtime.onStartup.addListener(async () => {
  logger.info('Service worker starting up');
  await initialize();
});

/**
 * Initialize on extension install/update
 */
chrome.runtime.onInstalled.addListener(async (details) => {
  logger.info(`Extension installed/updated: ${details.reason}`);
  await initialize();
});

/**
 * Main initialization function
 */
async function initialize(): Promise<void> {
  try {
    // Initialize IndexedDB
    await initDB();
    logger.info('Database initialized');

    // Restore state from last checkpoint
    const activeMission = await getActiveMission();
    if (activeMission) {
      const checkpoint = await getLatestCheckpoint(activeMission.id);
      if (checkpoint) {
        logger.info(`Restoring mission ${activeMission.id} from checkpoint`);
        // TODO: Restore Governor state from checkpoint
      }
    }

    // Start keep-alive and checkpoint intervals
    startIntervals();

    logger.info('Service worker initialized successfully');
  } catch (error) {
    logger.error('Failed to initialize service worker:', error);
  }
}

/**
 * Start keep-alive and checkpoint intervals
 */
function startIntervals(): void {
  // Keep-alive: prevent service worker termination
  if (keepaliveInterval) clearInterval(keepaliveInterval);
  keepaliveInterval = setInterval(() => {
    chrome.runtime.sendMessage({ type: 'keepalive' }).catch(() => {
      // Ignore errors (no listeners connected)
    });
  }, KEEPALIVE_INTERVAL);

  // Checkpoint: save state periodically
  if (checkpointInterval) clearInterval(checkpointInterval);
  checkpointInterval = setInterval(async () => {
    await createCheckpoint();
  }, CHECKPOINT_INTERVAL);
}

/**
 * Create checkpoint of current state
 */
async function createCheckpoint(): Promise<void> {
  try {
    const activeMission = await getActiveMission();
    if (!activeMission) return;

    // TODO: Serialize Governor state
    const state = {
      missionId: activeMission.id,
      timestamp: Date.now()
      // Add Governor state here
    };

    await saveCheckpoint(activeMission.id, state);
    logger.debug(`Checkpoint created for mission ${activeMission.id}`);
  } catch (error) {
    logger.error('Failed to create checkpoint:', error);
  }
}

/**
 * Handle service worker suspension
 */
chrome.runtime.onSuspend.addListener(async () => {
  logger.warn('Service worker suspending, saving state...');

  // Clear intervals
  if (keepaliveInterval) clearInterval(keepaliveInterval);
  if (checkpointInterval) clearInterval(checkpointInterval);

  // Save final checkpoint
  await createCheckpoint();

  logger.info('State saved, service worker suspending');
});

/**
 * Message handler for cross-context communication
 */
chrome.runtime.onMessage.addListener(
  (message: AgentMessage, sender, sendResponse) => {
    logger.debug('Message received:', message);

    // Handle different message types
    switch (message.type) {
      case 'keepalive':
        sendResponse({ ok: true });
        break;

      case 'task-assignment':
        // TODO: Route to Governor
        logger.info('Task assignment received:', message.payload);
        sendResponse({ ok: true });
        break;

      case 'task-result':
        // TODO: Update mission state
        logger.info('Task result received:', message.payload);
        sendResponse({ ok: true });
        break;

      case 'task-error':
        // TODO: Handle error with retry logic
        logger.error('Task error received:', message.payload);
        sendResponse({ ok: true });
        break;

      default:
        logger.warn('Unknown message type:', message.type);
        sendResponse({ ok: false, error: 'Unknown message type' });
    }

    // Keep channel open for async response
    return true;
  }
);

/**
 * Handle tab activation (for screenshot capture)
 */
chrome.tabs.onActivated.addListener((activeInfo) => {
  logger.debug('Tab activated:', activeInfo.tabId);
});

/**
 * Handle navigation events (for page state tracking)
 */
chrome.webNavigation.onCompleted.addListener((details) => {
  if (details.frameId === 0) {
    logger.debug('Navigation completed:', details.url);
  }
});

logger.info('Service worker script loaded');

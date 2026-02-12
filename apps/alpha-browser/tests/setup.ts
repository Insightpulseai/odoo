import { beforeAll, afterAll } from 'vitest';
import 'fake-indexeddb/auto';

// Setup fake IndexedDB for tests
beforeAll(() => {
  // Mock chrome API
  global.chrome = {
    runtime: {
      sendMessage: async () => ({ ok: true }),
      onMessage: {
        addListener: () => {}
      },
      onStartup: {
        addListener: () => {}
      },
      onInstalled: {
        addListener: () => {}
      },
      onSuspend: {
        addListener: () => {}
      }
    },
    tabs: {
      onActivated: {
        addListener: () => {}
      }
    },
    webNavigation: {
      onCompleted: {
        addListener: () => {}
      }
    },
    storage: {
      local: {
        get: async () => ({}),
        set: async () => {}
      }
    }
  } as any;
});

afterAll(() => {
  // Cleanup
});

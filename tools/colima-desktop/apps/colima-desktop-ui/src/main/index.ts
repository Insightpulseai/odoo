import { app, BrowserWindow } from 'electron';
import * as path from 'path';
import { createMenu } from './menu';
import { setupIPCHandlers, cleanupIPCHandlers } from './ipc-handlers';

let mainWindow: BrowserWindow | null = null;

/**
 * Get the renderer entry point based on environment.
 * In development: Vite dev server URL
 * In production: Path to packaged renderer HTML
 */
function getRendererEntry(): { kind: 'url' | 'file'; value: string } {
  // Dev mode: use Vite dev server
  if (process.env.NODE_ENV === 'development') {
    return { kind: 'url', value: 'http://localhost:5173' };
  }

  // Production mode: resolve renderer path from app root
  // app.getAppPath() returns the app root (where app.asar or Resources is)
  // dist-main and dist-renderer are siblings at the app root level
  const appPath = app.getAppPath();
  const rendererPath = path.join(appPath, 'dist-renderer', 'index.html');

  return { kind: 'file', value: rendererPath };
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    show: false,
  });

  // Load renderer
  const entry = getRendererEntry();
  if (entry.kind === 'url') {
    mainWindow.loadURL(entry.value);
  } else {
    mainWindow.loadFile(entry.value);
  }

  // Show when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow?.show();
  });

  // Hide to tray on close (macOS behavior)
  mainWindow.on('close', (event) => {
    if (!app.isQuitting) {
      event.preventDefault();
      mainWindow?.hide();
    }
  });

  // Setup IPC handlers
  setupIPCHandlers(mainWindow);

  return mainWindow;
}

app.on('ready', () => {
  createWindow();
  createMenu(mainWindow!);
});

app.on('window-all-closed', () => {
  // On macOS, don't quit when all windows closed
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  } else {
    mainWindow?.show();
  }
});

app.on('before-quit', () => {
  app.isQuitting = true;
  cleanupIPCHandlers();
});

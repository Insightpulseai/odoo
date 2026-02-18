"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path = __importStar(require("path"));
const menu_1 = require("./menu");
const ipc_handlers_1 = require("./ipc-handlers");
let mainWindow = null;
let isQuitting = false;
/**
 * Get the renderer entry point based on environment.
 * In development: Vite dev server URL
 * In production: Path to packaged renderer HTML
 */
function getRendererEntry() {
    // Dev mode: use Vite dev server
    if (process.env.NODE_ENV === 'development') {
        return { kind: 'url', value: 'http://localhost:5173' };
    }
    // Production mode: resolve renderer path from app root
    // app.getAppPath() returns the app root (where app.asar or Resources is)
    // dist-main and dist-renderer are siblings at the app root level
    const appPath = electron_1.app.getAppPath();
    const rendererPath = path.join(appPath, 'dist-renderer', 'index.html');
    return { kind: 'file', value: rendererPath };
}
function createWindow() {
    mainWindow = new electron_1.BrowserWindow({
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
    }
    else {
        mainWindow.loadFile(entry.value);
    }
    // Open DevTools in development only
    if (process.env.NODE_ENV === 'development') {
        mainWindow.webContents.openDevTools();
    }
    // Show when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow?.show();
    });
    // Hide to tray on close (macOS behavior)
    mainWindow.on('close', (event) => {
        if (!isQuitting) {
            event.preventDefault();
            mainWindow?.hide();
        }
    });
    // Setup IPC handlers
    (0, ipc_handlers_1.setupIPCHandlers)(mainWindow);
    return mainWindow;
}
electron_1.app.on('ready', () => {
    createWindow();
    (0, menu_1.createMenu)(mainWindow);
});
electron_1.app.on('window-all-closed', () => {
    // On macOS, don't quit when all windows closed
    if (process.platform !== 'darwin') {
        electron_1.app.quit();
    }
});
electron_1.app.on('activate', () => {
    if (electron_1.BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
    else {
        mainWindow?.show();
    }
});
electron_1.app.on('before-quit', () => {
    isQuitting = true;
    (0, ipc_handlers_1.cleanupIPCHandlers)();
});

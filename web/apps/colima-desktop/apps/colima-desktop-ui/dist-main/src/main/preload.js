"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
// Expose secure API to renderer via contextBridge
electron_1.contextBridge.exposeInMainWorld('colima', {
    // Status
    status: () => electron_1.ipcRenderer.invoke('colima:status'),
    // Lifecycle
    start: (opts) => electron_1.ipcRenderer.invoke('colima:start', opts),
    stop: () => electron_1.ipcRenderer.invoke('colima:stop'),
    restart: (opts) => electron_1.ipcRenderer.invoke('colima:restart', opts),
    // Config
    getConfig: () => electron_1.ipcRenderer.invoke('colima:getConfig'),
    setConfig: (config) => electron_1.ipcRenderer.invoke('colima:setConfig', config),
    // Logs
    tailLogs: (opts) => electron_1.ipcRenderer.invoke('colima:tailLogs', opts),
    // Diagnostics
    diagnostics: () => electron_1.ipcRenderer.invoke('colima:diagnostics'),
    // Events
    onStatusChange: (callback) => {
        const listener = (_event, status) => callback(status);
        electron_1.ipcRenderer.on('status:changed', listener);
        // Return unsubscribe function
        return () => {
            electron_1.ipcRenderer.removeListener('status:changed', listener);
        };
    },
});

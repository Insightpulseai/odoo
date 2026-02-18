"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.setupIPCHandlers = setupIPCHandlers;
exports.cleanupIPCHandlers = cleanupIPCHandlers;
const electron_1 = require("electron");
const BASE_URL = 'http://localhost:35100';
let statusPollInterval = null;
let lastStatus = null;
function setupIPCHandlers(window) {
    // Status
    electron_1.ipcMain.handle('colima:status', async () => {
        const res = await fetch(`${BASE_URL}/v1/status`);
        if (!res.ok)
            throw new Error(`Status request failed: ${res.statusText}`);
        return res.json();
    });
    // Start
    electron_1.ipcMain.handle('colima:start', async (_event, opts) => {
        const res = await fetch(`${BASE_URL}/v1/lifecycle/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(opts || {}),
        });
        if (!res.ok)
            throw new Error(`Start request failed: ${res.statusText}`);
        return res.json();
    });
    // Stop
    electron_1.ipcMain.handle('colima:stop', async () => {
        const res = await fetch(`${BASE_URL}/v1/lifecycle/stop`, {
            method: 'POST',
        });
        if (!res.ok)
            throw new Error(`Stop request failed: ${res.statusText}`);
        return res.json();
    });
    // Restart
    electron_1.ipcMain.handle('colima:restart', async (_event, opts) => {
        const res = await fetch(`${BASE_URL}/v1/lifecycle/restart`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(opts || {}),
        });
        if (!res.ok)
            throw new Error(`Restart request failed: ${res.statusText}`);
        return res.json();
    });
    // Get config
    electron_1.ipcMain.handle('colima:getConfig', async () => {
        const res = await fetch(`${BASE_URL}/v1/config`);
        if (!res.ok)
            throw new Error(`Get config failed: ${res.statusText}`);
        return res.json();
    });
    // Set config
    electron_1.ipcMain.handle('colima:setConfig', async (_event, config) => {
        const res = await fetch(`${BASE_URL}/v1/config`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
        });
        if (!res.ok)
            throw new Error(`Set config failed: ${res.statusText}`);
        return res.json();
    });
    // Tail logs
    electron_1.ipcMain.handle('colima:tailLogs', async (_event, opts) => {
        const params = new URLSearchParams();
        if (opts.tail)
            params.set('tail', opts.tail.toString());
        if (opts.source)
            params.set('source', opts.source);
        const res = await fetch(`${BASE_URL}/v1/logs?${params}`);
        if (!res.ok)
            throw new Error(`Tail logs failed: ${res.statusText}`);
        const data = await res.json();
        return data.lines || [];
    });
    // Diagnostics
    electron_1.ipcMain.handle('colima:diagnostics', async () => {
        const res = await fetch(`${BASE_URL}/v1/diagnostics`, { method: 'POST' });
        if (!res.ok)
            throw new Error(`Diagnostics failed: ${res.statusText}`);
        return res.json();
    });
    // Start status polling
    startStatusPolling(window);
}
function cleanupIPCHandlers() {
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
        statusPollInterval = null;
    }
    electron_1.ipcMain.removeHandler('colima:status');
    electron_1.ipcMain.removeHandler('colima:start');
    electron_1.ipcMain.removeHandler('colima:stop');
    electron_1.ipcMain.removeHandler('colima:restart');
    electron_1.ipcMain.removeHandler('colima:getConfig');
    electron_1.ipcMain.removeHandler('colima:setConfig');
    electron_1.ipcMain.removeHandler('colima:tailLogs');
    electron_1.ipcMain.removeHandler('colima:diagnostics');
}
function startStatusPolling(window) {
    statusPollInterval = setInterval(async () => {
        try {
            const res = await fetch(`${BASE_URL}/v1/status`);
            if (res.ok) {
                const status = await res.json();
                // Only emit if status changed
                if (JSON.stringify(status) !== JSON.stringify(lastStatus)) {
                    window.webContents.send('status:changed', status);
                    lastStatus = status;
                }
            }
        }
        catch (err) {
            // Silently ignore polling errors
        }
    }, 5000);
}

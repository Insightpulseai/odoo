"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.enableAutostart = enableAutostart;
exports.disableAutostart = disableAutostart;
exports.isAutostartEnabled = isAutostartEnabled;
const electron_1 = require("electron");
function enableAutostart() {
    electron_1.app.setLoginItemSettings({
        openAtLogin: true,
    });
}
function disableAutostart() {
    electron_1.app.setLoginItemSettings({
        openAtLogin: false,
    });
}
function isAutostartEnabled() {
    return electron_1.app.getLoginItemSettings().openAtLogin;
}

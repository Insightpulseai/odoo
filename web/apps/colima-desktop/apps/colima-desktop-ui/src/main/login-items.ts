import { app } from 'electron';

export function enableAutostart() {
  app.setLoginItemSettings({
    openAtLogin: true,
  });
}

export function disableAutostart() {
  app.setLoginItemSettings({
    openAtLogin: false,
  });
}

export function isAutostartEnabled(): boolean {
  return app.getLoginItemSettings().openAtLogin;
}

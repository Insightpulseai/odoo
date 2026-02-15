import { app } from 'electron';

export interface LoginItemSettings {
  openAtLogin: boolean;
  openAsHidden?: boolean;
}

export function enableAutostart(openAsHidden: boolean = false): void {
  app.setLoginItemSettings({
    openAtLogin: true,
    openAsHidden,
  });
}

export function disableAutostart(): void {
  app.setLoginItemSettings({
    openAtLogin: false,
  });
}

export function setAutostart(enabled: boolean, openAsHidden: boolean = false): void {
  if (enabled) {
    enableAutostart(openAsHidden);
  } else {
    disableAutostart();
  }
}

export function getAutostartStatus(): LoginItemSettings {
  const settings = app.getLoginItemSettings();
  return {
    openAtLogin: settings.openAtLogin,
    openAsHidden: settings.openAsHidden,
  };
}

export function isAutostartEnabled(): boolean {
  return app.getLoginItemSettings().openAtLogin;
}

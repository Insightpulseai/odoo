import { Menu, Tray, BrowserWindow, app, nativeImage } from 'electron';
import * as path from 'path';

let tray: Tray | null = null;

export function createMenu(window: BrowserWindow) {
  // Create tray icon
  const iconPath = path.join(__dirname, '../../resources/tray-icon.png');
  const icon = nativeImage.createFromPath(iconPath);
  tray = new Tray(icon.resize({ width: 16, height: 16 }));

  // Build menu
  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Colima Desktop',
      enabled: false,
    },
    { type: 'separator' },
    {
      label: 'Show Window',
      click: () => {
        window.show();
      },
    },
    {
      label: 'Settings',
      click: () => {
        window.show();
        window.webContents.send('navigate', '/settings');
      },
    },
    {
      label: 'Logs',
      click: () => {
        window.show();
        window.webContents.send('navigate', '/logs');
      },
    },
    { type: 'separator' },
    {
      label: 'Quit',
      click: () => {
        app.quit();
      },
    },
  ]);

  tray.setToolTip('Colima Desktop');
  tray.setContextMenu(contextMenu);
  
  // Click tray to show window
  tray.on('click', () => {
    window.show();
  });
}

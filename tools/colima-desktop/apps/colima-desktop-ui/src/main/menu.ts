import { app, Tray, Menu, nativeImage, BrowserWindow } from 'electron';
import * as path from 'path';

let tray: Tray | null = null;
let statusIcon: 'green' | 'red' | 'yellow' = 'red';

interface VMStatus {
  running: boolean;
  cpu: string;
  memory: string;
  uptime: string;
}

let currentStatus: VMStatus = {
  running: false,
  cpu: '0%',
  memory: '0 MB',
  uptime: '0s',
};

function getIconPath(status: 'green' | 'red' | 'yellow'): string {
  const iconName = `tray-icon-${status}.png`;
  return path.join(__dirname, '../../resources', iconName);
}

function createStatusIcon(status: 'green' | 'red' | 'yellow'): nativeImage {
  const size = 16;
  const canvas = {
    width: size,
    height: size,
  };

  const colors = {
    green: '#10b981',
    red: '#ef4444',
    yellow: '#f59e0b',
  };

  const color = colors[status];

  const iconPath = getIconPath(status);
  try {
    return nativeImage.createFromPath(iconPath);
  } catch {
    return nativeImage.createEmpty();
  }
}

function updateTrayMenu(mainWindow: BrowserWindow | null) {
  if (!tray) return;

  const template = [
    {
      label: 'Status',
      enabled: false,
    },
    {
      label: currentStatus.running ? 'Running' : 'Stopped',
      enabled: false,
    },
    { type: 'separator' as const },
    {
      label: `CPU: ${currentStatus.cpu}`,
      enabled: false,
      visible: currentStatus.running,
    },
    {
      label: `Memory: ${currentStatus.memory}`,
      enabled: false,
      visible: currentStatus.running,
    },
    {
      label: `Uptime: ${currentStatus.uptime}`,
      enabled: false,
      visible: currentStatus.running,
    },
    { type: 'separator' as const, visible: currentStatus.running },
    {
      label: 'Start VM',
      click: () => {
        handleStartVM();
      },
      enabled: !currentStatus.running,
    },
    {
      label: 'Stop VM',
      click: () => {
        handleStopVM();
      },
      enabled: currentStatus.running,
    },
    {
      label: 'Restart VM',
      click: () => {
        handleRestartVM();
      },
      enabled: currentStatus.running,
    },
    { type: 'separator' as const },
    {
      label: 'Settings',
      click: () => {
        if (mainWindow) {
          mainWindow.show();
          mainWindow.focus();
        }
      },
    },
    {
      label: 'View Logs',
      click: () => {
        handleViewLogs();
      },
    },
    { type: 'separator' as const },
    {
      label: 'Quit Colima Desktop',
      click: () => {
        app.quit();
      },
    },
  ];

  const contextMenu = Menu.buildFromTemplate(template);
  tray.setContextMenu(contextMenu);
}

function handleStartVM() {
  console.log('Starting VM...');
  updateStatus({
    running: true,
    cpu: '5%',
    memory: '2048 MB',
    uptime: '0s',
  });
}

function handleStopVM() {
  console.log('Stopping VM...');
  updateStatus({
    running: false,
    cpu: '0%',
    memory: '0 MB',
    uptime: '0s',
  });
}

function handleRestartVM() {
  console.log('Restarting VM...');
  updateStatus({
    running: false,
    cpu: '0%',
    memory: '0 MB',
    uptime: '0s',
  });

  setTimeout(() => {
    updateStatus({
      running: true,
      cpu: '5%',
      memory: '2048 MB',
      uptime: '0s',
    });
  }, 2000);
}

function handleViewLogs() {
  const logsWindow = new BrowserWindow({
    width: 800,
    height: 600,
    title: 'Colima Logs',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  logsWindow.loadURL('about:blank');
}

export function updateStatus(status: VMStatus) {
  currentStatus = status;

  const newIcon: 'green' | 'red' | 'yellow' = status.running ? 'green' : 'red';

  if (newIcon !== statusIcon) {
    statusIcon = newIcon;
    if (tray) {
      tray.setImage(createStatusIcon(statusIcon));
    }
  }

  updateTrayMenu(null);
}

export function createTray(mainWindow: BrowserWindow | null): Tray {
  const icon = createStatusIcon('red');
  tray = new Tray(icon);

  tray.setToolTip('Colima Desktop');

  updateTrayMenu(mainWindow);

  tray.on('click', () => {
    if (mainWindow) {
      if (mainWindow.isVisible()) {
        mainWindow.hide();
      } else {
        mainWindow.show();
        mainWindow.focus();
      }
    }
  });

  return tray;
}

export function destroyTray() {
  if (tray) {
    tray.destroy();
    tray = null;
  }
}

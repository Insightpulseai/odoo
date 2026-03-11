# Colima Desktop UI

**Optional Electron menubar app for Colima Desktop**

A modern, security-first Electron interface for managing Colima VMs. Requires the [Colima Desktop daemon](../../tools/colima-desktop) to be running.

**Status:** Phase 3 - Electron UI (Planned)

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Features](#features)
- [Security Model](#security-model)
- [Development](#development)
- [Building DMG](#building-dmg)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

Colima Desktop UI is a **menubar tray application** that provides visual controls for Colima VM management. It's designed as an optional enhancement to the CLI-first [Colima Desktop daemon](../../tools/colima-desktop).

### Key Characteristics

- ✅ **Menubar integration** - Lives in macOS menu bar, always accessible
- ✅ **Security-first** - Full Electron security model (contextIsolation, sandbox, contextBridge)
- ✅ **Daemon-backed** - All operations delegated to REST API (localhost:35100)
- ✅ **No privileged operations** - Renderer process fully sandboxed
- ✅ **React + Vite** - Modern UI framework with fast HMR
- ✅ **Login item support** - Auto-start on macOS login (optional)

### Why Optional?

The Colima Desktop daemon + CLI work perfectly without a GUI. This Electron app is for users who prefer:

- Visual status indicators (menubar icon shows VM state)
- Point-and-click controls (Start/Stop buttons)
- Interactive settings (sliders for CPU/RAM)
- Log viewer (tail -f style UI)

**Not required for:**
- Automation/scripting (use CLI)
- Server environments (headless daemon)
- CI/CD pipelines (REST API)

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Electron App (3 Processes)          │
├─────────────────────────────────────────────┤
│                                             │
│  Main Process (Privileged)                  │
│  ├─ BrowserWindow management                │
│  ├─ Menubar tray integration                │
│  ├─ IPC handlers (REST API delegation)      │
│  └─ Login item management                   │
│                                             │
│           ▼ (contextBridge)                 │
│                                             │
│  Preload Script (Security Boundary)         │
│  ├─ window.colima API surface               │
│  ├─ IPC request-response proxying           │
│  └─ Type-safe API definitions               │
│                                             │
│           ▼ (contextIsolation)              │
│                                             │
│  Renderer Process (Unprivileged)            │
│  ├─ React components (Status, Settings)     │
│  ├─ Zustand state management                │
│  ├─ No Node.js access (sandboxed)           │
│  └─ Vite dev server / bundled static files  │
│                                             │
└─────────────────┬───────────────────────────┘
                  │
                  │ HTTP (localhost:35100)
                  ▼
         ┌────────────────────┐
         │  Colima Desktop     │
         │  Daemon (Fastify)   │
         │  /v1/* REST API     │
         └────────────────────┘
```

### Directory Structure

```
apps/colima-desktop-ui/
├── src/
│   ├── main/                    # Main process (privileged)
│   │   ├── index.ts            # App lifecycle, BrowserWindow
│   │   ├── menu.ts             # Menubar tray integration
│   │   ├── preload.ts          # contextBridge API (security boundary)
│   │   └── ipc-handlers.ts     # ipcMain.handle (REST delegation)
│   ├── renderer/                # Renderer process (unprivileged)
│   │   ├── App.tsx             # Root React component
│   │   ├── components/
│   │   │   ├── Status.tsx      # VM status panel
│   │   │   ├── Controls.tsx    # Start/Stop/Restart buttons
│   │   │   ├── Settings.tsx    # CPU/Memory/Disk sliders
│   │   │   └── Logs.tsx        # Log viewer (tail -f style)
│   │   └── hooks/
│   │       └── useColima.ts    # React hooks for window.colima API
│   └── shared/
│       └── types.ts            # Shared types (API contracts)
├── electron-builder.yml         # DMG packaging config
├── vite.config.ts              # Vite renderer build config
├── package.json
├── tsconfig.json
└── README.md                   # This file
```

---

## Installation

### Prerequisites

1. **Colima Desktop daemon** installed and running:
   ```bash
   cd ../../tools/colima-desktop
   pnpm install && pnpm build
   pnpm link --global
   colima-desktop daemon start
   ```

2. **Node.js** >= 18.0.0
3. **pnpm** package manager

### From Source

```bash
# Navigate to UI app
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/apps/colima-desktop-ui

# Install dependencies
pnpm install

# Build renderer (Vite)
pnpm build

# Package as DMG (macOS)
pnpm package
```

### Install DMG

```bash
# Open packaged DMG
open dist/Colima-Desktop-*.dmg

# Drag to Applications folder
# Launch from Applications or via:
open /Applications/Colima\ Desktop.app
```

---

## Features

### 1. Menubar Tray Integration

**Icon:** Lives in macOS menubar (top-right)

**States:**
- 🟢 Green - VM running
- 🔴 Red - VM stopped
- 🟡 Yellow - VM starting/stopping
- ⚫ Gray - Daemon not connected

**Click behavior:**
- **Left-click:** Show/hide main window
- **Right-click:** Context menu (Quit, About, Settings)

### 2. Status Display

**Main window tabs:**

**Status Tab:**
- VM state (Running, Stopped, Error)
- Resource usage (CPU%, RAM usage, Disk usage)
- Uptime counter
- Colima + Lima versions
- Auto-refresh every 2 seconds

**Example:**
```
┌────────────────────────────────┐
│ Status                         │
├────────────────────────────────┤
│ State: Running                 │
│ CPU: 4 cores (23.5% usage)    │
│ Memory: 8 GB (3.2 GB used)    │
│ Disk: 60 GB (12.5 GB used)    │
│ Kubernetes: Disabled           │
│ Uptime: 1 day 2 hours          │
│                                │
│ [Start] [Stop] [Restart]      │
└────────────────────────────────┘
```

### 3. VM Controls

**Buttons:**
- **Start** - Start VM with current config
- **Stop** - Graceful VM shutdown
- **Restart** - Stop + Start (applies pending config changes)

**Behavior:**
- Buttons disabled during transitions (starting/stopping)
- Error messages shown in toast notifications
- Success confirmations with menubar icon animation

### 4. Settings Panel

**Resource Sliders:**

**CPU:**
- Range: 1-16 cores
- Current: Shows allocated + current usage
- Drag to adjust → marks restart required

**Memory:**
- Range: 1-32 GB
- Current: Shows allocated + used
- Drag to adjust → marks restart required

**Disk:**
- Range: 20-200 GB
- Current: Shows allocated + used
- **Warning:** Expanding only (cannot shrink)

**Kubernetes Toggle:**
- ON/OFF switch
- Shows current context when enabled
- Changing state → marks restart required

**Restart Warning:**
```
⚠️ Changes require VM restart
[Apply & Restart] [Cancel]
```

**Example:**
```
┌────────────────────────────────┐
│ Settings                       │
├────────────────────────────────┤
│ CPU:  [====●====] 6 cores     │
│       (currently: 4 → 6)      │
│                                │
│ Memory: [======●==] 12 GB     │
│         (currently: 8 → 12)   │
│                                │
│ Disk: [========●-] 80 GB      │
│       (currently: 60 → 80)    │
│                                │
│ Kubernetes: [●─] ON           │
│             (currently: OFF)  │
│                                │
│ ⚠️  Restart required           │
│ [Apply & Restart] [Cancel]    │
└────────────────────────────────┘
```

### 5. Logs Viewer

**Tabs:**
- Colima logs (colima CLI output)
- Lima logs (VM logs)
- Daemon logs (REST API logs)

**Features:**
- Tail -f style live updates
- Searchable/filterable
- Copy to clipboard
- Clear logs button
- Auto-scroll to bottom (toggle)

**Example:**
```
┌────────────────────────────────┐
│ Logs  [Colima] [Lima] [Daemon]│
├────────────────────────────────┤
│ 14:30:15 INFO Starting VM...   │
│ 14:30:20 INFO VM started       │
│ 14:30:22 INFO Docker ready     │
│                                │
│ [●] Auto-scroll  [Clear] [Copy]│
└────────────────────────────────┘
```

### 6. Login Item Integration

**macOS Login Items:**
- Checkbox in Settings → "Launch at login"
- Uses macOS `SMLoginItemSetEnabled` API
- App auto-starts on macOS boot (if enabled)
- Daemon must be configured with `autostart: true`

---

## Security Model

### Electron Security Principles

This app follows **Electron security best practices** strictly. All privileged operations happen in the main process, renderer is fully sandboxed.

### Process Security

**Main Process (Privileged):**
```typescript
// src/main/index.ts
app.whenReady().then(() => {
  const win = new BrowserWindow({
    webPreferences: {
      contextIsolation: true,        // ✅ REQUIRED
      nodeIntegration: false,        // ✅ REQUIRED
      sandbox: true,                 // ✅ REQUIRED
      preload: path.join(__dirname, 'preload.js')
    }
  });
});
```

**Owns:**
- BrowserWindow lifecycle
- Menubar tray management
- HTTP calls to daemon (localhost:35100)
- Filesystem access (logs export)
- Login item registration

**Forbidden:**
- Executing arbitrary commands
- Filesystem writes outside logs export
- Network access beyond localhost:35100

### Preload Script (Security Boundary)

```typescript
// src/main/preload.ts
import { contextBridge, ipcRenderer } from 'electron';

// ✅ ALLOWED - Narrow, type-safe API surface
contextBridge.exposeInMainWorld('colima', {
  status: () => ipcRenderer.invoke('colima:status'),
  start: (params) => ipcRenderer.invoke('colima:start', params),
  stop: () => ipcRenderer.invoke('colima:stop'),
  restart: (params) => ipcRenderer.invoke('colima:restart', params),
  getConfig: () => ipcRenderer.invoke('colima:getConfig'),
  setConfig: (config) => ipcRenderer.invoke('colima:setConfig', config),
  getLogs: (params) => ipcRenderer.invoke('colima:getLogs', params),
  generateDiagnostics: () => ipcRenderer.invoke('colima:diagnostics')
});

// ❌ FORBIDDEN - Raw IPC exposure
// contextBridge.exposeInMainWorld('ipc', ipcRenderer); // NEVER DO THIS
```

**Owns:**
- `window.colima` API definition
- IPC request-response proxying
- Type validation (TypeScript)

**Forbidden:**
- Raw `ipcRenderer` exposure
- Direct Node.js API access
- Filesystem operations

### Renderer Process (Unprivileged)

```typescript
// src/renderer/App.tsx
import { useColima } from './hooks/useColima';

export function App() {
  // ✅ ALLOWED - Use preload-exposed API
  const { status, start, stop } = useColima();

  // ❌ FORBIDDEN - No Node.js access (blocked by contextIsolation)
  // const fs = require('fs'); // TypeError: require is not defined
}
```

**Owns:**
- React UI rendering
- User input handling
- State management (Zustand)

**Forbidden:**
- Node.js API access (prevented by `contextIsolation`)
- Filesystem operations
- Network requests (beyond `window.colima` API)
- Child process spawning

### IPC Security Model

**Allowed Pattern (Type-Safe Request-Response):**

```typescript
// Main process handler
ipcMain.handle('colima:start', async (_event, params) => {
  // Validate params (Zod schema)
  const validated = LifecycleRequestSchema.parse(params);

  // Call daemon REST API (localhost only)
  const res = await fetch('http://localhost:35100/v1/lifecycle/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(validated)
  });

  return res.json();
});

// Renderer usage (via preload)
const result = await window.colima.start({ cpu: 4, memory: 8 });
```

**Forbidden Pattern (Arbitrary IPC):**

```typescript
// ❌ NEVER expose raw send/on
contextBridge.exposeInMainWorld('ipc', {
  send: (channel, data) => ipcRenderer.send(channel, data),
  on: (channel, callback) => ipcRenderer.on(channel, callback)
});

// Renderer could now call ANY channel
window.ipc.send('execute-evil-command', 'rm -rf /');
```

### Validation Rules

**All IPC payloads validated:**

```typescript
import { z } from 'zod';

const LifecycleRequestSchema = z.object({
  cpu: z.number().min(1).max(16).optional(),
  memory: z.number().min(1).max(32).optional(),
  disk: z.number().min(20).max(200).optional()
});

ipcMain.handle('colima:start', async (_event, params) => {
  // Throws if validation fails
  const validated = LifecycleRequestSchema.parse(params);
  // ... safe to use validated
});
```

### Security Audit Checklist

- [x] `contextIsolation` enabled in BrowserWindow
- [x] `nodeIntegration` disabled
- [x] `sandbox` enabled
- [x] Preload script uses `contextBridge` only
- [x] No raw `ipcRenderer` exposed to renderer
- [x] All IPC handlers validate payloads
- [x] Daemon API calls go to localhost only
- [x] No arbitrary command execution
- [x] Filesystem access restricted (logs export only)

---

## Development

### Prerequisites

- Node.js >= 18.0.0
- pnpm
- Colima Desktop daemon running (`colima-desktop daemon start`)

### Development Mode

```bash
cd apps/colima-desktop-ui

# Install dependencies
pnpm install

# Run Electron in dev mode (with HMR)
pnpm dev
```

**What happens:**
1. Vite dev server starts (renderer at http://localhost:5173)
2. Electron main process starts
3. Loads renderer from dev server (HMR enabled)
4. Changes to renderer → instant reload
5. Changes to main/preload → requires restart

### Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Development mode (Vite HMR) |
| `pnpm build` | Build renderer (Vite production bundle) |
| `pnpm package` | Create DMG (electron-builder) |
| `pnpm start` | Run packaged app (post-build) |
| `pnpm lint` | ESLint code quality |
| `pnpm typecheck` | TypeScript type checking |

### Project Structure

```typescript
// src/main/index.ts - Main process entrypoint
import { app, BrowserWindow } from 'electron';
import { createMenu } from './menu';
import { registerIpcHandlers } from './ipc-handlers';

app.whenReady().then(() => {
  createMenu(); // Menubar tray
  registerIpcHandlers(); // IPC handlers

  const win = new BrowserWindow({
    width: 400,
    height: 600,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Dev: load from Vite dev server
  // Prod: load from built files
  const url = process.env.VITE_DEV_SERVER_URL ||
    `file://${path.join(__dirname, '../renderer/index.html')}`;
  win.loadURL(url);
});
```

```typescript
// src/main/preload.ts - Security boundary
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('colima', {
  status: () => ipcRenderer.invoke('colima:status'),
  start: (params) => ipcRenderer.invoke('colima:start', params),
  // ... other methods
});
```

```typescript
// src/renderer/App.tsx - React UI
import { useColima } from './hooks/useColima';

export function App() {
  const { status, start, stop, loading } = useColima();

  return (
    <div>
      <Status data={status} />
      <Controls onStart={start} onStop={stop} disabled={loading} />
    </div>
  );
}
```

---

## Building DMG

### electron-builder Configuration

**File:** `electron-builder.yml`

```yaml
appId: com.insightpulseai.colima-desktop
productName: Colima Desktop
copyright: Copyright © 2026 InsightPulse AI

mac:
  category: public.app-category.developer-tools
  target:
    - target: dmg
      arch: [x64, arm64]
  icon: build/icon.icns
  hardenedRuntime: true
  gatekeeperAssess: false
  entitlements: build/entitlements.mac.plist
  entitlementsInherit: build/entitlements.mac.plist

dmg:
  contents:
    - x: 130
      y: 220
    - x: 410
      y: 220
      type: link
      path: /Applications
  background: build/dmg-background.png

files:
  - dist/**/*
  - package.json
  - node_modules/**/*

directories:
  output: dist-electron
```

### Build Process

```bash
# Build renderer (Vite)
pnpm build

# Package as DMG
pnpm package

# Output:
# dist-electron/Colima-Desktop-0.1.0-arm64.dmg
# dist-electron/Colima-Desktop-0.1.0-x64.dmg
```

### Code Signing (Optional for Internal Use)

**For distribution outside organization:**

```bash
# Get Apple Developer ID
# security find-identity -v -p codesigning

# Sign during build
export CSC_NAME="Developer ID Application: Your Name (TEAM_ID)"
pnpm package
```

**For internal use only:**
- No signing required
- User must approve on first launch (System Settings → Security)

### Distribution

**Internal:**
- Upload DMG to shared drive
- Users download + drag to Applications
- First launch: Right-click → Open (bypass Gatekeeper)

**Public (future):**
- Notarize with Apple
- Distribute via Homebrew cask:
  ```bash
  brew install --cask colima-desktop
  ```

---

## Testing

### Unit Tests (Renderer)

```bash
# Vitest for React components
pnpm test
```

**Test files:**
- `src/renderer/__tests__/Status.test.tsx`
- `src/renderer/__tests__/Controls.test.tsx`
- `src/renderer/__tests__/Settings.test.tsx`

**Example:**
```typescript
import { render, screen } from '@testing-library/react';
import { Status } from '../components/Status';

test('renders VM state', () => {
  const status = { state: 'running', cpu: { allocated: 4 } };
  render(<Status data={status} />);
  expect(screen.getByText('Running')).toBeInTheDocument();
});
```

### E2E Tests (Electron)

```bash
# Playwright for Electron
pnpm test:e2e
```

**Test scenarios:**
1. Launch app → menubar icon appears
2. Click icon → main window shows
3. Click Start → VM starts
4. Change settings → restart required flag
5. View logs → logs render
6. Generate diagnostics → bundle created

**Example:**
```typescript
import { _electron as electron } from 'playwright';

test('starts VM when Start button clicked', async () => {
  const app = await electron.launch({ args: ['.'] });
  const win = await app.firstWindow();

  await win.click('button:has-text("Start")');
  await win.waitForSelector('text=Running');

  await app.close();
});
```

---

## Troubleshooting

### Daemon Not Connected

**Symptom:** Menubar icon gray, "Daemon not connected" error

**Solution:**
```bash
# Check daemon status
colima-desktop daemon status

# Start daemon if not running
colima-desktop daemon start

# Restart UI app
```

### White Screen on Launch

**Symptom:** Electron window blank/white

**Causes:**
1. Renderer build failed
2. Vite dev server not running (dev mode)
3. Invalid path to built files

**Solution:**
```bash
# Dev mode: ensure Vite server running
pnpm dev

# Production: rebuild renderer
pnpm build
pnpm package
```

### IPC Timeout Errors

**Symptom:** "IPC request timeout" in console

**Causes:**
1. Daemon not responding (crashed)
2. Network localhost blocked (firewall)
3. Main process handler not registered

**Solution:**
```bash
# Check daemon logs
colima-desktop logs --source daemon

# Check firewall settings (allow localhost)
# Restart daemon
colima-desktop daemon stop
colima-desktop daemon start
```

### App Won't Start at Login

**Symptom:** Login item enabled but app doesn't launch

**Causes:**
1. App moved after login item registration
2. macOS security blocked auto-launch
3. Daemon `autostart` not configured

**Solution:**
```bash
# Disable then re-enable login item
# Settings → uncheck → check "Launch at login"

# Check macOS System Settings
# System Settings → General → Login Items
# Ensure "Colima Desktop" is allowed

# Configure daemon autostart
colima-desktop config set --autostart
```

---

## Contributing

See [../../spec/colima-desktop/constitution.md](../../spec/colima-desktop/constitution.md) for security and architecture constraints.

**Key rules:**
1. **contextIsolation** must remain enabled
2. **nodeIntegration** must remain disabled
3. **sandbox** must remain enabled
4. Preload script uses `contextBridge` only
5. No raw `ipcRenderer` exposure
6. All IPC handlers validate payloads

---

## License

MIT

---

## Related

- **Daemon:** [tools/colima-desktop](../../tools/colima-desktop)
- **Spec Kit:** [spec/colima-desktop](../../spec/colima-desktop)
- **Colima:** [github.com/abiosoft/colima](https://github.com/abiosoft/colima)

---

**Maintained by:** InsightPulse AI
**Repository:** [Insightpulseai/odoo](https://github.com/Insightpulseai/odoo)

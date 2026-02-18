# Colima Desktop — Quick Start

## First Launch

1. Open **Colima Desktop** from Applications (or menubar)
2. The menubar icon (🐳) appears in the top-right of your screen
3. Click the icon to open the control panel

## Starting Your First VM

1. Click the menubar icon → **New VM...**
2. Configure:
   - **Name**: `default` (or any name)
   - **Runtime**: `docker` (or `containerd`, `nerdctl`)
   - **CPU**: 2 (adjust as needed)
   - **Memory**: 2GB
3. Click **Start**
4. Wait for status to show **Running** (~30 seconds)

## Core Operations

| Action | Menu Item | CLI Equivalent |
|--------|-----------|----------------|
| Start VM | VM → Start | `colima start` |
| Stop VM | VM → Stop | `colima stop` |
| Restart VM | VM → Restart | `colima restart` |
| View logs | VM → Logs | `colima logs` |
| VM status | VM → Status | `colima status` |

## Using Docker After Start

Once the VM is running, Docker commands work normally in your terminal:

```bash
docker ps
docker run hello-world
docker compose up
```

## CLI Access (Daemon API)

The daemon runs on `http://127.0.0.1:35100` and is also accessible via CLI:

```bash
# Check daemon health
curl http://127.0.0.1:35100/health

# List VMs
curl http://127.0.0.1:35100/vms

# Start a VM
curl -X POST http://127.0.0.1:35100/vm/default/start

# Alternatively, use the installed CLI directly:
colima list
colima start
colima stop
```

## Settings

Click menubar icon → **Preferences**:

- **Startup**: Launch at login toggle
- **Notifications**: VM state change alerts
- **Log Level**: debug/info/warn (affects `~/.colima-desktop/daemon.log`)

## Viewing Logs

Three log sources are available from the **Logs** menu:

1. **Daemon log** — `~/.colima-desktop/daemon.log`
2. **Colima log** — Colima's internal output
3. **Docker log** — Docker daemon output

## Diagnostics

Click menubar icon → **Export Diagnostics** to create a support bundle:

```
~/.colima-desktop/diagnostics-<timestamp>.tar.gz
```

Attach this file when reporting issues.

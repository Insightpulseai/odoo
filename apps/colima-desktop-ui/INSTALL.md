# Colima Desktop - Installation Guide

**Version**: 0.1.0
**Last Updated**: 2026-02-16

---

## Prerequisites

### System Requirements
- **macOS**: 12.0 (Monterey) or later
- **Architecture**: Intel (x64) or Apple Silicon (arm64)
- **Colima**: Must be installed separately (`brew install colima`)
- **Docker**: Optional (Colima provides Docker runtime)

### Why Separate Colima Installation?

Colima Desktop **does not auto-install Colima** for security reasons:

1. **No Helper Tools**: Colima Desktop runs without privileged helper processes
2. **User Control**: You choose where and how Colima is installed
3. **Security Isolation**: Desktop app cannot modify system packages
4. **Principle of Least Privilege**: UI operates in sandboxed environment

See `spec/colima-desktop/constitution.md` for full security rationale.

---

## Installation Methods

### Method 1: Homebrew (Recommended)

**Coming Soon** - Homebrew formula under development (Phase 3)

```bash
# Future installation command
brew install insightpulseai/colima-desktop/colima-desktop
```

### Method 2: Manual DMG Installation

1. **Download DMG**
   - Intel Mac: `Colima-Desktop-0.1.0.dmg`
   - Apple Silicon: `Colima-Desktop-0.1.0-arm64.dmg`

2. **Mount DMG**
   ```bash
   open Colima-Desktop-0.1.0.dmg  # or -arm64.dmg
   ```

3. **Install Application**
   - Drag `Colima Desktop.app` to `Applications` folder
   - Eject DMG when complete

4. **First Launch**
   - Open from Applications folder
   - macOS Gatekeeper may show security prompt (if unsigned)
   - For unsigned builds: System Settings → Privacy & Security → "Open Anyway"

---

## Post-Installation Setup

### 1. Install Colima (if not already installed)

```bash
# Install Colima via Homebrew
brew install colima

# Verify installation
colima version
```

### 2. Launch Colima Desktop

```bash
# From Applications folder
open -a "Colima Desktop"

# Or via CLI
/Applications/Colima\ Desktop.app/Contents/MacOS/Colima\ Desktop
```

### 3. First Launch Setup

On first launch, Colima Desktop will:

1. **Detect Colima Installation**
   - If not found: Shows setup guide with `brew install colima` command
   - If found: Proceeds to main UI

2. **Create State Directory**
   - Location: `~/.colima-desktop/`
   - Contents: config.yaml, logs/, diagnostics/

3. **Start Background Daemon**
   - Port: `localhost:35100`
   - PID file: `~/.colima-desktop/daemon.pid`

---

## Verification

### Check Installation

```bash
# Verify app installed
ls -la /Applications/Colima\ Desktop.app

# Check state directory
ls -la ~/.colima-desktop/

# Test daemon running
curl http://localhost:35100/v1/status
```

### Expected Output

```json
{
  "status": "stopped",
  "uptime": 0,
  "version": "0.1.0",
  "colima_installed": true,
  "colima_version": "0.7.8"
}
```

---

## Configuration

### State Directory Structure

```
~/.colima-desktop/
├── config.yaml           # User configuration
├── daemon.pid            # Daemon process ID (lock file)
├── logs/
│   ├── daemon.log       # Daemon logs (JSON lines)
│   ├── colima.log       # Colima CLI output
│   └── lima.log         # Lima output
└── diagnostics/         # Generated bundles
    └── diag-YYYYMMDD-HHMM.tar.gz
```

### Configuration File

Edit `~/.colima-desktop/config.yaml`:

```yaml
# Colima VM resources
cpu: 4
memory: 8  # GB
disk: 60   # GB

# Daemon settings
daemon:
  port: 35100
  log_level: info

# UI preferences
ui:
  theme: system  # system, light, dark
  start_on_login: false
```

**Note**: Resource changes require VM restart (manual approval required)

---

## Troubleshooting

### App Won't Launch

**Symptom**: Double-clicking app does nothing

**Solutions**:
1. Check Console.app for crash logs
2. Run from terminal to see errors:
   ```bash
   /Applications/Colima\ Desktop.app/Contents/MacOS/Colima\ Desktop
   ```
3. Check macOS Gatekeeper settings:
   - System Settings → Privacy & Security
   - Look for blocked app message
   - Click "Open Anyway"

### Daemon Not Starting

**Symptom**: UI shows "Daemon offline" error

**Solutions**:
1. Check for port conflict (35100):
   ```bash
   lsof -i :35100
   ```
2. Check daemon logs:
   ```bash
   tail -f ~/.colima-desktop/logs/daemon.log
   ```
3. Manually start daemon:
   ```bash
   /Applications/Colima\ Desktop.app/Contents/Resources/app.asar.unpacked/daemon/start
   ```

### Colima Not Detected

**Symptom**: App shows "Colima not found" message

**Solutions**:
1. Verify Colima installed:
   ```bash
   which colima
   colima version
   ```
2. Install if missing:
   ```bash
   brew install colima
   ```
3. Add to PATH if installed elsewhere:
   ```bash
   export PATH="/path/to/colima:$PATH"
   ```

### Permission Errors

**Symptom**: "Cannot write to ~/.colima-desktop/" errors

**Solutions**:
1. Check directory permissions:
   ```bash
   ls -ld ~/.colima-desktop/
   ```
2. Fix permissions if needed:
   ```bash
   chmod 755 ~/.colima-desktop/
   ```
3. Check PID file ownership:
   ```bash
   ls -l ~/.colima-desktop/daemon.pid
   ```

### State Directory Conflicts

**Symptom**: Two instances of daemon running

**Solutions**:
1. Check PID file:
   ```bash
   cat ~/.colima-desktop/daemon.pid
   ```
2. Kill existing daemon:
   ```bash
   kill $(cat ~/.colima-desktop/daemon.pid)
   rm ~/.colima-desktop/daemon.pid
   ```
3. Restart app

---

## Uninstallation

### Remove Application

```bash
# Remove app
rm -rf /Applications/Colima\ Desktop.app

# Remove state directory (optional - preserves logs/config)
rm -rf ~/.colima-desktop/
```

### Preserve Configuration

To keep your configuration for future reinstall:

```bash
# Backup config
cp ~/.colima-desktop/config.yaml ~/colima-desktop-config-backup.yaml

# Remove only app and daemon
rm -rf /Applications/Colima\ Desktop.app
kill $(cat ~/.colima-desktop/daemon.pid) 2>/dev/null
rm ~/.colima-desktop/daemon.pid
```

---

## Security Notes

### Electron Security Model

Colima Desktop implements strict Electron security:

- **contextIsolation**: Enabled (renderer isolated from Node.js APIs)
- **nodeIntegration**: Disabled (no direct Node.js access in UI)
- **sandbox**: Enabled (renderer process sandboxed)
- **Preload script**: Only interface between main and renderer

### IPC Security

- All IPC handlers validate payloads
- No arbitrary command execution
- Privileged operations (CLI, file system) run in main process only
- Renderer cannot spawn processes or access filesystem

### Network Security

- Daemon binds to `localhost` only (127.0.0.1:35100)
- No remote access
- No external network calls (except Colima CLI operations)

### File System Security

- All state confined to `~/.colima-desktop/`
- Atomic writes prevent corruption
- Config validation before applying changes
- No writes outside state directory

---

## Getting Help

### Documentation
- Architecture: `spec/colima-desktop/plan.md`
- API Reference: `tools/colima-desktop/README.md`
- Security Model: `spec/colima-desktop/constitution.md`

### Issue Reporting
- GitHub Issues: [insightpulseai/odoo](https://github.com/insightpulseai/odoo/issues)
- Include diagnostics bundle: UI → Help → Export Diagnostics

### Diagnostics Collection

```bash
# Via UI
# Help menu → Export Diagnostics → Save tar.gz

# Manual collection
cd ~/.colima-desktop/
tar -czf diagnostics/diag-$(date +%Y%m%d-%H%M).tar.gz \
  config.yaml \
  logs/daemon.log \
  logs/colima.log \
  logs/lima.log
```

---

## Next Steps

After installation:

1. **Start Colima VM**: UI → Start button or `colima start`
2. **Configure Resources**: UI → Settings → Adjust CPU/RAM/Disk
3. **View Logs**: UI → Logs → Monitor VM activity
4. **Export Diagnostics**: UI → Help → Export (for troubleshooting)

For advanced usage, see `tools/colima-desktop/README.md` for CLI commands and daemon API reference.

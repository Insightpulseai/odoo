# Colima Desktop — Installation Guide

## Requirements

- macOS 12 Monterey or later (Intel or Apple Silicon)
- [Colima](https://github.com/abiosoft/colima) installed separately

## Why Isn't Colima Included?

Colima Desktop is a GUI wrapper, not an installer. Per our [security model](../../../../spec/colima-desktop/constitution.md):

- Installing system software requires elevated privileges — we don't ask for them
- Colima receives active development; bundling it would lock you to an outdated version
- You can upgrade Colima independently without reinstalling the UI

## Option A: Homebrew (Recommended — Phase 3, after signing)

```bash
# Add the InsightPulse AI tap
brew tap insightpulseai/colima-desktop

# Install Colima Desktop
brew install insightpulseai/colima-desktop/colima-desktop

# Also install Colima itself (required runtime)
brew install colima
```

## Option B: Manual DMG (Phase 1 — unsigned, current)

1. Download the DMG for your architecture:
   - `Colima Desktop-0.1.0.dmg` (Intel x64)
   - `Colima Desktop-0.1.0-arm64.dmg` (Apple Silicon)

2. Open the DMG and drag **Colima Desktop.app** to Applications

3. **First launch (unsigned builds only)**:
   - Right-click (or Control-click) the app icon
   - Select **Open** from the context menu
   - Click **Open** in the dialog
   - This is a one-time step — Gatekeeper will remember your choice

4. Install Colima separately:
   ```bash
   brew install colima
   ```

## Verifying Installation

After launch, the menubar icon should appear. Click it and select **Status** — you should see:

```
Daemon: running (port 35100)
Colima: detected
```

If Colima is not detected, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md#colima-not-found).

## Uninstalling

**Homebrew**:
```bash
brew uninstall insightpulseai/colima-desktop/colima-desktop
```

**Manual**:
1. Drag `Colima Desktop.app` from Applications to Trash
2. Remove state directory (optional):
   ```bash
   rm -rf ~/.colima-desktop
   ```

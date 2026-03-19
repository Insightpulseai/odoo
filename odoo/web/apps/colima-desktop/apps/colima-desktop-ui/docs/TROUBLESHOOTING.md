# Colima Desktop — Troubleshooting

## Colima Not Found

**Symptom**: Status shows `Colima: not detected`

**Fix**:
```bash
# Install Colima
brew install colima

# Verify it's on PATH
which colima
colima --version
```

If already installed, ensure your shell PATH is visible to GUI apps:
```bash
# Check if Colima is in standard locations
ls /usr/local/bin/colima 2>/dev/null || ls /opt/homebrew/bin/colima 2>/dev/null
```

Colima Desktop checks `/usr/local/bin`, `/opt/homebrew/bin`, and `~/.local/bin`. If Colima is elsewhere, file an issue.

---

## Daemon Won't Start

**Symptom**: Menubar icon shows error, status stuck at `Daemon: starting...`

**Steps**:
1. Check daemon log:
   ```bash
   cat ~/.colima-desktop/daemon.log
   ```

2. Check if port 35100 is in use:
   ```bash
   lsof -i :35100
   ```
   If occupied, kill the conflicting process or change ports (currently hardcoded per security policy).

3. Remove stale socket:
   ```bash
   rm -f ~/.colima-desktop/daemon.sock
   ```

4. Restart the app.

---

## App Won't Open (Gatekeeper Warning)

**Symptom**: "Colima Desktop can't be opened because it is from an unidentified developer"

**Fix (unsigned builds — Phase 1 only)**:
- Right-click the app → **Open** → **Open** in dialog
- This is a one-time step per machine

**After Phase 2 (signed builds)**: This warning will not appear.

---

## VM Won't Start

**Symptom**: VM start fails or hangs

**Steps**:
1. Check Colima logs: menubar → **Logs** → **Colima Log**
2. Try starting directly: `colima start`
3. If Colima reports Lima errors, try:
   ```bash
   colima delete && colima start
   ```
   (Warning: this removes the VM)

---

## Docker Commands Fail After VM Start

**Symptom**: `docker ps` returns `Cannot connect to the Docker daemon`

**Steps**:
1. Verify VM is running:
   ```bash
   colima status
   ```

2. Check Docker context:
   ```bash
   docker context ls
   docker context use colima
   ```

3. Restart Docker context:
   ```bash
   colima stop && colima start
   ```

---

## Menu Appears But VM Controls Are Grey

**Cause**: Daemon is running but Colima binary not found or VM not initialized.

**Fix**:
1. Install Colima if missing: `brew install colima`
2. Initialize default VM if first time: `colima start`
3. Restart Colima Desktop

---

## Logs and Diagnostics

**Log locations**:
- Daemon: `~/.colima-desktop/daemon.log`
- App: Console.app → search "Colima Desktop"

**Export diagnostics**:
- menubar → **Export Diagnostics** → creates `~/.colima-desktop/diagnostics-<ts>.tar.gz`
- Include this file in bug reports

---

## Filing Issues

[GitHub Issues](https://github.com/Insightpulseai/odoo/issues)

Include:
1. macOS version (`sw_vers`)
2. Architecture (`uname -m`)
3. Colima version (`colima --version`)
4. Diagnostics bundle (see above)
5. Steps to reproduce

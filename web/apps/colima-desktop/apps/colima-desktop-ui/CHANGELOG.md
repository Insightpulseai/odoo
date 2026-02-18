# Changelog

All notable changes to Colima Desktop are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- Phase 2: Code signing + notarization configuration (pending Apple Developer account)
- Phase 3: Homebrew formula (`Formula/colima-desktop.rb`)
- Phase 3: Formula auto-update script (`scripts/update-formula.sh`)
- Phase 4: User documentation (INSTALL.md, QUICKSTART.md, TROUBLESHOOTING.md)
- Phase 4: CI release workflow (`.github/workflows/colima-desktop-release.yml`)

---

## [0.1.0] — 2026-02-17 (Unsigned — Phase 1)

### Added
- Electron menubar app for Colima VM management (macOS only)
- Fastify daemon on `127.0.0.1:35100` with REST API
  - `GET /health` — daemon health check
  - `GET /vms` — list VMs
  - `POST /vm/:name/start` — start VM
  - `POST /vm/:name/stop` — stop VM
  - `POST /vm/:name/restart` — restart VM
  - `GET /vm/:name/logs` — fetch logs
  - `GET /diagnostics` — export support bundle
- CLI-first architecture: all operations available via direct Colima CLI and REST API
- IPC bridge (Electron main ↔ renderer) with strict contextIsolation
- State directory: `~/.colima-desktop/` (config, logs, socket)
- Settings: startup-at-login, notifications, log level
- Logs viewer: daemon, Colima, Docker
- Diagnostics export: `~/.colima-desktop/diagnostics-<ts>.tar.gz`
- DMG packaging: x64 (100MB) + arm64 (95MB) unsigned builds

### Security
- No privileged operations (no setuid, no helper, no auto-install)
- No external network exposure (daemon binds 127.0.0.1 only)
- Electron hardened runtime entitlements configured
- Security audit: 3 low, 4 moderate, 1 high (ip — unfixable, dev-only), 0 critical

### Known Limitations
- Unsigned DMG: requires right-click → Open on first launch (Gatekeeper bypass)
- No code signing or notarization (Apple Developer account required)
- No Homebrew distribution (requires signed DMG)

---

[Unreleased]: https://github.com/Insightpulseai/odoo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Insightpulseai/odoo/releases/tag/v0.1.0

---
name: iot
description: Connect and manage physical devices (printers, scanners, payment terminals) via IoT box or Windows virtual IoT.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# iot — Odoo 19.0 Skill Reference

## Overview

The Odoo Internet of Things (IoT) module connects physical devices — barcode scanners, receipt printers, payment terminals, measurement tools, scales, and displays — to an Odoo database. Two IoT system types are supported: the **IoT box** (a dedicated micro-computer with pre-installed Odoo IoT software) and **Windows virtual IoT** (the Odoo IoT program installed on a Windows PC). IT administrators and operations staff use this module to bridge hardware peripherals with Odoo workflows in Point of Sale, Manufacturing, and Inventory.

## Key Concepts

- **IoT box**: Plug-and-play micro-computer (Raspberry Pi-based) with pre-installed IoT firmware.
- **Windows virtual IoT**: Odoo IoT program installable on any Windows computer (MRP cameras/measurement tools not supported).
- **IoT subscription**: Required for production use; auto-created when the IoT system connects to a database.
- **Pairing code**: Temporary code (valid ~2 hours) displayed on the IoT box screen/printer or Windows IoT homepage; used for initial connection.
- **Connection token**: Alternative offline pairing method; generated in developer mode from the IoT app.
- **HTTPS certificate**: TLS/SSL cert auto-downloaded when the IoT system connects to a production database with an active subscription. Required by payment terminals.
- **IoT system form**: Odoo record for a connected IoT system; lists connected devices, domain address, image version.

## Core Workflows

### 1. Connect IoT box to Odoo database

1. Install the **Internet of Things (IoT)** app.
2. Ensure IoT box and browser are on the same network.
3. Open the IoT app, click **Connect**.
4. If auto-detected, the box connects automatically. Otherwise, use pairing code or connection token.
5. Wait for HTTPS certificate provisioning (URL changes to `*.odoo-iot.com`).

### 2. Connect Windows virtual IoT

1. Install the Odoo IoT program on a Windows computer.
2. Open `http://localhost:8069` in a browser on that computer.
3. Note the pairing code from the homepage.
4. In Odoo IoT app, click **Connect** > **Use Pairing Code** > enter code > **Connect**.

### 3. Connect using a connection token (offline pairing)

1. Enable developer mode.
2. IoT app > **Connect** > **Offline pairing** > copy the token.
3. Access IoT system homepage > **Configure** > paste token into **Server Token** > **Connect**.

### 4. Disconnect IoT system

1. Open IoT app, click the IoT system card.
2. Click the Actions icon > **Delete**.
3. Alternatively, access IoT homepage > **Configure** > **Disconnect**.

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `iot.box` | IoT system record (box or Windows IoT) |
| `iot.device` | Individual device connected to an IoT system |

### Menu Paths

- `IoT` app (main dashboard with IoT system cards)
- Device form accessible from IoT system card

### HTTPS Certificate Eligibility

- Database must be a **production** instance (not copy/staging/dev).
- Odoo subscription must be **In Progress**.
- Certificate URL pattern: `*.odoo-iot.com`.

### System Parameters (developer mode)

- IoT system form shows: Domain Address, Image Version, SSL Certificate End Date.
- **Automatic drivers update** checkbox controls handler auto-update on restart.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **MRP devices on Windows**: Cameras and measurement tools are not compatible with Windows virtual IoT. Use an IoT box for these.
- **Pairing code expiry**: The code expires ~2 hours after power-on. Restart the IoT system to get a new code, or use a connection token.
- **Non-production databases**: HTTPS certificates are only issued to production instances. Using test/staging databases causes certificate issues.
- **Multiple IoT systems**: Multiple systems can run simultaneously, but each must be on the same network as the connecting browser during setup.
- **Already connected**: If the IoT system is already paired to another database (e.g., test), disconnect it before connecting to the new one.

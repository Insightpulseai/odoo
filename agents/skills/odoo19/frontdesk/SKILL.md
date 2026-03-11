---
name: frontdesk
description: "Visitor check-in system with kiosk stations, host notifications, drink service, and visitor tracking."
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# Frontdesk — Odoo 19.0 Skill Reference

## Overview

The **Frontdesk** app provides a self-service visitor check-in system for buildings or locations without a dedicated receptionist. Visitors check in at a kiosk, optionally select a host and a drink, and the relevant staff are notified via email, SMS, or Discuss. The app tracks visitor arrivals, departures, drink requests, and supports planned visitors with Quick Check In. Reports cover visitor volume and drink consumption.

## Key Concepts

- **Station** — A physical check-in location (lobby, reception desk). Each station has a unique Kiosk URL, responsible people, and configurable options.
- **Kiosk** — Web-based check-in interface displayed on a dedicated device (tablet/PC). Accessed via the station's Kiosk URL or the Open Desk button.
- **Visitor** — A non-employee who checks in. Tracked with name, company, phone, email, host, station, check-in/out times, and drink request.
- **Planned Visitor** — A pre-registered visitor entry created in advance. Shows in the Quick Check In panel on the kiosk.
- **Host Selection** — Option allowing visitors to select who they are meeting, triggering notifications.
- **Drinks** — Optional beverage offerings configured per station. Each drink has a name, notified people, and sequence.
- **Self Check-In** — QR code displayed on kiosk for mobile check-in.
- **Side Message** — Custom text displayed on the kiosk after check-in.
- **Visitor Status** — Planned, Checked-In, Checked-Out, Cancelled.

## Core Workflows

### 1. Create a Station

1. Navigate to `Frontdesk → Configuration → Stations`, click **New**.
2. Enter Frontdesk Name and Responsibles (required).
3. Save to generate the Kiosk URL.
4. **Options tab**: Configure Host Selection, Authenticate Guest (Email/Phone/Organization as Required/Optional/None), Theme (Light/Dark), Self Check-In, Offer Drinks.
5. If Host Selection is enabled: configure Notify by Email (template), Notify by SMS (template), Notify by Discuss.
6. **Side Message tab**: Enter welcome text displayed after check-in.

### 2. Configure Drinks

1. Navigate to `Frontdesk → Configuration → Drinks`, click **New**.
2. Enter Drink Name (required), People to Notify (required), Sequence (display order).
3. Optionally upload a photo.

### 3. Set Up a Kiosk

1. Click **Open Desk** on a station card (main dashboard) or copy the Kiosk URL to a device browser.
2. The user is automatically signed out of the database (security measure).
3. Kiosk displays current date/time and check-in interface.

### 4. Visitor Check-In

1. Visitor approaches the kiosk, taps **Check in**.
2. Enters name and any required information (email, phone, organization).
3. If Host Selection is enabled, selects the person they are meeting.
4. If drinks are offered, selects a drink or declines.
5. Confirmation screen appears with side message.
6. Host and station responsibles are notified via configured channels (email/SMS/Discuss).

### 5. Planned Visitor Quick Check-In

1. Pre-register a visitor: `Frontdesk → Visitors`, click **New**. Enter Name and Station (required).
2. When the planned visitor arrives, their name appears in the Quick Check In panel on the kiosk.
3. Visitor taps their name to check in instantly.
4. Note: Planned visitors must be checked in via the Visitors list if not using the kiosk, to update their Planned status.

### 6. Manage Visitors

1. Navigate to `Frontdesk → Visitors` to see all visitors (default filter: Planned or Checked-In, Today).
2. Click **Check out** to log visitor departure.
3. Click **Drink Served** once a drink has been delivered.
4. Click **Print Badge** for planned visitors to generate a PDF badge.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `frontdesk.frontdesk` | Station definition |
| `frontdesk.visitor` | Visitor record |
| `frontdesk.drink` | Drink option |

### Key Fields

- `frontdesk.frontdesk`: `name`, `responsible_ids`, `kiosk_url`, `host_selection`, `authenticate_guest`, `theme`, `self_checkin`, `offer_drinks`, `drink_ids`
- `frontdesk.visitor`: `name`, `company_name`, `phone`, `email`, `host_id`, `station_id`, `check_in`, `check_out`, `duration`, `state` (planned/checked_in/checked_out/cancelled), `drink_ids`
- `frontdesk.drink`: `name`, `notify_user_ids`, `sequence`

### Important Menu Paths

- `Frontdesk` — station dashboard (Kanban)
- `Frontdesk → Visitors` — visitor list
- `Frontdesk → Configuration → Stations`
- `Frontdesk → Configuration → Drinks`
- `Frontdesk → Reporting → Visitors` — visitor count by month
- `Frontdesk → Reporting → Drinks` — drink request totals

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Planned Visitors feature with Quick Check In panel on kiosk.
- Self Check-In QR code option for mobile check-in.
- Visitor badge printing (PDF) for planned visitors.
- Kiosk auto-returns to welcome screen after 10 seconds of inactivity during check-in.
- Accessing a kiosk signs the user out of the database automatically.

## Common Pitfalls

- **Kiosk access signs out the database user.** This is an intentional security measure; use a dedicated device for kiosks.
- **Planned visitors who check in via kiosk create a duplicate entry.** Their original Planned status does not update. Inform planned visitors to not use the kiosk, or manually reconcile entries.
- **Visitors do not check themselves out.** Staff must check out visitors from the Visitors list for accurate records.
- **Notify by Discuss requires the Discuss app.** Discuss is installed by default but if uninstalled, Discuss notifications fail silently.
- **SMS notifications require IAP credits.** SMS messages to hosts consume credits.

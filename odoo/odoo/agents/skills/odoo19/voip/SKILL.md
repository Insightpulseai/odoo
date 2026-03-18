---
name: voip
description: VoIP/Phone app for making calls, managing call queues, and integrating telephony with CRM and Helpdesk
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# voip -- Odoo 19.0 Skill Reference

## Overview

The Odoo Phone app (formerly VoIP) enables businesses to handle voice calls over the internet by integrating directly with Odoo apps like CRM and Helpdesk. It provides a persistent softphone widget for making/receiving calls, transferring/forwarding calls, sending emails, managing contacts, and tracking call activities. The app supports verified providers (Axivox, OnSIP, DIDWW) and custom SIP/WebRTC providers.

## Key Concepts

- **Phone Widget (Softphone)**: A floating widget accessible via the phone icon in the navigation bar. Has four tabs: Keypad, Recent, Contacts, Activities.
- **VoIP (Voice over Internet Protocol)**: Technology for handling calls not made from a phone line.
- **SIP (Session Initiation Protocol)**: Handles setup, management, and termination of calls.
- **WebRTC**: Browser-based real-time communication protocol required for the Phone widget.
- **Call Queue**: Routing system for support teams; customers wait when no agents are available.
- **Dial Plans**: Rules defining how VoIP calls are routed.
- **Verified Providers**: Axivox, OnSIP, DIDWW. Each has specific configuration steps.
- **Access Roles**: No (no VoIP access), Officer (view and report on all calls), Administrator (view, report, manage settings).
- **VoIP Secret**: User-specific password for the VoIP service provider, configured in user profile > VoIP tab > Credentials.

## Core Workflows

1. **Make a Call**
   1. Click the Phone (softphone) icon in the top navigation bar.
   2. Use Keypad tab to dial a number, or search/select a contact from Contacts tab.
   3. Click the phone icon to initiate the call.
   4. Use in-call controls as needed.

2. **Transfer a Call**
   1. Answer an incoming call with the green phone icon.
   2. Click the left-right arrows icon.
   3. Enter the extension number of the target user.
   4. Click Transfer.

3. **Forward a Call**
   1. Answer the incoming call.
   2. Click the left-right arrows icon.
   3. Enter the full phone number to forward to.
   4. Click Transfer.

4. **Add a Call Activity from CRM Pipeline**
   1. Open CRM > Pipeline in Kanban view.
   2. Open the Phone widget to Activities tab.
   3. Hover over an opportunity, click the phone + plus icon to schedule a call.

5. **Send an Email via Phone Widget**
   1. Open the Phone widget, find a contact.
   2. Click the envelope icon.
   3. Fill in recipients, subject, body.
   4. Click Send (or schedule for later).

6. **Configure VoIP Provider**
   1. Go to Phone app > Configuration > Settings.
   2. Click New, enter provider information (websocket URL, domain).
   3. For Axivox/OnSIP/DIDWW, follow provider-specific setup docs.
   4. Requirements: SIP server via websocket + WebRTC support.

7. **Assign VoIP Permissions**
   1. Go to Settings > Users & Companies > Users.
   2. Select user, open Access Rights tab.
   3. Under Productivity > VoIP, select No / Officer / Administrator.

## Technical Reference

- **Key Models**: `voip.call`, `voip.phonecall`, `voip.configurator`
- **User VoIP Config**: User form > VoIP tab. Fields: `voip_username` (extension), `voip_secret` (password).
- **Settings**: Phone app > Configuration > Settings. Fields: websocket URL, OnSIP Domain.
- **Phone Widget Tabs**:
  - Keypad: Dial by name or number
  - Recent: Call history (incoming/outgoing)
  - Contacts: Access to Contacts app records
  - Activities: Scheduled call activities with Done/Edit/Cancel actions
- **Activity Actions**: Contact info, Leads/Create Lead, Open related record, Done, Edit, Cancel, Call, SMS.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Module renamed from "VoIP" to "Phone" (Odoo Phone) in 19.0. Technical module name may still reference `voip`.
- DIDWW added as a third verified provider alongside Axivox and OnSIP.
- Database administrators are NOT automatically granted VoIP administrator rights; access must be set explicitly.

## Common Pitfalls

- **Missing Parameter**: Refresh the window if this error appears in the widget.
- **Incorrect Number**: Use international format with `+` prefix and country code (e.g., +16506913277).
- **Websocket connection lost**: Caused by inactivity or too many browser tabs. Refresh the page.
- **Failed to start user agent**: Browser or OS is out of date. Update both.
- **Grayed-out widget**: Update browser/OS and check for conflicting Chrome extensions.
- **Cannot connect**: Missing VoIP Secret in user profile > VoIP tab > Credentials.

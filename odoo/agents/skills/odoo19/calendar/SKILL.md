---
name: calendar
description: Scheduling app for meetings, events, and availability sharing with third-party calendar sync
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# calendar -- Odoo 19.0 Skill Reference

## Overview

Odoo Calendar is a scheduling application for planning meetings, events, employee appraisals, and project coordination. It integrates with Outlook and Google calendars, links to appointments, and connects to other Odoo apps via chatter activities. Views include Day, Week, Month, and Year with optional weekend display.

## Key Concepts

- **Event**: A calendar entry with start/end time, attendees, optional recurrence, tags, privacy, reminders, and videocall URL.
- **Attendees**: Participants of an event. The sidebar checkbox filter shows/hides individual calendars to coordinate availability.
- **Recurrence**: Repeat options (Daily, Weekly, Monthly, etc.) with configurable end conditions (number of repetitions, end date, or forever).
- **Share Availabilities**: Feature to select time slots on a Day view and generate a booking link or appointment for attendees.
- **Appointment**: A configurable booking type linked from Calendar. Supports Users or Resources, scheduling windows, assignment methods, questions, and messages.
- **Tags**: Labels like "Customer Meeting" or "Internal Meeting" for filtering events.
- **Videocall URL**: Link for virtual meetings; can generate an Odoo meeting link directly.
- **Third-party Sync**: Outlook and Google calendar synchronization via Client ID / Client Secret in Calendar > Configuration > Settings.

## Core Workflows

1. **Plan an Event**
   1. Open Calendar, click on a target date.
   2. Enter event title; adjust Start date/time, tick All Day if needed.
   3. Add Attendees.
   4. Optionally paste a Videocall URL or click "+ Odoo meeting."
   5. Click Save & Close, or More Options for Duration, Recurrence, Tags, Privacy, Reminders, Description.

2. **Sync Third-Party Calendar**
   1. Navigate to Calendar > Configuration > Settings.
   2. Enter Client ID and Client Secret for Outlook and/or Google.
   3. Optionally pause synchronization via checkbox.
   4. Click Save.

3. **Create Activity from Chatter**
   1. On any record, click Activities in the chatter.
   2. Select an Activity Type (e.g., Meeting, Call for Demo).
   3. Click Open Calendar to create the event in Calendar.

4. **Share Availabilities**
   1. On the Calendar dashboard, click "Share Availabilities."
   2. Switch to Day view; click and drag to select available times.
   3. Click Open to configure the associated appointment (scheduling, assignment method, questions, messages).
   4. Click Share to generate a link, or Publish to the website.

5. **Coordinate Team Availability**
   1. On the Calendar dashboard, tick the Attendees checkbox.
   2. Tick/untick individual users to overlay their calendars.

## Technical Reference

- **Key Models**: `calendar.event`, `calendar.attendee`, `calendar.recurrence`, `appointment.type`, `appointment.resource`
- **Key Fields on `calendar.event`**: `name`, `start`, `stop`, `allday`, `recurrency`, `partner_ids` (attendees), `videocall_location`, `privacy`, `categ_ids` (tags), `alarm_ids` (reminders), `appointment_type_id`, `description`
- **Appointment Tabs**: Schedule (time slots), Options (website, timezone, location, videoconference, payment, CRM opportunities, reminders, emails), Questions (custom fields), Messages (intro/confirmation text)
- **Calendar Sync Settings**: `calendar.provider.google`, `calendar.provider.outlook`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Share Availabilities integrated directly into the Calendar dashboard with appointment configuration.
- Appointment types support Resources (rooms, tables) with capacity management and auto-assign.

## Common Pitfalls

- Selecting availability time slots in Share Availabilities only works in Day calendar views.
- Synced calendar events propagate across platforms; deleting in one calendar deletes in the other.
- The "Show weekends" toggle is under the view options dropdown and may be missed.

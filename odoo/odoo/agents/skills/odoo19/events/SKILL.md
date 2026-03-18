---
name: events
description: Event management application for creating, selling tickets, managing tracks/booths, and analyzing event revenues.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# events — Odoo 19.0 Skill Reference

## Overview

The Events application manages the full lifecycle of in-person and online events: creation, ticketing, attendee registration, communication scheduling, booth management, track/talk scheduling, registration desk check-in (barcode/QR), and revenue reporting. It integrates with Website (front-end event pages), Sales (ticket sales orders), CRM (lead generation rules), Email Marketing, SMS Marketing, Social Marketing, and WhatsApp.

## Key Concepts

- **Event**: The central record containing dates, venue, tickets, communications, questions, and notes. Progresses through Kanban stages: New > Booked > Announced > Ended > Cancelled.
- **Event Template**: Pre-configured settings (tickets, communications, booths, questions, notes, submenu options) applied when creating new events. Default templates: Exhibition, Training, Sport.
- **Ticket / Event Ticket**: A purchasable registration product with name, product, price, sales start/end dates, maximum quantity, and badge color. Product Type must be "Event Ticket".
- **Track**: A talk, lecture, demonstration, or presentation scheduled within an event. Stages: Proposal > Confirmed > Announced > Published > Refused > Cancelled.
- **Booth**: A rentable space within an event, assigned to a Booth Category with product and price. Stages: Available, Unavailable.
- **Booth Category**: A tier/type of booth (e.g., Standard, Premium) linked to an Event Booth product, with optional sponsorship configuration.
- **Communication**: Scheduled messages (Mail, SMS, Social Post, WhatsApp) triggered at intervals relative to registration or event dates.
- **Registration Question**: Post-registration questions (Name, Email, Phone, Company, Selection, Text Input) with Ask once per order support.
- **Registration Desk**: Mobile-friendly check-in interface supporting barcode/QR badge scanning or manual attendee selection.
- **Sponsor**: An exhibitor linked to an event, optionally created when a booth with "Create Sponsor" is booked. Has Sponsor Level (Gold/Silver/Bronze) and Type.

## Core Workflows

### 1. Create an Event

1. Navigate to Events app, click **New**.
2. Enter **Event Name** (required), set **Date** and **Display Timezone**.
3. Optionally set Language, Template, Tags, Organizer, Responsible, Company, Website, Venue.
4. Configure **Tickets** tab: Add ticket lines with Name, Product (Event Ticket type), Price, Sales Start/End, Maximum.
5. Configure **Communication** tab: Add scheduled communications (Mail/SMS/Social Post/WhatsApp) with Interval, Unit, and Trigger (After each registration, Before/After the event).
6. Configure **Questions** tab: Add registration questions (Name, Email, Phone, etc.).
7. Add **Notes** tab: Internal notes and Ticket Instructions.
8. Click **Go to Website** smart button, customize the page, toggle to Published.

### 2. Sell Event Tickets

1. Enable **Tickets** and/or **Online Ticketing** in Events > Configuration > Settings.
2. Create ticket lines in the Tickets tab of the event form.
3. **Via Sales app**: Create a quotation, add an Event Ticket product, select event and ticket tier in the "Configure an event" popup.
4. **Via Website**: Visitors click Register on the event page, select ticket tier and quantity, fill attendee questions, proceed to payment.

### 3. Manage Event Tracks

1. Enable **Schedule & Tracks** in Events > Configuration > Settings.
2. From the event form, click the **Tracks** smart button.
3. Click **New** to create a track: Title, Track Date, Location, Duration, Speaker info.
4. Optionally enable **Live Broadcast** (YouTube link) and **Event Gamification** (quiz).
5. Move track through stages: Proposal > Confirmed > Announced > Published.
6. Publish via the Go to Website smart button toggle.

### 4. Manage Event Booths

1. Enable **Booth Management** in Events > Configuration > Settings.
2. Create Booth Categories at Events > Configuration > Booth Categories (assign Event Booth product, price, sponsorship options).
3. From the event form, click **Booths** smart button, then **New**.
4. Assign a Name and Booth Category. Renter fields auto-populate on purchase.
5. Booths appear on the event website under "Get A Booth" submenu.

### 5. Registration Desk Check-in

1. Navigate to Events > Registration Desk.
2. Choose **Scan a badge** (camera-based barcode/QR scanning) or **Select Attendee** (manual lookup).
3. For badge scanning: grant camera access, position badge code in viewfinder.
4. For manual selection: find attendee card, click checkmark to mark as attended.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `event.event` | Event record |
| `event.event.template` | Event template |
| `event.event.ticket` | Event ticket definition |
| `event.registration` | Attendee registration |
| `event.track` | Event track (talk/presentation) |
| `event.booth` | Event booth |
| `event.booth.category` | Booth category/tier |
| `event.sponsor` | Event sponsor |
| `event.track.location` | Track location (room) |
| `event.question` | Registration question |
| `event.question.answer` | Registration question answer option |

### Key Fields (event.event)

- `name` — Event name (required)
- `date_begin`, `date_end` — Event start/end datetime
- `date_tz` — Display timezone
- `event_type_id` — Event template link
- `tag_ids` — Tags (Many2many)
- `organizer_id` — Organizer contact
- `user_id` — Responsible user
- `company_id` — Company (multi-company)
- `website_id` — Restrict to specific website
- `address_id` — Venue (res.partner)
- `seats_limited` — Boolean for registration limit
- `seats_max` — Maximum attendees
- `badge_format` — Badge dimension (A4 foldable, A6, 4 per sheet)

### Key Settings

| Setting | Effect |
|---------|--------|
| Schedule & Tracks | Enables track management and event agenda |
| Live Broadcast | YouTube integration for online tracks |
| Event Gamification | Post-track quizzes |
| Online Exhibitors | Display sponsors/exhibitors on event pages |
| Community Chat Rooms | Virtual conference rooms (Jitsi) |
| Booth Management | Booth creation, sales, and management |
| Tickets | Sell tickets via Sales orders |
| Online Ticketing | Sell tickets via website/eCommerce |
| Use Event Barcode | Barcode/QR scanning for check-in |

### Key Menu Paths

- `Events > Events` — Main event dashboard
- `Events > Configuration > Settings` — App settings
- `Events > Configuration > Event Templates` — Template management
- `Events > Configuration > Booth Categories` — Booth tier configuration
- `Events > Configuration > Track Locations` — Room/location management
- `Events > Reporting > Revenues` — Revenue analysis
- `Events > Registration Desk` — Attendee check-in

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18.0 vs 19.0 breaking changes documented -->

## Common Pitfalls

- **Event Ticket product type**: Event registration products must have Product Type set to "Event Ticket" on the product form. Otherwise they cannot be selected in the Tickets tab.
- **Submenu visibility**: The event website submenu (Get A Booth, Talks, Agenda, etc.) may not appear by default. Enable it via the website editor's Customize tab (Sub-Menu Specific toggle) or via Debug mode checkboxes on the event form.
- **Communication templates**: Default communications are pre-configured on new events (confirmation + 2 reminders). Editing email templates via Settings > Technical > Email Templates affects all events using that template.
- **Daily email sending limit**: Odoo enforces a default daily limit of 200 emails across all applications; event invites count toward this limit.
- **WhatsApp templates require Meta approval**: WhatsApp communication templates cannot be edited during active configuration and require separate Meta approval.

---
name: appointments
description: Self-service scheduling app for booking meetings, consultations, and resource-based appointments
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# appointments -- Odoo 19.0 Skill Reference

## Overview

Odoo Appointments is a self-service scheduling application that allows companies to automate appointment booking for meetings, consultations, and services. It supports user-based and resource-based availability, capacity management, CRM opportunity creation, online payments, custom questions, and integration with the website for public booking pages. Appointments integrate with Calendar, CRM, employee schedules, and more.

## Key Concepts

- **Appointment Type**: A configurable template defining duration, scheduling window, availability, assignment method, and options for a bookable appointment.
- **Resources**: Physical items (rooms, tables, courts) with defined capacity and timezone. Managed at Appointments > Configuration > Resources.
- **Linked Resources**: Resources that can be combined to handle larger demand (only with auto-assign method).
- **Pre-Booking Time**: Minimum advance notice required before an appointment can start.
- **Scheduling Window**: Either "Available now" (with days-into-future limit) or "Within a date range."
- **Allow Cancelling**: Time window before appointment during which customers can cancel.
- **Assignment Method**: Pick User/Resource then Time, Select Time then User/Resource, or Select Time then auto-assign (resources only).
- **Manage Capacities**: Limits participants per resource based on defined capacity.
- **Manual Confirmation**: Requires approval before a booking is finalized; slot remains reserved until confirmed/rejected.
- **Create Opportunities**: Auto-creates a CRM opportunity for each scheduled appointment (requires CRM app).
- **System Parameter**: `appointment.resource_max_capacity_allowed` overrides the default max capacity display of 12 on the website.

## Core Workflows

1. **Create an Appointment Type**
   1. Open Appointments app, click New.
   2. Enter Appointment Title and Duration.
   3. Set Pre-Booking Time and Scheduling Window.
   4. Configure Allow Cancelling time window.
   5. Select Availability on: Users or Resources, then pick specific users/resources.
   6. Choose Assignment Method.
   7. Configure Schedule tab (days/times), Options tab (location, videoconference, reminders, guests), Questions tab, Messages tab.
   8. Save.

2. **Publish an Appointment to the Website**
   1. Open the appointment type record.
   2. Click the "Go to Website" smart button.
   3. Toggle from Unpublished to Published.

3. **Create a Resource**
   1. Navigate to Appointments > Configuration > Resources.
   2. Click New.
   3. Enter Name, Capacity, Timezone.
   4. Optionally set Linked Resources and Description.

4. **Configure Questions for Booking**
   1. Open an appointment type, go to Questions tab.
   2. Click Add a line.
   3. Enter Question, select Answer Type.
   4. Tick Mandatory Answer if required.
   5. Save & Close or Save & New.

5. **Override Resource Capacity Limit**
   1. Enable Developer Mode.
   2. Go to Settings > Technical > Parameters > System Parameters.
   3. Create new parameter: Key = `appointment.resource_max_capacity_allowed`, Value = desired max.

## Technical Reference

- **Key Models**: `appointment.type`, `appointment.resource`, `appointment.slot`, `appointment.question`
- **Appointment Type Fields**: `name`, `appointment_duration`, `min_schedule_hours` (pre-booking), `max_schedule_days`, `allow_cancel_hours`, `availability_on` (users/resources), `assign_method`, `schedule_based_on`, `question_ids`, `reminder_ids`
- **Resource Fields**: `name`, `capacity`, `timezone`, `linked_resource_ids`, `description`
- **Options Tab Fields**: `front_end_display`, `timezone`, `location`, `videoconference_link` (Odoo Discuss / Google Meet), `manual_confirmation`, `create_opportunity`, `reminder_ids`, `allow_guests`, `confirmation_email_template_id`, `cancelation_email_template_id`, `cc_to`
- **Schedule Tab**: Day-of-week time slots (from/to).
- **Messages Tab**: Introduction Message, Extra Message on Confirmation.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Pre-Booking Time field added to enforce minimum advance booking.
- Allow Cancelling field limits late cancellations with configurable error message.
- Up-front Payment option requires online payment before booking confirmation.
- Confirmation and Cancellation email templates configurable per appointment type.

## Common Pitfalls

- Website booking only displays resource capacity up to 12 by default; override with the `appointment.resource_max_capacity_allowed` system parameter.
- Linked Resources only work with the auto-assign assignment method; they are ignored for other methods.
- If a customer tries to cancel within the restricted window, they see an error with contact info (resource creator or assigned user).
- The Create Opportunities option is only visible if the CRM app is installed.
- Messages tab content is visible to customers; do not include internal-only information.

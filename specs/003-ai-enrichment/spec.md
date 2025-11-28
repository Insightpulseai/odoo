# Spec 003: AI Enrichment Agent

## 1. Goal
Turn the Odoo CRM into an intelligent database. When a new contact is created, an AI Agent should analyze their email domain, determine their industry, and auto-tag them in Odoo.

## 2. Architecture
* **Trigger:** Odoo "Automated Action" (Python) -> n8n Webhook.
* **Processor:** n8n + GPT-4o Mini.
* **Output:** Odoo (Write Tag + Internal Note).

## 3. Requirements
* **Speed:** Must process in <5 seconds.
* **Resilience:** If AI fails, Odoo must not crash.
* **Logic:**
    1.  Extract domain from email.
    2.  AI determines Industry (e.g., "Logistics") and Summary.
    3.  Check if Tag "Logistics" exists in Odoo.
    4.  If not, create it.
    5.  Update Contact with Tag and Summary.

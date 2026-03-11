---
name: integrations
description: Third-party integrations — mail plugins, Unsplash, geolocation, Google Translate, and cloud storage.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# integrations — Odoo 19.0 Skill Reference

## Overview

The Integrations module groups external service connections that extend Odoo's functionality: **Mail Plugins** (Outlook/Gmail sidebar for CRM, Helpdesk, Projects), **Unsplash** (stock photo library), **Geolocation** (OpenStreetMap or Google Places API for contact mapping and routes), **Google Translate** (chatter message translation), and **Cloud Storage** (Google Cloud Storage or Microsoft Azure Blob for attachment offloading). These integrations are configured in Settings and used across multiple Odoo applications.

## Key Concepts

- **Mail Plugins**: Free browser extensions for Outlook and Gmail that create leads, tasks, and tickets from the mailbox, and enrich contacts. Lead Enrichment uses IAP credits.
- **Unsplash**: Stock photography library integrated into the media picker. Odoo Online works out of the box; Odoo.sh/on-premise requires an Unsplash API key.
- **Geolocation**: Maps contacts/places on a map; supports OpenStreetMap (free, community-maintained) or Google Places API (paid, detailed).
- **Google Translate**: Translates chatter messages to the user's preferred language via Cloud Translation API. Requires a Google API key and billing account.
- **Cloud Storage**: Offloads chatter/email attachments to Google Cloud Storage or Microsoft Azure Blob. Odoo-generated files (sales orders, etc.) and Documents/Sign files always stay on the database server.

## Core Workflows

### 1. Install and use Mail Plugins (Outlook/Gmail)

1. Install the Mail Plugin for Outlook or Gmail from the respective app store.
2. The plugin adds a sidebar in the email client.
3. From an email, create CRM leads, project tasks, or helpdesk tickets.
4. Lead Enrichment populates contact data (uses Lead Generation IAP credits).

### 2. Configure Unsplash (Odoo.sh / on-premise)

1. Create an Unsplash account and register a new application (prefix name with `Odoo:`).
2. Copy the Access Key and Application ID.
3. Settings > General Settings > enable **Unsplash Image Library** > enter credentials.

### 3. Enable Geolocation

1. Settings > Integrations > activate **Geo Localization**.
2. Choose **Open Street Map** (free) or **Google Place Map** (enter API key).
3. Contacts and addresses can now be located on a map.

### 4. Configure Google Translate

1. Google API Console: create project "Odoo Translate".
2. Enable **Cloud Translation API** (requires billing).
3. Create API key credentials; optionally restrict to database URL and Cloud Translation API.
4. Odoo: Settings > Discuss section > **Message Translation** > paste API key > Save.
5. In any chatter, click `...` menu > **Translate**.

### 5. Set up Cloud Storage (Google Cloud)

1. Google Cloud: create service account, download JSON key.
2. Create a Cloud Storage bucket, grant service account **Storage Admin** role.
3. Install **Cloud Storage Google** module.
4. Settings > Cloud Storage > select **Google Cloud Storage** > enter bucket name > upload JSON key > set minimum file size.

### 6. Set up Cloud Storage (Microsoft Azure)

1. Azure: register app, note client/tenant IDs, create client secret.
2. Create storage account and container; configure CORS rules and role assignment (**Storage Blobs Data Contributor**).
3. Install **Cloud Storage Azure** module.
4. Settings > Cloud Storage > select **Azure Cloud Azure** > enter account name, container, tenant ID, client ID, client secret.

## Technical Reference

### Modules

| Module | Technical Name |
|--------|---------------|
| Mail Plugin (Outlook) | `mail_plugin_outlook` |
| Mail Plugin (Gmail) | `mail_plugin_gmail` |
| Unsplash Integration | (built-in to web) |
| Geolocation | `base_geolocalize` |
| Google Translate | (Discuss integration) |
| Cloud Storage Google | `cloud_storage_google` |
| Cloud Storage Azure | `cloud_storage_azure` |

### Menu Paths

- `Settings > Integrations > Geo Localization`
- `Settings > General Settings > Unsplash Image Library`
- `Settings > Discuss > Message Translation`
- `Settings > Cloud Storage`

### Storage Limits (reference)

| Hosting | Limit |
|---------|-------|
| Odoo Online | 100 GB |
| Odoo.sh Shared | 512 GB |
| Odoo.sh Dedicated | 4 TB |
| On-premise | Infrastructure-dependent |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Unsplash rate limit**: Non-Odoo-Online users are limited to a test key with max 50 requests/hour.
- **Google Translate billing**: The Cloud Translation API requires an active Google billing account; calls are not free.
- **OpenStreetMap accuracy**: Community-maintained data may be incomplete or inaccurate in some areas.
- **Cloud Storage scope**: Only chatter/email attachments are offloaded. Odoo-generated documents (SO PDFs, invoices) and Documents/Sign files remain on the server.
- **Azure client secret expiry**: Default expiry is 180 days. A new secret must be created and updated in Odoo before it expires.

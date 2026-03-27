# Google Workspace Extensibility Platform -- Knowledge Base

> Applies to: InsightPulseAI Gmail Add-on and future Google Workspace integrations
> Current add-on: Apps Script, clasp-deployed, Gmail-only
> Last researched: 2026-03-27

---

## Table of Contents

1. [Extend Google Workspace Overview](#1-extend-google-workspace-overview)
2. [Architecture Options](#2-architecture-options)
3. [Google Workspace Add-ons (Unified Model)](#3-google-workspace-add-ons-unified-model)
4. [Authentication Patterns for External Services](#4-authentication-patterns-for-external-services)
5. [Gmail-Specific Extensibility](#5-gmail-specific-extensibility)
6. [APIs and SDKs](#6-apis-and-sdks)
7. [Deployment and Distribution](#7-deployment-and-distribution)
8. [Security and Compliance](#8-security-and-compliance)
9. [Limitations and Gotchas](#9-limitations-and-gotchas)
10. [Recommendations for InsightPulseAI](#10-recommendations-for-insightpulseai)

---

## 1. Extend Google Workspace Overview

Reference: https://developers.google.com/workspace/extend

### 1.1 Extension Types

Google Workspace supports several extension models, each targeting different surfaces:

| Extension Type | Surface | UI Model | Runtime Options |
|---|---|---|---|
| **Google Workspace Add-ons** | Gmail, Calendar, Drive, Docs, Sheets, Slides | Card Service (JSON cards) | Apps Script or HTTP (any language) |
| **Editor Add-ons** | Docs, Sheets, Slides, Forms | HTML/CSS sidebars + dialogs | Apps Script only |
| **Google Chat Apps** | Google Chat | Cards + messages + dialogs | Apps Script, HTTP, Pub/Sub, AppSheet |
| **Google Meet Add-ons** | Google Meet | iframe (full web app) | Any web framework (iframe SDK) |
| **Link Previews / Smart Chips** | Docs, Sheets, Slides | Hover cards from pasted URLs | Apps Script or HTTP |
| **Third-Party Resource Creation** | Docs (@ menu) | Form dialog for creating external resources | Apps Script or HTTP |
| **Drive Apps** | Google Drive | Custom "Open with" and "New" actions | Web app with Drive API |
| **Calendar Conferencing Add-ons** | Google Calendar | Conference solution provider | Apps Script |

### 1.2 Add-on Type Comparison

There are two distinct add-on families:

**Google Workspace Add-ons (Unified)**
- Single codebase works across Gmail, Calendar, Drive, Docs, Sheets, Slides
- Card-based UI via CardService (Apps Script) or JSON (HTTP)
- Works on desktop and mobile
- Customizable homepages per host app
- This is the current and recommended model

**Editor Add-ons (Legacy)**
- Extend only Docs, Sheets, Slides, or Forms
- Full HTML/CSS UI via sidebars and dialogs
- Desktop only
- Must be implemented in Apps Script
- Cannot be directly upgraded to Workspace Add-ons (requires rewrite to Card UI)
- Still supported but not the recommended path for new development

### 1.3 Google Chat Apps

Google Chat apps (formerly "bots") are a separate category that can:
- Respond to messages in spaces and DMs
- Send proactive messages via webhooks or API
- Present card-based interactive UIs
- Use slash commands

Architecture options for Chat apps:
- **HTTP service**: Receives events via HTTP POST (most flexible)
- **Pub/Sub**: Asynchronous messaging, works behind firewalls
- **Apps Script**: Simplest setup, limited scalability
- **AppSheet**: No-code option
- **ADK/A2A agents**: AI agent integration (new in 2025)

Important 2025 change: Starting June 16, 2025, default function names for Chat app triggers change:
- `onAddToSpace` becomes `onAddedToSpace`
- `onRemoveFromSpace` becomes `onRemovedFromSpace`

### 1.4 Google Meet Add-ons

Meet add-ons are fundamentally different from other add-on types:
- Loaded as **iframes** inside Google Meet (not Card-based)
- Use the **Meet Add-ons SDK** (`@anthropic/meet-addon-sdk` style package)
- Two display surfaces: **side panel** and **main stage**
- Real-time collaboration via shared state
- Must be published through Google Workspace Marketplace
- Require full web development (any framework -- React, Vue, plain HTML)

Key interfaces:
- `MeetSidePanelClient`: Initial entry point, always visible
- `MeetMainStageClient`: Full-screen collaborative area
- `createAddonSession()`: Signals loading complete
- `notifySidePanel()` / `loadSidePanel()`: Cross-surface communication

Reference: https://developers.google.com/workspace/meet/add-ons/guides/overview

---

## 2. Architecture Options

Reference: https://developers.google.com/workspace/add-ons/guides/alternate-runtimes

### 2.1 Apps Script-Based Add-ons

**What we currently use for InsightPulseAI.**

| Aspect | Detail |
|---|---|
| Language | Google Apps Script (JavaScript ES6+ with V8 runtime) |
| Hosting | Google's servers (zero infrastructure) |
| Deployment | clasp push + Apps Script deployment |
| UI | CardService API (programmatic card building) |
| Auth to Google | Automatic via script scopes |
| Auth to external | UrlFetchApp with manual OAuth2 (library) |
| Storage | PropertiesService (9KB/key, 500KB total) |
| Execution limit | 6 minutes per execution (30 min for some Workspace accounts) |
| Network | UrlFetchApp (50MB GET response, 50MB POST) |
| Debugging | Stackdriver / Cloud Logging |
| Testing | Limited (no native test framework) |

**Strengths:**
- Zero infrastructure cost
- Automatic Google auth
- Fast prototyping
- Built-in services (GmailApp, DriveApp, etc.)
- No server maintenance

**Weaknesses:**
- 6-minute execution timeout
- No native dependency management (no npm/pip)
- Limited testing infrastructure
- PropertiesService storage limits (500KB total per user)
- No custom runtime environment
- Scaling is opaque (Google-managed)
- Cannot use binary libraries or native modules

### 2.2 Cloud-Based (HTTP) Add-ons

**The alternative runtime model -- any language, any hosting.**

| Aspect | Detail |
|---|---|
| Language | Any (Node.js, Python, Go, Java, etc.) |
| Hosting | Any HTTPS endpoint (Cloud Run, Azure Functions, etc.) |
| Deployment | Google Cloud Console > Marketplace SDK > HTTP Deployments |
| UI | JSON card definitions (identical visual output to CardService) |
| Auth to Google | ID token validation on incoming requests |
| Auth to external | Standard HTTP clients, any OAuth library |
| Storage | Any (database, Key Vault, Redis, etc.) |
| Execution limit | Determined by your hosting platform |
| Network | Unlimited (your runtime) |
| Debugging | Your logging infrastructure |
| Testing | Standard test frameworks for your language |

**How it works:**
1. Register HTTPS endpoints in the Google Cloud Console under Marketplace SDK > HTTP Deployments
2. Provide a JSON manifest defining triggers, scopes, and endpoint URLs
3. Google sends HTTP POST requests to your endpoints when triggers fire
4. Your service returns JSON card definitions
5. Google renders the cards identically to Apps Script CardService output

**Request validation:**
- Every request from Google includes an Authorization header with a Bearer token (ID token)
- Validate the token using Google's public keys
- The `authorizationEventObject` contains `userOAuthToken` and `userIdToken` for accessing Google services on behalf of the user

**Strengths:**
- Full language/framework choice
- Standard dependency management
- Full testing infrastructure
- No execution time limits (your infra)
- Unlimited storage options
- Standard CI/CD pipelines
- Binary library support
- Better error handling and debugging

**Weaknesses:**
- Infrastructure cost and maintenance
- Must handle token validation
- Must return properly formatted JSON cards
- More complex initial setup
- Must manage scaling yourself

Reference: https://developers.google.com/workspace/add-ons/guides/alternate-runtimes

### 2.3 Hybrid Approaches

You can combine both models:
- **Apps Script for simple triggers**, HTTP for complex processing
- **Apps Script as a thin proxy** that calls your backend
- **Gradual migration**: Start with Apps Script, move critical paths to HTTP

Our current InsightPulseAI add-on already follows a hybrid pattern:
- Apps Script handles UI rendering (CardService)
- UrlFetchApp calls Odoo backend for all data operations
- PropertiesService stores session tokens

### 2.4 When to Use Which Architecture

| Scenario | Recommendation |
|---|---|
| Prototype or MVP | Apps Script |
| Internal tool, < 50 users | Apps Script |
| Complex backend logic | HTTP (Cloud-based) |
| External service integration (primary function) | HTTP -- or Apps Script if UrlFetchApp suffices |
| Need npm/pip packages | HTTP |
| Need > 6 min execution | HTTP |
| Need > 500KB user storage | HTTP |
| Multi-language team | HTTP |
| Enterprise scale (1000+ users) | HTTP |
| Need existing CI/CD | HTTP |
| Cost-sensitive, simple logic | Apps Script |

### 2.5 Migration Path: Apps Script to Cloud-Based

The migration is not a rewrite -- it's a **re-hosting with JSON output**:

1. **Card UI**: Replace `CardService.newXxx()` calls with equivalent JSON objects. The visual output is identical.
2. **Triggers**: Map Apps Script trigger functions to HTTP endpoint URLs in the manifest.
3. **Auth**: Replace `PropertiesService` token storage with database/Key Vault. Replace `UrlFetchApp` with standard HTTP client.
4. **Google services**: Replace `GmailApp.getMessageById()` with Gmail API calls using the user's OAuth token from the request.
5. **Manifest**: Move from `appsscript.json` to the HTTP deployment manifest in Google Cloud Console.
6. **Deployment**: Replace `clasp push` with your CI/CD pipeline deploying to your hosting platform.

The JSON card format maps 1:1 to CardService:

```javascript
// Apps Script
CardService.newCardBuilder()
  .setHeader(CardService.newCardHeader().setTitle("Hello"))
  .addSection(
    CardService.newCardSection().addWidget(
      CardService.newTextParagraph().setText("World")
    )
  )
  .build();

// Equivalent JSON (HTTP add-on response)
{
  "action": {
    "navigations": [{
      "pushCard": {
        "header": { "title": "Hello" },
        "sections": [{
          "widgets": [{
            "textParagraph": { "text": "World" }
          }]
        }]
      }
    }]
  }
}
```

---

## 3. Google Workspace Add-ons (Unified Model)

Reference: https://developers.google.com/workspace/add-ons/overview

### 3.1 How the Unified Model Works

A Google Workspace Add-on is a single deployment that can extend multiple Google Workspace apps simultaneously. The manifest defines:

- **Common properties**: Name, logo, homepage trigger, universal actions
- **Per-host configuration**: Gmail triggers, Calendar triggers, Drive triggers, etc.
- **Scopes**: OAuth scopes required across all hosts

When a user installs the add-on, it appears in all configured host apps. The same code handles requests from Gmail, Calendar, Drive, etc., but receives different event objects depending on the host.

### 3.2 Manifest Structure (appsscript.json)

```json
{
  "addOns": {
    "common": {
      "name": "Add-on Name",
      "logoUrl": "https://...",
      "homepageTrigger": {
        "runFunction": "homepage"
      },
      "universalActions": [
        { "label": "Open App", "openLink": "https://..." }
      ]
    },
    "gmail": {
      "contextualTriggers": [
        { "unconditional": {}, "onTriggerFunction": "onGmailMessage" }
      ],
      "composeTrigger": {
        "selectActions": [
          { "text": "Insert from Odoo", "runFunction": "onCompose" }
        ],
        "draftAccess": "METADATA"
      }
    },
    "calendar": {
      "homepageTrigger": { "runFunction": "calendarHomepage" },
      "eventOpenTrigger": { "runFunction": "onCalendarEventOpen" },
      "eventUpdateTrigger": { "runFunction": "onCalendarEventUpdate" },
      "eventAttachmentTrigger": { "runFunction": "onCalendarEventAttachment" },
      "currentEventAccess": "READ_WRITE"
    },
    "drive": {
      "homepageTrigger": { "runFunction": "driveHomepage" },
      "onItemsSelectedTrigger": { "runFunction": "onDriveItemsSelected" }
    },
    "docs": {
      "homepageTrigger": { "runFunction": "docsHomepage" },
      "onFileScopeGrantedTrigger": { "runFunction": "onDocsFileScope" },
      "linkPreviewTriggers": [
        {
          "runFunction": "onLinkPreview",
          "patterns": [
            { "hostPattern": "erp.insightpulseai.com", "pathPrefix": "/web" }
          ],
          "labelText": "InsightPulseAI",
          "logoUrl": "https://..."
        }
      ]
    },
    "sheets": { "...similar to docs..." },
    "slides": { "...similar to docs..." }
  }
}
```

### 3.3 CardService Widgets Reference

Complete list of available CardService widget methods:

**Container Widgets:**
| Method | Purpose | Notes |
|---|---|---|
| `newCardBuilder()` | Top-level card container | Required |
| `newCardHeader()` | Card header with title, subtitle, image | One per card |
| `newCardSection()` | Section container for widgets | Multiple allowed |
| `newFixedFooter()` | Sticky footer with buttons | One per card |

**Content Widgets:**
| Method | Purpose | Notes |
|---|---|---|
| `newTextParagraph()` | Formatted text block | Supports HTML subset |
| `newDecoratedText()` | Text with top/bottom labels, icon, optional switch/button | **Replacement for deprecated `newKeyValue()`** |
| `newKeyValue()` | **DEPRECATED** -- use `newDecoratedText()` instead | Still works but should be migrated |
| `newImage()` | Display an image | URL-based |
| `newDivider()` | Horizontal line separator | No configuration needed |

**Interactive Widgets:**
| Method | Purpose | Notes |
|---|---|---|
| `newTextButton()` | Clickable text button | Action or OpenLink |
| `newImageButton()` | Clickable icon button | Predefined icons or URL |
| `newTextInput()` | Single-line text field | With hint, validation |
| `newSelectionInput()` | Checkboxes, radio, dropdown | Multiple types |
| `newDatePicker()` | Date selection | |
| `newTimePicker()` | Time selection | |
| `newDateTimePicker()` | Combined date+time | |
| `newSuggestions()` | Autocomplete suggestions | For text inputs |
| `newSwitch()` | Toggle switch | On DecoratedText |

**Layout Widgets:**
| Method | Purpose | Notes |
|---|---|---|
| `newGrid()` | Grid of items with images | 1-2 cols (side panel), 2-3 cols (dialog) |
| `newGridItem()` | Individual grid cell | Image + text + identifier |
| `newColumns()` | Two-column layout | Max 2 columns |
| `newColumn()` | Column within Columns | Alignment options |
| `newButtonSet()` | Horizontal button group | Groups multiple buttons |
| `newCollapseControl()` | Expand/collapse section | |

**Action Widgets:**
| Method | Purpose | Notes |
|---|---|---|
| `newAction()` | Callback action definition | setFunctionName, setParameters |
| `newActionResponseBuilder()` | Build action response | Navigation, notifications |
| `newNavigation()` | Card navigation | push, pop, update |
| `newOpenLink()` | Open URL in browser | OVERLAY or FULL_SIZE |
| `newAuthorizationAction()` | Trigger auth flow | For third-party OAuth |
| `newAuthorizationException()` | Force auth prompt | setAuthorizationUrl, setResourceDisplayName |
| `newNotification()` | Toast notification | setText |
| `newSuggestionResponseBuilder()` | Autocomplete response | |
| `newUniversalActionResponseBuilder()` | Universal action response | |

**Important deprecation note:**
`CardService.newKeyValue()` is deprecated. Our current add-on (`context.gs`, `homepage.gs`, `auth.gs`) uses `newKeyValue()` extensively. It should be migrated to `newDecoratedText()`:

```javascript
// DEPRECATED (current code)
CardService.newKeyValue()
  .setTopLabel("Name")
  .setContent("John Doe")

// REPLACEMENT
CardService.newDecoratedText()
  .setTopLabel("Name")
  .setText("John Doe")
```

### 3.4 Trigger Types

| Trigger | Host | Fires When |
|---|---|---|
| `homepageTrigger` | All | Add-on opened (no specific context) |
| `contextualTriggers` (unconditional) | Gmail | Any email message opened |
| `composeTrigger` | Gmail | Compose window opened with add-on active |
| `eventOpenTrigger` | Calendar | Calendar event opened |
| `eventUpdateTrigger` | Calendar | Calendar event saved/updated |
| `eventAttachmentTrigger` | Calendar | Calendar event attachment added |
| `conferenceSolution` | Calendar | Conference created |
| `onItemsSelectedTrigger` | Drive | Files selected in Drive |
| `onFileScopeGrantedTrigger` | Docs/Sheets/Slides | User grants file-level access |
| `linkPreviewTriggers` | Docs/Sheets/Slides | URL matching pattern pasted |
| `createActionTriggers` | Docs | @ menu resource creation |

### 3.5 Cross-Host Deployment

A single add-on can serve multiple hosts with per-host customization:

```javascript
function homepage(e) {
  var hostApp = e.hostApp;
  switch(hostApp) {
    case "GMAIL": return gmailHomepage(e);
    case "CALENDAR": return calendarHomepage(e);
    case "DRIVE": return driveHomepage(e);
    case "DOCS": return docsHomepage(e);
    case "SHEETS": return sheetsHomepage(e);
    default: return genericHomepage(e);
  }
}
```

The event object's `hostApp` field indicates which Google Workspace app triggered the request.

---

## 4. Authentication Patterns for External Services

Reference: https://developers.google.com/workspace/add-ons/guides/connect-third-party-service

### 4.1 Overview of Auth Patterns

| Pattern | Use Case | Complexity | Security |
|---|---|---|---|
| API Key (stored in UserProperties) | Simple backends, single-user | Low | Medium |
| OAuth2 via Apps Script library | Standard third-party OAuth flows | Medium | High |
| Service Account | Server-to-server, no user context | Medium | High |
| AuthorizationException flow | Card-based auth prompt | Medium | High |
| ID Token passthrough (HTTP add-ons) | Cloud-based add-ons accessing Google services | Low | High |

### 4.2 Our Current Pattern (InsightPulseAI)

The current add-on uses a **custom session token pattern**:

1. User provides Odoo credentials (API key or browser OAuth)
2. Add-on exchanges credentials for a session token via Odoo bridge endpoint
3. Token stored in `PropertiesService.getUserProperties()`
4. Token sent as `Authorization: Bearer` header on subsequent bridge calls
5. Token has an expiry; expired tokens trigger re-auth

This pattern works but has limitations:
- PropertiesService has 9KB per key / 500KB total limits
- No automatic token refresh for provider-based sessions
- Manual CSRF nonce management
- No encrypted storage (PropertiesService is plaintext)

### 4.3 OAuth2 to External Services (Standard Pattern)

For connecting to external OAuth2 services like Odoo behind Azure Front Door:

```javascript
// Using the Apps Script OAuth2 library
// https://github.com/googleworkspace/apps-script-oauth2

function getOdooOAuthService() {
  return OAuth2.createService('odoo')
    .setAuthorizationBaseUrl('https://erp.insightpulseai.com/auth_oauth/authorize')
    .setTokenUrl('https://erp.insightpulseai.com/auth_oauth/token')
    .setClientId('YOUR_CLIENT_ID')
    .setClientSecret('YOUR_CLIENT_SECRET')
    .setCallbackFunction('authCallback')
    .setPropertyStore(PropertiesService.getUserProperties())
    .setScope('openid profile email')
    .setParam('response_type', 'code');
}

function authCallback(request) {
  var service = getOdooOAuthService();
  var authorized = service.handleCallback(request);
  if (authorized) {
    return HtmlService.createHtmlOutput('Connected! Close this tab.');
  }
  return HtmlService.createHtmlOutput('Authorization denied.');
}
```

### 4.4 AuthorizationException Flow

The CardService provides a built-in auth flow for third-party services:

```javascript
function checkAuth() {
  var service = getOdooOAuthService();
  if (!service.hasAccess()) {
    CardService.newAuthorizationException()
      .setAuthorizationUrl(service.getAuthorizationUrl())
      .setResourceDisplayName('InsightPulseAI ERP')
      .setCustomUiCallback('createAuthCard')
      .throwException();
  }
}

function createAuthCard() {
  // Custom card shown when auth is needed
  // For public add-ons, you MUST use a custom card (not the default)
  return CardService.newCardBuilder()
    .setHeader(CardService.newCardHeader().setTitle('Connect to ERP'))
    .addSection(
      CardService.newCardSection()
        .addWidget(CardService.newTextParagraph().setText('Sign in to access your ERP data.'))
        .addWidget(
          CardService.newTextButton()
            .setText('Sign In')
            .setAuthorizationAction(
              CardService.newAuthorizationAction()
                .setAuthorizationUrl(getOdooOAuthService().getAuthorizationUrl())
            )
        )
    )
    .build();
}
```

**Important**: For public Marketplace add-ons, you must use a custom authorization card for all hosts except Google Chat. The default basic authorization card is only allowed for internal/private add-ons.

### 4.5 Token Storage Options

| Storage | Capacity | Scope | Encryption | Best For |
|---|---|---|---|---|
| `UserProperties` | 9KB/key, 500KB total | Per user per script | None (plaintext) | Small tokens, preferences |
| `ScriptProperties` | 9KB/key, 500KB total | Shared across all users | None | Config, shared state |
| `CacheService` | 100KB/key, 25MB total | Volatile (TTL-based) | None | Temporary data |
| External DB (via HTTP) | Unlimited | Custom | Custom | Production tokens, large state |
| Google Cloud Secret Manager | Unlimited | Per project | Google-managed | Secrets, API keys |

**Recommendation for InsightPulseAI**: For the current Apps Script architecture, `UserProperties` is appropriate for session tokens. If migrating to HTTP, use Azure Key Vault (already in our stack) for credential storage and a database for session state.

### 4.6 Best Practices for Enterprise Backend Connection

For connecting to Odoo behind Azure Front Door:

1. **Use API keys or OAuth2 tokens** -- never passwords
2. **Whitelist your backend URL** in `urlFetchWhitelist` (already done: `https://erp.insightpulseai.com/`)
3. **Set reasonable timeouts** in UrlFetchApp (default is 60 seconds, well within 6-min limit)
4. **Handle 401/403 gracefully** -- show re-auth card, not error
5. **Use JSON-RPC 2.0** consistently (already done in our bridge calls)
6. **Validate response structure** before accessing nested properties
7. **Log errors to Stackdriver** (already done via `Logger.log()`)
8. **Use `muteHttpExceptions: true`** to handle HTTP errors gracefully (already done)

---

## 5. Gmail-Specific Extensibility

Reference: https://developers.google.com/workspace/add-ons/gmail

### 5.1 Contextual Triggers

Gmail contextual triggers fire when a user opens an email message.

**Current limitation**: Gmail contextual triggers only support `unconditional` criteria -- they fire for **every** email message, regardless of content. There is no way to filter by sender, subject, or body content at the trigger level. Filtering must be done in your trigger function code.

Our add-on correctly uses unconditional triggers:
```json
"contextualTriggers": [
  { "unconditional": {}, "onTriggerFunction": "onGmailMessage" }
]
```

### 5.2 Compose Triggers

Compose triggers display an add-on card when the user opens the compose window:

```json
"composeTrigger": {
  "selectActions": [
    { "text": "Insert from Odoo", "runFunction": "onCompose" }
  ],
  "draftAccess": "METADATA"
}
```

**Draft access levels:**
- `NONE`: No access to draft content
- `METADATA`: Access to recipient lists (To, CC, BCC) -- requires `gmail.addons.current.message.metadata` scope
- Not available: full draft body access (must use Gmail API separately)

Our add-on does NOT currently use compose triggers. This is a potential enhancement for inserting Odoo record references into emails.

### 5.3 Message Read Access

When a contextual trigger fires, the event object includes `e.gmail.messageId`. Use this to access message data:

```javascript
var message = GmailApp.getMessageById(messageId);
var from = message.getFrom();       // Sender
var subject = message.getSubject();  // Subject
var body = message.getPlainBody();   // Plain text body
var html = message.getBody();        // HTML body
var to = message.getTo();            // Recipients
var cc = message.getCc();            // CC
var date = message.getDate();        // Date
var attachments = message.getAttachments(); // Attachments
```

**Scope requirements:**
- `gmail.addons.current.message.readonly` -- read current message
- `gmail.addons.current.message.metadata` -- read metadata only
- `gmail.addons.current.action.compose` -- interact with compose
- `gmail.readonly` -- read all messages (broader scope, triggers security review)

### 5.4 Side Panel Behavior

- Add-on cards render in a **right-side panel** in Gmail
- Panel width is fixed (~300-360px) -- cannot be resized by the add-on
- Grid widgets show 1-2 columns in the side panel, 2-3 in dialogs
- Cards auto-scroll if content exceeds panel height
- Maximum 100 widgets per card
- No custom HTML/CSS (card-based only for Workspace Add-ons)

### 5.5 Navigation and Action Callbacks

```javascript
// Push a new card onto the navigation stack
CardService.newNavigation().pushCard(card)

// Pop back to previous card
CardService.newNavigation().popCard()

// Pop to root card
CardService.newNavigation().popToRoot()

// Update current card in-place
CardService.newNavigation().updateCard(card)

// Open link in browser
CardService.newOpenLink()
  .setUrl("https://...")
  .setOpenAs(CardService.OpenAs.OVERLAY)      // or FULL_SIZE
  .setOnClose(CardService.OnClose.RELOAD_ADD_ON)  // or NOTHING

// Show toast notification
CardService.newActionResponseBuilder()
  .setNotification(CardService.newNotification().setText("Done!"))
  .build()
```

---

## 6. APIs and SDKs

### 6.1 Gmail API vs Apps Script Gmail Service

| Feature | Apps Script GmailApp | Advanced Gmail Service | Gmail REST API |
|---|---|---|---|
| Access model | Built-in service | Apps Script wrapper | HTTP/REST |
| Message read | `GmailApp.getMessageById()` | `Gmail.Users.Messages.get()` | `GET /gmail/v1/users/{id}/messages/{id}` |
| Threading | `GmailApp.getThreadById()` | `Gmail.Users.Threads.get()` | Full thread API |
| Labels | Basic label operations | Full label management | Full label management |
| Push notifications | Not available | Not available | `Users.watch()` with Pub/Sub |
| Batch operations | Limited | Batch requests | Full batch API |
| Raw message access | `getRawContent()` | `format: 'raw'` | `format=raw` |
| Complexity | Simplest | Medium | Most flexible |

**Our add-on uses** the basic `GmailApp` service, which is sufficient for reading sender email and subject from opened messages.

### 6.2 Google Workspace Events API

Enables push subscriptions for changes across Workspace apps:
- Subscribe to events (message received, calendar updated, etc.)
- Receive notifications via Cloud Pub/Sub or webhooks
- Useful for real-time sync scenarios
- Not typically used within add-ons (add-ons use triggers instead)

### 6.3 Apps Script API

Allows external applications to execute Apps Script functions:
- `scripts.run` -- execute a function remotely
- Useful for testing and external orchestration
- Requires OAuth2 authentication
- 6-minute execution timeout applies

### 6.4 Admin SDK

For organization-wide deployment and management:
- Domain-wide delegation of authority
- User and group management
- Organization unit management
- Licensing and entitlement management

### 6.5 Marketplace SDK

For publishing and managing app listings:
- Configure OAuth consent screen
- Manage app visibility (public/private/domain)
- Track installations
- Manage app versions

---

## 7. Deployment and Distribution

Reference: https://developers.google.com/workspace/marketplace/how-to-publish

### 7.1 Internal (Organization) Deployment

**For InsightPulseAI's current use case (private, single-org).**

Steps:
1. Create a standard Google Cloud project (not the default Apps Script project)
2. Link the Apps Script project to the GCP project
3. Enable the Google Workspace Marketplace SDK API
4. Configure the Marketplace SDK:
   - Set visibility to **Private** (organization only)
   - Configure OAuth consent screen
   - Declare all required scopes
5. Submit for publishing
6. **Private apps are immediately available** to all users in the Google Workspace organization

**No review process required for private apps.**

### 7.2 Public Marketplace Publishing

For future external distribution:

1. All steps from internal deployment plus:
2. **OAuth verification** (3-5 days for sensitive scopes)
3. **Security assessment** for restricted scopes (weeks, third-party assessor)
4. App review by Google team
5. Must use custom authorization cards (not default prompts)
6. Must handle granular consent (since May 2025)
7. Marketplace listing with description, screenshots, support info

### 7.3 Domain-Wide Installation by Admins

Google Workspace admins can:
- Install apps for their entire domain, specific OUs, or groups
- Pre-approve OAuth scopes (no user consent prompt)
- Service accounts get automatic permissions during domain-wide install
- Control which users can install Marketplace apps
- Monitor installed apps and their scopes

### 7.4 Testing and Staging Workflows

**Apps Script add-ons:**
- Use **head deployment** for development testing (auto-updates on save)
- Create **versioned deployments** for staging/production
- Test with specific Gmail accounts
- Use `clasp push` for deployment from git
- No separate staging environment (test with head deployment)

**HTTP add-ons:**
- Multiple deployments possible (dev, staging, prod)
- Each deployment has its own endpoint URLs
- Standard CI/CD applies
- Can use environment variables for configuration

### 7.5 Version Management

- Apps Script: Version = snapshot of code at a point in time
- Deployments reference a specific version or "head" (latest)
- `clasp push` updates the project code but does not create a version
- `clasp version` creates a numbered version
- `clasp deploy` creates/updates a deployment pointing to a version
- Marketplace listing references a specific deployment

---

## 8. Security and Compliance

### 8.1 OAuth Scope Classification

| Category | Review Required | Timeline | Example |
|---|---|---|---|
| Non-sensitive | None | Immediate | `script.locale`, `userinfo.email` |
| Sensitive | OAuth verification | 3-5 business days | `gmail.addons.current.message.readonly`, `calendar.readonly` |
| Restricted | Full security assessment | Weeks (third-party audit) | `gmail.readonly`, `gmail.modify`, `drive` |

**Our current scopes analysis:**

| Scope | Category | Notes |
|---|---|---|
| `gmail.readonly` | **Restricted** | Full Gmail read -- triggers security review |
| `gmail.addons.current.message.readonly` | Sensitive | Read only the open message |
| `gmail.addons.current.action.compose` | Sensitive | Compose interaction |
| `script.external_request` | Non-sensitive | UrlFetchApp access |
| `script.locale` | Non-sensitive | Locale detection |
| `gmail.addons.execute` | Non-sensitive | Add-on execution |
| `userinfo.email` | Non-sensitive | User email |

**Issue**: We currently request `gmail.readonly` (restricted scope). If we only need the current message, we should drop this to `gmail.addons.current.message.readonly` (sensitive, not restricted). This significantly simplifies the review process for public publishing.

### 8.2 Granular Consent (2025 Requirement)

Since May 27, 2025 (new HTTP add-ons) and December 1, 2025 (all HTTP add-ons):
- Users can selectively grant individual scopes
- Add-ons receive the list of granted scopes in `authorizationEventObject.authorizedScopes`
- Add-ons must gracefully handle partial scope grants
- Must request missing scopes when needed for specific features

**This does not currently apply to Apps Script add-ons** in the same way, but Apps Script IDE users can now selectively authorize scopes.

### 8.3 Security Review Process

For **public** add-ons with restricted scopes:
1. Submit OAuth verification request
2. Google reviews data access declarations
3. If restricted scopes are used: engage third-party security assessor (Google-approved)
4. Security assessment evaluates data handling, storage, access controls
5. Assessment must be renewed annually
6. Process can take several weeks

For **private** (organization-only) add-ons:
- No Google security review required
- Restricted scopes can be used freely
- Organization admin controls access

### 8.4 Data Access Declarations

Required for Marketplace publishing:
- Declare what user data is accessed and why
- Declare how data is stored and for how long
- Declare data sharing with third parties
- Must comply with Google API Services User Data Policy
- Must have a published privacy policy URL

### 8.5 Enterprise Compliance Considerations

For InsightPulseAI connecting to Odoo behind Azure Front Door:
- Data flows: Gmail (Google) --> Apps Script (Google) --> Odoo (Azure) --> PostgreSQL (Azure)
- PII handling: Email addresses, names, message content cross boundaries
- Token storage: Session tokens in Google PropertiesService (Google-managed, per-user)
- No data at rest in the add-on itself (all data lives in Odoo)
- Azure Front Door provides TLS termination, WAF, DDoS protection
- UrlFetchApp uses HTTPS by default (enforced by `urlFetchWhitelist`)

---

## 9. Limitations and Gotchas

### 9.1 Card Service Rendering Differences

| Issue | Detail |
|---|---|
| Side panel width | Fixed ~300-360px, cannot be customized |
| Grid columns | 1-2 in side panel, 2-3 in dialog |
| Image rendering | Different padding/scaling across hosts |
| HTML in text | Only a subset of HTML tags supported in `TextParagraph` |
| `newKeyValue` | Deprecated; some hosts may render differently than `newDecoratedText` |
| Mobile rendering | Cards render differently on mobile Gmail app |
| Dark mode | Card colors may not adapt to dark mode properly |

### 9.2 Execution Time Limits

| Context | Limit |
|---|---|
| Apps Script general | 6 minutes |
| Apps Script (Google Workspace accounts) | Up to 30 minutes |
| Simple trigger (onOpen, onEdit) | 30 seconds |
| Workspace Studio add-ons (Gemini Alpha) | 2 minutes |
| HTTP add-ons | Determined by hosting platform |

### 9.3 Quota Limits (Apps Script)

| Resource | Consumer Account | Workspace Account |
|---|---|---|
| Script runtime / day | 90 min | 6 hours |
| Triggers total / user | 20 | 20 |
| UrlFetch calls / day | 20,000 | 100,000 |
| UrlFetch data received / call | 50 MB | 50 MB |
| PropertiesService / value | 9 KB | 9 KB |
| PropertiesService / total | 500 KB | 500 KB |
| CacheService / value | 100 KB | 100 KB |
| CacheService / total | 25 MB | 25 MB |
| Email send / day | 100 | 1,500 |
| Calendar events created / day | 5,000 | 10,000 |

### 9.4 Network Call Limitations (Apps Script)

- `UrlFetchApp` is the only way to make HTTP calls
- No WebSocket support
- No streaming responses
- No gRPC
- Cannot set custom TLS certificates
- Cannot use client certificates for mTLS
- Maximum response size: 50 MB
- Default timeout: 60 seconds (configurable)
- Synchronous only (no async/await for network calls)
- URLs must be in `urlFetchWhitelist` for add-ons

### 9.5 PropertiesService Gotchas

- **No encryption**: Values stored as plaintext
- **No TTL**: Must implement expiry manually (as we do with `odoo_session_expires`)
- **No atomic operations**: Race conditions possible with concurrent access
- **Size limits**: 9 KB per value, 500 KB total per property store
- **String only**: Must serialize/deserialize complex objects
- **No enumeration by prefix**: Cannot query "all keys starting with X"

### 9.6 Known Incompatibilities

| Issue | Detail |
|---|---|
| Editor add-ons cannot become Workspace Add-ons | Requires full rewrite from HTML to Card UI |
| Legacy Gmail add-ons auto-upgraded | If not manually upgraded, get generic homepage |
| `newKeyValue()` deprecated | Still works but may be removed |
| Chat apps have separate auth model | Chat-specific service account patterns |
| Meet add-ons are entirely different | iframe-based, not card-based |
| File-scoped triggers in Editors | Require explicit user grant per document |
| Mobile Gmail app limitations | Some card features not available on mobile |

### 9.7 Common Development Pitfalls

1. **Forgetting `muteHttpExceptions: true`** -- UrlFetchApp throws on non-200 by default
2. **Not handling `e.gmail.messageId` being undefined** -- happens on homepage trigger
3. **Assuming all scopes are granted** -- granular consent means partial grants possible
4. **Storing large data in PropertiesService** -- hits 500KB limit silently
5. **Not whitelisting URLs** -- `urlFetchWhitelist` is enforced for add-ons
6. **Using `gmail.readonly` when `gmail.addons.current.message.readonly` suffices** -- unnecessarily triggers restricted scope review
7. **Not testing on mobile** -- card rendering differs significantly
8. **Hardcoding timezone** -- use `script.locale` scope and `Session.getScriptTimeZone()`

---

## 10. Recommendations for InsightPulseAI

### 10.1 Should We Stay on Apps Script or Migrate to Cloud-Based?

**Recommendation: Stay on Apps Script for now, plan for HTTP migration at scale.**

| Factor | Apps Script (Current) | HTTP (Future) |
|---|---|---|
| Our user base | < 50 users (internal) | Good fit | Overkill |
| Infrastructure | Zero cost, zero ops | Would need Azure Function/Container |
| Integration with Odoo | UrlFetchApp works fine | More flexibility, but same pattern |
| Testing | Limited but acceptable for internal | Full test suite possible |
| CI/CD | clasp push from git | Standard Azure DevOps pipeline |
| Execution limits | 6 min is enough for our bridge calls | Irrelevant for simple bridge calls |
| Token storage | PropertiesService is adequate | Could use Azure Key Vault |

**Migration trigger**: If any of these occur, migrate to HTTP:
- User base exceeds 200+ users
- Need npm packages (e.g., for AI/ML processing in the add-on)
- Need > 6 minute execution (unlikely for bridge calls)
- Need > 500KB user storage
- Public Marketplace publishing requires better testability
- Need to share add-on infrastructure with other services

### 10.2 Should We Convert to Workspace Add-on (Unified) from Gmail Add-on?

**Recommendation: Yes, upgrade to Workspace Add-on. Minimal effort, significant benefit.**

Our add-on is already structured as a Workspace Add-on in `appsscript.json`:
- Has `addOns.common` with homepage trigger
- Has `addOns.gmail` with contextual triggers
- Uses CardService (not HTML/CSS)

To fully leverage the unified model:

1. **Immediate** (low effort):
   - Migrate `newKeyValue()` to `newDecoratedText()` throughout
   - Drop `gmail.readonly` scope if `gmail.addons.current.message.readonly` suffices
   - Add `calendar` section to manifest (show Odoo events related to calendar entries)

2. **Short-term** (medium effort):
   - Add `docs` and `sheets` sections with `linkPreviewTriggers` for `erp.insightpulseai.com` URLs
   - When users paste Odoo links in Docs/Sheets, show a smart chip preview with record details
   - Add compose trigger for inserting Odoo record references into email drafts

3. **Future** (higher effort):
   - Add Drive integration (link Drive files to Odoo records)
   - Add Calendar integration (show Odoo context when viewing calendar events)
   - Add third-party resource creation (create Odoo leads from @ menu in Docs)

### 10.3 Multi-Host Support Effort Estimate

| Host | Effort | Value | Priority |
|---|---|---|---|
| Gmail (current) | Done | High | -- |
| Docs/Sheets link previews | 2-3 days | High | 1 |
| Gmail compose trigger | 1-2 days | Medium | 2 |
| Calendar event context | 3-5 days | Medium | 3 |
| Drive file linking | 3-5 days | Low-Medium | 4 |
| Google Chat app | 5-10 days (separate) | Medium | 5 |
| Google Meet add-on | 10+ days (different SDK) | Low | Not recommended |

**Link previews in Docs/Sheets have the best effort-to-value ratio.** Users paste Odoo URLs in documents regularly, and showing a smart chip with record name, status, and assignee is high-value and low-effort.

### 10.4 Auth Pattern Recommendation for Odoo Behind Azure Front Door

**Recommended architecture (current + improvements):**

```
Gmail Add-on (Apps Script)
  |
  |-- UrlFetchApp (HTTPS) --> Azure Front Door (TLS, WAF)
  |                               |
  |                               v
  |                           Odoo ERP (ACA)
  |                               |
  |                               v
  |                           PostgreSQL
  |
  |-- PropertiesService (session tokens, per-user)
```

**Improvements to implement:**

1. **Drop `gmail.readonly` scope**: Replace with `gmail.addons.current.message.readonly`. This is sufficient for our use case (reading the currently open message) and avoids restricted scope review.

2. **Implement proper OAuth2 flow for provider auth**: Instead of the current "open browser, paste code" pattern, use `CardService.newAuthorizationAction()` with the OAuth2 Apps Script library. This provides a smoother user experience.

3. **Add token refresh**: Currently, expired provider sessions require full re-auth. Implement automatic token refresh using refresh tokens stored in UserProperties.

4. **Consider the Apps Script OAuth2 library**: https://github.com/googleworkspace/apps-script-oauth2 -- this handles the OAuth2 dance, token storage, and refresh automatically.

5. **For HTTP migration (future)**: Use Azure Key Vault for token storage, Azure Managed Identity for service-to-service auth, and standard OAuth2 libraries in your language of choice.

### 10.5 Architecture Decision Matrix

| Decision | Current | Recommended | Rationale |
|---|---|---|---|
| Runtime | Apps Script | Apps Script (keep) | Sufficient for internal use, zero infrastructure |
| Add-on type | Gmail add-on | Workspace Add-on (upgrade) | Unlock Docs/Sheets/Calendar with minimal effort |
| Card API | `newKeyValue()` | `newDecoratedText()` | `newKeyValue` is deprecated |
| Gmail scope | `gmail.readonly` (restricted) | `gmail.addons.current.message.readonly` (sensitive) | Avoid restricted scope review |
| Auth to Odoo | Custom session token | Keep + add OAuth2 library for provider flow | Smoother UX, automatic refresh |
| Token storage | PropertiesService | PropertiesService (keep) | Adequate for < 200 users |
| Backend protocol | JSON-RPC 2.0 | JSON-RPC 2.0 (keep) | Working correctly, Odoo-native |
| Deployment | clasp push | clasp push (keep) | Simple, git-integrated |
| Distribution | Private/internal | Private first, public later | No review needed for private |
| Chat integration | None | Separate Google Chat app | Different surface, different value prop |
| Meet integration | None | Skip | Low value for ERP workflows |

---

## Appendix A: Key URLs

| Resource | URL |
|---|---|
| Extend Google Workspace | https://developers.google.com/workspace/extend |
| Workspace Add-ons Overview | https://developers.google.com/workspace/add-ons/overview |
| Add-on Types | https://developers.google.com/workspace/add-ons/concepts/types |
| HTTP Alternate Runtimes | https://developers.google.com/workspace/add-ons/guides/alternate-runtimes |
| CardService Reference | https://developers.google.com/apps-script/reference/card-service/card-service |
| Widgets Reference | https://developers.google.com/workspace/add-ons/concepts/widgets |
| Third-Party Service Auth | https://developers.google.com/workspace/add-ons/guides/connect-third-party-service |
| Gmail Add-on Triggers | https://developers.google.com/workspace/add-ons/concepts/workspace-triggers |
| Compose Triggers | https://developers.google.com/workspace/add-ons/gmail/extending-compose-ui |
| Restrictions | https://developers.google.com/workspace/add-ons/guides/workspace-restrictions |
| Quotas | https://developers.google.com/apps-script/guides/services/quotas |
| PropertiesService | https://developers.google.com/apps-script/guides/properties |
| Marketplace Publishing | https://developers.google.com/workspace/marketplace/how-to-publish |
| OAuth Scope Verification | https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification |
| Link Previews / Smart Chips | https://developers.google.com/workspace/add-ons/guides/preview-links-smart-chips |
| Third-Party Resource Creation | https://developers.google.com/workspace/add-ons/guides/create-insert-resource-smart-chip |
| Meet Add-ons SDK | https://developers.google.com/workspace/meet/add-ons/guides/overview |
| Google Chat Apps | https://developers.google.com/workspace/chat/overview |
| Chat App Architecture | https://developers.google.com/chat/concepts/structure |
| Granular Consent | https://developers.google.com/workspace/chat/authenticate-authorize-granular-oauth-permissions |
| Apps Script OAuth2 Library | https://github.com/googleworkspace/apps-script-oauth2 |
| Workspace Add-ons Release Notes | https://developers.google.com/workspace/add-ons/release-notes |

## Appendix B: Current Add-on File Inventory

| File | Purpose | Key Functions |
|---|---|---|
| `appsscript.json` | Manifest (scopes, triggers, config) | -- |
| `config.gs` | Tenant config, API paths, provider registry | `apiUrl()` |
| `auth.gs` | Session management, provider auth, API key auth | `getOdooSession()`, `startProviderAuth()`, `handleLogin()`, `fetchBridge()` |
| `homepage.gs` | Homepage trigger card | `homepage()` |
| `context.gs` | Contextual trigger (email opened) | `onGmailMessage()`, `contextCard()` |
| `actions.gs` | CRM/ticket/chatter action handlers | `createLead()`, `createTicket()`, `logToChatter()` |
| `.clasp.json` | clasp deployment config | -- |
| `package.json` | @types/google-apps-script for IDE support | -- |

---

*Last researched: 2026-03-27*
*Applies to: Google Workspace Add-ons documentation as of March 2026*

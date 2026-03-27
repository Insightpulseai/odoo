# Google Workspace Marketplace Publishing -- Knowledge Base

> Applies to: InsightPulseAI Gmail Add-on (Apps Script, clasp-deployed)
> Script ID: `1QaH14jbBl7PcvjLXgkzZogh6SzqS_kXoTJ_MzzmavW6CRLMANG24Ko4q`
> Last researched: 2026-03-27

---

## Table of Contents

1. [Developer Prerequisites](#1-developer-prerequisites)
2. [Publishing Flow](#2-publishing-flow)
3. [OAuth and Security Review](#3-oauth-and-security-review)
4. [Gmail Add-on Specifics](#4-gmail-add-on-specifics)
5. [Deployment Architecture](#5-deployment-architecture)
6. [Best Practices](#6-best-practices)
7. [Current Add-on Audit](#7-current-add-on-audit)

---

## 1. Developer Prerequisites

### 1.1 Standard GCP Project (Mandatory)

Apps Script creates a default GCP project automatically, but **the default project cannot be used for Marketplace publication**. You must:

1. Go to [Google Cloud Console](https://console.cloud.google.com/) > Create Project.
2. Name it descriptively (e.g., `insightpulseai-gmail-addon`).
3. Note the project number -- you will need it to link the Apps Script project.
4. Switch the Apps Script project from the default GCP project to this standard project.

**How to link**: In the Apps Script editor, go to Project Settings > Google Cloud Platform (GCP) Project > Change project, then enter the standard project number.

Equivalent via clasp: there is no CLI command to change the GCP project. This must be done in the Apps Script web editor or via the Apps Script API.

### 1.2 APIs to Enable in GCP

Enable these APIs in the standard GCP project:

| API | Purpose |
|-----|---------|
| Gmail API | Required for gmail.* scopes |
| Apps Script API | Required for clasp push/deploy |
| Google Workspace Marketplace SDK | Required for Marketplace configuration and publishing |
| Google Workspace Add-ons API | Required for add-on deployment |

### 1.3 OAuth Consent Screen Configuration

1. Go to APIs & Services > OAuth consent screen.
2. **User type**: Select "External" for public apps, or "Internal" for org-only (requires Google Workspace paid edition).
3. **App information**: App name, user support email, developer contact email.
4. **Scopes**: Add all scopes declared in `appsscript.json` (see Section 3 for classification).
5. **Test users**: Add email addresses of test users (max 100 while in "Testing" status).
6. **Publishing status**: Starts as "Testing" (limited to test users). Must be pushed to "In production" for Marketplace publishing.

### 1.4 Verified Domain Requirements

- The domain used in the OAuth consent screen (`insightpulseai.com`) must be verified in Google Search Console or via the GCP domain verification flow.
- The privacy policy URL and terms of service URL must be hosted on the verified domain.
- The `logoUrl` in `appsscript.json` (`https://erp.insightpulseai.com/web/static/img/logo.png`) must be accessible and served from a verified domain.

### 1.5 Developer Account

- The GCP project owner must be a Google account (personal or Workspace).
- For organization-internal publishing, the account must belong to the target Google Workspace domain.
- For public publishing, any Google account can be the publisher, but the app will be reviewed by Google.

---

## 2. Publishing Flow

### 2.1 Marketplace SDK Configuration

1. Enable the **Google Workspace Marketplace SDK** in the GCP project.
2. Navigate to the Marketplace SDK configuration page in GCP console.
3. Fill out the **App Configuration** tab:
   - **App Integration**: Select "Apps Script" and provide the deployment ID.
   - **App Visibility**: Choose Public, Private (org-only), or Unlisted. **This choice is permanent and cannot be changed after saving.**
   - **Install Settings**: Configure whether the app can be individually installed, admin-installed, or both.
   - **OAuth Scopes**: List all scopes from `appsscript.json`. These must match exactly.

### 2.2 Visibility Options

| Visibility | Who Can Find It | Google Review Required | Edition Required |
|------------|----------------|----------------------|-----------------|
| **Public** | Anyone on Marketplace | Yes (full review) | Any Google account |
| **Private** (org-only) | Users in your Google Workspace org | No | Google Workspace paid edition (Business Starter or higher) |
| **Unlisted** | Only via direct URL | Yes (if public scopes) | Any Google account |

**For InsightPulseAI v1 (private-first strategy)**:
- If publishing to the W9 Studio Google Workspace (`w9studio.net`), use **Private** visibility.
- Private apps are immediately available to the organization without Google review.
- The publishing Google Workspace account must belong to the target domain.

**For org-only / internal publishing**: Google Workspace Business Starter, Business Standard, Business Plus, Enterprise, Education, or Nonprofits editions all support internal Marketplace publishing. Google Workspace Essentials Starter (free) does NOT support internal Marketplace publishing.

### 2.3 Store Listing Configuration

Fill out the **Store Listing** tab:

| Field | Requirement |
|-------|-------------|
| App name | "InsightPulseAI for Gmail" (max 50 chars) |
| Short description | Max 140 characters |
| Detailed description | Full feature overview, max 16,000 characters |
| Category | Business Tools or Productivity |
| Application icon (32x32) | PNG, 32x32 pixels |
| Application icon (48x48) | PNG, 48x48 pixels |
| Application icon (96x96) | PNG, 96x96 pixels |
| Screenshots | At least 1, recommended 3-5. Show key features. |
| Banner | 220x140 pixels |
| Privacy policy URL | Must be on verified domain |
| Terms of service URL | Must be on verified domain |
| Support URL | Where users get help |
| Developer website | Organization website |

**Screenshot requirements**:
- Must show actual add-on UI in Gmail context.
- Must be high-quality and representative of current functionality.
- Do not include Google product branding or logos in custom screenshots.

### 2.4 Review and Approval Process

**Private/org-internal apps**: No Google review. Available immediately after publishing.

**Public apps**: Full review process:

| Phase | Typical Duration | Notes |
|-------|-----------------|-------|
| Marketplace SDK configuration review | 3-7 business days | Listing, metadata, screenshots |
| OAuth verification (sensitive scopes) | 3-6 weeks | Requires video demo, justification |
| OAuth verification (restricted scopes) | 4-8+ weeks | Additionally requires CASA security assessment |
| Combined end-to-end (public + sensitive) | 4-10 weeks | Can be longer during high-volume periods |

**Expediting**: There is no official fast-track. Real-world reports from 2025 show OAuth verification delays of 8+ weeks during high-volume periods.

### 2.5 Common Rejection Reasons

1. **Scope mismatch**: Scopes in OAuth consent screen, Marketplace SDK, and `appsscript.json` do not match exactly.
2. **Missing or inadequate privacy policy**: Must be publicly accessible, on verified domain, and explicitly describe data handling for each scope.
3. **Branding violations**: Using Google product icons, logos, or colors in app icon/screenshots. Icon must be wholly original.
4. **Multiple permission screens**: There should only be one permission prompt at install time.
5. **Functionality issues**: App crashes, errors, or non-functional features during review.
6. **Insufficient scope justification**: Reviewer cannot understand why a specific scope is needed.
7. **Missing demo video**: Required for sensitive/restricted scope verification.
8. **Inaccessible external endpoints**: If `https://erp.insightpulseai.com/` is down during review, the app will fail.

---

## 3. OAuth and Security Review

### 3.1 Scope Classification for This Add-on

| Scope | Classification | Verification Required |
|-------|---------------|----------------------|
| `gmail.readonly` | **Sensitive** | OAuth verification (video demo + justification) |
| `gmail.addons.current.message.readonly` | **Non-sensitive** (add-on scope) | No additional verification |
| `gmail.addons.current.action.compose` | **Non-sensitive** (add-on scope) | No additional verification |
| `script.external_request` | **Non-sensitive** | No additional verification |
| `script.locale` | **Non-sensitive** | No additional verification |
| `gmail.addons.execute` | **Non-sensitive** (add-on scope) | No additional verification |
| `userinfo.email` | **Non-sensitive** | No additional verification |

**Key finding**: The `gmail.addons.*` scopes are purpose-built for Gmail add-ons and are classified as non-sensitive. They provide scoped access to only the currently open message/action context, which is the recommended approach. However, `gmail.readonly` is a **sensitive scope** that grants read access to all messages, which triggers OAuth verification.

**Recommendation**: Evaluate whether `gmail.readonly` is truly needed. The add-on currently uses `GmailApp.getMessageById(messageId)` in the contextual trigger, which may work with just `gmail.addons.current.message.readonly`. If `gmail.readonly` can be removed, the entire OAuth sensitive-scope verification process can be avoided for public publishing.

### 3.2 Sensitive Scope Verification Requirements

If `gmail.readonly` is retained:

1. **Justification letter**: Explain why the add-on needs `gmail.readonly` and why narrower add-on scopes are insufficient.
2. **Demo video**: Record a screencast (unlisted YouTube) showing:
   - The add-on installation flow.
   - The consent screen with scopes listed.
   - Each feature that uses the sensitive scope.
   - How user data is handled and displayed.
3. **Privacy policy**: Must explicitly describe:
   - What Gmail data is accessed.
   - How it is processed (sent to `erp.insightpulseai.com`).
   - What is stored and for how long.
   - How users can request data deletion.
4. **Homepage with privacy link**: The domain homepage must have a visible link to the privacy policy.

### 3.3 Restricted Scope Implications

None of the current scopes are restricted. If the add-on ever adds scopes like `gmail.modify`, `gmail.compose` (full), or `mail.google.com`, it would trigger:

- **CASA (Cloud Application Security Assessment)**: Third-party security audit.
- **Annual renewal**: The security assessment must be renewed every year.
- **Limited Use compliance**: Must comply with the Google API Services User Data Policy "Limited Use" requirements.

### 3.4 Data Handling Declarations

For Marketplace and OAuth verification, declare:

| Data Type | Access | Storage | Sharing |
|-----------|--------|---------|---------|
| Sender email address | Read from open message | Sent to Odoo, stored as contact/lead reference | Shared with Odoo ERP instance |
| Email subject | Read from open message | Sent to Odoo for record naming | Shared with Odoo ERP instance |
| Message ID | Read from Gmail API | Not persisted beyond session | Not shared |
| User email (Gmail) | Read via Session API | Stored in user properties for session | Not shared externally |
| Odoo session token | Received from Odoo | Stored in user properties (encrypted by Google) | Not shared |
| Odoo API key | User-provided | Stored in user properties (encrypted by Google) | Sent to Odoo for auth |

**Important**: `PropertiesService.getUserProperties()` is per-user, per-script, and encrypted at rest by Google. This is the correct storage mechanism for add-on credentials.

### 3.5 Privacy Policy Requirements

The privacy policy must cover:

1. **Identity of the data controller**: InsightPulseAI.
2. **Data collected**: Email sender, subject, user email for auth.
3. **Purpose of data collection**: CRM integration, lead creation, ticket creation, chatter logging.
4. **Third-party data sharing**: Data is sent to the user's configured Odoo ERP instance.
5. **Data retention**: How long session tokens and credentials are stored.
6. **User rights**: How to disconnect, delete stored data, and contact support.
7. **Security measures**: HTTPS-only communication, per-user encrypted storage.
8. **Contact information**: Support email and physical address (required).
9. **Limited Use disclosure**: Affirmative statement that the app complies with Google API Services User Data Policy.

---

## 4. Gmail Add-on Specifics

### 4.1 Legacy Gmail Add-on vs Workspace Add-on

| Feature | Legacy Gmail Add-on | Google Workspace Add-on |
|---------|-------------------|------------------------|
| Extends | Gmail only | Gmail, Calendar, Drive, Docs, Sheets, Slides |
| Homepage trigger | Not supported | Supported |
| Contextual triggers | Gmail message context | Gmail message + compose context |
| Manifest format | `gmail` section only | `addOns.common` + `addOns.gmail` |
| Status | **Deprecated** (still functional) | **Current / recommended** |
| Marketplace publishable | Yes (but legacy) | Yes |
| CardService version | V1 (limited widgets) | V1 + newer widgets |

**The current add-on uses the Workspace Add-on manifest format** (`addOns.common` + `addOns.gmail`), which is correct and current.

### 4.2 CardService API: newKeyValue vs newDecoratedText

**`CardService.newKeyValue()` is officially deprecated.** The replacement is `CardService.newDecoratedText()`.

| Deprecated Method | Replacement Method |
|------------------|-------------------|
| `newKeyValue().setTopLabel(x)` | `newDecoratedText().setTopLabel(x)` |
| `newKeyValue().setContent(x)` | `newDecoratedText().setText(x)` |
| `newKeyValue().setBottomLabel(x)` | `newDecoratedText().setBottomLabel(x)` |
| `newKeyValue().setOnClickAction(x)` | `newDecoratedText().setOnClickAction(x)` |
| `newKeyValue().setButton(x)` | `newDecoratedText().setButton(x)` |
| `newKeyValue().setSwitch(x)` | `newDecoratedText().setSwitchControl(x)` |
| `newKeyValue().setMultiline(true)` | `newDecoratedText().setWrapText(true)` |

**Current add-on status**: The add-on uses `newKeyValue()` extensively in `homepage.gs` and `context.gs`. These must be migrated to `newDecoratedText()` before Marketplace submission to avoid review issues and future breakage.

### 4.3 Contextual Trigger Configuration

The current manifest uses an **unconditional contextual trigger**:

```json
"gmail": {
  "contextualTriggers": [
    {
      "unconditional": {},
      "onTriggerFunction": "onGmailMessage"
    }
  ]
}
```

This fires for every opened email message. For Marketplace review:
- This is acceptable but must be justified (the add-on provides CRM context for any sender).
- The trigger function must be fast (under 30 seconds, ideally under 5 seconds).
- If the Odoo bridge is slow or down, the add-on must handle errors gracefully (not crash).

### 4.4 Homepage Trigger Configuration

The current manifest correctly declares a homepage trigger:

```json
"common": {
  "homepageTrigger": {
    "runFunction": "homepage",
    "enabled": true
  }
}
```

This renders when the user opens the add-on sidebar without a specific message selected. The homepage shows connection status, tenant info, and quick actions.

### 4.5 URL Fetch Whitelist

The manifest includes:

```json
"urlFetchWhitelist": [
  "https://erp.insightpulseai.com/"
]
```

This is required for any add-on that makes external HTTP requests. All `UrlFetchApp.fetch()` calls must target URLs that match this whitelist. The whitelist uses prefix matching, so `https://erp.insightpulseai.com/ipai/mail_plugin/session` matches.

---

## 5. Deployment Architecture

### 5.1 Clasp-to-Marketplace Relationship

```
Local code (.gs files)
    |
    v  clasp push
Apps Script project (cloud)
    |
    v  clasp deploy / Apps Script editor
Versioned deployment (immutable snapshot)
    |
    v  Deployment ID entered in Marketplace SDK
Marketplace listing (references deployment)
```

**Key concepts**:

1. **`clasp push`**: Uploads local files to the Apps Script project. Does NOT create a version or deployment.
2. **`clasp deploy`**: Creates a new versioned deployment (immutable snapshot of current code). Returns a deployment ID.
3. **Marketplace SDK**: References a specific deployment ID. To update the published add-on, create a new deployment and update the Marketplace SDK configuration.
4. **Head deployment**: The always-latest deployment used for testing. NOT suitable for Marketplace.

### 5.2 Linking Apps Script to GCP Project

1. Open the Apps Script project in the web editor.
2. Go to Project Settings (gear icon).
3. Under "Google Cloud Platform (GCP) Project", click "Change project".
4. Enter the **project number** (not project ID) of the standard GCP project.
5. Confirm the switch.

**After linking**:
- The OAuth consent screen from the GCP project applies to the Apps Script project.
- APIs enabled in the GCP project are available to the script.
- The Marketplace SDK in the GCP project can reference this script's deployments.

### 5.3 Version Management and Update Rollout

```bash
# Development workflow
clasp push                        # Upload code changes
clasp deploy -d "v1.0.0"         # Create immutable deployment
# Note the deployment ID (AKf...)

# Update workflow
clasp push                        # Upload new code
clasp deploy -d "v1.1.0"         # Create new deployment
# Update Marketplace SDK with new deployment ID

# List deployments
clasp deployments                 # Show all deployments with IDs
```

**Rollback**: Since each deployment is an immutable snapshot, rolling back means updating the Marketplace SDK to point to a previous deployment ID.

**User update propagation**: After updating the Marketplace SDK configuration:
- For individually installed add-ons: Users get the update automatically (Google caches aggressively; may take up to 24 hours).
- For admin-installed add-ons: The update propagates to all domain users automatically.

### 5.4 Testing Before Publication

**Phase 1 -- Developer testing (no Marketplace)**:
1. Use `clasp push` to update the script.
2. Open Gmail and access the add-on from the side panel.
3. The "head" deployment is used automatically for the script owner.

**Phase 2 -- Test users (OAuth consent screen)**:
1. In GCP > OAuth consent screen, add test user email addresses.
2. While the app is in "Testing" publishing status, only these users can install.
3. Max 100 test users.

**Phase 3 -- Draft testers (Marketplace SDK)**:
1. In the Marketplace SDK > Store Listing > Draft Tester section, add email addresses.
2. These users can preview the Marketplace listing and install the draft version.
3. Use the unlisted URL provided by the Marketplace SDK to share with testers.

**Phase 4 -- Publication**:
1. For private: Publish immediately to the organization.
2. For public: Submit for Google review.

---

## 6. Best Practices

### 6.1 Marketplace Listing Optimization

- **App name**: Clear, descriptive, includes the host app. "InsightPulseAI for Gmail" or "InsightPulseAI -- Odoo CRM for Gmail".
- **Short description**: Focus on the primary value. "Connect Gmail to your Odoo ERP. Create leads, tickets, and tasks from any email."
- **Detailed description**: Structure with headers, bullet points, feature list. Include: what it does, who it is for, key features, how to get started.
- **Screenshots**: Show the contextual card with real data, the homepage, the login flow, and a create-lead action result. 3-5 screenshots is optimal.
- **Category**: "Business Tools" is most appropriate.

### 6.2 User Consent and Data Minimization

- **Remove `gmail.readonly` if possible**: This is the single most impactful change for reducing verification burden. Test whether `gmail.addons.current.message.readonly` alone is sufficient for `GmailApp.getMessageById()`.
- **Minimize stored data**: The add-on correctly uses `UserProperties` (per-user, encrypted). Do not store message content.
- **Clear session management**: The `clearSession()` function properly removes all stored credentials. Expose this clearly in the UI.
- **Transparent data flow**: The privacy policy must describe exactly what data leaves the browser (sender email, subject) and where it goes (Odoo ERP).

### 6.3 Error Handling for Add-on Edge Cases

| Scenario | Current Handling | Recommendation |
|----------|-----------------|----------------|
| No message ID in event | Returns error card | Correct |
| Odoo bridge unreachable | Returns null, shows generic error | Add retry with exponential backoff for transient failures |
| Session expired | Returns login card | Correct |
| Bridge returns error JSON | Logs and returns null | Surface the error message to the user when actionable |
| `UrlFetchApp` quota exceeded | Unhandled exception | Wrap in try/catch, show "Please try again in a moment" |
| Add-on render timeout (30s) | Unhandled | Ensure bridge calls complete within 10-15 seconds |

### 6.4 Performance in Gmail Sidebar Context

- **Target latency**: Homepage should render in under 2 seconds. Contextual card in under 5 seconds.
- **Gmail add-on execution limit**: 30 seconds per trigger invocation. If the Odoo bridge is slow, the add-on will timeout.
- **Caching**: Consider using `CacheService.getUserCache()` to cache Odoo contact lookups for 5-10 minutes. This reduces bridge calls for repeated opens of emails from the same sender.
- **Payload size**: Keep CardService responses small. Gmail sidebar has limited real estate. Limit lists to 5 items (the add-on already does this for leads/tickets).
- **External fetch optimization**: The `urlFetchWhitelist` enables preflight caching by Google. Ensure the Odoo bridge returns proper `Cache-Control` headers for idempotent endpoints.

---

## 7. Current Add-on Audit

### 7.1 Issues to Fix Before Publishing

| Priority | Issue | File(s) | Action |
|----------|-------|---------|--------|
| **P0** | `newKeyValue()` is deprecated | `homepage.gs`, `context.gs`, `auth.gs` | Migrate all instances to `newDecoratedText().setText()` / `.setTopLabel()` |
| **P1** | `gmail.readonly` scope may be unnecessary | `appsscript.json` | Test if `gmail.addons.current.message.readonly` alone supports `GmailApp.getMessageById()` in contextual triggers |
| **P1** | No standard GCP project linked | Project settings | Create standard GCP project and link |
| **P1** | No privacy policy URL | Marketplace listing | Create and host at `https://insightpulseai.com/privacy` or `https://erp.insightpulseai.com/privacy` |
| **P2** | No terms of service URL | Marketplace listing | Create and host on verified domain |
| **P2** | Missing Marketplace icon assets | Marketplace listing | Generate 32x32, 48x48, 96x96 PNG icons |
| **P2** | Missing screenshots | Marketplace listing | Capture 3-5 screenshots of add-on in Gmail |
| **P3** | No `CacheService` for contact lookups | `context.gs` | Add caching layer for bridge responses |
| **P3** | Error messages are generic | `actions.gs` | Surface specific Odoo error details when safe |

### 7.2 Scope Reduction Analysis

Current scopes in `appsscript.json`:

```
gmail.readonly                              -> SENSITIVE: may be removable
gmail.addons.current.message.readonly       -> OK: required for contextual trigger
gmail.addons.current.action.compose         -> OK: required for compose actions
script.external_request                     -> OK: required for UrlFetchApp
script.locale                               -> OK: required for useLocaleFromApp
gmail.addons.execute                        -> OK: required for add-on execution
userinfo.email                              -> OK: required for user identification
```

**Test plan for `gmail.readonly` removal**:
1. Remove `gmail.readonly` from `appsscript.json`.
2. Push via `clasp push`.
3. Open a Gmail message with the add-on active.
4. Verify `GmailApp.getMessageById(e.gmail.messageId)` still works with only `gmail.addons.current.message.readonly`.
5. If it works: the scope can be permanently removed, eliminating the need for sensitive-scope OAuth verification.
6. If it fails: the scope must be retained, and OAuth verification with video demo is required.

### 7.3 Publishing Checklist

**Pre-requisites**:
- [ ] Standard GCP project created and linked to Apps Script project
- [ ] Gmail API enabled in GCP project
- [ ] Apps Script API enabled in GCP project
- [ ] Google Workspace Marketplace SDK enabled in GCP project
- [ ] OAuth consent screen configured with all scopes
- [ ] Domain verified (`insightpulseai.com`)
- [ ] Privacy policy hosted and accessible
- [ ] Terms of service hosted and accessible

**Code readiness**:
- [ ] All `newKeyValue()` migrated to `newDecoratedText()`
- [ ] `gmail.readonly` scope tested for removability
- [ ] Error handling covers all edge cases
- [ ] Bridge endpoints (`erp.insightpulseai.com`) are stable and responsive
- [ ] `urlFetchWhitelist` covers all external URLs

**Marketplace assets**:
- [ ] App icon: 32x32, 48x48, 96x96 PNG (original, no Google branding)
- [ ] Screenshots: 3-5 showing key features in Gmail context
- [ ] Banner image: 220x140 pixels
- [ ] Short description (max 140 chars)
- [ ] Detailed description (max 16,000 chars)
- [ ] Category selected
- [ ] Support URL configured

**Deployment**:
- [ ] `clasp deploy` with version description
- [ ] Deployment ID noted
- [ ] Deployment ID entered in Marketplace SDK App Configuration
- [ ] Visibility option selected (Private for v1)
- [ ] Draft testers added and validated
- [ ] Store listing preview reviewed

**For public publishing only (Phase 3)**:
- [ ] OAuth verification submitted (if sensitive scopes retained)
- [ ] Demo video recorded and uploaded (unlisted YouTube)
- [ ] Scope justification written
- [ ] CASA security assessment (only if restricted scopes added)

---

## Sources

- [Publish apps to the Google Workspace Marketplace](https://developers.google.com/workspace/marketplace/how-to-publish)
- [Publish an add-on overview](https://developers.google.com/workspace/add-ons/how-tos/publish-add-on-overview)
- [Configure your app in the Marketplace SDK](https://developers.google.com/workspace/marketplace/enable-configure-sdk)
- [Configure OAuth consent screen](https://developers.google.com/workspace/marketplace/configure-oauth-consent-screen)
- [Create a store listing](https://developers.google.com/workspace/marketplace/create-listing)
- [App review process and requirements](https://developers.google.com/workspace/marketplace/about-app-review)
- [Marketplace program policies](https://developers.google.com/workspace/marketplace/terms/policies)
- [Google Workspace API user data and developer policy](https://developers.google.com/workspace/workspace-api-user-data-developer-policy)
- [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy)
- [Sensitive scope verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/sensitive-scope-verification)
- [Restricted scope verification](https://developers.google.com/identity/protocols/oauth2/production-readiness/restricted-scope-verification)
- [Choose Gmail API scopes](https://developers.google.com/workspace/gmail/api/auth/scopes)
- [Workspace add-on scopes](https://developers.google.com/workspace/add-ons/concepts/workspace-scopes)
- [Triggers for Google Workspace add-ons](https://developers.google.com/workspace/add-ons/concepts/workspace-triggers)
- [Homepages for Workspace add-ons](https://developers.google.com/workspace/add-ons/concepts/homepages)
- [Upgrade legacy Gmail add-ons](https://developers.google.com/workspace/add-ons/how-tos/upgrade-addons)
- [Class CardService reference](https://developers.google.com/apps-script/reference/card-service/card-service)
- [Class KeyValue (deprecated)](https://developers.google.com/apps-script/reference/card-service/key-value)
- [Class DecoratedText](https://developers.google.com/apps-script/reference/card-service/decorated-text)
- [Use clasp CLI](https://developers.google.com/apps-script/guides/clasp)
- [Create and manage deployments](https://developers.google.com/apps-script/concepts/deployments)
- [Google Cloud projects for Apps Script](https://developers.google.com/apps-script/guides/cloud-platform-projects)
- [Update a published add-on](https://developers.google.com/workspace/add-ons/how-tos/update-published-add-on)
- [Restricted Scopes reference](https://support.google.com/cloud/answer/13464325)
- [OAuth App Verification Help Center](https://support.google.com/cloud/answer/13463073)

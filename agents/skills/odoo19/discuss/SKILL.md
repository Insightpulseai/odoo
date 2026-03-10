---
name: discuss
description: Internal communication app for messages, channels, video calls, and chatter
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# discuss -- Odoo 19.0 Skill Reference

## Overview

Odoo Discuss is an internal communication application that enables messaging, notes, file sharing, and video calls. It provides a persistent chat window across all Odoo applications and a dedicated Discuss dashboard with Inbox, Starred, and History views. Discuss also powers the chatter feature present on nearly every record in the database, enabling communication, activity scheduling, and file attachment directly on records.

## Key Concepts

- **Inbox**: Aggregates unread messages and notifications for the current user.
- **Starred**: Messages bookmarked by the user for quick reference.
- **History**: Chatter updates for records the user follows or is tagged in.
- **Direct Messages**: Private one-to-one or group conversations between users.
- **Channels**: Persistent group conversations organized by team, department, or topic. Channels support privacy settings (Authorized Group, Auto Subscribe Groups/Departments).
- **Meetings**: Video calls initiated from Discuss or direct messages using WebRTC.
- **Chatter**: Record-level communication thread for messages, notes, activities, and file attachments.
- **Followers**: Users/contacts subscribed to a record's chatter updates; subscription types are configurable.
- **Canned Responses**: Reusable shortcut-to-substitution text snippets (prefix `::`) available in chatter, channels, DMs, Live Chat, and WhatsApp.
- **ICE Servers**: TURN/STUN servers (via Twilio or custom) required for WebRTC calls when participants are behind symmetric NAT.
- **User Status**: Online (green), Away (orange), Offline (white), Out of Office (airplane).

## Core Workflows

1. **Send a Direct Message**
   1. Open Discuss, click `+` next to Direct Messages.
   2. Search for and select one or more contacts.
   3. Press Enter to create the conversation.
   4. Type message and send.

2. **Create a Channel**
   1. Click `+` next to Channels in the sidebar.
   2. Name the channel.
   3. Open channel settings (gear icon) to set Privacy, Authorized Group, and Auto Subscribe Groups.
   4. Add members via the Members tab or the invite icon.

3. **Log a Note on a Record (via Chatter)**
   1. Open any record with a chatter thread.
   2. Click "Log note" above the composer.
   3. Type note; use `@` to tag internal users or contacts.
   4. Press Ctrl+Enter or click send.

4. **Send a Message from Chatter**
   1. Open a record, click "Send message."
   2. All followers are auto-added as recipients.
   3. Optionally expand to full composer (expand icon) for email template selection, CC, attachments.
   4. Click Send.

5. **Schedule an Activity**
   1. Click "Activities" button on the chatter.
   2. Select Activity Type, set Summary, Assigned to, Due Date.
   3. Click Schedule (or Schedule & Mark as Done, or Done & Schedule Next).

6. **Start a Meeting (Video Call)**
   1. From Discuss dashboard: click "Start a meeting," invite people.
   2. From a DM: click the phone icon in the top-right corner.
   3. Controls: Mute, Deafen, Camera, Raise Hand, Share Screen, Full Screen.

7. **Use a Canned Response**
   1. In any chatter/chat composer, type `::` followed by shortcut text.
   2. Select from dropdown list, or type full shortcut and press Enter.

## Technical Reference

- **Key Models**: `mail.channel`, `mail.message`, `mail.activity`, `mail.followers`, `discuss.channel`, `mail.canned.response`
- **Notification Preference**: Per-user setting at Settings > Manage Users > Preferences tab. Options: "Handle by Emails" or "Handle in Odoo."
- **ICE Server Config**: Settings > General Settings > Discuss > "Use Twilio ICE servers" (Account SID + Auth Token). Custom ICE server list also configurable.
- **Canned Responses Config**: Discuss > Configuration > Canned Responses. Fields: Shortcut, Substitution, Authorized Group.
- **Chatter Integrations**: WhatsApp (Enterprise only), Google Translate (requires API key in Settings > Discuss > Message Translation).
- **AI Text Generation**: Available in expanded chatter composer via the AI icon (requires AI app or IAP credits).

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Canned responses now available in WhatsApp messages in addition to Live Chat, Discuss, and Chatter.
- AI text generation integrated into the expanded chatter composer.
- Chatter search feature allows searching messages/notes by keyword within a record thread.

## Common Pitfalls

- Leaving a DM conversation does not delete message history; a new DM with the same participants restores it.
- Followers are auto-added as message recipients. Remove followers before sending if they should not receive the message.
- Editing a sent message does not re-send the updated text to recipients.
- The "Add a description" field for DMs is only available for group messages with more than two participants.
- For on-premise deployments, the `python3-gevent` package is required for Discuss voice/video calls on Ubuntu.

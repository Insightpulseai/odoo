---
name: livechat
description: Odoo Live Chat for real-time website visitor communication with operators, chatbots, and canned responses
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# livechat -- Odoo 19.0 Skill Reference

## Overview

Odoo Live Chat enables real-time communication between website visitors and support operators. It supports multiple channels with configurable rules, chatbot automation, canned responses, operator commands, customer ratings, and detailed reporting. Live Chat integrates with CRM (lead creation), Helpdesk (ticket creation/search), and the Discuss app for conversation management. It can be embedded on Odoo websites or third-party sites via a JavaScript widget.

## Key Concepts

- **Channel**: A live chat channel containing operators, display options, rules, and a widget. Multiple channels can exist.
- **Operator**: A database user who responds to live chat requests. Added to channels via the Operators tab. Chat windows appear in the bottom-right corner of the screen regardless of the current page.
- **Channel Rules**: Define when and how the live chat button appears on specific URLs. Options: Show, Show with notification, Open automatically (with timer), Hide. Rules can filter by URL regex and country (requires GeoIP).
- **Chatbot**: An automated conversation program following a scripted flow. Assigned to channel rules. Can be set to activate only when no operators are available.
- **Chatbot Step Types**: Text, Question (with answers and optional links), Email, Phone, Forward to Operator, Free Input, Free Input (Multi-Line), Create Lead (CRM), Create Ticket (Helpdesk).
- **Only If**: Conditional step execution in chatbot scripts -- a step is displayed only if specific previous answers were selected.
- **Canned Responses**: Preconfigured text substitutions triggered by shortcuts (e.g., typing `:shortcut` or `::` to list all). Created per user, shared via Authorized Groups.
- **Commands**: Operator-only keywords typed in the chat window:
  - `/help` -- Show available commands
  - `/ticket` -- Create a Helpdesk ticket from the conversation
  - `/search_tickets` -- Search Helpdesk tickets by keyword or number
  - `/history` -- Show visitor's last 15 visited pages
  - `/lead` -- Create a CRM lead from the conversation
  - `/leave` -- Exit the conversation (operator only)
- **Ratings**: After closing a chat, visitors can rate satisfaction (Satisfied/Okay/Dissatisfied) and add comments. Ratings can be published on the website.
- **Online Chat Name**: Operator display name shown to visitors (configurable in user profile, defaults to full user name).
- **Online Chat Language**: Languages spoken by an operator, used for conversation assignment (set in user profile).
- **Live Chat Expertise**: Operator specialization areas. Chatbots prioritize forwarding to operators with matching expertise.
- **Widget**: Embeddable JavaScript snippet for adding live chat to third-party (non-Odoo) websites. Also provides a shareable direct chat link.
- **GeoIP**: Geographical IP detection for country-based channel rules. Auto-installed on Odoo Online; requires manual setup on-premise.

## Core Workflows

### 1. Create and Configure a Live Chat Channel

1. Go to `Live Chat` app, click `New`.
2. Enter `Channel Name`.
3. **Operators tab**: The creator is added by default. Click `Add` to add more operators.
4. **Options tab**:
   - Livechat Button: Set `Notification text`, customize button color.
   - Livechat Window: Edit `Welcome Message`, `Chat Input Placeholder`, customize header color.
5. **Channel Rules tab**: Click `Add a line` to create rules:
   - Live Chat Button: Show / Show with notification / Open automatically / Hide.
   - Chatbot: Select a chatbot (optionally enable `Enabled only if no operator`).
   - URL Regex: Specify which pages the rule applies to (e.g., `/shop`, `/` for all).
   - Open automatically timer: Seconds delay before auto-opening.
   - Country: Restrict to specific countries (requires GeoIP).
6. **Widget tab**: Copy the embed code for third-party websites, or copy the direct chat link.
7. Save.

### 2. Build a Chatbot

1. Go to `Live Chat > Configuration > Chatbots`, click `New`.
2. Enter `Chatbot Name` and add a photo.
3. In the `Script` tab, click `Add a Line` for each dialog step:
   - Enter `Message` text.
   - Select `Step Type`: Text, Question, Email, Phone, Forward to Operator, Free Input, Free Input (Multi-Line), Create Lead, Create Ticket.
   - For Question type: add answers via `Add a Line`, optionally with `Optional Link` URLs.
   - Set `Only If` field to make the step conditional on previous answers.
4. Click `Test` to simulate the chatbot conversation.
5. Verify no dead-ends exist (all paths lead to a conclusion).
6. Add the chatbot to a channel: open the channel, go to `Channel Rules` tab, create or edit a rule, select the chatbot in the `Chatbot` field.

### 3. Set Up Canned Responses

1. Go to `Live Chat > Configuration > Canned Responses`, click `New`.
2. Enter `Shortcut` (the trigger text).
3. Enter `Substitution` (the full response that replaces the shortcut).
4. Select `Authorized Groups` to share with other operators (default: creator only).
5. Operators use canned responses by typing `:shortcut` or `::` to browse the list.

### 4. Manage Customer Ratings

1. Ratings are collected automatically when visitors close a chat window.
2. View ratings: `Live Chat > Report > Customer Ratings` (Kanban, list, pivot, or graph views).
3. Publish channel ratings on website: open channel, click `Go to Website` smart button, toggle `Unpublished` to `Published`.
4. Add ratings page to website: create a new page with URL `livechat` (exact name required).
5. Hide individual ratings: click a rating in the report, check `Visible Internally Only`.

### 5. Participate as an Operator

1. Set `Online Chat Name` and `Online Chat Language` in user profile (`My Profile > Preferences`).
2. Set `Live Chat Expertise` for skill-based routing.
3. Join a channel: `Live Chat` app, click `Join` on the channel's Kanban card.
4. Chat windows appear in the bottom-right corner of any page. Also accessible via `Discuss` app.
5. Use commands (`/help`, `/ticket`, `/lead`, `/history`, `/leave`) and canned responses (`:shortcut` or `::`) during conversations.
6. Operators inactive for 30+ minutes are auto-disconnected from the channel.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `im_livechat.channel` | Live chat channel |
| `im_livechat.channel.rule` | Channel rule (display/chatbot/URL/country) |
| `chatbot.script` | Chatbot definition |
| `chatbot.script.step` | Chatbot script step |
| `chatbot.script.answer` | Chatbot step answer option |
| `mail.shortcode` | Canned response |
| `rating.rating` | Customer rating |

### Key Fields

- `im_livechat.channel`: `name`, `user_ids` (operators), `rule_ids`, `button_text`, `default_message`, `input_placeholder`, `button_color`, `header_color`
- `im_livechat.channel.rule`: `action` (display/auto_popup/hide), `chatbot_script_id`, `regex_url`, `auto_popup_timer`, `country_ids`
- `chatbot.script.step`: `message`, `step_type` (text/question/email/phone/forward_operator/free_input/free_input_multi_line/create_lead/create_ticket), `triggering_answer_ids` (Only If)
- `mail.shortcode`: `shortcode_type`, `source` (shortcut text), `substitution` (replacement text), `group_ids` (authorized groups)

### Reports

| Report | Path | Description |
|--------|------|-------------|
| Sessions History | `Live Chat > Report > Sessions History` | Session overview with transcripts, duration, messages, ratings |
| Session Statistics | `Live Chat > Report > Session Statistics` | Statistical overview with measures: speakers, duration, messages, ratings, response time |
| Operator Analysis | `Live Chat > Report > Operator Analysis` | Per-operator performance: session count, avg duration, avg rating, response time |
| Customer Ratings | `Live Chat > Report > Customer Ratings` | Rating overview with comments, filterable by Kanban/list/pivot/graph |

### Session Statistics Measures

- `# of speakers`, `Days of activity`, `Duration of Session (min)`, `Is visitor anonymous`, `Messages per session`, `Rating`, `Session not rated`, `Time to answer (sec)`, `Visitor is Happy`, `Count`

### Operator Analysis Measures

- `# of Sessions`, `Average duration`, `Average rating`, `Time to answer`, `Count`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Chatbot step type `Free Input (Multi-Line)` available for longer visitor responses.
- Operator `Live Chat Expertise` field for skill-based chatbot routing.
- `Online Chat Language` on operator profiles for language-based conversation assignment.
- Canned responses support `Authorized Groups` for sharing across operators.
- Chatbot `Only If` field supports multiple previous answers (all must be selected for the step to trigger).
- `Create Lead` and `Create Ticket` chatbot step types for direct CRM/Helpdesk integration.
- `/search_tickets` command for searching Helpdesk tickets by keyword or number.
- Rating publish workflow requires a page named exactly `livechat`.

## Common Pitfalls

- **No operator fallback**: If a chatbot forwards to an operator and none are available, the chatbot continues with subsequent steps. Always add follow-up steps after `Forward to Operator` to handle the no-operator scenario.
- **Dead-end scripts**: If a visitor's answer has no matching follow-up step, the conversation stops. The visitor must refresh the chat window to restart. Always test chatbot scripts thoroughly.
- **Operator inactivity timeout**: Operators inactive in Odoo for 30+ minutes are auto-disconnected from the channel and stop receiving chat requests.
- **GeoIP required for country rules**: Country-based channel rules require GeoIP installation. Auto-installed on Odoo Online, but requires manual setup on on-premise databases.
- **Ratings page URL**: The website page for published ratings must have the URL `livechat` exactly. Other names will not link to the ratings data.

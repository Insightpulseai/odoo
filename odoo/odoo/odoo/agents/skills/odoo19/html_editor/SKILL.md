---
name: html_editor
description: Rich-text editor for HTML fields — toolbar formatting, powerbox commands, media insertion, and AI tools.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# html_editor — Odoo 19.0 Skill Reference

## Overview

The Odoo rich-text editor provides WYSIWYG editing for HTML fields throughout the platform — Internal Notes, Description fields, Knowledge articles, and Studio report editor. It features a floating toolbar for text formatting, a powerbox command system (triggered by `/`) for inserting structural elements, media, navigation widgets, and AI-assisted content generation and translation. All users who create or edit rich-text content interact with this editor.

## Key Concepts

- **Toolbar**: Floating formatting bar that appears when text is selected. Includes font style, size, bold/italic/underline, font color, background color, links, AI writing, and expanded options (font family, strikethrough, lists, alignment, AI translation).
- **Powerbox**: Command palette triggered by typing `/` in the editor. Insert tables, columns, lists, banners, headings, media, links, buttons, emojis, and ratings.
- **Odoo AI**: Inline AI content generation (prompt-based) and AI translation to installed languages.
- **Media insertion**: Insert images (Unsplash search, URL, upload), documents, icons, and videos (YouTube, Vimeo, Dailymotion, Youku) via the `/Media` command.
- **Drag handle**: Hover over any block element to reveal a drag icon for reordering content.
- **Media editor toolbar**: Click an inserted image to access preview, description, caption, shape (rounded/circle), shadow, thumbnail, padding, resize, transform, crop, link, replace, and delete options.
- **Icon editor toolbar**: Click an inserted icon to change font color, background color, size (1x-5x), spin animation, or replace.

## Core Workflows

### 1. Format text with the toolbar

1. Select or double-click text in an HTML field.
2. The toolbar appears with formatting options.
3. Apply: font style (Header 1-6, Normal, Paragraph, Code, Quote), size, bold (`Ctrl+B`), italic (`Ctrl+I`), underline (`Ctrl+U`), font color, link.
4. Click the expand icon for additional options: font family, strikethrough, background color, remove format, list type, alignment, AI translation.

### 2. Use powerbox commands

1. Type `/` at the start of a line or in a new paragraph.
2. Type the command name or browse categories: Structure, Banner, Format, Media, Navigation, Widget.
3. Select the command to insert the element.

### 3. Insert and edit media

1. Type `/Media` or click the media icon in the tooltip.
2. Choose tab: Images (Unsplash/URL/upload), Documents, Icons, Videos.
3. Select or upload the media.
4. Click an inserted image to access the media editor toolbar for cropping, resizing, linking, etc.

### 4. Generate content with AI

1. Select text or position cursor.
2. In the toolbar, click **Odoo AI**.
3. Write a prompt or click a suggestion.
4. AI-generated content is inserted inline.

### 5. Translate content with AI

1. Select text.
2. In the expanded toolbar, click **Translate with AI**.
3. Choose from installed languages.

## Technical Reference

### Powerbox Command Categories

| Category | Commands |
|----------|----------|
| **Structure** | Separator, 2/3/4 Columns, Table, Bulleted list, Numbered list, Checklist, Toggle list |
| **Banner** | Banner Info, Success, Warning, Danger |
| **Format** | Heading 1/2/3, Text, Switch direction, Quote, Code |
| **Media** | Media (image/icon), Upload a file |
| **Navigation** | Link, Button, Table Of Contents |
| **Widget** | Emoji, 3 Stars, 5 Stars |

### Keyboard Shortcuts in Editor

| Action | Shortcut |
|--------|----------|
| Bold | `Ctrl/Cmd + B` |
| Italic | `Ctrl/Cmd + I` |
| Underline | `Ctrl/Cmd + U` |
| Start numbered list | Type `1.`, `1)`, `A.`, or `A)` |
| Start bulleted list | Type `*` or `-` |

### Image Crop Aspect Ratios

Flexible, 16:9, 4:3, 1:1, 2:3

### Video Sources

YouTube, Vimeo, Dailymotion, Youku (also supports embed code)

### Video Options

Autoplay, Loop, Hide controls, Hide fullscreen button, Start time

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Powerbox requires line start or new paragraph**: The `/` command works best at the beginning of a line; it may not activate mid-sentence.
- **App-specific commands excluded**: Some powerbox commands are specific to apps (e.g., Knowledge) and do not appear in all HTML fields.
- **AI features require configuration**: Odoo AI content generation and translation may require specific setup or subscription features.
- **Table editing via hover menu**: Table column/row operations are accessed by hovering over the table to reveal the ellipsis menu — not through right-click or toolbar.

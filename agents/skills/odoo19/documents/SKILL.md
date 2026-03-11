---
name: documents
description: Document management system with file centralization, sharing, tagging, PDF splitting, and AI sorting
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# documents -- Odoo 19.0 Skill Reference

## Overview

Odoo Documents is a file management application for storing, viewing, organizing, and sharing files within Odoo. It provides folder structures under Company and My Drive sections, file centralization from other Odoo apps, access-rights management, PDF split/merge, email aliases, tagging, and AI-powered auto-sorting. It serves as the storage backend for Spreadsheets and integrates with Sign for electronic signatures.

## Key Concepts

- **Sections**: All, Company, My Drive, Shared with me, Recent, Trash.
- **Folders**: Organizational containers in Company or My Drive. Support sub-folders, email aliases, automation rules, and AI auto-sort.
- **File Centralization**: Auto-routes attachments from other apps (Accounting, HR, etc.) into designated Documents folders. Enabled by default per app on install.
- **Tags**: Color-coded labels for categorizing files. Configurable at Documents > Configuration > Tags.
- **Deletion Delay**: Trashed items are permanently deleted after a configurable period (default 30 days).
- **Access Rights**: Viewer or Editor roles per user/contact. General access for Internal users and link-based access. Discoverable toggle for link sharing.
- **Email Aliases**: Folder-specific email addresses that auto-save incoming attachments/emails as files.
- **Linked Records**: Files can reference a specific Odoo record via the "Linked to" field.
- **Details Panel**: Side panel showing file/folder info, tags, owner, contact, and chatter.
- **File Requests**: Placeholder files sent to users as reminders to upload specific documents.
- **PDF Split/Merge**: Split a PDF at page boundaries; merge multiple PDFs into one (replaces originals).
- **AI Auto-sort**: Uses Odoo AI to organize folder contents based on a prompt and trigger actions.

## Core Workflows

1. **Upload a File**
   1. Select the target folder in the tree.
   2. Click New > Upload (or drag and drop from desktop).
   3. Max 64MB per file on Odoo Online.

2. **Create a Folder**
   1. Select the parent section (Company or My Drive).
   2. Click New > Folder.
   3. Enter folder name and Save.

3. **Share a File or Folder**
   1. Select file/folder, click Share (or gear icon > Share for folders).
   2. Invite users/contacts via email; set role to Viewer or Editor.
   3. Configure General access for Internal users and Access through link.
   4. Click Share or Copy Links.

4. **Split a PDF**
   1. Open the PDF file.
   2. Click Actions > Split PDF.
   3. Click scissors icons between pages to add/remove split points.
   4. Click Split.

5. **Merge PDFs**
   1. Navigate to folder, Ctrl+click to select multiple PDFs.
   2. Click Actions > Merge PDFs.
   3. Optionally add more files and reorder.
   4. Click Split to merge (original PDFs are replaced).

6. **Request a File**
   1. Click New > Request.
   2. Enter Document Name, Request To, optional Due Date, Tags, Message.
   3. Click Request. A placeholder appears in the folder.

7. **Set Up File Centralization**
   1. Go to Documents > Configuration > Settings.
   2. Under File Centralization, enable/disable per app.
   3. Configure default folders and tags per app.

## Technical Reference

- **Key Models**: `documents.document`, `documents.folder`, `documents.tag`, `documents.share`
- **Key Fields on `documents.document`**: `name`, `folder_id`, `tag_ids`, `owner_id`, `partner_id` (contact), `res_model` / `res_id` (linked record), `type` (binary/url), `url`
- **Folder Actions**: Download, Rename, Share, Add Star, Info & Tags, Move to Trash, Actions on Select (server actions), Automations, AI Auto-sort
- **File Actions**: Duplicate, Move to Trash, Rename, Info & Tags, Move, Create Shortcut, Manage Versions, Lock, Copy Links, Split PDF
- **File Digitization**: Finance folder files can be converted to Vendor Bill, Customer Invoice, or Credit Note via AI digitization.
- **Shortcuts**: A pointer to a file allowing access from multiple folders without duplication.
- **Version Management**: View all versions, download specific versions, upload new versions.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- AI Auto-sort feature added to folders (requires Odoo AI app).
- File shortcuts (non-duplicating pointers) now available.
- Enhanced sharing portal with discoverable/non-discoverable link options.

## Common Pitfalls

- Changing file centralization folder/tags only affects new files; existing files remain unchanged.
- Deleting a record in an app with centralization enabled moves its attachments to Documents trash.
- Merging PDFs replaces the originals; there is no undo.
- File centralization cannot be disabled for Accounting documents.
- Portal users can only access Documents through the customer portal Documents card.

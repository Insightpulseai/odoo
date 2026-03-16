---
name: elearning
description: Odoo eLearning for creating online courses, managing content, certifications, and gamification
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# elearning -- Odoo 19.0 Skill Reference

## Overview

Odoo eLearning allows organizations to create and publish online courses with structured content (videos, documents, images, articles, quizzes), manage attendees, track progress, issue certifications, and gamify the learning experience with karma points. Courses can be free or paid (via eCommerce integration), and content can be managed from either the website frontend or the backend. The module integrates with Forum for community discussions and Surveys for certifications.

## Key Concepts

- **Course**: A container for structured learning content. Has a title, tags, image, description, and configurable options for access, display, and communication.
- **Content Item**: An individual lesson within a course. Types: Image, Article, Document, Video, Quiz.
- **Section**: A grouping mechanism within a course to organize content items.
- **Certification**: An assessment (via the Surveys app) added to a course to certify attendee skills.
- **Course Group**: A category with tags that allows website visitors to filter courses on the `/slides` page.
- **Content Tag**: Labels visible on the course Contents dashboard to identify lesson types (e.g., theory, exercises).
- **Enroll Policy**: Controls how users join a course -- `Open`, `On invitation`, or `On payment`.
- **Show course to**: Visibility setting -- `Everyone`, `Signed In`, `Course Attendees`, `Anyone with the link`.
- **Display Mode**: `Training` (sequential, ordered content) or `Documentation` (content accessible in any order, with featured content).
- **Karma Points**: Gamification points earned through course interactions (reviews, completions). Shared across all forums, courses, etc. on a single Odoo website.
- **Prerequisites**: Courses that users are advised to complete before accessing the current course.
- **Content Types**:
  - *Image*: JPG, JPEG, PNG, SVG, GIF, WEBP (max 25MB). Upload or Google Drive link.
  - *Article*: Website page customized via the website builder.
  - *Document*: PDF upload or Google Drive link (Slides, Docs, Sheets).
  - *Video*: YouTube, Google Drive, or Vimeo link.
  - *Quiz*: Questions with multiple answers, correct answer marking, karma point rewards.
- **Additional Resources**: Supplementary links or files attached to content items.
- **Allow Preview**: Makes individual content accessible to non-enrolled visitors.
- **Allow Download**: Enables download for Document-type content.
- **Paid Courses**: Requires eCommerce module. Course is linked to a product with `Course` as its Product Type.

## Core Workflows

### 1. Create and Configure a Course

1. Go to `eLearning > Courses > Courses`, click `New`.
2. Enter `Course Title`, add `Tags` for filtering.
3. Add an image (hover camera placeholder, click Edit).
4. **Content tab**: Click `Add Section` to organize, `Add Content` for lessons, `Add Certification` for assessments.
5. **Description tab**: Add a short description displayed on the website.
6. **Options tab**:
   - Course: Assign `Responsible` user, select `Website` (for multi-website).
   - Access rights: Set `Prerequisites`, `Show course to` (visibility), `Enroll Policy` (Open/On invitation/On payment).
   - Communication: Enable `Allow Reviews`, link a `Forum`, set `New Content Notification` and `Completion Notification` email templates.
   - Display: Choose `Training` (sequential) or `Documentation` (any order).
7. **Karma tab**: Set karma point rewards for Review and Finish. Set karma requirements for Add Review, Add Comment, Vote.
8. Save the course.

### 2. Create Content Items

1. Go to `eLearning > Courses > Contents`, click `New`.
2. Enter `Content Title` and optional `Tags`.
3. **Document tab**: Select `Course`, choose `Content Type` (Image/Article/Document/Video/Quiz), set `Responsible`, enter `Duration`, toggle `Allow Preview`.
4. **Description tab**: Add a description for the About section on the website.
5. **Additional Resources tab**: Click `Add a line` to attach supplementary links or files.
6. **Quiz tab**: Set `Points Rewards`, click `Add a line` to create questions, enter answers, mark correct answers, add comments.
7. Save the content item.

### 3. Publish a Course

1. Publish content items first: click `Go to Website` on each content form, toggle `Unpublished` to `Published`.
2. Publish the course: access the main course page on the frontend, toggle `Unpublished` to `Published`.
3. Published content is only visible once its parent course is also published.
4. Unpublishing a course hides both the course and all its content.

### 4. Manage Attendees and Access

1. For `Open` enroll policy: anyone who can see the course can enroll. Any eLearning Officer/Manager can add or invite attendees.
2. For `On invitation`: only invited people can enroll. Uninvited visitors can request access (creates a to-do for the Responsible user). Only the Responsible user or Manager can add/invite attendees.
3. For `On payment`: requires `Paid courses` setting enabled. Course linked to a product. Officers can invite; only Responsible/Manager can add (payment not required when added by Responsible/Manager).
4. Add attendees via `Add attendees` button. Invite via `Invite` button.
5. Contact attendees en masse via `Contact Attendees` button (requires Email Marketing user rights and Mailing setting enabled).

### 5. Manage Course Groups and Tags

1. Course Groups: `eLearning > Configuration > Course Groups`. Click `New`, add name, enable `Menu Entry` for website filtering, add tags with colors.
2. Content Tags: `eLearning > Configuration > Content Tags`. Click `New`, enter name.
3. Tags help users filter courses and identify content types on the website.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `slide.channel` | Course |
| `slide.slide` | Content item (slide/lesson) |
| `slide.channel.tag` | Course tag |
| `slide.channel.tag.group` | Course group (tag group) |
| `slide.slide.tag` | Content tag |

### Key Fields

- `slide.channel`: `name`, `tag_ids`, `description`, `website_id`, `enroll_policy` (open/invite/payment), `visibility` (public/connected/members/link), `channel_type` (training/documentation), `prerequisite_channel_ids`, `allow_comment`, `forum_id`, `product_id`, `karma_review`, `karma_finish`
- `slide.slide`: `name`, `channel_id`, `slide_category` (image/article/document/video/quiz), `url`, `datas`, `duration`, `is_preview`, `is_published`, `total_views`, `public_views`

### Settings (`eLearning > Configuration > Settings`)

| Setting | Description |
|---------|-------------|
| `Certifications` | Enable attendee assessment and certification |
| `Paid Courses` | Enable selling course access (installs eCommerce) |
| `Mailing` | Enable mass mailings to course attendees |
| `Forum` | Enable dedicated forums per course |

### Access Rights

| Role | Capabilities |
|------|-------------|
| eLearning Officer | Manage content, invite attendees (Open/On payment), cannot add attendees for invitation-only courses |
| eLearning Manager | Full management, grant/refuse access requests, add/invite attendees for all enroll policies |

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Content type `Image` supports WEBP format and Google Drive retrieval.
- Content type `Article` uses the website builder for customization on the frontend.
- `Allow Download` option for Document-type content.
- `# of Public Views` and `# Total Views` read-only fields on content items.
- Paid courses require a product with `Course` as the Product Type.
- Access request creates a to-do assigned to the Responsible user (not just a notification).
- `Contact Attendees` button for mass mailing requires both eLearning Officer role and Email Marketing User access rights.

## Common Pitfalls

- **Publish order matters**: Content items should be published before the course itself. Published content is not visible until its parent course is published.
- **Unpublishing a course**: Hides both the course and all its content from the audience, even if individual items are still toggled to Published.
- **Paid courses installs eCommerce**: Enabling `Paid Courses` auto-installs the eCommerce module, which may impact your Odoo pricing plan.
- **Karma points are global**: A user's karma points are shared across all forums, courses, and websites on a single Odoo database. Setting high karma requirements on one course affects access based on activity elsewhere.
- **One pending question per forum**: When content requires validation, only one pending question per user is allowed per forum, which can block further submissions until the first is approved.

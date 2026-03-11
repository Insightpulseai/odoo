---
name: to_do
description: Personal task management app with kanban pipeline, stages, activities, and project task conversion
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# to_do -- Odoo 19.0 Skill Reference

## Overview

Odoo To-Do is a lightweight personal task management application for organizing individual tasks. It provides a kanban pipeline with customizable personal stages, supports tags, assignees for sharing, rich text editing, activity scheduling, and conversion of to-dos into project tasks. To-dos also appear as private tasks in the Project app's "My Tasks" view.

## Key Concepts

- **To-Do**: A personal task card displayed on the kanban pipeline. Contains a title, optional tags, assignees, and rich text description.
- **Personal Stages**: User-specific kanban columns (e.g., New, In Progress, Done). Each user manages their own stages independently.
- **Assignees**: Adding assignees shares the to-do with those users.
- **Activities**: Scheduled follow-up actions on to-dos (e.g., calls, emails, meetings) with type, due date, and assignment.
- **Convert to Task**: Transforms a to-do into a project task in the Project app. The to-do moves to the selected project.
- **Private Tasks**: To-dos appear with a padlock icon in Project app's "My Tasks" view.
- **Command Palette**: Create a to-do from anywhere via Ctrl+K > "Add a To-Do" or via the clock button > "Add a To-Do."

## Core Workflows

1. **Create a To-Do**
   1. Open the To-Do app, click New or the + button next to a stage.
   2. Enter a title.
   3. Click Add to save quickly, or Edit for more options.
   4. In Edit mode: add Tags, Assignees, and description content (supports `/` commands for formatting, media, links, widgets).

2. **Create a To-Do from Anywhere**
   1. Press Ctrl+K to open the command palette.
   2. Click "Add a To-Do."
   3. Or: click the clock button in the header, then "Add a To-Do."

3. **Manage the Pipeline**
   1. Drag and drop to-dos between stages.
   2. Click "+ Personal Stage" to create a new stage.
   3. Click the gear icon next to a stage to Fold, Edit, or Delete it.

4. **Schedule an Activity**
   1. On the To-Do dashboard, click the clock button on a to-do.
   2. Click "+ Schedule an activity."
   3. Select Activity Type, Due date, Assigned to, and optional Summary.
   4. Click Schedule.

5. **Convert a To-Do to a Project Task**
   1. Open a to-do.
   2. Click the gear button > "Convert to Task."
   3. Select Project, Assignees, and Tags.
   4. Click "Convert to Task."

## Technical Reference

- **Key Models**: `project.task` (to-dos are private project tasks with `project_id` = False)
- **Key Fields**: `name` (title), `tag_ids`, `user_ids` (assignees), `description`, `personal_stage_type_ids`
- **Personal Stages**: Stored per user. Not shared across users. Managed via the pipeline UI.
- **Integration with Project**: To-dos appear in Project > My Tasks as private tasks (padlock icon). Converting a to-do sets the `project_id` field.
- **Activity Types**: Configurable per app. The "To Do" activity type does NOT create a to-do task.
- **Editor**: Supports `/` slash commands for headings, lists, media, links, and widgets.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs -->

## Common Pitfalls

- The "To Do" activity type in the activity scheduler is NOT the same as creating a to-do task. It is a regular activity.
- Personal stages are user-specific; other users see their own stages, not yours.
- Adding assignees shares the to-do with those users; removing assignees revokes shared access.
- To-dos appear as private tasks in Project only if the Project app is installed.

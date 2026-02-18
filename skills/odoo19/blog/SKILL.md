---
name: blog
description: Odoo Blog for creating and managing blog posts with tags, customizable layouts, and community engagement
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# blog -- Odoo 19.0 Skill Reference

## Overview

Odoo Blog allows users to create and manage blog posts on their Odoo website to engage audiences and build a community. It supports multiple blogs, categorized tags, customizable homepage and post layouts, sidebar options, comments, social sharing, archives, and integration with the website builder for drag-and-drop content design. Blog pages are dynamic pages auto-generated at `/blog`.

## Key Concepts

- **Blog**: A named container for blog posts. Multiple blogs can exist on a single website. The `Blog` menu item is auto-added to the website menu when the first blog is created. Configured via `Website > Configuration > Blogs: Blogs`.
- **Blog Post**: An individual article within a blog. Created from the website frontend via `+New > Blog Post`. Must be published to be visible.
- **Tags**: Labels for filtering posts. Visitors can filter by tag from the blog homepage sidebar. Tags belong to a tag category for grouped display.
- **Tag Categories**: Groupings of tags displayed by theme in the sidebar. Managed via `Website > Configuration > Blogs: Tag Categories`.
- **Blog Homepage**: The listing page for a blog showing all its posts. Customizable layout and sidebar options apply to all blog homepages.
- **Top Banner**: Blog homepage header. Options: `Name/Latest Post` (shows latest post title) or `Drop Zone for Building Blocks` (removes banner, allows custom building blocks).
- **Layout**: Post listing format -- `Grid` or `List`. Sub-options: `Cards` (card effect), `Increase Readability`.
- **Sidebar**: Optional side panel containing `About us`, `Archives`, `Follow Us` (social media links), and `Tags List`.
- **Posts List**: Cover image display options (`Cover` / `No Cover`). Sub-options: `Author`, `Comments/Views Stats`, `Teaser & Tags`.
- **Post Sidebar**: Per-post sidebar with `Archive`, `Author`, `Blog List`, `Share Links`, `Tags`.
- **Breadcrumb**: Path navigation displayed on posts.
- **Comments**: Visitor commenting on posts (enabled via `Bottom > Comments`).
- **Select To Tweet**: Visitors can tweet selected text from a post.
- **Next Article**: Navigation to the next post at the bottom.

## Core Workflows

### 1. Create a Blog

1. Go to `Website > Configuration > Blogs: Blogs`, click `New`.
2. Enter `Blog Name` and `Blog Subtitle`.
3. Save. The `Blog` menu item is auto-added to the website navigation.

### 2. Add a Blog Post

1. Go to the website, click `+New` in the top-right corner, select `Blog Post`.
2. Select the target `Blog` from the dropdown.
3. Enter the post's `Title`.
4. Click `Save`.
5. Write the post content. Use `/` in the text editor to format and add elements.
6. Customize the page using the website builder (building blocks, images from Unsplash).
7. Toggle `Unpublished` to `Published` in the upper-right corner.

### 3. Manage Tags

1. Go to `Website > Configuration > Blogs: Tags`, click `New`.
2. Enter the tag `Name`.
3. Select or create a `Category` (tag categories group tags in the sidebar).
4. In `Used in`, click `Add a line` to apply the tag to existing posts.
5. Tags can also be added directly from a post: click `Edit > Customize`, select the post's cover, and under `Tags` click `Choose a record...`.

### 4. Customize Blog Homepage

1. Open a blog homepage on the website.
2. Click `Edit > Customize`.
3. Configure (applies to all blog homepages):
   - **Top Banner**: `Name/Latest Post` or `Drop Zone for Building Blocks`.
   - **Layout**: `Grid` or `List`. Enable `Cards` and/or `Increase Readability`.
   - **Sidebar**: Toggle on/off. Sub-options: `Archives`, `Follow Us`, `Tags List`.
   - **Posts List**: `Cover` or `No Cover`. Sub-options: `Author`, `Comments/Views Stats`, `Teaser & Tags`.
4. Click `Save`.

### 5. Customize Blog Posts

1. Open a blog post on the website.
2. Click `Edit > Customize`.
3. Configure (applies to all posts):
   - **Layout**: `Title Inside Cover` or `Title above Cover`. Enable `Increase Readability`.
   - **Sidebar**: Toggle on/off. Sub-options: `Archive`, `Author`, `Blog List`, `Share Links`, `Tags`.
   - **Breadcrumb**: Toggle on/off.
   - **Bottom**: `Next Article` (navigation to next post), `Comments` (enable visitor comments).
   - **Select To Tweet**: Allow visitors to tweet selected text.
4. Click `Save`.

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `blog.blog` | Blog container |
| `blog.post` | Blog post/article |
| `blog.tag` | Blog tag |
| `blog.tag.category` | Tag category for grouping |

### Key Fields

- `blog.blog`: `name`, `subtitle`, `website_id`
- `blog.post`: `name`, `blog_id`, `tag_ids`, `is_published`, `author_id`, `create_date`, `content`, `website_id`
- `blog.tag`: `name`, `category_id`, `post_ids`
- `blog.tag.category`: `name`

### Menu Paths

| Path | Description |
|------|-------------|
| `Website > Configuration > Blogs: Blogs` | Manage blogs |
| `Website > Configuration > Blogs: Tags` | Manage tags |
| `Website > Configuration > Blogs: Tag Categories` | Manage tag categories |

### Dynamic URLs

- `/blog` -- Blog listing page (all blogs)
- `/blog/<blog-slug>` -- Specific blog homepage
- `/blog/<blog-slug>/<post-slug>` -- Specific blog post

### Installation

If the Blog module is not installed, click `+New` on the website builder, select `Blog Post`, and click `Install`.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Blog posts support the `/` command in the text editor for formatting and adding elements.
- Unsplash integration for copyright-free images.
- `Select To Tweet` feature for visitor engagement.
- `Drop Zone for Building Blocks` option for the top banner replaces the default banner with fully customizable building blocks.
- Layout options include `Cards` effect for grid/list views.
- Plausible analytics recommended for tracking blog traffic.

## Common Pitfalls

- **Settings apply globally**: Blog homepage customization (layout, sidebar, posts list options) applies to all blog homepages, not individual blogs. Similarly, post customization applies to all posts.
- **Publishing required**: Posts must be explicitly toggled from `Unpublished` to `Published` to be visible to website visitors. This is easy to forget after creating content.
- **Tag categories matter for sidebar display**: Tags without a category will not be grouped thematically in the sidebar's Tags List. Create tag categories to organize tags meaningfully.
- **Social media links from building block**: The `Follow Us` sidebar links are populated from the Social Media building block placed somewhere on the website, not from blog-specific configuration.
- **Dynamic pages**: Blog pages (`/blog/*`) are dynamic pages and therefore cannot have their indexed/visibility properties edited the same way as static pages.

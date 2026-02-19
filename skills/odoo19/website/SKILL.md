---
name: website
description: Odoo Website builder for creating, designing, and managing websites without code
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# website -- Odoo 19.0 Skill Reference

## Overview

Odoo Website is a full-featured website builder that lets users create, design, and manage web pages without advanced technical skills. It provides drag-and-drop building blocks, theme customization, SEO tools, multi-website support, analytics integration, domain name management, and mail groups. It serves as the foundational web layer for eCommerce, Blog, Forum, eLearning, and other customer-facing Odoo applications.

## Key Concepts

- **Building Blocks**: Drag-and-drop UI components split into *Categories* (structural containers) and *Inner Content* (elements like images, videos, social media placed inside category blocks).
- **Theme**: Global visual configuration covering colors (5 theme colors, status colors), fonts (paragraph, heading, button), page layout, and button styles. Switchable at any time.
- **Color Presets**: Predefined color combinations applied across building blocks (background, text, headings, links, buttons).
- **Pages (Static)**: Manually created pages with fixed content, custom URLs, and configurable properties (visibility, indexing, publish date).
- **Pages (Dynamic)**: Auto-generated pages from apps/modules (e.g., `/shop`, `/blog`). Managed differently from static pages.
- **Header / Footer**: Persistent site-wide navigation and branding elements.
- **SEO**: Content optimization via meta tags, keywords, alt tags, sitemaps, robots.txt, structured data (schema.org microdata), and hreflang tags.
- **Domain Name**: Custom domain mapping to Odoo database and website. Free 1-year domain for Odoo Online.
- **Multi-Website**: Multiple independent websites from a single database, each with its own domain, theme, pages, languages, and products.
- **Mail Groups**: Public email discussion groups (`website_mail_group` module) allowing website visitors to participate via email.
- **Plausible Analytics**: Privacy-friendly analytics integrated into Odoo (free for Odoo Online databases using `odoo.com` domain).
- **Link Tracker**: URL tracking tool for marketing campaign attribution.
- **Visibility Settings**: Conditional display/hide of building blocks based on device, logged-in status, or other criteria.
- **Grid / Cols Layout**: Two layout modes for building blocks -- Grid (free positioning via drag-and-drop) and Cols (column-based with configurable elements per line).
- **Web Base URL**: The root URL of the database, affecting portal links and emails. Auto-set when an admin logs in via a domain. Freeze with `web.base.url.freeze` system parameter.

## Core Workflows

### 1. Create a New Page

1. Open Website app, click `+ New` in top-right, select `Page`.
2. Choose a template category (Basic, About, Landing Pages, Gallery, Services, Pricing Plans, Team, Custom).
3. Enter a `Page Title` (used for menu and URL).
4. Click `Create`.
5. Customize with the website editor (building blocks, themes).
6. Click `Save`.
7. Toggle `Unpublished` to `Published` in upper-right corner.

### 2. Customize the Website Theme

1. Click `Edit` on any page.
2. Go to the `Theme` tab.
3. Switch Theme: Click `Switch Theme` in the Website section.
4. Colors: Click color dots or palette icon to change theme colors. Edit `Color Presets` for per-block color distribution.
5. Fonts: Select font family and size for Paragraphs, Headings, Buttons, Input Fields. Add custom fonts via `Add a Custom Font`.
6. Page Layout: Select a layout from the dropdown. Customize background (image, pattern, or blank).
7. Buttons: Configure primary/secondary styles (Fill, Outline, Flat), padding, round corners.
8. Click `Save`.

### 3. Configure a Custom Domain Name

1. Add a CNAME record pointing `www.yourdomain.com` to your Odoo database address (e.g., `mycompany.odoo.com`).
2. (Optional) Redirect naked domain to `www` subdomain using Cloudflare or DNS provider.
3. Map domain to database: Odoo Online -- use database manager > Domain Names > Use my own domain. Odoo.sh -- Branches > Settings > Custom domains.
4. Map domain to website: `Website > Configuration > Settings`, enter domain in `Domain` field, Save.
5. SSL certificate auto-generated via Let's Encrypt (up to 24 hours).

### 4. Set Up SEO for a Page

1. Access the page, go to `Website > Site > Optimize SEO`.
2. Edit `Title` tag (concise, descriptive) and `Description` tag.
3. Use `Fill with AI` for auto-generated meta title, description, and keyword suggestions.
4. Add keywords in the Keywords field, click `Add` to see usage analysis.
5. Set a social share image.
6. Toggle `Indexed` on/off in page properties to control search engine indexing.
7. Edit `robots.txt` via `Website > Configuration > Settings > SEO > Edit robots.txt`.

### 5. Set Up Multi-Website

1. Go to `Website > Configuration > Settings`.
2. Click `+ New Website`.
3. Specify Website Name, domain, company, languages, default language.
4. Click `Create`.
5. Switch between websites using the selector next to `+New`.
6. Configure each website independently (settings are per-website).
7. Control content availability via the `Website` field on records (empty = all websites, specific = one website).

## Technical Reference

### Models

| Model | Description |
|-------|-------------|
| `website` | Website configuration record |
| `website.page` | Static website pages |
| `website.menu` | Website menu items |
| `website.redirect` | URL redirect mappings (301, 302, 308, 404) |
| `website.mail.group` | Mail group configuration (`website_mail_group` module) |
| `website.mail.group.message` | Mail group messages |
| `website.mail.group.moderation` | Moderation rules for mail groups |

### Key Fields

- `website.page`: `url`, `is_published`, `date_publish`, `is_indexed`, `visibility` (public/signed_in/restricted_group/password), `is_homepage`, `website_id`
- `website`: `domain`, `name`, `company_id`, `default_lang_id`
- `website.redirect`: `url_from`, `url_to`, `type` (301/302/308/404), `active`, `sequence`, `website_id`

### System Parameters

| Key | Purpose |
|-----|---------|
| `web.base.url` | Root URL of the database |
| `web.base.url.freeze` | Set to `True` to prevent auto-update of base URL on admin login |
| `website.plausible_script` | Override Plausible.io script URL |
| `website.plausible_server` | Override Plausible.io server URL |

### Important URLs

- `/sitemap.xml` -- Auto-generated sitemap (cached, updated every 12 hours, 45000 URLs per chunk)
- `/robots.txt` -- Auto-generated robots.txt
- `/web/login` -- Login page (building blocks can be added)
- `/groups` -- Mail groups page

### Sitemap Attributes

- `<loc>`: Page URL
- `<lastmod>`: Last modification date (auto-computed from related object)
- `<priority>`: Normalized priority (default 16 for static pages; modules can implement custom algorithms)

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- Page creation uses a template selector with categories (Basic, About, Landing Pages, Gallery, Services, Pricing Plans, Team, Custom).
- Building blocks are split into `Categories` (structural) and `Inner Content` (elements).
- Grid layout mode available alongside column-based layouts.
- `Fill with AI` available in SEO optimizer for auto-generating meta titles, descriptions, and keyword suggestions.
- AI-based content generation available via `/` command in text editor.
- Color Presets system for predefined color combinations across building blocks.
- Image auto-compression and WebP conversion on upload.
- Hreflang and x-default tags auto-included for multilingual pages.
- Structured data (schema.org microdata) for events, eCommerce products, forum posts, and contact addresses.
- 308 Redirect/Rewrite type available for permanent redirection of dynamic pages.

## Common Pitfalls

- **SSL certificate delay**: After mapping a domain, certificate generation via Let's Encrypt can take up to 24 hours; validation attempts continue for 5 days. No certificate is generated for naked domains.
- **web.base.url auto-update**: When an admin logs in via the original `mycompany.odoo.com` address, the web base URL resets. Set `web.base.url.freeze` = `True` to prevent this.
- **Multi-website content**: Pages created from the frontend are only available on the website where they were created. Backend-created records default to all websites. Each website must have its own homepage.
- **robots.txt limitations**: `robots.txt` prevents crawling but does not guarantee a page will not be indexed -- pages can still appear in search results if linked from other crawled pages.
- **Plausible custom domain**: Free Plausible.io only works with `odoo.com` domains. Custom domains require a separate Plausible.io account and subscription.

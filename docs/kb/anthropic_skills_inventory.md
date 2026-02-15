# Anthropic Skills Inventory

## Overview

The `anthropics/skills` repository contains a collection of "skills" designed to enhance AI agent capabilities. Each skill is a self-contained directory with instructions (`SKILL.md`) and resources.

## Key Skills for Odoo Development

### 1. `webapp-testing` (Testing)

- **Purpose:** End-to-end testing of web applications using Playwright.
- **Key Features:**
  - Helper scripts for managing local servers (`scripts/with_server.py`).
  - Decision tree for handling static vs. dynamic content.
  - "Reconnaissance-then-action" pattern: Inspect DOM -> Identify Selectors -> Execute.
- **Relevance:** Can be adapted for Odoo Tour testing or external black-box testing of Odoo UIs.

### 2. `frontend-design` (UI/UX)

- **Purpose:** Creating high-quality, distinctive frontend interfaces.
- **Philosophy:** Avoid "generic AI aesthetics". Commit to bold design choices (Typography, Color, Motion).
- **Guidelines:**
  - Use variable-based theming.
  - Prioritize CSS-only motion where possible.
  - Create "atmosphere" with distinct backgrounds and textures.
- **Relevance:** aligns with Odoo's Owl framework for building custom snippets, themes, and dashboards.

### 3. `mcp-builder` (Integration)

- **Purpose:** Building Model Context Protocol (MCP) servers.
- **Workflow:**
  1.  **Research:** Understand the API/Data source.
  2.  **Implementation:** Build the server using SDKs.
  3.  **Review:** Verification and testing.
  4.  **Evaluation:** Creating QA baselines.
- **Relevance:** Essential for extending Odoo's capabilities to external tools or creating an "Odoo MCP Server" for other agents.

## Other Available Skills

| Skill                         | Description                        | Category     |
| :---------------------------- | :--------------------------------- | :----------- |
| `algorithmic-art`             | Generative art logic               | Creative     |
| `brand-guidelines`            | Enforcing brand voice/style        | Enterprise   |
| `doc-coauthoring`             | Collaborative writing workflows    | Productivity |
| `docx`, `xlsx`, `pptx`, `pdf` | Document manipulation and creation | Documents    |
| `internal-comms`              | Corporate communication patterns   | Enterprise   |
| `slack-gif-creator`           | Fun automation example             | Creative     |
| `theme-factory`               | Generating color themes/palettes   | Creative     |
| `web-artifacts-builder`       | Building static web artifacts      | Development  |

## Usage

To use a skill:

1.  **Load Context:** Read the `SKILL.md` file.
2.  **Load Resources:** Ingest any provided scripts or templates.
3.  **Follow Protocol:** Adhere to the defined workflow (e.g., "Reconnaissance-then-action").

## Source

- [GitHub Repository](https://github.com/anthropics/skills)

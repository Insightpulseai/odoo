# PRD: Odoo App Agent Skills

## Problem

The InsightPulse AI platform needs structured, reusable agent skills covering 16 service domains across Odoo consulting, app development, web development, and UI/UX design. Currently, these workflows are ad-hoc and not codified as executable skill definitions.

## Solution

Create a skill registry with YAML-defined skills organized into 4 categories (16 skills total), backed by an Odoo module (`ipai_agent_skills`) that provides the runtime models for skill execution tracking and orchestration.

## Service Domains

### Category 1: Odoo Services (5 skills)
| Skill | Key | Purpose |
|-------|-----|---------|
| Odoo Consultation | `odoo.consultation` | Discovery, gap analysis, module recommendations |
| Odoo Implementation | `odoo.implementation` | Environment setup, module install, go-live |
| Odoo Customization | `odoo.customization` | Custom module development, model extensions |
| Odoo Deployment | `odoo.deployment` | Production deployment, Docker, infrastructure |
| Odoo Support & Training | `odoo.support.training` | Troubleshooting, documentation, training |

### Category 2: App Development (5 skills)
| Skill | Key | Purpose |
|-------|-----|---------|
| App Development | `app.development` | General orchestration, routes to specialized |
| App Strategy & Consulting | `app.strategy` | Technology assessment, architecture planning |
| Custom App Development | `app.custom.development` | Full-stack app building with Odoo integration |
| Mobile App Design | `app.mobile.design` | Mobile wireframes, prototypes, offline-first |
| App Maintenance & Support | `app.maintenance` | Dependency updates, monitoring, bug fixes |

### Category 3: Web Development (5 skills)
| Skill | Key | Purpose |
|-------|-----|---------|
| App Marketing & Launch | `app.marketing.launch` | Launch strategy, landing pages, analytics |
| Web Development | `web.development` | Full-stack web application building |
| Custom Web Design | `web.custom.design` | Brand identity, design systems, responsive |
| Website Backend Solutions | `web.backend` | APIs, auth, database, infrastructure |
| E-Commerce Solutions | `web.ecommerce` | Odoo-powered online stores |

### Category 4: Design & Maintenance (2 skills)
| Skill | Key | Purpose |
|-------|-----|---------|
| Website Maintenance | `web.maintenance` | Performance, security, SEO, updates |
| UI/UX Design | `design.ui.ux` | Research, wireframes, design systems, testing |

## Success Criteria

- All 16 skills defined as valid YAML with intents, tools, workflow, schemas
- Odoo module installable with skill registry model
- Slash commands for key workflows (/consult, /implement, /deploy)
- Skills pass schema validation

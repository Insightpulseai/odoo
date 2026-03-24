---
id: og-card
title: InsightPulseAI OG Card
category: brand
owner: design
status: approved
intent: generate
surface: social-preview
aspect_ratio: "1200x630"
model_family: gemini-image
tags:
  - brand
  - og-card
  - social
  - launch
brand:
  corporate: InsightPulseAI
  assistant_family: Pulser
  allowed_public_names:
    - InsightPulseAI
    - Pulser
  forbidden_public_names:
    - Odoo Copilot
    - Ask Odoo Copilot
    - Pulsar
variables:
  - name: headline
    description: Primary social headline
    required: true
    default: Run Odoo in the Cloud with Practical AI
prompt: |
  Design a premium 1200x630 Open Graph card for InsightPulseAI.

  Headline: "{{headline}}"
  Brand: InsightPulseAI
  Optional sublabel: Powered by Pulser

  Create a polished enterprise SaaS social card with a dark premium background, subtle geometric dashboard layers, soft glow accents, and a clean modern layout. Use strong hierarchy and high contrast so the card remains readable at thumbnail size.

  Composition: logo/wordmark top-left, headline centered-left, supporting visual on the right using abstract panels, cloud operations cues, analytics motifs, and workflow intelligence. No stock characters, no cheesy robots, no clutter, no excessive icons.

  Style: modern B2B SaaS, restrained AI aesthetic, crisp sans-serif typography, premium dark navy/charcoal palette with subtle electric accents.

  Output requirements: launch-ready, clean safe margins, legible small-preview rendering, no watermark, no extra text beyond the approved brand and headline.
---

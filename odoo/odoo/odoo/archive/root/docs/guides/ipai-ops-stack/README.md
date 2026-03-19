# ipai-ops-stack Template

This directory contains reference templates for the `ipai-ops-stack` repository.

## Overview

The ops stack is a separate repository that hosts runtime collaboration and automation services:
- Mattermost (chat.insightpulseai.com)
- Focalboard (boards.insightpulseai.com)
- n8n (n8n.insightpulseai.com)
- Superset (superset.insightpulseai.com)

## Usage

1. Create the new repository:
   ```bash
   gh repo create jgtolentino/ipai-ops-stack --public
   ```

2. Copy these templates:
   ```bash
   cp -r docs/templates/ipai-ops-stack/* ~/ipai-ops-stack/
   ```

3. Customize `.env.example` with your values

4. Deploy:
   ```bash
   cd ~/ipai-ops-stack
   cp docker/.env.example docker/.env
   # Edit docker/.env
   ./scripts/up.sh
   ```

## File Structure

```
ipai-ops-stack/
├── docker/
│   ├── docker-compose.yml    # Main compose file
│   ├── .env.example          # Environment template
│   └── .gitignore
├── caddy/
│   └── Caddyfile             # Reverse proxy config
├── scripts/
│   ├── up.sh
│   ├── down.sh
│   ├── logs.sh
│   ├── healthcheck.sh
│   ├── backup.sh
│   └── restore.sh
├── n8n/
│   └── workflows/            # Exported workflow JSONs
└── docs/
    ├── SETUP.md
    └── DNS_TLS.md
```

## DNS Requirements

Configure these A records pointing to your server IP:
- chat.insightpulseai.com
- boards.insightpulseai.com
- n8n.insightpulseai.com
- superset.insightpulseai.com

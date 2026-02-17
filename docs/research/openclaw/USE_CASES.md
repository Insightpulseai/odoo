# OpenClaw Use Cases

> Research date: 2026-02-17
> Source: Official docs, GitHub, community, security advisories

---

## What OpenClaw Is

OpenClaw is a **self-hosted, model-agnostic AI agent runtime** (MIT, TypeScript/Node.js) that turns messaging apps into interfaces for an autonomous assistant capable of executing real-world tasks on your own infrastructure. 200k+ GitHub stars. Previously named Clawd / Clawdbot / Moltbot.

- **Repo**: github.com/openclaw/openclaw
- **Docs**: docs.openclaw.ai
- **Architecture**: Hub-and-spoke — single Gateway process (WebSocket server) managing sessions, tools, agents, memory, and routing.

---

## Architecture Overview

| Component | Description |
|-----------|-------------|
| **Gateway** | Long-running Node.js daemon; WebSocket control plane; watches `~/.openclaw/openclaw.json` |
| **Agent Runtime** | Input → context assembly → model call → tool execution → state persistence → reply |
| **Workspace** | Per-agent directory: `SOUL.md` (persona), `USER.md` (prefs), `AGENTS.md`, skills |
| **Sessions** | Per-channel chat history with automatic compaction (summarization) |
| **Multi-Agent Routing** | Multiple isolated agents in one Gateway, routed via bindings on channel/account/peer/chatType |
| **Nodes** | Companion apps (macOS, iOS, Android) for Canvas rendering, camera capture, notifications |

---

## Core Tools (8)

File read/write, shell command execution, web access (fetch), message sending.

## Advanced Tools (17)

| Tool | Capability |
|------|-----------|
| **Browser** | Full Chrome DevTools Protocol; AI Snapshot for page comprehension; click, type, screenshot, PDF |
| **Canvas** | Agent-driven visual workspace rendered on connected Nodes |
| **Nodes** | Discover paired devices; send notifications; capture camera/screen |
| **Cron** | Scheduled tasks, webhooks, Gmail Pub/Sub triggers |
| **Sessions** | Spawn sub-agents, manage multi-session state |
| **Memory** | Persistent memory stored as local Markdown; searchable knowledge base |
| **Gateway** | Control gateway configuration, channel management |
| **Message** | Send messages across any connected channel (13+ messaging platforms) |

## Plugin Ecosystem

| Plugin | Description |
|--------|-------------|
| **Lobster** | Typed workflow runtime — composable YAML/JSON pipelines with approval gates |
| **ClawHub** | 5,705+ community-built skills (AgentSkills-compatible) |

---

## Use Cases by Category

### Personal Automation

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **Morning Briefing** | Cron + web fetch + message | Cron schedule (daily) | Telegram/WhatsApp message with calendar, weather, emails, CI failures | VPS / homelab | Google Calendar, Gmail, weather APIs |
| **Inbox Triage** | Email scanning + categorization | Cron (2x/day) or Gmail Pub/Sub | Spam unsubscribed, categorized by urgency, summaries sent | VPS | Gmail, Outlook |
| **Package Tracking** | Browser automation + cron | Tracking numbers from chat | Dashboard updates, delivery notifications | Local / VPS | Carrier APIs |
| **Travel Planning** | Web search + browser + memory | Natural language request | Itineraries, booking links, calendar events | Local / VPS | Google Flights |
| **Personal Knowledge Base** | Memory tool + file storage | URLs, articles dropped into chat | Searchable memory store, custom dashboard | Local / homelab | Next.js |
| **Voice Journal** | Voice transcription + memory | Voice notes via mobile/desktop | Transcribed daily journal entries | Mobile + homelab | ElevenLabs, Whisper |

### DevOps & Development

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **CI/CD Monitoring** | Cron + webhook + message | GitHub Actions / GitLab CI webhooks | Build failure alerts, status summaries to Slack/Discord | VPS | GitHub Actions, Jenkins |
| **PR Summarization** | Browser/API + LLM | New PR webhook or cron | Human-readable summaries of code changes | VPS / local | GitHub, GitLab |
| **Autonomous Debug & Deploy** | Shell + browser + git | Voice or text command | Diagnose failure, update configs, redeploy, submit PR | Local / VPS | Git, Docker, cloud CLIs |
| **Mobile-First Coding** | Shell + file tools + message | WhatsApp/Telegram messages | Code edits, builds, deployments from phone | VPS | Git, npm |

### Business Intelligence & Monitoring

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **KPI Snapshots** | Browser automation + cron | Monday morning cron | Screenshot of dashboard + summary to Slack | VPS | Google Analytics, Jira |
| **Ad Campaign Optimization** | Browser + LLM analysis | Cron or manual trigger | Google Ads review, optimization recommendations | VPS | Google Ads, Meta Ads |
| **Earnings Report Tracking** | Web scraping + cron | Earnings season schedule | Previews, alerts, summaries of financial filings | VPS | Financial data APIs |

### Smart Home / IoT

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **Natural Language Home Control** | ha-mcp skill + message | Text/voice via any channel | Device control (lights, climate, locks) | Homelab | Home Assistant, ha-mcp |
| **Proactive Household Routines** | Cron + Home Assistant | Time/sensor triggers | Automated scenes, reminders, status reports | Homelab | Zigbee/Z-Wave |

### Multi-Agent Orchestration

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **Solo Founder Agent Team** | Multi-agent routing + sessions | Single Telegram interface | 4+ specialized agents (strategy, dev, marketing, business) with shared memory | VPS / homelab | Claude, GPT, DeepSeek |
| **Delegated Task Chains** | Lobster workflows + spawning | Complex request to parent agent | Sub-agents spawned with timeouts, results aggregated | VPS | Lobster |
| **MCP Bridge Orchestration** | MCP server + Gateway | Claude Desktop / Claude Code invocation | OpenClaw executes tasks on behalf of another AI client | Local + cloud | MCP protocol |

### Research & Content

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **Automated Content Research** | Web scraping + cron + memory | Daily cron, 109+ sources | Quality-scored tech news digest | VPS | RSS, Twitter API |
| **Reddit/X Opportunity Mining** | Browser + LLM analysis | Cron schedule | Pain points identified, MVP specs generated | VPS | Reddit, Twitter/X |
| **SEO Content Generation** | LLM + web research + file | Client brief via chat | Blog posts, product descriptions | Local / VPS | WordPress |

### Financial / Trading

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **24/7 Crypto Trading** | Browser + API + cron | Market conditions, arbitrage | Automated trades, Telegram alerts | VPS (isolated) | Exchange APIs |
| **Portfolio Monitoring** | Cron + web fetch | Scheduled intervals | Movement alerts, daily summaries | VPS | Financial APIs |

### Legal Tech

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **Contract Review & Clause Extraction** | LegalDoc AI skill + file | Upload contract via chat | Key issues flagged, clause extraction (indemnification, IP, non-compete) | Local (privacy) | Ollama |
| **Private Document Assistant** | Ollama + file + memory | Local document upload | Summaries, search, Q&A without external API calls | Homelab | Local LLMs |

### Freelance / Economic

| Use Case | Core Capability | Inputs / Triggers | Outputs / Side Effects | Deployment | Adjacent Tools |
|----------|----------------|-------------------|----------------------|------------|---------------|
| **ClawWork: Agent as Coworker** | Full tool suite + LLM | Professional task assignments | Completed tasks across 44 industries | Cloud / VPS | ClawWork framework |
| **Freelance Task Execution** | Shell + browser + file + LLM | Client requests via chat | Code, content, automation deliverables | VPS | Freelance platforms |

---

## Deployment Contexts

| Deployment | Description | Cost | Best For |
|-----------|-------------|------|----------|
| **Laptop (local)** | Direct install, `openclaw onboard` wizard | Free + API keys | Learning, dev |
| **Docker (local)** | Containerized, mounts `~/.openclaw` + workspace | Free + API keys | Security-conscious |
| **Homelab** | Dedicated always-on hardware (Mac Mini / NUC) | Hardware + API keys | 24/7 assistant, smart home |
| **VPS** | DigitalOcean 1-Click ($12/mo), Hostinger ($5/mo) | $5-12/mo + API keys | Always-on production |
| **Cloudflare Workers** | Serverless via moltworker; experimental | $5/mo | Slack/Discord only |
| **Docker Model Runner** | Local LLMs via Docker Desktop | Free (needs GPU) | Max privacy, zero recurring |

---

## Security Landscape (Critical)

| Issue | Detail |
|-------|--------|
| **CVE-2026-25253** | Critical RCE (CVSS 8.8): hijack local instances via malicious links, steal auth tokens |
| **230+ malicious ClawHub skills** | 26% of 31k analyzed skills had at least one vulnerability |
| **ClawHavoc campaign** | 335 infostealer packages deploying Atomic macOS Stealer, keyloggers, backdoors |
| **Plaintext API key leakage** | Credentials stolen via prompt injection or unsecured endpoints |
| **Persistent memory poisoning** | Attacker tricks agent into writing malicious instructions into SOUL.md |

### Required Mitigations
- Run in Docker containers or VMs, never on primary machine
- VirusTotal scanning for ClawHub skills before installation
- Restrict network egress to allow-lists
- Inject API keys as env vars, never in context window
- Use `tools.deny` to limit tool surface area

---

## Key Resources

| Resource | URL |
|----------|-----|
| Official docs | docs.openclaw.ai |
| GitHub org (18 repos) | github.com/openclaw |
| Awesome Skills | github.com/VoltAgent/awesome-openclaw-skills |
| Awesome Use Cases | github.com/hesamsheikh/awesome-openclaw-usecases |
| ClawHub (skill registry) | github.com/openclaw/clawhub |
| Lobster workflows | github.com/openclaw/lobster |
| ClawWork benchmark | github.com/HKUDS/ClawWork |
| MCP bridge | github.com/freema/openclaw-mcp |
| Security analysis (Cisco) | blogs.cisco.com/ai/personal-ai-agents-like-openclaw-are-a-security-nightmare |

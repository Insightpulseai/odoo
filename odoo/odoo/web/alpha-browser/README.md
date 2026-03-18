# Alpha Browser

Next-generation browser extension with vision-first grounding and multi-agent orchestration.

## Overview

Alpha Browser combines and surpasses the capabilities of Google Antigravity and Claude Chrome extension, featuring:

- **Vision-First Grounding**: Screenshots + OCR → DOM anchoring for reliable element targeting
- **Multi-Agent Orchestration**: Governor coordinates 5 specialized Workers (DOM, Form, Nav, Extract, Verify)
- **Session Persistence**: Mission-state checkpointing with crash recovery (MV3 service worker constraints)
- **Zero-Trust Identity**: Device pairing without central auth server
- **Local LLM Orchestration**: WebGPU inference for privacy and speed (cloud fallback)
- **Action Reliability**: Visual verification, retry logic, HITL escalation

## Current Status: Phase 1 - Foundation (Weeks 1-3)

**Implemented**:
- ✅ Project scaffold with Chrome Extension Manifest V3
- ✅ Service worker with lifecycle management and keepalive
- ✅ Content script for DOM interaction
- ✅ IndexedDB storage with Dexie.js (missions, checkpoints, memory)
- ✅ Basic popup UI with React + TanStack Query
- ✅ TypeScript types and shared utilities
- ✅ Structured logging system
- ✅ Offscreen document for future vision processing

**Next Steps** (Phase 1 Completion):
- [ ] Install dependencies with `pnpm install`
- [ ] Test extension loads in Chrome Dev Mode
- [ ] Verify service worker sends/receives messages (<100ms latency)
- [ ] Test screenshots saved to IndexedDB (WebP compressed, <50KB)
- [ ] Validate popup displays mission state

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Chrome Extension (Manifest V3)                    │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐         │
│  │   Popup UI   │◄──►│   Service    │◄──►│   Content    │         │
│  │   (React)    │    │   Worker     │    │   Script     │         │
│  └──────────────┘    │  (Governor)  │    └──────────────┘         │
│                      └──────────────┘                               │
│                             │                                        │
│                     ┌───────┴────────┐                              │
│                     │  Worker Agents  │                             │
│                     │  (5 types)      │                             │
│                     └─────────────────┘                             │
├─────────────────────────────────────────────────────────────────────┤
│                     Offscreen Document                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Vision Processor (DeepSeek-OCR) + Local LLM (WebGPU)       │  │
│  └──────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                     IndexedDB Storage                                │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                   │
│  │  Missions  │  │  RAG       │  │ Checkpoints│                   │
│  └────────────┘  └────────────┘  └────────────┘                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Getting Started

### Prerequisites

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Chrome/Edge browser

### Installation

```bash
# Install dependencies
pnpm install

# Development build with hot reload
pnpm dev

# Production build
pnpm build

# Run tests
pnpm test
```

### Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `dist/` directory from this project
5. Extension should appear in toolbar

## Development

### Project Structure

```
web/alpha-browser/
├── src/
│   ├── background/          # Service worker (Governor)
│   ├── content/             # Content scripts (page interaction)
│   ├── popup/               # Extension popup UI (React)
│   ├── offscreen/           # Offscreen document (heavy compute)
│   ├── agents/              # Agent implementations
│   ├── storage/             # IndexedDB abstraction (Dexie.js)
│   ├── vision/              # Vision processing (Phase 2)
│   ├── llm/                 # Local LLM integration (Phase 4)
│   ├── identity/            # Zero-trust identity (Phase 4)
│   └── shared/              # Shared utilities
├── public/
│   ├── manifest.json        # Chrome Extension Manifest V3
│   └── icons/               # Extension icons
├── tests/
│   ├── e2e/                 # Playwright E2E tests
│   ├── unit/                # Vitest unit tests
│   └── fixtures/            # Test data
├── docs/
│   ├── architecture.md      # System design
│   ├── agent-protocol.md    # Agent communication spec
│   └── vision-pipeline.md   # Vision processing details
└── README.md                # This file
```

### Phase Roadmap

**Phase 1: Foundation** (Weeks 1-3) - **CURRENT**
- Chrome Extension scaffold + Manifest V3
- Service worker lifecycle + keepalive
- Content script + DOM interaction
- IndexedDB storage + checkpointing
- Basic popup UI

**Phase 2: Vision Grounding** (Weeks 4-6)
- Offscreen document with WebGPU
- ONNX Runtime integration (DeepSeek-OCR)
- Visual anchoring (OCR → DOM)
- Visual verification (before/after diff)
- WebGPU viability assessment (Go/No-Go decision)

**Phase 3: Agent Orchestration** (Weeks 7-9)
- Governor agent (mission planning + coordination)
- Worker agents (DOM, Form, Nav, Extract, Verify)
- Agent protocol (typed messages + timeouts)
- Mission state machine + checkpointing
- HITL escalation UI

**Phase 4: Polish & Launch** (Weeks 10-12)
- Local LLM integration (if WebGPU viable)
- RAG memory system
- Zero-trust identity + device pairing
- UI/UX polish + settings panel
- Chrome Web Store submission

## Key Technical Decisions

### Vision-First vs DOM-First
**Choice**: Vision-First (screenshots + OCR → DOM anchoring)

**Rationale**: Works with Canvas/WebGL, resilient to React/Vue re-renders, enables semantic understanding

### Multi-Agent vs Single-Agent
**Choice**: Multi-Agent (Governor + 5 Workers)

**Rationale**: Specialization, parallelism, fault tolerance, extensibility

### Local LLM vs Cloud-Only
**Choice**: Hybrid (local WebGPU + cloud fallback)

**Rationale**: Privacy (OCR local), cost efficiency, low latency for simple tasks, capability for complex reasoning

### IndexedDB vs Supabase
**Choice**: IndexedDB (local-first) with optional Supabase sync

**Rationale**: Offline-first, fast (<100ms latency), private, optional cloud sync

### Chrome Extension vs Standalone App
**Choice**: Chrome Extension (Manifest V3)

**Rationale**: Native browser integration, no separate installation, access to chrome.* APIs

## Testing

```bash
# Run all tests
pnpm test

# Unit tests
pnpm test:unit

# E2E tests
pnpm test:e2e

# Vision tests (Phase 2)
pnpm test:vision

# Agent tests (Phase 3)
pnpm test:agents
```

## Contributing

This is a greenfield project under active development. Phase 1 (Foundation) is complete with core infrastructure in place.

## License

Proprietary - InsightPulse AI

## Contact

For questions or issues, contact the InsightPulse AI team.

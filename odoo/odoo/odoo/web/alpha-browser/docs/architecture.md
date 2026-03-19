# Alpha Browser Architecture

## System Overview

Alpha Browser is a Chrome Extension (Manifest V3) that implements vision-first browser automation with multi-agent orchestration.

### Core Components

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

## Extension Contexts

### 1. Service Worker (Background)

**File**: `src/background/service-worker.ts`

**Purpose**: Long-lived background context for Governor agent and coordination

**Constraints** (Manifest V3):
- Terminates after 30s-5min of inactivity
- No persistent global state
- Must serialize state to IndexedDB before suspension

**Lifecycle Management**:
- Keep-alive: Ping every 20s to prevent termination
- Checkpointing: Save state every 30s or after each action
- Crash recovery: Restore from last checkpoint on startup

**Responsibilities**:
- Governor agent coordination
- Message routing between contexts
- Mission state management
- Worker agent lifecycle

### 2. Content Script

**File**: `src/content/content-main.ts`

**Purpose**: DOM access and manipulation in web pages

**Injection**: Automatically into all URLs via manifest

**Responsibilities**:
- DOM element interaction (click, type, scroll, hover)
- Screenshot capture coordination
- DOM structure extraction
- Action execution and verification

### 3. Popup UI

**Files**: `src/popup/popup.tsx`, `src/popup/App.tsx`

**Purpose**: User interface for mission management and HITL approval

**Framework**: React + TanStack Query

**Responsibilities**:
- Mission creation and status display
- Action log visualization
- HITL approval interface
- Settings panel (Phase 4)

### 4. Offscreen Document

**File**: `src/offscreen/offscreen-main.ts`

**Purpose**: Isolated context for heavy compute (ONNX inference)

**Creation**: Dynamic via `chrome.offscreen.createDocument`

**Responsibilities** (Phase 2+):
- Vision model inference (DeepSeek-OCR)
- Local LLM execution (Phi-3-mini via WebGPU)
- Visual verification (pixelmatch + SSIM)

## Agent Architecture

### Governor Agent

**File**: `src/agents/governor.ts` (Phase 3)

**Role**: Mission coordinator and task router

**Responsibilities**:
- Mission planning (decompose goal into steps)
- Task assignment to Worker agents
- Progress monitoring and checkpointing
- Error handling and retry logic
- HITL escalation for ambiguous actions

**State Machine**:
```
pending → active → completed
              ↓
            paused
              ↓
            failed
```

### Worker Agents (5 Types)

**1. DOM Worker** (`src/agents/workers/dom-worker.ts`)
- DOM operations: click, type, scroll, hover
- Element targeting via visual anchors + DOM selectors
- Action verification via screenshots

**2. Form Worker** (`src/agents/workers/form-worker.ts`)
- Intelligent form filling with field detection
- Validation rule extraction
- Auto-complete suggestions

**3. Nav Worker** (`src/agents/workers/nav-worker.ts`)
- Page navigation and URL management
- Tab creation and switching
- History management

**4. Extract Worker** (`src/agents/workers/extract-worker.ts`)
- Structured data extraction from pages
- Table parsing and CSV export
- Content scraping with rate limiting

**5. Verify Worker** (`src/agents/workers/verify-worker.ts`)
- Visual verification (before/after comparison)
- Semantic verification (expected state validation)
- Error detection and retry triggers

### Agent Communication Protocol

**File**: `src/agents/protocol.ts` (Phase 3)

**Message Types**:
- `task-assignment`: Governor → Worker (task assignment)
- `task-result`: Worker → Governor (task completion)
- `task-error`: Worker → Governor (task failure)
- `keepalive`: Self-ping to prevent service worker termination
- `state-checkpoint`: Periodic state serialization
- `hitl-request`: Request user approval for ambiguous action
- `hitl-response`: User approval/rejection

**Message Format**:
```typescript
interface AgentMessage {
  id: string;              // Unique message ID
  from: AgentType;
  to: AgentType;
  type: MessageType;
  payload: unknown;
  timestamp: number;
  timeout: number;         // Default 5000ms
}
```

**Timeout Handling**:
- All messages have 5s timeout
- Retry logic: 3 attempts with exponential backoff
- Fallback to HITL if unrecoverable

## Storage Layer

### IndexedDB Schema

**File**: `src/storage/db.ts`

**Technology**: Dexie.js wrapper for IndexedDB

**Tables**:

1. **missions**: Mission state and progress
   - Primary key: `id`
   - Indexes: `status`, `createdAt`, `updatedAt`
   - Schema: See `Mission` type in `src/shared/types.ts`

2. **checkpoints**: Service worker state snapshots
   - Primary key: `id`
   - Indexes: `missionId`, `timestamp`
   - Schema: See `Checkpoint` type

3. **memory**: Long-term RAG memory (Phase 4)
   - Primary key: `id`
   - Indexes: `missionId`, `timestamp`, `tags`
   - Schema: See `MemoryEntry` type

### Checkpoint Strategy

**Frequency**: Every 30s or after each action (whichever comes first)

**Content**:
- Mission ID and current step
- Governor agent state (active plan, context)
- Worker agent states (pending tasks)
- Timestamp for staleness detection

**Recovery**:
- On service worker startup, check for active mission
- If checkpoint exists, restore state
- Resume from last completed step

## Vision Processing Pipeline (Phase 2)

### Screenshot Capture

**Flow**:
1. Service worker requests screenshot
2. Content script calls `chrome.tabs.captureVisibleTab`
3. Compress to WebP (quality 0.8, target <50KB)
4. Save to IndexedDB with mission association

### OCR Processing

**Model**: DeepSeek-OCR (INT8 quantized, ~180MB)

**Runtime**: ONNX Runtime Web with WebGPU acceleration

**Flow**:
1. Load screenshot from IndexedDB
2. Send to offscreen document for inference
3. Extract text + bounding boxes
4. Map bounding boxes to DOM elements
5. Generate visual signatures (SHA-256 hashes)

### Visual Anchoring

**Strategy**: Multi-fallback approach

**Priority Chain**:
1. **Visual Signature**: SHA-256 hash of image region
2. **Text Content + Position**: OCR text + bounding box
3. **DOM Selector**: Traditional CSS selector
4. **HITL Approval**: User selects element manually

**Visual Signature Generation**:
```
1. Extract pixel region from screenshot (bounding box)
2. Resize to 64x64px (canonical size)
3. Convert to grayscale
4. Compute SHA-256 hash
```

### Visual Verification

**Before/After Comparison**:
1. Capture screenshot before action
2. Execute action
3. Capture screenshot after action
4. Send both to offscreen document
5. Run pixelmatch for pixel-level diff
6. Calculate SSIM for structural similarity
7. Return confidence score (0-1)

**Success Criteria**:
- Confidence >0.95 → Success
- Confidence 0.7-0.95 → Warning (check logs)
- Confidence <0.7 → Failure (retry)

## Local LLM Integration (Phase 4)

### Model Tiers

**Tier 1: Local** (Privacy-first)
- Model: Phi-3-mini (INT8 quantized, ~150MB)
- Runtime: WebGPU via ONNX Runtime Web
- Use cases: Action planning, simple reasoning
- Latency target: <2s

**Tier 2: Cloud Free** (Cost-efficient)
- Model: GPT-4o-mini or Claude 3.5 Haiku
- Use cases: Complex reasoning, multi-step planning
- Cost: Free tier or low-cost

**Tier 3: Cloud Premium** (Capability-first)
- Model: Claude 3.5 Sonnet or GPT-4o
- Use cases: Ambiguous actions, HITL assistance
- Cost: Premium tier

### Model Router

**File**: `src/llm/model-registry.ts` (Phase 4)

**Selection Logic**:
1. Check local model availability (WebGPU support)
2. Estimate task complexity
3. Select tier based on:
   - Complexity score
   - User budget preferences
   - Previous success rates

**Fallback Chain**: Local → Cloud Free → Cloud Premium

## Security & Privacy

### Zero-Trust Identity (Phase 4)

**File**: `src/identity/pairing.ts`

**Device Pairing**:
1. Generate Ed25519 keypair (Web Crypto API)
2. Display QR code with public key + challenge
3. Second device scans QR
4. Cryptographic handshake (no central server)
5. Store private key in IndexedDB (encrypted)

### Data Privacy

**Local-First Approach**:
- Screenshots never leave device (OCR runs locally)
- Mission state stored in IndexedDB (browser-local)
- Optional cloud sync via Supabase (end-to-end encrypted)

**API Key Storage**:
- Chrome storage API (synced across devices)
- Never hardcoded in extension code
- User-managed via settings panel

## Performance Targets

| Metric | Target | Current (Phase 1) |
|--------|--------|-------------------|
| Service worker keepalive | 100% uptime | ✅ 100% (ping every 20s) |
| Message latency | <100ms | ✅ <50ms (local) |
| Checkpoint write | <100ms | ✅ <50ms (Dexie.js) |
| Screenshot compression | <50KB | 🚧 Phase 2 |
| OCR latency | <1s | 🚧 Phase 2 |
| Visual verification | <500ms | 🚧 Phase 2 |
| Local LLM inference | <2s | 🚧 Phase 4 |
| Action success rate | >90% | 🚧 Phase 3 |

## Error Handling

### Retry Logic

**Configuration**:
- Max retries: 3
- Initial delay: 500ms
- Backoff factor: 2x
- Max delay: 5s

**Retry Triggers**:
- Network errors
- Element not found
- Timeout errors
- Visual verification failure

### HITL Escalation

**Triggers**:
- Unrecoverable errors after 3 retries
- Ambiguous actions (multiple targets)
- Low confidence scores (<0.7)
- User-defined approval gates

**UI**:
- Popup notification with screenshot
- Action description + options
- Timeout: 60s (auto-abort if no response)

## Testing Strategy

### Unit Tests (Vitest)

**Coverage Target**: >80%

**Focus Areas**:
- Storage layer (CRUD operations)
- Agent protocol (message routing)
- Utility functions (retry, timeout, serialization)

### E2E Tests (Playwright)

**Scenarios**:
- Mission creation and execution
- Service worker crash recovery
- Visual anchoring accuracy
- HITL approval flow

### Performance Tests

**Benchmarks**:
- Screenshot capture + compression latency
- OCR inference latency
- Visual verification latency
- Checkpoint write latency

## Future Enhancements

### Swarm Intelligence (Post-Launch)

**Cross-Device Coordination**:
- Share learned patterns across user's devices
- Distributed mission execution
- Consensus-based action validation

### Advanced RAG Memory

**Semantic Search**:
- Vector embeddings for memory entries
- Similarity search for past missions
- Pattern learning from user behavior

### Cost Optimization

**Automatic Tier Selection**:
- Track model costs and success rates
- Optimize tier selection dynamically
- Budget enforcement and alerts

---

**Last Updated**: 2026-02-12 (Phase 1 Complete)

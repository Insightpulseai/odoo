# IPAI AI Agents UI

React + Fluent UI v9 panel for AI agents in Odoo CE 18.

## Features

- Modern Ask AI panel built with React 18 and Microsoft Fluent UI v9
- Command palette integration (Alt+Shift+F)
- Agent selection with provider switching
- Threaded conversations with message history
- Citation rendering with source links
- Confidence scoring display
- Light/dark theme switching
- Responsive design

## Installation

1. Install the module in Odoo:
   - Go to Apps
   - Search for "IPAI AI Agents UI"
   - Install

2. Configure an AI provider:
   - Go to Settings → AI Providers
   - Create and configure a provider (e.g., Kapa, OpenAI)

3. Build the React bundle (for development):
   ```bash
   cd addons/ipai/ipai_ai_agents_ui/ui
   npm install
   npm run build
   ```

## Usage

- Press **Alt+Shift+F** to open the Ask AI panel
- Or go to **AI → Ask AI (Fluent UI)** in the menu
- Select an agent from the dropdown
- Type your question and press Enter or click Send

## Architecture

```
ipai_ai_agents_ui/
├── __manifest__.py           # Odoo module manifest
├── controllers/
│   └── main.py               # JSON-RPC endpoints (bootstrap, ask, feedback)
├── static/
│   ├── src/                  # Odoo integration JS
│   │   ├── command_palette.js
│   │   └── ai_panel_react_action.js
│   └── lib/                  # Built React bundle
│       ├── ipai_ai_ui.iife.js
│       └── ipai_ai_ui.css
├── ui/                       # React source code
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx
│       ├── app/App.tsx
│       └── lib/odooRpc.ts
└── views/
    └── menu.xml
```

## Environment Variables

Required for full functionality:

```bash
# Supabase KB for RAG retrieval
IPAI_SUPABASE_URL=https://<project>.supabase.co
IPAI_SUPABASE_SERVICE_ROLE_KEY=<key>

# LLM Provider (OpenAI-compatible)
IPAI_LLM_API_KEY=<key>
IPAI_LLM_BASE_URL=https://api.openai.com/v1
IPAI_LLM_MODEL=gpt-4o-mini

# Optional: Embeddings for vector search
IPAI_EMBEDDINGS_PROVIDER=openai
IPAI_EMBEDDINGS_MODEL=text-embedding-3-small
```

## Development

To develop the React UI:

```bash
cd addons/ipai/ipai_ai_agents_ui/ui
npm install
npm run dev    # Start Vite dev server
npm run build  # Build for production
```

The build script automatically copies the bundle to `static/lib/`.

## Dependencies

- `ipai_ai_core` - Provider registry, threads, messages, citations
- React 18
- Fluent UI v9

## API Endpoints

All endpoints use Odoo JSON-RPC and require session authentication.

### GET /ipai_ai_agents/bootstrap

Returns available agents and user context.

### POST /ipai_ai_agents/ask

Send a message and get AI response with citations.

Parameters:
- `provider_id`: ID of the AI provider to use
- `message`: User's question
- `thread_id`: Optional existing thread ID

### POST /ipai_ai_agents/feedback

Submit feedback on an AI response.

Parameters:
- `message_id`: ID of the message
- `rating`: "helpful" or "not_helpful"

## License

LGPL-3

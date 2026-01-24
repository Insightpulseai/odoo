# OCR / Document Understanding Routing Matrix

**Last Updated**: 2026-01-24

## Overview

This document defines the routing strategy for document processing across different OCR and vision engines. The goal is to balance cost, accuracy, privacy, and speed based on use case.

## Engines

| Engine | Type | Best For | Deployment |
|--------|------|----------|------------|
| **PaddleOCR** | OCR | Fast baseline, receipts, simple docs | Self-hosted / on-device |
| **LandingAI ADE** | Document AI | Layout-aware parsing, tables, forms, checkboxes | Cloud API |
| **VLM (DeepSeek/GPT-4V)** | Vision LLM | Semantic understanding, describe, freeform queries | Cloud API |

## Routing Matrix

### By Mode

| Mode | Primary Engine | Fallback | Rationale |
|------|----------------|----------|-----------|
| `plain_ocr` | PaddleOCR | VLM | Cost-effective, deterministic |
| `find` | PaddleOCR + text index | VLM | Search extracted text first; VLM for semantic search |
| `describe` | VLM | PaddleOCR (text only) | Requires multimodal understanding |
| `freeform` | VLM | PaddleOCR (text only) | Instruction-following needs LLM |

### By Input Type

| Input | Condition | Route | Output |
|-------|-----------|-------|--------|
| Mobile camera receipt | Offline / low latency | PaddleOCR | text + boxes |
| Scanned invoice PDF | Complex layout, tables | LandingAI ADE | semantic chunks + groundings |
| Form with checkboxes | Layout-aware extraction | LandingAI ADE | fields + values |
| UI screenshot | Visual regression triage | VLM | structured verdict |
| Handwritten notes | Variable quality | PaddleOCR → VLM | text + confidence |

### By Environment

| Environment | Available Engines | Default |
|-------------|-------------------|---------|
| Mobile offline | PaddleOCR (embedded) | PaddleOCR |
| Mobile online | All | PaddleOCR, escalate to ADE |
| Server batch | All | ADE for complex, PaddleOCR for simple |
| Edge Function | PaddleOCR (backend) + ADE | Route by mode |

## Decision Logic

```
┌─────────────────────────────────────────────┐
│              Incoming Request               │
│         (image/PDF + mode + prompt)         │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │  Route by Mode  │
        └────────┬────────┘
                 │
    ┌────────────┼────────────┬────────────┐
    │            │            │            │
    ▼            ▼            ▼            ▼
plain_ocr     find       describe    freeform
    │            │            │            │
    ▼            ▼            ▼            ▼
 Paddle      Paddle+       VLM         VLM
             Index
    │            │            │            │
    └────────────┴────────────┴────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Circuit Breaker │
        │   Check         │
        └────────┬────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
    Primary OK?      Fallback
        │                 │
        ▼                 ▼
    Return           Return with
    Result          fallback_used=true
```

## API Contract

### Request

```
POST /api/ocr?engine={engine}&mode={mode}&prompt={prompt}
Content-Type: multipart/form-data

file: <image or PDF>
```

### Query Parameters

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `engine` | `paddle`, `landingai`, `vlm`, `auto` | `auto` | Force specific engine or let router decide |
| `mode` | `plain_ocr`, `find`, `describe`, `freeform` | `plain_ocr` | Processing mode |
| `prompt` | string | null | Search term or instruction |

### Response

```json
{
  "request_id": "uuid",
  "engine": "paddle",
  "mode": "plain_ocr",
  "text": "extracted text...",
  "boxes": [
    {"label": "text", "x": 0.12, "y": 0.10, "w": 0.16, "h": 0.05}
  ],
  "chunks": [],
  "raw_model_response": {},
  "metadata": {
    "fallback_used": false,
    "latency_ms": 234,
    "content_type": "image/png"
  }
}
```

## Integration Points

### Supabase Edge Function

```
supabase/functions/doc-ocr/index.ts
```

### MCP Server

```
mcp/servers/doc-ocr-server/
```

### Job Queue

```
mcp_jobs.jobs with job_type = 'ocr_parse'
```

## Related Documentation

- [CAPS Report](./CAPS_REPORT.md) - Cost/Accuracy/Privacy/Speed analysis
- [Dump Analysis](../evidence/20260124-dump-analysis/) - Full engineering analysis

# CAPS Report — Cost / Accuracy / Privacy / Speed

**Last Updated**: 2026-01-24

## Overview

This report evaluates OCR and document processing engines across four dimensions critical for production deployment decisions.

## Engine Comparison Matrix

| Dimension | PaddleOCR | LandingAI ADE | VLM (GPT-4V/DeepSeek) |
|-----------|-----------|---------------|----------------------|
| **Cost** | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| **Accuracy** | ★★★☆☆ | ★★★★★ | ★★★★☆ |
| **Privacy** | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| **Speed** | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |

## Detailed Analysis

### PaddleOCR

| Dimension | Rating | Details |
|-----------|--------|---------|
| **Cost** | Low | Self-hosted; no per-call fees; GPU optional |
| **Accuracy** | Good | Excellent for clean text; degrades on complex layouts, tables, checkboxes |
| **Privacy** | Best | Fully local/on-prem; data never leaves your infrastructure |
| **Speed** | High | ~50-200ms per image on CPU; <50ms on GPU |

**Best For:**
- High-volume processing where cost matters
- Privacy-sensitive documents
- Mobile offline processing
- Simple receipts, invoices without tables
- Baseline/fallback engine

**Limitations:**
- No semantic understanding
- Poor on complex layouts
- No checkbox/form field extraction
- Requires self-hosting infrastructure

### LandingAI ADE (Agentic Document Extraction)

| Dimension | Rating | Details |
|-----------|--------|---------|
| **Cost** | Moderate | Usage-based cloud pricing; varies by volume |
| **Accuracy** | Excellent | Strong on complex layouts, tables, forms; grounded chunks for RAG |
| **Privacy** | Moderate | Cloud-based; review data handling policy |
| **Speed** | Moderate | 1-5s per document; network latency included |

**Best For:**
- Complex documents with tables, forms
- Invoices requiring field extraction
- Documents needing structured output for downstream processing
- RAG ingestion (produces semantic chunks)

**Limitations:**
- Requires API key and network
- Higher cost than self-hosted OCR
- Data leaves your infrastructure
- Rate limits apply

### VLM (Vision Language Models)

| Dimension | Rating | Details |
|-----------|--------|---------|
| **Cost** | High | Per-token pricing; images are expensive |
| **Accuracy** | Very Good | Strong semantic understanding; can follow instructions |
| **Privacy** | Variable | Cloud-based; depends on vendor policy |
| **Speed** | Moderate-Slow | 2-10s depending on model and prompt complexity |

**Best For:**
- Semantic understanding ("describe this document")
- Instruction-following ("find all mentions of...")
- Visual regression triage
- Ambiguous cases requiring reasoning

**Limitations:**
- Most expensive option
- Overkill for simple OCR
- Can hallucinate
- Not deterministic

## Cost Modeling

### Monthly Cost Estimates (10,000 documents/month)

| Engine | Compute | API Calls | Storage | Total |
|--------|---------|-----------|---------|-------|
| PaddleOCR | $50 (CPU instance) | $0 | $10 | **$60** |
| LandingAI ADE | $0 | ~$500-1000 | $10 | **$510-1010** |
| VLM (GPT-4V) | $0 | ~$2000-5000 | $10 | **$2010-5010** |

*Estimates based on typical document sizes and complexity. Actual costs vary.*

### Break-Even Analysis

| Scenario | Recommended Engine |
|----------|-------------------|
| <1000 docs/month, simple | PaddleOCR |
| 1000-10,000 docs/month, mixed | PaddleOCR + ADE (routed) |
| >10,000 docs/month, complex | PaddleOCR baseline + ADE escalation |
| Privacy-critical | PaddleOCR only |
| Accuracy-critical (legal/financial) | ADE primary |

## Privacy Considerations

### Data Flow by Engine

| Engine | Data Location | Retention | Compliance |
|--------|---------------|-----------|------------|
| PaddleOCR | Your infrastructure | Your control | Full compliance |
| LandingAI ADE | LandingAI cloud | Per policy | Review ToS |
| VLM | OpenAI/Anthropic cloud | Per policy | Review ToS |

### Recommendations

1. **Default to PaddleOCR** for non-sensitive documents
2. **Use ADE** only when layout complexity requires it
3. **Audit data flow** before processing PII/PHI
4. **Consider on-prem VLM** for sensitive semantic tasks

## Speed Benchmarks

### Latency by Document Type (p50)

| Document Type | PaddleOCR | LandingAI ADE | VLM |
|---------------|-----------|---------------|-----|
| Single-page receipt | 80ms | 1.2s | 3s |
| Multi-page invoice | 400ms | 3.5s | 8s |
| Complex form | 150ms | 2s | 5s |
| Handwritten note | 200ms | 2.5s | 4s |

### Throughput

| Engine | Docs/minute (single worker) |
|--------|----------------------------|
| PaddleOCR | 30-60 |
| LandingAI ADE | 10-20 |
| VLM | 5-10 |

## Decision Framework

```
                    ┌─────────────────┐
                    │ Document Input  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Privacy Check   │
                    │ (PII/PHI/etc?)  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         PII Present    No PII      Uncertain
              │              │              │
              ▼              ▼              ▼
         PaddleOCR     Check Layout    Review Policy
         (always)           │              │
                    ┌───────┴───────┐      │
                    │               │      │
               Simple          Complex     │
                    │               │      │
                    ▼               ▼      │
               PaddleOCR    LandingAI ADE  │
                                    │      │
                            Check Accuracy │
                            Requirements   │
                                    │      │
                           ┌────────┴──────┴────────┐
                           │                        │
                       Standard               High Accuracy
                           │                        │
                           ▼                        ▼
                       Return                  Add VLM
                       Result               Verification
```

## Monitoring Metrics

Track these metrics per engine:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Latency p95 | <2s | >5s |
| Error rate | <1% | >5% |
| Cost per doc | Varies | >2x baseline |
| Fallback rate | <10% | >25% |

## Related Documentation

- [OCR Routing Matrix](./OCR_ROUTING_MATRIX.md)
- [Dump Analysis](../evidence/20260124-dump-analysis/)
- [MCP Jobs System](../infra/MCP_JOBS_SYSTEM.md)

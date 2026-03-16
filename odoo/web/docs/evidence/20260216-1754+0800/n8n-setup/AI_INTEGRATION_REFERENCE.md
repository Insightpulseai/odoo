# n8n AI Integration Reference

**Purpose**: Reference guide for n8n self-hosted AI capabilities (Ollama + Qdrant)
**Status**: REFERENCE (not a completion claim)
**Timezone**: Asia/Manila (UTC+08:00)

---

## Overview

The n8n Self-hosted AI Starter Kit provides local AI capabilities for n8n workflows without cloud dependencies. This integration adds:

✅ **Ollama** - Local LLM platform (Llama, Mistral, etc.)
✅ **Qdrant** - High-performance vector database
✅ **AI Workflows** - Pre-built templates for common AI tasks

**Key Benefits**:
- 🔒 **Privacy**: All AI processing stays local (no data sent to cloud)
- 💰 **Cost**: No API fees for LLM usage
- ⚡ **Speed**: Local inference (no network latency)
- 🎯 **Control**: Full control over models and data

**Source**: https://github.com/n8n-io/self-hosted-ai-starter-kit

---

## Architecture Integration

### Current Setup (Verified)
```yaml
Existing Infrastructure:
  - n8n: https://n8n.insightpulseai.com (container: ipai-n8n)
  - Database: Supabase PostgreSQL
  - Network: ipai-network
  - Host: 178.128.112.214 (DigitalOcean droplet)
```

### Target Setup (After Integration)
```yaml
Enhanced Infrastructure:
  - n8n: https://n8n.insightpulseai.com (existing)
  - Ollama: http://localhost:11434 (new container)
  - Qdrant: http://localhost:6333 (new container)
  - Shared Storage: /data/shared (file uploads)
  - Network: ipai-network (shared)
```

---

## Prerequisites

**System Requirements**:
- Docker installed and running
- Minimum 8GB RAM available (16GB recommended)
- 20GB free disk space for models
- CPU or GPU for inference (GPU optional but faster)

**Network Requirements**:
- Ports available: 11434 (Ollama), 6333 (Qdrant)
- Internal network communication between containers

---

## Component Overview

### Ollama Container
**Purpose**: Local LLM inference platform
**Port**: 11434
**Storage**: Docker volume `ollama_storage`
**Models**: Download via `ollama pull <model-name>`

**Recommended Models**:
- **Small & Fast**: Llama 3.2 (3B) ~2GB, Phi-3 Mini (3.8B)
- **Medium**: Mistral 7B, Llama 3.1 (8B)
- **Large**: Llama 3.1 (70B) - requires 64GB RAM
- **Specialized**: CodeLlama (code), nomic-embed-text (embeddings)

### Qdrant Container
**Purpose**: Vector database for RAG (Retrieval Augmented Generation)
**Port**: 6333
**Storage**: Docker volume `qdrant_storage`
**Collections**: Created via API or n8n workflows

---

## [MANUAL_REQUIRED]

### Container Deployment
**What**: Deploy Ollama and Qdrant containers on droplet
**Why**: Requires SSH access and Docker orchestration on production host
**Evidence**: Starter kit repository at https://github.com/n8n-io/self-hosted-ai-starter-kit

**Minimal human action**:
1. SSH to droplet: `ssh root@178.128.112.214`
2. Create Docker volumes for persistent storage
3. Deploy containers to `ipai-network` network
4. Download initial LLM model (e.g., Llama 3.2)
5. Verify health endpoints respond correctly

**Then**: Credentials can be added in n8n UI

### n8n Credential Configuration
**What**: Add Ollama and Qdrant credentials in n8n
**Why**: n8n requires UI-only credential setup (no API endpoint for credential creation)

**Minimal human action**:
1. In n8n UI (https://n8n.insightpulseai.com):
   - Navigate to Credentials → Add Credential
   - Search "Ollama" → Add "Ollama API"
   - Configure: Base URL = `http://ipai-ollama:11434`
   - Test connection and save

2. Add Qdrant credentials:
   - Navigate to Credentials → Add Credential
   - Search "Qdrant" → Add "Qdrant API"
   - Configure: URL = `http://ipai-qdrant:6333`
   - API Key: (leave empty for local instance)
   - Test connection and save

**Then**: AI nodes available for workflow automation

---

## Available AI Workflows

### 1. AI Agent Chat (Simple Q&A)
**Workflow**: Chat Trigger → AI Agent → Ollama Chat Model
**Use Cases**:
- Customer support chatbot
- Internal knowledge base Q&A
- Document summarization

### 2. PDF Document Q&A (RAG)
**Workflow**: Webhook → Read PDF → Extract Text → Split Text → Create Embeddings → Store in Qdrant → Query → Ollama Chat → Return Answer
**Use Cases**:
- Financial document analysis
- Legal contract review
- Research paper summarization

### 3. Odoo + AI Integration
**Workflow**: Schedule Trigger → Odoo: Get Records → AI Classification → Ollama Chat Model → Odoo: Update Records
**Use Cases**:
- Auto-categorize support tickets
- Sentiment analysis of customer feedback
- Auto-generate product descriptions
- Invoice data extraction and validation

---

## Resource Management

### CPU vs GPU Inference

**Current Setup** (CPU only):
```yaml
Performance:
  - Small models (3B): 2-5 seconds per response
  - Medium models (7B): 5-15 seconds per response
  - Large models (70B): Not recommended on CPU

Resource Usage:
  - Llama 3.2 (3B): ~4GB RAM
  - Mistral 7B: ~8GB RAM
  - Running inference: Additional 2-4GB RAM
```

**GPU Setup** (Optional, for faster inference):
- Requires Nvidia GPU + nvidia-docker
- Recreate Ollama container with `--gpus all` flag
- Significantly faster inference (sub-second for small models)

### Model Management

**Model Storage Location**: Docker volume `ollama_storage` → `/root/.ollama/models` in container

**Operations**:
- List models: `docker exec ipai-ollama ollama list`
- Remove unused: `docker exec ipai-ollama ollama rm <model-name>`
- Pull new model: `docker exec ipai-ollama ollama pull <model-name>`

---

## Security Considerations

### Network Security
**Internal Access Only** (Recommended):
- Ollama and Qdrant only accessible within Docker network
- No external access to ports 11434 and 6333
- Only n8n can communicate with Ollama/Qdrant

**External Access** (If needed):
- Add nginx reverse proxy for Ollama (authenticated)
- Not recommended for production without authentication

### Data Privacy
**Benefits of Local AI**:
- ✅ All data stays on your infrastructure
- ✅ No data sent to OpenAI, Anthropic, or other cloud providers
- ✅ Full control over model and data storage
- ✅ GDPR/compliance friendly

**Risks**:
- ⚠️ Local models less capable than GPT-4/Claude
- ⚠️ Requires more infrastructure resources
- ⚠️ Model updates require manual pulling

---

## Monitoring and Maintenance

### Health Checks
```bash
# Check container status
docker ps | grep -E "(ipai-ollama|ipai-qdrant)"

# Check Ollama API
curl http://localhost:11434/api/version

# Check Qdrant API
curl http://localhost:6333/collections
```

### Resource Monitoring
```bash
# Container resource usage
docker stats ipai-ollama ipai-qdrant --no-stream

# Disk usage for AI models
docker exec ipai-ollama du -sh /root/.ollama
```

### Logs
```bash
# Ollama logs
docker logs ipai-ollama --tail 50

# Qdrant logs
docker logs ipai-qdrant --tail 50

# n8n AI workflow execution logs
# View in n8n UI: Executions tab
```

---

## Troubleshooting

### Issue: Ollama Model Download Slow
**Symptom**: Model download taking >30 minutes
**Check**: Network connectivity and download progress in logs
**Solution**: Use smaller model (llama3.2 instead of llama3.1:70b) or wait for completion

### Issue: n8n Can't Connect to Ollama
**Symptom**: "Connection refused" error in n8n workflows
**Check**: Both containers on same network, Ollama container running
**Solution**: Ensure both containers on `ipai-network`, use container name `ipai-ollama:11434` (not localhost)

### Issue: Out of Memory During Inference
**Symptom**: Ollama container crashes or freezes
**Check**: Available memory and container memory usage
**Solution**: Use smaller model (3B instead of 7B), increase droplet RAM, or reduce concurrent workflows

---

## Cost & Performance Comparison

### Cloud AI vs Local AI

| Factor | Cloud (OpenAI/Anthropic) | Local (Ollama + Qdrant) |
|--------|--------------------------|-------------------------|
| **Setup** | 5 minutes (API key) | 30 minutes (install) |
| **Cost** | $10-100/month (usage) | $0 (included in hosting) |
| **Speed** | 1-3 seconds | 2-15 seconds (CPU) |
| **Quality** | Excellent (GPT-4) | Good (Llama 3.1) |
| **Privacy** | Data sent to cloud | 100% local |
| **Limits** | API rate limits | Hardware only |
| **Models** | Latest always | Manual updates |

### When to Use Local AI

**Good Use Cases**:
- ✅ High-volume processing (1000+ requests/day)
- ✅ Privacy-sensitive data (PII, financial)
- ✅ Cost-sensitive workloads
- ✅ Offline environments

**Not Ideal**:
- ❌ Requires GPT-4 level quality
- ❌ Low latency critical (<1 second)
- ❌ Limited infrastructure resources
- ❌ Need latest model features

---

## Next Steps

### Immediate Actions
- [ ] Deploy Ollama and Qdrant containers (see [MANUAL_REQUIRED] section)
- [ ] Download Llama 3.2 model
- [ ] Configure n8n credentials (see [MANUAL_REQUIRED] section)
- [ ] Test simple chat workflow
- [ ] Import AI templates from n8n gallery

### Future Enhancements
- [ ] Add GPU support for faster inference
- [ ] Deploy specialized models (code, embeddings)
- [ ] Create Odoo + AI integration workflows
- [ ] Set up monitoring and alerting
- [ ] Build custom AI agents for business processes

---

## Related Documentation

- **n8n Admin Setup**: `ADMIN_SETUP_REFERENCE.md` (first-time account creation)
- **n8n-Odoo Integration**: `ODOO_INTEGRATION_REFERENCE.md` (Odoo workflow integration)
- **Ollama Docs**: https://ollama.com/library
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **n8n AI Docs**: https://docs.n8n.io/advanced-ai/

---

**Note**: This is a reference document, not a claim of completion. See `IMPLEMENTATION_SUMMARY.md` for current implementation status and remaining manual steps.

---

## APPENDIX: Verification Commands

**Only use if deploying containers (requires SSH access)**:

```bash
# Verify Ollama health
curl http://localhost:11434/api/version

# Test Ollama inference
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?",
  "stream": false
}'

# Verify Qdrant health
curl http://localhost:6333/collections

# Check container status
docker ps | grep -E "(ipai-ollama|ipai-qdrant)"

# Check Ollama models
docker exec ipai-ollama ollama list
```

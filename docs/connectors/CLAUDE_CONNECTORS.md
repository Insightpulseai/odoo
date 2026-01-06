# Claude Connector Configuration Guide

## Overview

This guide documents the recommended Claude connectors for the InsightPulse Finance SSC platform.

## Connector Priority Matrix

| Connector | Priority | Status | Use Case |
|-----------|----------|--------|----------|
| Google Drive | Critical | Connected | Document access, receipt storage |
| GitHub | Critical | Connected | Code repository, issue tracking |
| n8n | Critical | **To Connect** | Workflow automation, debugging |
| Gmail | Critical | **To Connect** | Invoice emails, BIR confirmations |
| Google Calendar | High | **To Connect** | Deadlines, filing dates |
| Vercel | Medium | **To Connect** | Deployment visibility |
| Figma | Low | Optional | Design work |

## Connector Setup Instructions

### n8n Connector (Critical)

The n8n connector enables Claude to:
- View workflow execution status
- Trigger workflows on demand
- Debug failed workflow runs
- Analyze workflow configurations

**Setup Steps:**
1. In Claude.ai, go to Settings → Connectors
2. Search for "n8n" or use custom webhook
3. Configure with your n8n instance URL: `https://n8n.insightpulseai.net`
4. Authenticate with n8n API key

**API Key Generation (n8n):**
```bash
# In n8n, go to Settings → API → Create API Key
# Copy the key for Claude connector setup
```

### Gmail Connector (Critical)

Enables:
- Reading invoice emails from vendors
- Accessing BIR confirmation emails
- Processing receipt attachments

**Setup Steps:**
1. Settings → Connectors → Gmail
2. Sign in with finance@insightpulseai.net (or designated inbox)
3. Grant read permissions
4. Configure folder filters for Finance-related emails

**Recommended Filters:**
- Label: `invoices` - Vendor invoices
- Label: `bir` - BIR correspondence
- Label: `receipts` - Expense receipts

### Google Calendar Connector (High)

Enables:
- BIR filing deadline awareness
- Month-end close schedule visibility
- Team availability checking

**Setup Steps:**
1. Settings → Connectors → Google Calendar
2. Sign in with your Google account
3. Select calendars to share:
   - `BIR Tax Calendar`
   - `Finance SSC Operations`
   - `Month-End Close`

### Vercel Connector (Medium)

Enables:
- Deployment status checking
- Build log analysis
- Environment variable awareness

**Setup Steps:**
1. Settings → Connectors → Vercel
2. Authenticate with Vercel account
3. Select projects to monitor

## Security Considerations

### Data Access Scopes

| Connector | Scope | Sensitive Data Warning |
|-----------|-------|----------------------|
| Google Drive | Read | May contain financial documents |
| Gmail | Read | May contain PII, TINs |
| n8n | Read/Execute | Can trigger workflows |
| Calendar | Read | No sensitive data |

### Best Practices

1. **Never share in Claude prompts:**
   - Tax Identification Numbers (TINs)
   - Bank account numbers
   - Employee SSS/PhilHealth IDs
   - Passwords or API keys

2. **Safe to share:**
   - Invoice amounts (without vendor TIN)
   - General financial queries
   - Deadline questions
   - Workflow debugging info

3. **Use Claude for:**
   - Policy questions
   - Process guidance
   - Code assistance
   - Data analysis (aggregated)

## Connector Health Monitoring

### Daily Checks

```bash
# Test n8n connectivity
curl -s https://n8n.insightpulseai.net/api/v1/workflows \
  -H "X-N8N-API-KEY: $N8N_API_KEY" | jq '.data | length'

# Should return number of workflows
```

### Troubleshooting

**n8n Connection Issues:**
1. Verify n8n is running: `docker ps | grep n8n`
2. Check API key validity
3. Verify network connectivity from Claude

**Gmail Access Issues:**
1. Re-authenticate connector
2. Check OAuth token expiry
3. Verify folder permissions

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLAUDE CONNECTORS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │Google Drive  │     │    Gmail     │     │   GitHub     │    │
│  │  (Connected) │     │ (To Connect) │     │  (Connected) │    │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘    │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              │                                  │
│                              ▼                                  │
│                    ┌─────────────────┐                         │
│                    │     Claude      │                         │
│                    │   (AI Agent)    │                         │
│                    └────────┬────────┘                         │
│                              │                                  │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │     n8n      │     │   Calendar   │     │   Vercel     │    │
│  │ (To Connect) │     │ (To Connect) │     │ (To Connect) │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Next Steps

1. **Immediate**: Connect n8n and Gmail
2. **This Week**: Connect Google Calendar
3. **Optional**: Connect Vercel and Figma as needed

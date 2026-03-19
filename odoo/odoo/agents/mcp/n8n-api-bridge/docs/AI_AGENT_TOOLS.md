# AI Agent Tool Support

The n8n MCP Bridge now supports **AI agent tools**, enabling advanced workflow patterns like automated support ticket resolution, knowledge base queries, and intelligent automation.

## Overview

AI agent tools allow Claude to:
1. **Discover** tool nodes in n8n workflows (jiraTool, notionTool, custom tools)
2. **Execute** workflows with AI-generated context and parameters
3. **Integrate** with n8n's LangChain AI agents for sophisticated automation

This unlocks patterns from reference workflows like:
- Automated JIRA support ticket resolution with knowledge base search
- Sentiment analysis for customer satisfaction tracking
- AI-powered document classification and routing

## New MCP Tools

### 1. `n8n_list_workflow_tools`

Discover AI agent tools available in n8n workflows.

**Use Cases:**
- Find all JIRA search tools
- Discover knowledge base query tools
- List custom Odoo/Supabase tools

**Parameters:**
```typescript
{
  workflowId?: string;  // Search specific workflow (omit for all)
  toolType?: string;    // Filter by type (e.g., "jiraTool", "notionTool")
}
```

**Example Usage:**
```
"List all AI agent tools in n8n workflows"
"Find tools in workflow kvlnRew0mAg3Xdri"
"Show me all Notion tools available"
```

**Response Format:**
```json
{
  "total_tools": 2,
  "tools": [
    {
      "tool_id": "workflow-id:node-id",
      "name": "Find Similar Issues",
      "type": "n8n-nodes-base.jiraTool",
      "workflow": "Auto-Resolve Support Tickets",
      "description": "Search JIRA for similar issues",
      "operation": "getAll"
    },
    {
      "tool_id": "workflow-id:node-id",
      "name": "Query Knowledge Base",
      "type": "n8n-nodes-base.notionTool",
      "workflow": "Auto-Resolve Support Tickets",
      "description": "Search Notion for product documentation",
      "operation": "search"
    }
  ]
}
```

---

### 2. `n8n_execute_workflow_with_context`

Execute workflow with AI-generated context, enabling workflows to use LLM parameters.

**Use Cases:**
- Run support automation with AI-analyzed issue description
- Trigger workflows with sentiment analysis results
- Execute knowledge base searches with AI-extracted search terms

**Parameters:**
```typescript
{
  workflowId: string;               // Workflow to execute
  inputData?: Record<string, any>;  // Standard input data
  aiContext?: {
    message?: string;               // AI message/prompt
    variables?: Record<string, any> // AI-generated variables
  }
}
```

**Example Usage:**
```
"Execute workflow kvlnRew0mAg3Xdri with context: {
  aiContext: {
    message: 'Customer is asking about invoice payment methods',
    variables: {
      issue_category: 'billing',
      urgency: 'high',
      search_terms: 'payment methods invoice wire transfer'
    }
  }
}"
```

**Response Format:**
```json
{
  "execution_id": "12345",
  "workflow_id": "kvlnRew0mAg3Xdri",
  "status": "success",
  "started_at": "2026-02-20T20:00:00Z",
  "stopped_at": "2026-02-20T20:00:15Z",
  "outputs": {
    "AI Agent": [{
      "solution_found": true,
      "response": "Wire transfer instructions: ...",
      "short_summary": "Payment method query resolved"
    }]
  }
}
```

---

### 3. `n8n_get_tool_definition`

Get detailed schema and parameters for a specific tool node.

**Use Cases:**
- Understand tool input requirements
- Validate tool availability
- Extract tool schemas for integration

**Parameters:**
```typescript
{
  workflowId: string;  // Workflow containing the tool
  nodeId: string;      // Tool node ID
}
```

**Example Usage:**
```
"Show me the schema for tool workflow-id:node-id"
"Get definition for JIRA search tool in workflow kvlnRew0mAg3Xdri"
```

**Response Format:**
```json
{
  "tool_id": "workflow-id:node-id",
  "name": "Find Similar Issues",
  "type": "n8n-nodes-base.jiraTool",
  "workflow": "Auto-Resolve Support Tickets",
  "description": "Search JIRA for similar issues using JQL",
  "operation": "getAll",
  "schema": {
    "type": "object",
    "properties": {
      "jql": { "type": "string" },
      "limit": { "type": "number" }
    }
  },
  "parameters": {
    "limit": 4,
    "operation": "getAll",
    "toolDescription": "Search JIRA for similar issues"
  }
}
```

---

## Integration with n8n LangChain Nodes

### Supported LangChain Nodes

The AI tool system works with these n8n LangChain nodes:

1. **AI Agent** (`@n8n/n8n-nodes-langchain.agent`)
   - Primary node for AI agent workflows
   - Connects to tool nodes
   - Uses structured output parsing

2. **Text Classifier** (`@n8n/n8n-nodes-langchain.textClassifier`)
   - Classify text into categories
   - Decision routing based on classification

3. **Sentiment Analysis** (`@n8n/n8n-nodes-langchain.sentimentAnalysis`)
   - Analyze customer satisfaction
   - Trigger actions based on sentiment

4. **Basic LLM Chain** (`@n8n/n8n-nodes-langchain.chainLlm`)
   - Simple LLM operations
   - Generate text, summarize, extract info

5. **Tool Nodes** (various)
   - `jiraTool` - JIRA operations
   - `notionTool` - Notion queries
   - `httpRequestTool` - Custom API calls
   - Custom tools for Odoo, Supabase

### Example Workflow Pattern

```
Schedule Trigger
  ↓
Get Unresolved Issues (Odoo/JIRA)
  ↓
Text Classifier (classify issue state)
  ├─ "resolved" → Sentiment Analysis → Close or Escalate
  ├─ "pending" → AI Agent with Tools → Auto-resolve
  └─ "waiting" → LLM Chain → Generate reminder
```

---

## Odoo Integration Examples

### 1. Auto-Resolve Overdue Invoices

**Workflow:** `10_mcp_odoo_invoice_automation.json`

**Nodes:**
- Schedule Trigger (daily)
- Odoo Query (overdue invoices)
- Text Classifier (payment status)
- AI Agent with Odoo Tool (search similar invoices)
- Supabase Tool (query payment history)
- Slack notification

**Claude Usage:**
```
"List tools in the invoice automation workflow"
"Execute invoice automation with context: {
  aiContext: {
    message: 'Customer asking about payment status for INV-2026-001',
    variables: { invoice_id: 'INV-2026-001', customer_id: '123' }
  }
}"
```

---

### 2. Smart Task Assignment

**Workflow:** `11_mcp_odoo_task_triage.json`

**Nodes:**
- Odoo Trigger (new task created)
- Text Classifier (task type: bug, feature, support)
- AI Agent with Odoo Tool (find similar tasks, suggest assignee)
- Slack notification

**Claude Usage:**
```
"Show me Odoo task assignment tools"
"Execute task triage for new task with AI context"
```

---

### 3. Expense Policy Validation

**Workflow:** `12_mcp_odoo_expense_validator.json`

**Nodes:**
- Odoo Trigger (expense report submitted)
- AI Agent with OCR Tool (extract receipt data)
- Supabase Tool (query policy documents)
- Text Classifier (compliant, needs clarification, violation)
- Slack notification + Odoo approval workflow

**Claude Usage:**
```
"List expense validation tools"
"Execute expense validator with receipt data"
```

---

## Best Practices

### 1. Tool Discovery
```
# Start by discovering available tools
"List all AI agent tools in n8n"

# Filter by type
"Show me Odoo tools"
"Find Supabase query tools"

# Check specific workflow
"What tools are in workflow kvlnRew0mAg3Xdri?"
```

### 2. Tool Execution
```
# Always provide AI context for AI-powered workflows
"Execute workflow with context: {
  aiContext: {
    message: 'User query here',
    variables: { extracted: 'data' }
  }
}"

# Check execution results
"Show execution details for execution 12345"
```

### 3. Error Handling
```
# Get tool schema before executing
"Get tool definition for workflow-id:node-id"

# Check execution status
"List recent executions for workflow kvlnRew0mAg3Xdri"

# Retry failed executions
"Retry execution 12345"
```

---

## Architecture

### AI Tool Flow

```
Claude Desktop
    ↓
MCP Bridge (n8n_list_workflow_tools)
    ↓
n8n Public API (/api/v1/workflows)
    ↓
Parse workflow nodes → Filter tool nodes → Return tools
```

### Execution Flow

```
Claude Desktop
    ↓
MCP Bridge (n8n_execute_workflow_with_context)
    ↓
n8n Public API (/api/v1/workflows/{id}/execute)
    ↓
Workflow executes with AI context
    ↓
AI Agent node uses tools (JIRA, Notion, Odoo)
    ↓
Return execution results to Claude
```

---

## Configuration

No additional configuration required. AI tool support is enabled by default when:
- ✅ `N8N_BASE_URL` is set
- ✅ `N8N_API_KEY` is valid
- ✅ Workflows contain tool nodes (jiraTool, notionTool, etc.)

**Write Operations:**
- Set `ALLOW_MUTATIONS=true` to enable `n8n_execute_workflow_with_context`

---

## Troubleshooting

### "No tools found"
- Check workflows contain tool nodes
- Tool nodes must have type ending in "Tool" or `toolDescription` parameter
- Verify API key has access to workflows

### "Execution failed"
- Check workflow is active
- Verify input data matches workflow expectations
- Enable `ALLOW_MUTATIONS=true` for execution

### "Tool not found"
- Use correct tool_id format: `workflow-id:node-id`
- Check workflow exists and is accessible
- Verify node hasn't been deleted/renamed

---

## Next Steps

1. ✅ **Discover Tools**: `"List all AI agent tools"`
2. ✅ **Get Schema**: `"Get tool definition for workflow-id:node-id"`
3. ✅ **Execute**: `"Execute workflow with AI context"`
4. ✅ **Monitor**: `"Show execution details"`

**Ready to build AI-powered automation!** 🚀

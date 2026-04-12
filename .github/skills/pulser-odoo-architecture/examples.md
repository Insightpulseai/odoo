# pulser-odoo-architecture -- Worked Examples

## Example 1: Rejecting a Parallel Approval Engine

**Scenario**: A PR proposes that the Foundry copilot agent auto-approve expense
reports under PHP 5,000 when confidence is high, bypassing the Odoo approval
workflow.

**Boundary check**:
```
Lane: Foundry (AI plane) attempting to own approval authority
Odoo owns: expense.expense approval workflow (account.move, res.users approver)
Anti-pattern: parallel approval engine
Decision: REJECT
```

**Required fix** -- Foundry may surface a recommendation and create a draft
approval activity in Odoo. The Odoo user approves. Foundry never confirms.

```yaml
# ssot/agent-platform/foundry_tool_policy.yaml  -- AFTER fix
tools:
  - name: suggest_expense_approval
    type: function
    approval: required          # human gate mandatory for any approval-adjacent action
    description: "Surfaces an approval recommendation to the Odoo approver. Does not confirm."
    odoo_write: false
    odoo_activity_create: true  # creates an activity, not an approval record
```

**Key decision**: Recommendation is Foundry's job. Approval is Odoo's job. These
are different operations and must never collapse into one.

---

## Example 2: Classifying an Optional Azure Service

**Scenario**: A team member proposes adding Azure Cognitive Search as a default
MVP requirement for Pulser for Odoo to enable semantic search over Odoo records.

**Boundary check**:
```
Proposed: Azure AI Search — mandatory
Current: Not in ssot/azure/runtime_topology.yaml
MVP scope: ipai_odoo_copilot chat + approval-gated actions; no RAG required for MVP
Decision: Downgrade to optional (post-MVP grounding)
```

**SSOT update**:
```yaml
# ssot/azure/runtime_topology.yaml  -- excerpt
optional_services:
  - name: azure-ai-search
    resource_group: rg-ipai-dev
    index: odoo-kb-index
    classification: optional
    required_for_mvp: false
    required_when: "SSOT requires grounding for ipai_odoo_copilot beyond FAQ scope"
    status: not_provisioned
```

**MCP query that supported this decision**:
```
microsoft_docs_search("Azure AI Foundry agent grounding optional knowledge base")
Result: Grounding via AI Search is optional — agents function without it.
        Only required when agent answers must be anchored to a corpus.
        For MVP chat assistants, model instructions alone may suffice.
```

---

## Example 3: Confirming Odoo Truth Boundaries for Tax Intelligence

**Scenario**: Reviewing whether `ipai_tax_intelligence` should compute BIR tax
amounts in Foundry or in Odoo.

**Boundary check**:
```
Lane: Tax computation
Odoo owns: account.tax, account.move, BIR compliance (ipai_tax_intelligence addon)
Foundry role: surface alerts, suggest corrections, draft memos — not compute tax
Decision: Tax engine stays in Odoo. Foundry reads computed amounts, never writes them.
```

**AGENTS.md excerpt consulted**:
```
Odoo truth boundaries include: workflow, approvals, accounting, tax, expense, liquidation.
Foundry may: surface, suggest, draft, explain. Foundry may not: own, compute, confirm.
```

**Resulting tool binding**:
```yaml
# ssot/agent-platform/foundry_tool_policy.yaml
tools:
  - name: get_tax_summary
    type: function
    approval: not_required      # read-only Odoo query
    odoo_write: false
  - name: flag_tax_discrepancy
    type: function
    approval: required          # creates an activity in Odoo — gate required
    odoo_write: false
    odoo_activity_create: true
```

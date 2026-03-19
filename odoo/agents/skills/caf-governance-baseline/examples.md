# Examples — caf-governance-baseline

## Example 1: Initial governance baseline establishment

**Input**: New Azure environment with no governance policies, requesting baseline setup.

**Output**:
- Maturity: Initial (no formal governance)
- Policy audit:
  - Assigned: 0 custom policies
  - Recommended baseline: allowed locations (Southeast Asia), require tags, audit unmanaged disks
  - Gap: 100% — no policies assigned
- Naming compliance: 85% (most resources follow convention, 3 exceptions)
- Tagging: 0% (no tags on any resource)
- Cost management: No budgets, no alerts, 12 Advisor recommendations unreviewed
- Identity: Owner role on 2 accounts, no PIM, no Conditional Access
- Roadmap:
  1. (Week 1) Assign required tags policy in audit mode
  2. (Week 1) Create cost budget with 80%/100% alerts
  3. (Week 2) Assign allowed locations policy in deny mode
  4. (Week 2) Review and remediate Advisor recommendations
  5. (Week 3) Enable PIM for Owner role
  6. (Week 4) Move tagging policy from audit to deny after remediation

## Example 2: Governance maturity upgrade (Defined to Managed)

**Input**: Governance policies documented but manually enforced, requesting automation.

**Output**:
- Maturity: Defined (policies documented, manual enforcement)
- Target: Managed (automated policy enforcement via Azure Policy)
- Policy audit:
  - Documented policies: 8
  - Automated via Azure Policy: 2
  - Gap: 6 policies need Azure Policy definitions
- Actions:
  1. Convert documented naming policy to Azure Policy (built-in: naming convention)
  2. Convert tagging requirement to Azure Policy (built-in: require tag and its value)
  3. Add deployment acceleration: require Bicep for all new resources
  4. Enable policy compliance dashboard in Azure Portal
  5. Add policy compliance check to CI/CD pipeline
- Expected outcome: 100% policy automation, real-time compliance dashboard

## Example 3: Cost governance alert response

**Input**: Cost budget alert triggered at 80% threshold for `rg-ipai-ai-dev`.

**Output**:
- Alert: `rg-ipai-ai-dev` at 80% of $200/mo budget ($160 spent, 20 days remaining)
- Top cost drivers:
  - Azure OpenAI (`oai-ipai-dev`): $95 (59%)
  - Document Intelligence (`docai-ipai-dev`): $35 (22%)
  - Azure AI Search (`srch-ipai-dev`): $20 (12%)
- Recommendations:
  1. Review Azure OpenAI token consumption — check for runaway prompts
  2. Evaluate Document Intelligence tier — Standard may be oversized for current volume
  3. Consider pausing AI Search if not actively used
- Governance action: No deny policy needed — alert and review is sufficient for dev environment

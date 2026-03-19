# Deprecated Tool Exception Request Template

## Tool Information

- **Tool name**: <name>
- **Vendor**: <vendor>
- **Deprecation date**: <date>
- **Current version**: <version>

## Exception Request

### 1. No canonical alternative exists

Describe why no canonical alternative can perform the required operation:
- [ ] Researched Databricks CLI
- [ ] Researched Azure CLI / azd
- [ ] Researched Odoo CLI
- [ ] No alternative found for: <specific operation>

### 2. Only path to business outcome

Describe the business outcome that requires this tool:
- Business requirement: <description>
- Why canonical tools cannot achieve this: <reasoning>

### 3. Time-boxed deadline

- Exception valid until: <ISO date>
- Migration to canonical tool planned for: <ISO date>
- Responsible person: <name>

### 4. Documentation

- Exception documented at: `docs/contracts/DEPRECATED_TOOL_EXCEPTIONS.md`
- Added to deprecation registry: Yes/No

### 5. Migration plan

- Migration plan filed at: <path>
- Target canonical tool: <tool>
- Migration steps:
  1. <step>
  2. <step>
  3. <step>

## Approval

- [ ] All 5 criteria met
- [ ] Reviewed by platform-cli-judge
- [ ] Approved by: <name>
- [ ] Exception added to registry with expiry date

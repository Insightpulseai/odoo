# Checklist — azure-cli-resource-operations

## Pre-execution

- [ ] Confirmed azd cannot accomplish this task
- [ ] Correct az CLI command group identified
- [ ] Resource group and resource name verified
- [ ] Output format specified (--output json/table/tsv)
- [ ] For destructive operations: justification documented

## Execution

- [ ] Command constructed with all required parameters
- [ ] Structured output captured
- [ ] No secrets exposed in command output
- [ ] Error handling for common failure modes

## Post-execution

- [ ] Operation result verified
- [ ] Evidence captured for audit trail
- [ ] If configuration change: post-change verification completed
- [ ] If destructive: rollback path documented

# Skill: Google Workspace Operations (gws)
# Domain: Automation & Collaboration
# Tool: ./bin/gws

## Description
This skill provides the Pulser Assistant with direct access to Google Workspace via the **gws CLI**. It covers Drive, Gmail, Calendar, and Sheets operations using structured JSON output.

## Instructions
1. **Always use the structured output**: `gws` returns JSON. Parse it for precise data extraction.
2. **Handle Scopes**: If a command fails with 403 (unauthorized), check if the required scope is enabled.
3. **Helper Commands**: Prefer commands prefixed with `+` for common workflows (e.g., `+send`, `+agenda`).
4. **Dry Runs**: Use `--dry-run` to preview large mutations.

## Common Recipes

### Gmail
- **Send Email**: `./bin/gws gmail +send --to "recipient@example.com" --subject "Title" --body "Content"`
- **List Messages**: `./bin/gws gmail users messages list --params '{"maxResults": 5}'`
- **Triage Inbox**: `./bin/gws gmail +triage`

### Drive
- **List Files**: `./bin/gws drive files list --params '{"pageSize": 10}'`
- **Upload File**: `./bin/gws drive +upload ./path/to/file.pdf --name "Report Name"`
- **Get File Info**: `./bin/gws drive files get --params '{"fileId": "ID"}'`

### Calendar
- **View Agenda**: `./bin/gws calendar +agenda`
- **Insert Event**: `./bin/gws calendar +insert --summary "Meeting" --start "2026-04-18T10:00:00Z" --end "2026-04-18T11:00:00Z"`

### Sheets
- **Append Row**: `./bin/gws sheets +append --spreadsheet "ID" --values "Col1,Col2,Col3"`
- **Read Range**: `./bin/gws sheets +read --spreadsheet "ID" --range "Sheet1!A1:B10"`

## Error Handling
- **Exit Code 1**: API Error (Check params/quota).
- **Exit Code 2**: Auth Error (Run `gws auth login`).
- **Exit Code 3**: Validation Error (Check flags).

---
*Reference: platform/ssot/google-workspace/gws-cli-adoption.yaml*

# Figma Dev Mode Access Implementation Report

**Date:** 2026-01-24T21:04:00Z
**Scope:** figma-dev-mode-access
**Branch:** claude/figma-dev-mode-access-TTldM

## Summary

Implemented Figma Dev Mode access configuration and verification tooling for the IPAI platform, enabling developers to properly integrate with Figma's developer-facing "inspect + specs + code snippets" surface.

## Files Changed

### New Files

| File | Purpose |
|------|---------|
| `figma.config.json` | Root-level Code Connect configuration for component mapping |
| `scripts/figma/verify_dev_mode_access.sh` | Verification script for Dev Mode access prerequisites |
| `scripts/figma/figma_export_variables.sh` | Variables export script (Enterprise API + fallback) |

### Modified Files

| File | Change |
|------|--------|
| `.env.example` | Added `FIGMA_ACCESS_TOKEN` and `FIGMA_FILE_KEY` environment variables |
| `CLAUDE.md` | Added Figma Dev Mode Access section with seat requirements and setup commands |

## Key Decisions

### 1. Seat Type Documentation

Documented the critical distinction between seat types:
- **Dev/Full seats**: Include Dev Mode access
- **Collab/View-only seats**: Do NOT include Dev Mode

This addresses a common confusion where developers with view-only access cannot use Dev Mode features.

### 2. Variables API Graceful Degradation

The `figma_export_variables.sh` script handles Enterprise-only API limitations:
- Attempts Variables REST API export
- On 403 (plan limitation), creates placeholder file with fallback recommendations
- Suggests Code Connect or Figma Tokens Studio as alternatives

### 3. Code Connect as Primary Bridge

Positioned Code Connect CLI as the primary design-to-code bridge:
- Root-level `figma.config.json` for project-wide mappings
- Component paths include `apps/*/src/components/**/*` and `packages/*/src/components/**/*`
- Import path aliases configured for control-room, web, and design-tokens packages

## Verification Checklist

- [x] `.env.example` contains `FIGMA_ACCESS_TOKEN` placeholder
- [x] `.env.example` contains `FIGMA_FILE_KEY` placeholder
- [x] `figma.config.json` is valid JSON with Code Connect schema
- [x] `verify_dev_mode_access.sh` is executable and has proper error handling
- [x] `figma_export_variables.sh` handles Enterprise API limitations gracefully
- [x] `CLAUDE.md` documents seat requirements and setup commands

## Evidence Files

```
docs/evidence/20260124-2104/figma-dev-mode-access/
├── implementation_report.md (this file)
└── git_state.txt
```

## Usage

```bash
# Set environment
export FIGMA_ACCESS_TOKEN=figd_xxxxxxxxxxxxx
export FIGMA_FILE_KEY=your_file_key_here

# Verify access
./scripts/figma/verify_dev_mode_access.sh

# Install Code Connect
npm install --global @figma/code-connect@latest

# Publish mappings
npx figma connect publish --token="$FIGMA_ACCESS_TOKEN"

# Export variables (Enterprise)
./scripts/figma/figma_export_variables.sh
```

## References

- [Figma Dev Mode Documentation](https://help.figma.com/hc/en-us/articles/35498519152663)
- [Code Connect Quickstart](https://developers.figma.com/docs/code-connect/quickstart-guide/)
- [Variables REST API](https://developers.figma.com/docs/rest-api/variables-endpoints/)
- [Figma MCP Server](https://www.figma.com/blog/introducing-figma-mcp-server/)

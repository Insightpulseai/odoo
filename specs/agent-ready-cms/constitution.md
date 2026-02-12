# Constitution — Agent-Ready CMS

## Non-Negotiables

These invariants must never be violated:

### 1. Agent Contract Structure
- Every repo MUST have `CLAUDE.md` at root
- Every repo MUST have `docs/README.md`
- Numbered folders (01-09) MUST have README.md stubs

### 2. Documentation Taxonomy
- Folder structure follows 01-Discovery → 09-Analytics → 99-Archive pattern
- No additional numbered folders without explicit approval
- Each folder serves a single, clear purpose

### 3. Output Contract
- All significant changes produce: apply/test/deploy/validate commands
- Rollback strategy required for deployment changes
- Evidence-based claims (no speculation)

### 4. Animation Accessibility
- All animations MUST respect `prefers-reduced-motion`
- No autoplay audio without user consent
- Focus states visible for all interactive elements

### 5. Odoo Theme Module Standards
- LGPL-3 license in `__manifest__.py`
- Odoo 19 compatibility
- OCA-compatible structure (if applicable)
- Assets loaded via manifest `assets` key (not legacy `xml`)

### 6. Template Idempotency
- All generator scripts MUST be idempotent
- Re-running scaffold on existing repo = no harmful side effects
- Existing content preserved unless explicitly overwritten

### 7. CI Guard Enforcement
- Agent docs guard workflow required in org repos
- PRs modifying docs structure trigger validation
- Failing guard = PR blocked

## Success Criteria

A repo is "agent-ready" when:

1. ✅ `CLAUDE.md` exists at root with valid output contract
2. ✅ `docs/README.md` exists with folder index
3. ✅ All 11 numbered folders have README.md
4. ✅ CI guard passes without warnings
5. ✅ Agent can locate context within 3 file reads

## Trade-offs Accepted

- **Minimal over comprehensive**: READMEs start as stubs; content added as needed
- **Convention over configuration**: Fixed folder structure, no customization
- **Automation over manual**: PRs generated programmatically for org-wide rollout

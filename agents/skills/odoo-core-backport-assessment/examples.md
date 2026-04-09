# Examples — odoo-core-backport-assessment

## Example 1: Generic fix available in OCB

**Input**: `account.move` sequence generation fails on fiscal year rollover

**Output**:
- Issue: Sequence generation for account.move resets incorrectly at fiscal year boundary
- Upstream status: Fixed in Odoo 18.0 (commit abc123), backport to 17.0 not needed
- OCB status: Available in OCB 18.0 branch (commit def456)
- Change scope: generic (affects all Odoo users)
- Recommendation: Apply OCB backport
- Risk: low
- Evidence: OCB 18.0 commit def456, upstream 18.0 commit abc123

## Example 2: Project-specific override needed

**Input**: `res.partner` needs custom TIN validation for Philippine BIR format

**Output**:
- Issue: Partner TIN field needs PH-specific format validation (XXX-XXX-XXX-XXX)
- Upstream status: not applicable (country-specific)
- OCB status: not applicable (project-specific requirement)
- Change scope: project-specific (Philippine BIR compliance)
- Recommendation: Create `ipai_bir_tax_compliance` override using `_inherit = 'res.partner'`
- Risk: low
- Evidence: BIR TIN format specification, existing ipai_bir_tax_compliance module

## Example 3: Wait for upstream

**Input**: `mail.thread` performance regression in large recordsets

**Output**:
- Issue: mail.thread tracking writes cause N+1 queries on large recordsets
- Upstream status: PR #45678 merged into 18.0, scheduled for next point release
- OCB status: not yet backported (waiting for upstream release)
- Change scope: generic
- Recommendation: Wait for upstream point release (estimated 2 weeks). If urgent, apply OCB PR when available.
- Risk: medium (performance issue, not data corruption)

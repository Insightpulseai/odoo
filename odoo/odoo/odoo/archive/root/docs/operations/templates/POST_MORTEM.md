# Incident: <Brief Description>

**Date**: <timestamp_utc>
**Severity**: Critical | High | Medium | Low
**Impact**: <User-facing impact>
**Resolution Time**: <Time to fix>

## Timeline

- **HH:MM UTC**: Incident detected
- **HH:MM UTC**: Evidence collected (incident_snapshot.sh)
- **HH:MM UTC**: Root cause identified
- **HH:MM UTC**: Fix applied
- **HH:MM UTC**: Verification passed
- **HH:MM UTC**: Incident resolved

## Root Cause

<Definitive module/file/line with explanation>

## Error Envelope

```json
<Paste error_envelope.json>
```

## Fix Applied

<Describe minimal fix>

## Verification

- [ ] curl /web/login returns 200
- [ ] No errors in logs for 10 minutes
- [ ] Visual parity check passes (if UI change)
- [ ] Affected functionality tested manually

## Prevention

<How to prevent recurrence>

## Lessons Learned

<What we learned>

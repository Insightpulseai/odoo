# Allowed Operations — Template

## Read-only (always safe)

- `<tool> list ...`
- `<tool> show ...`
- `<tool> status ...`
- `<tool> logs ...`

## Controlled write (requires verification after)

- `<tool> create ...`
- `<tool> update ...`
- `<tool> deploy ...`

## Blocked by default

- `<tool> delete ...` — requires explicit allowlisting
- `<tool> destroy ...` — requires explicit allowlisting
- `<tool> exec/ssh/console` — interactive, not skill-compatible
- Any command that writes secrets to files

## Admin/bootstrap (separate skill)

- `<tool> login`
- `<tool> auth setup`
- `<tool> init`

# UX Guidelines (Best Practices)

## P0 — Must Have (CRITICAL)

- **Clear hierarchy** — one primary action per screen; visual weight guides the eye
- **Immediate feedback** — every user action gets a visible response (loading, success, error)
- **Actionable errors** — error messages explain what went wrong AND how to fix it, placed near the field

## P1 — Should Have (HIGH)

- **Consistent spacing and alignment** — use the spacing scale; never eyeball padding
- **Predictable navigation** — users should always know where they are and how to go back
- **Content-first empty states** — guide users to their first action; don't show blank pages
- **Touch target size** — minimum 44x44px for all interactive elements

## P2 — Nice to Have (MEDIUM)

- **Animation timing** — 150-300ms for micro-interactions; never > 500ms
- **Transform performance** — animate `transform` and `opacity`, not `width` or `height`
- **Skeleton loading** — show content shape during async operations; avoid blank flash
- **Reduced motion** — respect `prefers-reduced-motion` media query

## Anti-Patterns (Never Do)

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Mystery-meat navigation | Users can't identify links or actions | Use clear labels, not just icons |
| Placeholder-only labels | Labels disappear on focus; users forget context | Always use persistent `<label>` elements |
| Non-dismissable modals | Users feel trapped | Always provide close/escape mechanism |
| Infinite scroll without position | Users can't bookmark or return to position | Add pagination or "back to top" |
| Auto-playing media | Disrupts user focus; accessibility violation | Let user opt-in to play |
| Color-only indicators | Colorblind users miss the signal | Add text, icon, or pattern |

## Tips for Better Results

Search UX guidance using:
```bash
python3 skills/ui-ux-pro-max/scripts/search.py "animation accessibility z-index" --domain ux
```

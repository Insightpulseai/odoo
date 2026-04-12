# Formatting QA Sub-Skill

> Lane-specific format and layout validation for Office artifacts.

## Role

Runs format-level checks on generated artifacts before the publishability
review gate. Each studio lane has specific checks.

## Checks by lane

### PowerPoint
- Slide bounds: no text or visual overflow
- Font consistency: single font family, consistent sizes
- Visual hierarchy: title > subtitle > body > caption
- Color palette: restrained, brand-safe
- Chart readability: labels visible, axes labeled

### Word
- Pagination: no orphan headers, clean page breaks
- Heading hierarchy: H1 > H2 > H3 consistent throughout
- Margins and spacing: professional document standards
- Table formatting: no cell overflow, consistent column widths
- Header/footer: document title, page numbers, date

### Excel
- Cell overflow: no truncated content
- Column widths: appropriate for content
- Print area: defined and clean
- Conditional formatting: RAG indicators render correctly
- Chart styling: consistent with workbook theme

## Output

- Per-check pass/fail with specific fix instructions
- Overall format score (0–100%)
- Auto-fix suggestions where possible

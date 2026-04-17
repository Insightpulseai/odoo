# Content guidelines

Follow these guidelines for all documentation, UI text, and inline comments. Adapted from Odoo 18 content standards.

## Language

- Write in **American English**.
- Use **present tense** and **imperative mood**.
- Be concise. Remove filler words.
- No marketing language, superlatives, or promotional tone.

## Titles and headings

- Use **sentence case** (capitalize only the first word and proper nouns).
- Keep titles concise and descriptive.
- Do not start with "How to" or "Guide to".
- Do not use pronouns in titles.

| Do | Do not |
|----|--------|
| Configure SMTP settings | How to configure your SMTP settings |
| Install a custom module | A guide to installing modules |
| Set up the devcontainer | Setting up your development container |

## Structure

### Lists

- Use **numbered lists** for sequential steps.
- Use **bulleted lists** for non-sequential items.
- Start each list item with a capital letter.
- End list items with a period if they are complete sentences.

### Code blocks

Use fenced code blocks for all actionable steps:

````markdown
```bash
docker compose up -d
```
````

Specify the language for syntax highlighting (`bash`, `python`, `sql`, `yaml`, `json`).

### Tables

Use tables for structured comparisons, configuration values, and reference data. Align columns for readability in the source.

### Admonitions

Use MkDocs Material admonitions for callouts:

```markdown
!!! note "Optional title"
    Content here.

!!! warning "Optional title"
    Content here.

!!! danger "Optional title"
    Content here.

!!! tip "Optional title"
    Content here.
```

| Type | Use for |
|------|---------|
| `note` | Supplementary information |
| `tip` | Helpful suggestions |
| `warning` | Potential pitfalls or deprecated items |
| `danger` | Critical rules that must not be violated |

## Tone

- Direct and evidence-based.
- Write for practitioners, not executives.
- State facts. Do not hedge with "might", "could", "should consider".
- If something is required, say "must" or use imperative mood.

| Do | Do not |
|----|--------|
| Run the health check before deploying. | You should consider running the health check. |
| This module requires PostgreSQL 16. | This module might work best with PostgreSQL 16. |
| Never hardcode secrets. | It's generally a good idea to avoid hardcoding secrets. |

## Images

When documentation requires screenshots or diagrams:

- Width: **768-933px**.
- No annotations or markups on screenshots.
- Use compressed PNGs.
- Write descriptive ALT text for every image.
- Store images in `docs-site/docs/assets/images/`.

```markdown
![Odoo module installation screen](../assets/images/module-install.png)
```

## Diagrams

Prefer Mermaid diagrams over static images for architecture and flow diagrams. Mermaid renders in MkDocs Material without additional plugins.

```markdown
​```mermaid
graph LR
    A[Source] --> B[Target]
​```
```

# Docs Site Repo Template

Scaffold for a documentation site (MkDocs Material or similar).

## Expected Structure

```text
<docs-site-name>/
├── .github/
│   └── workflows/
├── docs/
│   ├── index.md
│   ├── getting-started/
│   └── reference/
├── overrides/      # Theme overrides
├── mkdocs.yml
├── requirements.txt
├── CLAUDE.md
└── README.md
```

## Conventions

- Built with MkDocs Material.
- Deployed to GitHub Pages or Azure Static Web Apps.
- Navigation defined in `mkdocs.yml`, not generated.
- No runtime secrets required.

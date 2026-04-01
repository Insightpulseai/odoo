# Library Repo Template

Scaffold for a shared library or package repository.

## Expected Structure

```text
<library-name>/
├── .github/
│   └── workflows/
├── src/            # Library source code
├── tests/          # Unit and integration tests
├── docs/           # API documentation
├── CLAUDE.md
├── README.md
├── pyproject.toml  # or package.json
└── LICENSE
```

## Conventions

- Published to internal registry (Azure Artifacts or npm).
- Semantic versioning enforced.
- CI runs lint + test on every PR.
- No runtime secrets -- libraries must be stateless.

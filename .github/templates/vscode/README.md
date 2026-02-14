# VS Code + EditorConfig Template

**Org-wide baseline for consistent development environments across all repos.**

## What's Included

- `extensions.json` - Core VS Code extensions (Python/Ruff, Docker, YAML, Prettier, etc.)
- `settings.json` - Deterministic editor settings (formatters, linting, file handling)
- `.editorconfig` - Cross-editor baseline (works in Vim, Emacs, IntelliJ, etc.)
- `.prettierrc.json` - JS/TS/YAML/MD formatting rules
- `pyproject.toml` - Python formatting (Ruff configuration)

## How to Use

### For New Repos

```bash
# Copy all template files to repo root
cp -r .github/templates/vscode/.editorconfig .
cp -r .github/templates/vscode/.prettierrc.json .
cp -r .github/templates/vscode/pyproject.toml .  # If Python repo

# Merge VS Code configs (keep repo-specific extensions)
mkdir -p .vscode
# Manually merge extensions.json and settings.json
```

### For Existing Repos

1. **Check current setup**:
   - Does `.editorconfig` exist? If not, copy from template
   - Does `.vscode/extensions.json` list Black? Remove it, add Ruff
   - Does `.vscode/settings.json` use Ruff as Python formatter?

2. **Update DevContainer** (if exists):
   - Remove `ms-python.black-formatter` from extensions
   - Add `charliermarsh.ruff` to extensions
   - Set `"[python]": { "editor.defaultFormatter": "charliermarsh.ruff" }`

3. **Verify**:
   ```bash
   # Check Black removed
   ! grep -q "black-formatter" .vscode/extensions.json
   ! grep -q "black-formatter" .devcontainer/devcontainer.json

   # Check Ruff present
   grep -q "charliermarsh.ruff" .vscode/extensions.json
   ```

## Enforcement

CI workflow `.github/workflows/dev-env-gate.yml` enforces:
- `.editorconfig` exists
- Black not present in DevContainer
- Ruff is primary Python formatter
- Docker Compose validates (if present)

## Customization

**Repo-Specific Extensions**:
- Keep your repo-specific extensions (e.g., `odoo.odoo-language-server` for Odoo repos)
- Add them to `recommendations` array in `.vscode/extensions.json`

**Repo-Specific Settings**:
- Keep Python analysis paths (e.g., Odoo addons paths)
- Merge template settings with existing settings

## Standards

| Standard | Value |
|----------|-------|
| **Python Formatter** | Ruff (charliermarsh.ruff) |
| **JS/TS Formatter** | Prettier (esbenp.prettier-vscode) |
| **YAML Formatter** | redhat.vscode-yaml |
| **Python Indent** | 4 spaces |
| **JS/TS/YAML Indent** | 2 spaces |
| **Line Endings** | LF (Unix) |
| **Final Newline** | Required |

## Migration from Black

If your repo currently uses Black:

1. Remove `ms-python.black-formatter` from all configs
2. Add `charliermarsh.ruff` to extensions
3. Update `pyproject.toml` to use Ruff (see template)
4. Update `.vscode/settings.json` and `.devcontainer/devcontainer.json` to use Ruff
5. Run `ruff format .` to reformat (compatible with Black)

Ruff is 10-100x faster than Black and actively maintained.

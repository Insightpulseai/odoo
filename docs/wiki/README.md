# Wiki Pages Source

This directory contains the source files for the GitHub wiki at:
https://github.com/jgtolentino/odoo-ce/wiki

## Files

| File | Wiki Page Name |
|------|----------------|
| `Home.md` | Home |
| `Releases-and-Changelog.md` | Releases & Changelog |
| `Modules-and-Features.md` | Modules & Features |

## Syncing to Wiki

### Option 1: Manual Copy

Copy the content of each `.md` file to the corresponding wiki page via the GitHub UI:
1. Go to https://github.com/jgtolentino/odoo-ce/wiki
2. Click "Edit" on each page
3. Paste the content from the corresponding file

### Option 2: Clone Wiki Repo

```bash
git clone git@github.com:jgtolentino/odoo-ce.wiki.git
cd odoo-ce.wiki

# Copy files (adjust filenames as needed)
cp ../odoo-ce/docs/wiki/Home.md ./Home.md
cp ../odoo-ce/docs/wiki/Releases-and-Changelog.md ./Releases-&-Changelog.md
cp ../odoo-ce/docs/wiki/Modules-and-Features.md ./Modules-&-Features.md

git add -A
git commit -m "docs(wiki): update wiki pages from docs/wiki/"
git push
```

### Option 3: GitHub Actions (Future)

A workflow could be added to auto-sync `docs/wiki/*.md` to the wiki repo on push to main.

## Naming Convention

GitHub wiki pages use the filename (minus `.md`) as the page title. Special characters like `&` in page names work but require URL encoding in links.

- `Home.md` → wiki home page
- `Releases-and-Changelog.md` → "Releases and Changelog" page
- Use hyphens instead of spaces in filenames

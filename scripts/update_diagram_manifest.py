#!/usr/bin/env python3
"""
Update Diagram Manifest

Scans docs/diagrams/architecture for .drawio files and updates manifest.json.
Can be run manually or as a post-generation hook from MCP.

Usage:
    python scripts/update_diagram_manifest.py
    python scripts/update_diagram_manifest.py --add-diagram fin-workspace-overview.drawio --provider digitalocean
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path


DIAGRAMS_DIR = Path(__file__).parent.parent / 'docs' / 'diagrams' / 'architecture'
MANIFEST_PATH = DIAGRAMS_DIR / 'manifest.json'


def load_manifest():
    """Load existing manifest or create default structure."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f)

    return {
        "version": "1.0.0",
        "description": "Architecture diagrams manifest for fin-workspace / mybrick platform",
        "lastUpdated": datetime.now().isoformat(),
        "diagrams": [],
        "providers": {
            "azure": {"iconLibrary": "https://github.com/jgraph/drawio-libs/tree/master/azure"},
            "digitalocean": {"iconLibrary": "custom"},
            "kubernetes": {"iconLibrary": "https://github.com/jgraph/drawio-libs/tree/master/kubernetes"},
            "aws": {"iconLibrary": "https://github.com/jgraph/drawio-libs/tree/master/aws"},
            "gcp": {"iconLibrary": "https://github.com/jgraph/drawio-libs/tree/master/gcp"}
        },
        "githubIntegration": {
            "org": "jgtolentino",
            "repo": "odoo-ce",
            "branch": "main",
            "basePath": "docs/diagrams/architecture"
        }
    }


def save_manifest(manifest):
    """Save manifest to file."""
    manifest['lastUpdated'] = datetime.now().isoformat()

    with open(MANIFEST_PATH, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Updated manifest at {MANIFEST_PATH}")


def scan_diagrams():
    """Scan directory for .drawio files."""
    diagrams = []

    for drawio_file in DIAGRAMS_DIR.glob('*.drawio'):
        diagram_id = drawio_file.stem

        # Look for corresponding image
        image_file = None
        for ext in ['.png', '.svg', '.jpg']:
            preview = DIAGRAMS_DIR / 'previews' / f'{diagram_id}{ext}'
            if preview.exists():
                image_file = f'previews/{diagram_id}{ext}'
                break

        diagrams.append({
            'id': diagram_id,
            'file_drawio': drawio_file.name,
            'file_image': image_file,
            'last_modified': datetime.fromtimestamp(drawio_file.stat().st_mtime).isoformat()
        })

    return diagrams


def update_manifest():
    """Update manifest with scanned diagrams."""
    manifest = load_manifest()
    scanned = scan_diagrams()

    # Build lookup of existing diagrams
    existing = {d['id']: d for d in manifest['diagrams']}

    # Update or add diagrams
    for scanned_diag in scanned:
        diag_id = scanned_diag['id']

        if diag_id in existing:
            # Update file paths and timestamps
            existing[diag_id]['file_drawio'] = scanned_diag['file_drawio']
            existing[diag_id]['file_image'] = scanned_diag['file_image']
            existing[diag_id]['last_updated'] = scanned_diag['last_modified']
        else:
            # Add new diagram with defaults
            manifest['diagrams'].append({
                'id': diag_id,
                'title': diag_id.replace('-', ' ').replace('_', ' ').title(),
                'description': f'Auto-discovered diagram: {diag_id}',
                'providers': ['generic'],
                'source': 'auto-scan',
                'file_drawio': scanned_diag['file_drawio'],
                'file_image': scanned_diag['file_image'],
                'last_updated': scanned_diag['last_modified'],
                'tags': [],
                'components': {'count': 0, 'types': []}
            })

    # Remove diagrams that no longer exist
    scanned_ids = {d['id'] for d in scanned}
    manifest['diagrams'] = [d for d in manifest['diagrams'] if d['id'] in scanned_ids]

    save_manifest(manifest)
    return manifest


def add_diagram(filename: str, provider: str = 'generic', title: str = None,
                description: str = None, tags: list = None):
    """Add or update a specific diagram in the manifest."""
    manifest = load_manifest()

    diagram_id = Path(filename).stem

    # Check if diagram exists
    existing_idx = None
    for i, d in enumerate(manifest['diagrams']):
        if d['id'] == diagram_id:
            existing_idx = i
            break

    diagram_entry = {
        'id': diagram_id,
        'title': title or diagram_id.replace('-', ' ').replace('_', ' ').title(),
        'description': description or f'Architecture diagram: {diagram_id}',
        'providers': [provider] if isinstance(provider, str) else provider,
        'source': 'manual',
        'file_drawio': filename,
        'file_image': f'previews/{diagram_id}.png',
        'last_updated': datetime.now().isoformat(),
        'tags': tags or [],
        'components': {'count': 0, 'types': []}
    }

    if existing_idx is not None:
        manifest['diagrams'][existing_idx] = diagram_entry
        print(f"Updated diagram: {diagram_id}")
    else:
        manifest['diagrams'].append(diagram_entry)
        print(f"Added diagram: {diagram_id}")

    save_manifest(manifest)
    return manifest


def generate_readme():
    """Generate README for the diagrams directory."""
    manifest = load_manifest()

    readme_content = f"""# Architecture Diagrams

This directory contains cloud architecture diagrams for the fin-workspace / mybrick platform.

## Diagrams

| Name | Providers | Updated | Draw.io |
|------|-----------|---------|---------|
"""

    github = manifest.get('githubIntegration', {})
    base_url = f"https://app.diagrams.net/?mode=github#H{github.get('org', 'jgtolentino')}/{github.get('repo', 'odoo-ce')}/{github.get('branch', 'main')}/{github.get('basePath', 'docs/diagrams/architecture')}"

    for diag in manifest['diagrams']:
        providers = ', '.join(diag.get('providers', ['generic']))
        updated = diag.get('last_updated', 'N/A')[:10]
        drawio_link = f"[Open]({base_url}/{diag['file_drawio']})"
        readme_content += f"| {diag['title']} | {providers} | {updated} | {drawio_link} |\n"

    readme_content += """
## Usage

### Viewing Diagrams

1. Click "Open" in the table above to edit in draw.io with GitHub integration
2. Or open `.drawio` files directly in the draw.io desktop app

### Adding New Diagrams

```bash
# Add via script
python scripts/update_diagram_manifest.py --add-diagram my-diagram.drawio --provider azure

# Or use MCP skill
# "Create an architecture diagram for the Kubernetes cluster"
```

### Generating from Infrastructure

```bash
# Azure Resource Graph export
az graph query -q "resources | project name, type, location" -o json > infra_snapshots/azure/topology.json

# DigitalOcean export
doctl compute droplet list -o json > infra_snapshots/digitalocean/droplets.json

# Then generate diagram via MCP
```

## Directory Structure

```
architecture/
├── manifest.json           # Diagram metadata
├── README.md              # This file
├── *.drawio               # Source diagrams
└── previews/              # PNG/SVG exports
    └── *.png
```

## Icon Libraries

- [Azure Icons](https://github.com/jgraph/drawio-libs/tree/master/azure)
- [Kubernetes Icons](https://github.com/jgraph/drawio-libs/tree/master/kubernetes)
- [AWS Icons](https://github.com/jgraph/drawio-libs/tree/master/aws)
- [GCP Icons](https://github.com/jgraph/drawio-libs/tree/master/gcp)

## References

- [diagram-ai-generator](https://github.com/carlosmgv02/diagram-ai-generator)
- [draw.io Azure Diagrams](https://www.drawio.com/blog/azure-diagrams)
- [draw.io GitHub Integration](https://github.com/jgraph/drawio-github)
"""

    readme_path = DIAGRAMS_DIR / 'README.md'
    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print(f"Generated README at {readme_path}")


def main():
    parser = argparse.ArgumentParser(description='Update architecture diagrams manifest')
    parser.add_argument('--scan', action='store_true', help='Scan and update manifest')
    parser.add_argument('--add-diagram', type=str, help='Add/update a specific diagram')
    parser.add_argument('--provider', type=str, default='generic', help='Provider for the diagram')
    parser.add_argument('--title', type=str, help='Title for the diagram')
    parser.add_argument('--description', type=str, help='Description for the diagram')
    parser.add_argument('--tags', type=str, help='Comma-separated tags')
    parser.add_argument('--readme', action='store_true', help='Generate README')

    args = parser.parse_args()

    # Ensure directory exists
    DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)
    (DIAGRAMS_DIR / 'previews').mkdir(exist_ok=True)

    if args.add_diagram:
        tags = args.tags.split(',') if args.tags else []
        add_diagram(args.add_diagram, args.provider, args.title, args.description, tags)
    elif args.scan or not any([args.add_diagram, args.readme]):
        update_manifest()

    if args.readme:
        generate_readme()


if __name__ == '__main__':
    main()

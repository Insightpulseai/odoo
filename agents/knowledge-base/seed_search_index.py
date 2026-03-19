#!/usr/bin/env python3
"""
Seed Azure AI Search index with knowledge base content.

Prerequisites:
  - Azure CLI authenticated (az login)
  - Search service srch-ipai-dev in rg-ipai-ai-dev

Usage:
  python3 seed_search_index.py
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

SEARCH_SERVICE = "srch-ipai-dev"
SEARCH_RG = "rg-ipai-ai-dev"
SEARCH_URL = f"https://{SEARCH_SERVICE}.search.windows.net"
INDEX_NAME = "ipai-knowledge-base"
API_VERSION = "2024-07-01"
KB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_FILE = os.path.join(KB_DIR, "index-schema.json")
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_admin_key():
    """Get admin key from Azure CLI."""
    result = subprocess.run(
        [
            "az", "search", "admin-key", "show",
            "--service-name", SEARCH_SERVICE,
            "--resource-group", SEARCH_RG,
            "--query", "primaryKey", "-o", "tsv"
        ],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: Failed to get admin key: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def api_request(key, method, path, body=None):
    """Make a request to the Azure AI Search REST API."""
    url = f"{SEARCH_URL}/{path}?api-version={API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": key,
    }
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8")) if resp.read else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8") if e.fp else ""
        return e.code, body_text


def check_index_exists(key):
    """Check if the index already exists."""
    url = f"{SEARCH_URL}/indexes/{INDEX_NAME}?api-version={API_VERSION}"
    req = urllib.request.Request(url, headers={"api-key": key}, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def create_index(key):
    """Create the search index from schema file."""
    with open(SCHEMA_FILE) as f:
        schema = json.load(f)

    url = f"{SEARCH_URL}/indexes/{INDEX_NAME}?api-version={API_VERSION}"
    data = json.dumps(schema).encode("utf-8")
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json", "api-key": key},
        method="PUT"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Index '{INDEX_NAME}' created successfully (HTTP {resp.status})")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"ERROR creating index (HTTP {e.code}): {body}", file=sys.stderr)
        return False


def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    meta = {}
    if match:
        fm = match.group(1)
        for line in fm.split('\n'):
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip().strip('"')] = v.strip().strip('"')
        content = content[match.end():]
    return meta, content


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Split text into overlapping chunks at paragraph boundaries."""
    paragraphs = re.split(r'\n\n+', text)
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # Keep overlap from the end of the current chunk
            if overlap > 0:
                current_chunk = current_chunk[-overlap:] + "\n\n" + para
            else:
                current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def collect_documents():
    """Walk the knowledge base directory and chunk all markdown files."""
    docs = []
    file_count = 0

    for root, dirs, files in os.walk(KB_DIR):
        # Skip hidden dirs and the script itself
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath) as fh:
                raw = fh.read()

            file_count += 1
            meta, content = parse_frontmatter(raw)
            category = os.path.basename(root)
            title = meta.get('title', fname.replace('.md', '').replace('-', ' ').title())
            kb_scope = meta.get('kb_scope', category)
            group_ids_str = meta.get('group_ids', '')
            # Parse group_ids from YAML-like list
            group_ids = re.findall(r'"([^"]+)"', group_ids_str) if group_ids_str else []
            last_updated = meta.get('last_updated', datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
            if len(last_updated) == 10:  # date only
                last_updated += "T00:00:00Z"

            source_rel = os.path.relpath(filepath, KB_DIR)
            chunks = chunk_text(content)

            for idx, chunk in enumerate(chunks):
                doc_id = hashlib.md5(f"{source_rel}:{idx}".encode()).hexdigest()
                doc = {
                    "@search.action": "upload",
                    "id": doc_id,
                    "title": title,
                    "content": chunk,
                    "kb_scope": kb_scope,
                    "group_ids": group_ids if group_ids else ["public"],
                    "source_file": source_rel,
                    "chunk_index": idx,
                    "last_updated": last_updated,
                }
                docs.append(doc)

    return docs, file_count


def upload_documents(key, docs):
    """Upload documents to the search index in batches."""
    BATCH_SIZE = 100
    total = len(docs)
    uploaded = 0

    for i in range(0, total, BATCH_SIZE):
        batch = docs[i:i + BATCH_SIZE]
        payload = json.dumps({"value": batch}).encode("utf-8")
        url = f"{SEARCH_URL}/indexes/{INDEX_NAME}/docs/index?api-version={API_VERSION}"
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json", "api-key": key},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                succeeded = sum(1 for r in result.get("value", []) if r.get("status"))
                failed = sum(1 for r in result.get("value", []) if not r.get("status"))
                uploaded += succeeded
                if failed > 0:
                    print(f"  Batch {i // BATCH_SIZE + 1}: {succeeded} succeeded, {failed} failed")
                else:
                    print(f"  Batch {i // BATCH_SIZE + 1}: {succeeded}/{len(batch)} uploaded")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8")
            print(f"  ERROR uploading batch {i // BATCH_SIZE + 1} (HTTP {e.code}): {body}", file=sys.stderr)

    return uploaded


def get_doc_count(key):
    """Get the document count from the index."""
    url = f"{SEARCH_URL}/indexes/{INDEX_NAME}/docs/$count?api-version={API_VERSION}"
    req = urllib.request.Request(url, headers={"api-key": key}, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            return int(resp.read().decode("utf-8"))
    except urllib.error.HTTPError:
        return -1


def main():
    print("=== Azure AI Search — Knowledge Base Seeder ===\n")

    # Step 1: Get admin key
    print("[1/5] Retrieving admin key from Azure CLI...")
    key = get_admin_key()
    print(f"  Key retrieved ({len(key)} chars)")

    # Step 2: Check/create index
    print(f"\n[2/5] Checking index '{INDEX_NAME}'...")
    if check_index_exists(key):
        print(f"  Index '{INDEX_NAME}' already exists — skipping creation")
    else:
        print(f"  Creating index '{INDEX_NAME}' from {SCHEMA_FILE}...")
        if not create_index(key):
            sys.exit(1)

    # Step 3: Collect and chunk documents
    print(f"\n[3/5] Collecting documents from {KB_DIR}...")
    docs, file_count = collect_documents()
    print(f"  {file_count} files → {len(docs)} chunks")

    # Step 4: Upload
    print(f"\n[4/5] Uploading {len(docs)} documents...")
    uploaded = upload_documents(key, docs)
    print(f"  Total uploaded: {uploaded}/{len(docs)}")

    # Step 5: Verify
    print(f"\n[5/5] Verifying document count...")
    count = get_doc_count(key)
    print(f"  Index document count: {count}")

    # Summary
    print(f"\n=== Summary ===")
    print(f"  Service:    {SEARCH_URL}")
    print(f"  Index:      {INDEX_NAME}")
    print(f"  Files:      {file_count}")
    print(f"  Chunks:     {len(docs)}")
    print(f"  Uploaded:   {uploaded}")
    print(f"  Verified:   {count}")

    if count > 0:
        print("\n  Status: SUCCESS")
    else:
        print("\n  Status: VERIFY MANUALLY (count may take a moment to update)")


if __name__ == "__main__":
    main()

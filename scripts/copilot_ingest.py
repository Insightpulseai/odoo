#!/usr/bin/env python3
import os
import hashlib
import json
from pathlib import Path

# Config
KB_DIR = Path("kb")
OUT_DIR = Path("out/copilot_index")
MANIFEST_FILE = OUT_DIR / "manifest.json"

def compute_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def chunk_text(text, chunk_size=1000, overlap=100):
    # Simple character-based chunking for determinism MVP
    # In prod: use token-based split (tiktoken) via optional dependency
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start += (chunk_size - overlap)
    return chunks

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    
    documents = []
    
    # scan KB
    for root, _, files in os.walk(KB_DIR):
        for file in sorted(files):
            if not file.endswith(".md"):
                continue
            
            path = Path(root) / file
            content = path.read_text(encoding="utf-8")
            
            # Simple metadata extraction (frontmatter-lite)
            title = file
            lines = content.splitlines()
            if lines and lines[0].startswith("# "):
                title = lines[0][2:].strip()
                
            chunks = chunk_text(content)
            
            doc_entry = {
                "source": str(path),
                "title": title,
                "content_hash": compute_hash(content),
                "chunks_count": len(chunks),
                "chunks": []
            }
            
            for i, chunk_text_content in enumerate(chunks):
                doc_entry["chunks"].append({
                    "index": i,
                    "content_hash": compute_hash(chunk_text_content),
                    # We store hash of chunk for manifest, actual content could be in a separate jsonl
                    "preview": chunk_text_content[:50].replace("\n", " ") + "..."
                })
                
            documents.append(doc_entry)
            
    # Write manifest
    # Sort by source for stability
    documents.sort(key=lambda x: x["source"])
    
    manifest = {
        "version": "1.0",
        "generated_at_utc": "deterministic-timestamp-ignored-for-diff", 
        "documents": documents
    }
    
    # Write to JSON with indent for deterministic diff
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Generated manifest at {MANIFEST_FILE}")

if __name__ == "__main__":
    main()

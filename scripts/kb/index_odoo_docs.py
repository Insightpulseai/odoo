"""
Index a pinned snapshot of https://github.com/odoo/documentation (branch 19.0)
into docs/kb/odoo19/index/* JSON artifacts.

Outputs (deterministic):
  - manifest.json: list of indexed files + sha256 + bytes + mtime
  - sections.json: extracted headings/anchors per file (best-effort)
  - topics.json: topic_map.yaml resolution -> files
  - skills_coverage.json: which skills declare which topics and whether covered

Requirements:
  - docs/kb/odoo19/UPSTREAM_PIN.json must contain pinned_commit != "REPLACE_WITH_SHA"
  - docs/kb/odoo19/upstream/ must exist
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # handled with a clear error


ROOT = Path(__file__).resolve().parents[2]
KB_ROOT_DEFAULT = ROOT / "docs" / "kb" / "odoo19"
INDEX_DIR_NAME = "index"
UPSTREAM_DIR_NAME = "upstream"


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
RST_HEADING_UNDERLINE_RE = re.compile(r"^([=\-~^\"`:#*+_])\1{2,}\s*$")


def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        raise SystemExit(
            "PyYAML is required for scripts/kb/index_odoo_docs.py. "
            "Add it to your dev deps (requirements-dev.txt / uv toolchain) or vendor a tiny YAML parser."
        )
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _is_text_file(path: Path) -> bool:
    # only index likely-doc files (avoid images/binaries)
    return path.suffix.lower() in {".md", ".rst", ".txt"}


def _iter_upstream_files(upstream: Path) -> List[Path]:
    files: List[Path] = []
    for p in upstream.rglob("*"):
        if p.is_file() and _is_text_file(p):
            files.append(p)
    files.sort()
    return files


def _extract_sections_md(content: str) -> List[Dict[str, Any]]:
    sections: List[Dict[str, Any]] = []
    for i, line in enumerate(content.splitlines(), start=1):
        m = HEADING_RE.match(line)
        if not m:
            continue
        level = len(m.group(1))
        title = m.group(2).strip()
        anchor = _slugify(title)
        sections.append(
            {
                "format": "md",
                "line": i,
                "level": level,
                "title": title,
                "anchor": anchor,
            }
        )
    return sections


def _extract_sections_rst(content: str) -> List[Dict[str, Any]]:
    # very lightweight RST heading inference: a title line followed by underline of === or ---
    lines = content.splitlines()
    out: List[Dict[str, Any]] = []
    for i in range(0, len(lines) - 1):
        title = lines[i].rstrip()
        underline = lines[i + 1].rstrip()
        if not title or not underline:
            continue
        if RST_HEADING_UNDERLINE_RE.match(underline) and len(underline) >= max(3, len(title) // 2):
            # map underline char to a pseudo-level (best effort)
            ch = underline[0]
            level = {"=": 1, "-": 2, "~": 3, "^": 4}.get(ch, 5)
            out.append(
                {
                    "format": "rst",
                    "line": i + 1,
                    "level": level,
                    "title": title.strip(),
                    "anchor": _slugify(title.strip()),
                }
            )
    return out


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s


def _rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def _validate_pin(pin: Dict[str, Any]) -> None:
    pinned_commit = (pin.get("pinned_commit") or "").strip()
    if not pinned_commit or pinned_commit == "REPLACE_WITH_SHA":
        raise SystemExit(
            "UPSTREAM_PIN.json pinned_commit is not set. "
            "Set it to the commit SHA you vendored under docs/kb/odoo19/upstream/."
        )


def _match_topic_files(upstream_files_rel: List[str], include_paths: List[str]) -> List[str]:
    # include_paths are glob-ish rooted in upstream/ (e.g., "content/developer/**")
    matched: List[str] = []
    for relp in upstream_files_rel:
        for inc in include_paths:
            # translate to Path.match semantics (glob)
            if Path(relp).match(inc):
                matched.append(relp)
                break
    return sorted(set(matched))


def _collect_skill_sources(repo_root: Path) -> List[Tuple[str, Path]]:
    # find any agents/skills/**/KB_SOURCES.yaml
    skills_dir = repo_root / "agents" / "skills"
    if not skills_dir.exists():
        return []
    out: List[Tuple[str, Path]] = []
    for p in skills_dir.rglob("KB_SOURCES.yaml"):
        skill_id = p.parent.name  # folder name is skill-id by convention
        out.append((skill_id, p))
    out.sort(key=lambda x: x[0])
    return out


def build_manifest(upstream: Path, files: List[Path]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for p in files:
        b = p.read_bytes()
        st = p.stat()
        entries.append(
            {
                "path": _rel(p, upstream),
                "sha256": _sha256_bytes(b),
                "bytes": st.st_size,
                "mtime": int(st.st_mtime),
            }
        )
    return {"schema_version": "1.0.0", "entries": entries}


def build_sections(upstream: Path, files: List[Path]) -> Dict[str, Any]:
    by_file: Dict[str, Any] = {}
    for p in files:
        relp = _rel(p, upstream)
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # skip weird encodings; keep it deterministic
            continue
        if p.suffix.lower() == ".md":
            sections = _extract_sections_md(content)
        elif p.suffix.lower() == ".rst":
            sections = _extract_sections_rst(content)
        else:
            sections = []
        if sections:
            by_file[relp] = sections
    return {"schema_version": "1.0.0", "files": by_file}


def build_topics(upstream_rel_files: List[str], topic_map: Dict[str, Any]) -> Dict[str, Any]:
    topics = topic_map.get("topics") or []
    out_topics: List[Dict[str, Any]] = []
    for t in topics:
        tid = t.get("id")
        label = t.get("label")
        include_paths = t.get("include_paths") or []
        matched = _match_topic_files(upstream_rel_files, include_paths)
        out_topics.append(
            {
                "id": tid,
                "label": label,
                "include_paths": include_paths,
                "matched_files": matched,
                "matched_count": len(matched),
            }
        )
    return {
        "schema_version": "1.0.0",
        "topic_map_version": topic_map.get("version", 1),
        "topics": out_topics,
    }


def build_skills_coverage(
    repo_root: Path,
    kb_root: Path,
    topics_json: Dict[str, Any],
) -> Dict[str, Any]:
    # Resolve per-skill KB_SOURCES.yaml -> topics -> whether topic exists and has files
    topic_index: Dict[str, Dict[str, Any]] = {t["id"]: t for t in topics_json.get("topics", [])}
    skill_sources = _collect_skill_sources(repo_root)
    skills_out: List[Dict[str, Any]] = []
    for skill_id, src_path in skill_sources:
        doc = _load_yaml(src_path)
        kb_entries = doc.get("kb") or []
        deps: List[Dict[str, Any]] = []
        ok = True
        for ent in kb_entries:
            topics = ent.get("topics") or []
            required = bool(ent.get("required", False))
            for tid in topics:
                t = topic_index.get(tid)
                present = t is not None
                covered = bool(t and t.get("matched_count", 0) > 0)
                if required and (not present or not covered):
                    ok = False
                deps.append(
                    {
                        "topic_id": tid,
                        "required": required,
                        "topic_present": present,
                        "topic_has_files": covered,
                    }
                )
        skills_out.append(
            {
                "skill_id": skill_id,
                "kb_sources_path": _rel(src_path, repo_root),
                "ok": ok,
                "dependencies": deps,
            }
        )
    return {"schema_version": "1.0.0", "skills": skills_out}

    args = ap.parse_args()

    kb_root = Path(args.kb_root).resolve()
    repo_root = kb_root.parents[2]  # ../../.. from docs/kb/odoo19

    # Layers
    upstream_dir = kb_root / "upstream"
    # Deployed stack docs default location
    stack_dir = repo_root / "templates" / "odooops-console" / "src" / "content" / "docs" / "stack"
    # Overrides default location
    overrides_dir = (
        repo_root
        / "templates"
        / "odooops-console"
        / "src"
        / "content"
        / "docs"
        / "upstream_overrides"
    )

    pin_path = kb_root / "UPSTREAM_PIN.json"
    index_dir = kb_root / "index"
    topic_map_path = index_dir / "topic_map.yaml"

    if not pin_path.exists():
        raise SystemExit(f"Missing {pin_path}")
    if not topic_map_path.exists():
        raise SystemExit(f"Missing topic map: {topic_map_path}")

    # Validation
    pin = _read_json(pin_path)
    _validate_pin(pin)

    # 1. Collect all candidate files from all layers
    # We map slug -> {layer: path}
    # Slug is relative path from layer root, without extension (roughly)
    # Actually, for upstream, structure is `content/foo/bar.rst` -> slug `foo/bar`
    # For stack/overrides, it mirrors this or is flat?
    # Stack: `runtime.md` -> `runtime`
    # Overrides: `foo/bar.md` -> `foo/bar`

    slug_map: Dict[str, Dict[str, Path]] = {}

    def _collect(layer_name: str, root: Path, is_upstream: bool = False):
        if not root.exists():
            return
        files = _iter_upstream_files(root)  # Reuse helper, it just globs recursive
        for p in files:
            rel = p.relative_to(root)
            # Upstream has `content/` prefix usually?
            # Step 1297 find output was `docs/kb/odoo19/upstream/content/last_build.rst`
            # So upstream root is `docs/kb/odoo19/upstream`?
            # If so, rel path is `content/foo/bar.rst`.
            # User wants standard slug.
            # If overrides mimic this, they should be `content/foo/bar.md`?
            # Or is the slug logic inside the loader handling the `content` dir?
            # The loader handles `upstream/content` specifically.
            # So for Slug unification:
            # - Upstream: strip `content/` prefix if present? Or keeps it?
            # The loader takes `slugParts`. If URL is `/docs/developer/reference`, slug is `developer/reference`.
            # Upstream file is `content/developer/reference.rst`.
            # So slug = rel_path minus "content/" prefix minus extension.

            slug_rel = rel.with_suffix("").as_posix()
            if is_upstream and slug_rel.startswith("content/"):
                slug = slug_rel[len("content/") :]
            else:
                slug = slug_rel

            if slug not in slug_map:
                slug_map[slug] = {}
            slug_map[slug][layer_name] = p

    # Collect order doesn't matter for map construction, priority handled later
    _collect("upstream", upstream_dir, is_upstream=True)
    _collect("stack", stack_dir)
    _collect("override", overrides_dir)

    # 2. Resolve Precedence (Override > Stack > Upstream)
    resolved_files: List[Path] = []
    # Also keep track of which layer won for manifest
    resolved_layer_map: Dict[Path, str] = {}

    for slug, layers in slug_map.items():
        if "override" in layers:
            winner = layers["override"]
            resolved_layer_map[winner] = "override"
        elif "stack" in layers:
            winner = layers["stack"]
            resolved_layer_map[winner] = "stack"
        elif "upstream" in layers:
            winner = layers["upstream"]
            resolved_layer_map[winner] = "upstream"
        else:
            continue
        resolved_files.append(winner)

    resolved_files.sort()

    # 3. Build Artifacts based on RESOLVED files
    # Note: `build_manifest` previously assumed all files vs upstream root.
    # Now we have mixed roots. We need a new manifest structure or adapt.
    # User asked for "single index".
    # Let's adjust build_manifest to support mixed sources.
    # But for backward compatibility with existing viewing tools (if any),
    # we might need to be careful.
    # Actually, the manifest is mostly for integrity.

    # Let's build a "Global Manifest" listing inputs from all layers
    full_manifest_entries = []
    for layer, root in [
        ("upstream", upstream_dir),
        ("stack", stack_dir),
        ("override", overrides_dir),
    ]:
        if not root.exists():
            continue
        # List all files present, whether resolved or not (for audit)
        layer_files = _iter_upstream_files(root)
        for p in layer_files:
            b = p.read_bytes()
            st = p.stat()
            full_manifest_entries.append(
                {
                    "path": _rel(p, root),  # Relative to its own root
                    "layer": layer,
                    "sha256": _sha256_bytes(b),
                    "bytes": st.st_size,
                    "mtime": int(st.st_mtime),
                    "is_active": p in resolved_files,
                }
            )

    manifest = {"schema_version": "2.0.0", "entries": full_manifest_entries}

    # Re-implement build_sections to handle mixed paths (absolute)
    # The original `build_sections` took `upstream` root to calculate rel path.
    # Now we use the Slug (derived) or the Path as key?
    # `sections.json` uses `relp` as key.
    # We should use the SLUG as key for the frontend?
    # Or keep file path?
    # If we use file path, the frontend needs to map slug -> file path -> sections.
    # The current `loader.ts` loads file content. It doesn't use `sections.json`.
    # `sections.json` is for Search/Nav.
    # So `sections.json` should key by `slug` (the URL path), OR the search index should use it.
    # The previous `build_search_index` iterated `files_sections`.
    # Let's verify `build_sections` output format.
    # It returns `{"files": { "rel/path.md": [...] }}`.
    # And `build_search_index` generated href as `/docs/{file_slug}`.
    # So if we change `rel/path.md` to be the "Active File Identifier", it should work.

    # We will compute sections for RESOLVED files only.
    files_sections: Dict[str, Any] = {}
    for p in resolved_files:
        # We need the slug again to key it?
        # Or we key by the relative path from the layer root?
        # To avoid ambiguity, maybe we key by `layer:relpath`?
        # But `build_topics` wants files list.
        # Let's try to maintain the "relative path" abstraction but standardized.
        # If upstream is `content/foo.rst`, we key as `content/foo.rst`.
        # If stack is `runtime.md`, we key as `runtime.md`.
        # This might collide if `stack/content/foo.md` exists.
        # But we resolved precedence already.

        # Let's compute 'virtual path' matching the upstream structure if possible.
        # Or simply use the absolute path or a stable ID.
        # The simplest stable ID is the Slug + Extension.
        # But the extension varies (.rst vs .md).
        # Let's use the slug as the canonical ID for logic?
        # But `build_topics` matches glob patterns against paths.
        # Upstream topics include paths like `content/developer/**`.
        # So we must preserve that structure for upstream files.
        # For stack/overrides, we should probably pretend they are in `content/custom` or similar?
        # OR just use their relative path from their layer root.

        layer = resolved_layer_map[p]
        root = {"upstream": upstream_dir, "stack": stack_dir, "override": overrides_dir}[layer]
        rel_p = _rel(p, root)

        # Read content
        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if p.suffix.lower() == ".md":
            sects = _extract_sections_md(content)
        elif p.suffix.lower() == ".rst":
            sects = _extract_sections_rst(content)
        else:
            sects = []

        if sects:
            files_sections[f"{layer}:{rel_p}"] = sects  # Disambiguate by layer

    sections = {"schema_version": "2.0.0", "files": files_sections}

    # 4. Build Topics (using Upstream Rel Paths primarily, or all?)
    # `topic_map` usually filters upstream files.
    # Stack/Overrides might not be covered by topic map globs.
    # But user wants "single index".
    # If we want Stack docs in the nav, they need to be in `topics.json`.
    # We might need to auto-add them or rely on `topic_map.yaml` being updated.
    # For now, we will pass the "Virtual Paths" (layer:rel_p) to `build_topics`.
    # And we assume `topic_map.yaml` might be updated later to include `stack:**` etc.
    # Or we construct a default "Stack" topic if missing?
    # User requirement: "Search index: include upstream + overlays + deployed".
    # `build_topics` is mostly for Nav.
    # `build_search_index` is for Search.

    # We pass all keys of files_sections to build_topics.
    all_virtual_paths = sorted(files_sections.keys())
    topics = build_topics(all_virtual_paths, _load_yaml(topic_map_path))

    # 5. Skills Coverage
    skills_coverage = build_skills_coverage(repo_root, kb_root, topics)

    # 6. Nav & Search
    # `build_nav` uses `topics`.
    # `build_search_index` uses `sections`.

    # We need to adjust `build_search_index` to handle the `layer:rel_p` format
    # and generate correct hrefs.

    # We need to monkeypath/rewrite `build_search_index` and `build_nav` slightly
    # inside this script?
    # Since I am replacing the `main` and preserving imports,
    # I should also update `build_search_index` and `build_nav` above or inline logic.
    # But `replace_file_content` works on ranges.
    # I am replacing `main()` onwards (line 344+).
    # I should actually replace the helper functions too if they need changes.
    # `build_nav` line 303: `slug = str(Path(file_path).with_suffix(""))`
    # If file_path is `upstream:content/foo.rst`, Path() might chop it weirdly.
    # We need a robust `get_href(virtual_path)` helper.

    # Let's define the helper inside `main` context or inject it?
    # Better to rewrite the helpers in this file.
    # BUT I am restricted to `replace_file_content`.
    # I will replace the helpers AND main.

    pass  # Replaced below


def get_href(virtual_path: str) -> str:
    # virtual_path is "layer:rel/path.ext"
    if ":" in virtual_path:
        layer, rel = virtual_path.split(":", 1)
    else:
        layer, rel = "unknown", virtual_path

    p = Path(rel)
    # Remove extension
    slug = str(p.with_suffix(""))

    # Upstream content usually has `content/` prefix -> strip it for URL
    if layer == "upstream" and slug.startswith("content/"):
        slug = slug[len("content/") :]
    elif layer == "upstream" and slug.startswith("content"):  # exact content
        slug = ""  # root? unlikely

    return f"/docs/{slug}"


def build_nav(topics_data: Dict[str, Any], sections_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    nav = []
    topics = topics_data.get("topics", [])
    files_sections = sections_data.get("files", {})

    for topic in topics:
        topic_title = topic.get("label", "Untitled")
        matched_files = topic.get("matched_files", [])

        items = []
        for vpath in matched_files:
            # vpath is "layer:path"
            file_sections = files_sections.get(vpath, [])
            title = vpath
            if file_sections:
                h1 = next((s for s in file_sections if s["level"] == 1), None)
                if h1:
                    title = h1["title"]
                else:
                    title = file_sections[0]["title"]

            href = get_href(vpath)
            items.append({"title": title, "href": href, "path": vpath})

        if items:
            nav.append({"title": topic_title, "links": items})
    return nav


def build_search_index(sections_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    index = []
    files_sections = sections_data.get("files", {})
    for vpath, sections in files_sections.items():
        if not sections:
            continue

        href_base = get_href(vpath)

        # Context title
        h1 = next((s for s in sections if s["level"] == 1), None)
        context_title = h1["title"] if h1 else vpath

        for section in sections:
            anchor = section.get("anchor", "")
            title = section.get("title", "")

            index.append(
                {
                    "title": title,
                    "path": vpath,
                    "href": f"{href_base}#{anchor}" if anchor else href_base,
                    "context": context_title,
                    "level": section.get("level"),
                }
            )
    return index


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb-root", default=str(KB_ROOT_DEFAULT))
    ap.add_argument("--fail-on-skill-coverage", action="store_true")
    args = ap.parse_args()

    kb_root = Path(args.kb_root).resolve()
    repo_root = kb_root.parents[2]

    upstream_dir = kb_root / "upstream"
    stack_dir = repo_root / "templates" / "odooops-console" / "src" / "content" / "docs" / "stack"
    overrides_dir = (
        repo_root
        / "templates"
        / "odooops-console"
        / "src"
        / "content"
        / "docs"
        / "upstream_overrides"
    )

    pin_path = kb_root / "UPSTREAM_PIN.json"
    index_dir = kb_root / "index"
    topic_map_path = index_dir / "topic_map.yaml"

    if not pin_path.exists():
        raise SystemExit(f"Missing {pin_path}")
    if not topic_map_path.exists():
        raise SystemExit(f"Missing {topic_map_path}")

    _validate_pin(_read_json(pin_path))

    # 1. Collect
    slug_map = {}

    def _collect(layer, root, is_upstream=False):
        if not root.exists():
            return
        for p in _iter_upstream_files(root):
            rel = p.relative_to(root)
            slug = rel.with_suffix("").as_posix()
            if is_upstream and slug.startswith("content/"):
                slug = slug[len("content/") :]
            if slug not in slug_map:
                slug_map[slug] = {}
            slug_map[slug][layer] = p

    _collect("upstream", upstream_dir, is_upstream=True)
    _collect("stack", stack_dir)
    _collect("override", overrides_dir)

    # 2. Resolve
    resolved_files = []
    resolved_layer_map = {}
    for slug, layers in slug_map.items():
        if "override" in layers:
            w, l = layers["override"], "override"
        elif "stack" in layers:
            w, l = layers["stack"], "stack"
        elif "upstream" in layers:
            w, l = layers["upstream"], "upstream"
        else:
            continue
        resolved_files.append(w)
        resolved_layer_map[w] = l
    resolved_files.sort()

    # 3. Manifest (Full)
    entries = []
    for layer, root in [
        ("upstream", upstream_dir),
        ("stack", stack_dir),
        ("override", overrides_dir),
    ]:
        if not root.exists():
            continue
        for p in _iter_upstream_files(root):
            entries.append(
                {
                    "path": _rel(p, root),
                    "layer": layer,
                    "sha256": _sha256_bytes(p.read_bytes()),
                    "bytes": p.stat().st_size,
                    "is_active": p in resolved_files,
                }
            )
    manifest = {"schema_version": "2.0.0", "entries": entries}

    # 4. Sections (Active only)
    files_sections = {}
    for p in resolved_files:
        layer = resolved_layer_map[p]
        root = {"upstream": upstream_dir, "stack": stack_dir, "override": overrides_dir}[layer]
        rel_p = _rel(p, root)
        vpath = f"{layer}:{rel_p}"

        try:
            content = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if p.suffix == ".md":
            s = _extract_sections_md(content)
        elif p.suffix == ".rst":
            s = _extract_sections_rst(content)
        else:
            s = []

        if s:
            files_sections[vpath] = s

    sections = {"schema_version": "2.0.0", "files": files_sections}

    # 5. Topics
    topic_map = _load_yaml(topic_map_path)
    topics = build_topics(sorted(files_sections.keys()), topic_map)

    # 6. Nav & Search
    nav = build_nav(topics, sections)
    search_index = build_search_index(sections)

    # Coverage
    skills_coverage = build_skills_coverage(repo_root, kb_root, topics)

    _write_json(index_dir / "manifest.json", manifest)
    _write_json(index_dir / "sections.json", sections)
    _write_json(index_dir / "topics.json", topics)
    _write_json(index_dir / "skills_coverage.json", skills_coverage)
    _write_json(index_dir / "nav.json", nav)
    _write_json(index_dir / "index.json", search_index)

    if args.fail_on_skill_coverage:
        bad = [s for s in skills_coverage.get("skills", []) if not s.get("ok")]
        if bad:
            raise SystemExit(f"Skill coverage check failed: {bad}")

    print(
        f"Indexed {len(resolved_files)} active files (from {len(entries)} total) into {index_dir}"
    )


if __name__ == "__main__":
    main()

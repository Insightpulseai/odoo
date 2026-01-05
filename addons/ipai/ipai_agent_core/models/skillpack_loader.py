# -*- coding: utf-8 -*-
"""Skillpack loader - imports JSON skill definitions into Odoo database."""

import json
import logging
import os
from pathlib import Path

_logger = logging.getLogger(__name__)

# Default paths to search for skillpack
DEFAULT_SKILLPACK_PATHS = [
    # 1) Repo root skillpack (recommended)
    "/home/user/odoo-ce/skillpack",
    # 2) Docker mount point
    "/mnt/extra-addons/skillpack",
]


def _read_json(path):
    """Read and parse JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _find_skillpack_manifest():
    """Find skillpack manifest.json in default paths."""
    # Also check relative to module
    module_dir = Path(__file__).parent.parent
    local_skillpack = module_dir / "skillpack"

    paths_to_check = list(DEFAULT_SKILLPACK_PATHS)
    if local_skillpack.exists():
        paths_to_check.insert(0, str(local_skillpack))

    for base in paths_to_check:
        manifest_path = Path(base) / "manifest.json"
        if manifest_path.is_file():
            _logger.info("Found skillpack at: %s", manifest_path)
            return manifest_path

    return None


def load_skillpack_from_default_paths(env):
    """
    Load skillpack manifest.json into database.

    Upserts tools, knowledge sources, and skills from JSON.
    Safe to call multiple times (idempotent).
    """
    manifest_path = _find_skillpack_manifest()
    if not manifest_path:
        _logger.warning("No skillpack manifest.json found in default paths")
        return

    try:
        manifest = _read_json(manifest_path)
    except Exception as e:
        _logger.error("Failed to read skillpack manifest: %s", e)
        return

    Tool = env["ipai.agent.tool"].sudo()
    Knowledge = env["ipai.agent.knowledge_source"].sudo()
    Skill = env["ipai.agent.skill"].sudo()

    # Upsert tools
    for t in manifest.get("tools", []):
        key = t.get("key")
        if not key:
            continue

        existing = Tool.search([("key", "=", key)], limit=1)
        vals = {
            "name": t.get("name", key),
            "key": key,
            "description": t.get("description", ""),
            "target_model": t.get("target_model", ""),
            "target_method": t.get("target_method", ""),
            "input_schema_json": json.dumps(t.get("input_schema", {})),
            "output_schema_json": json.dumps(t.get("output_schema", {})),
            "requires_admin": t.get("requires_admin", False),
            "is_active": True,
        }

        if existing:
            existing.write(vals)
            _logger.debug("Updated tool: %s", key)
        else:
            Tool.create(vals)
            _logger.debug("Created tool: %s", key)

    # Upsert knowledge sources
    for k in manifest.get("knowledge", []):
        key = k.get("key")
        if not key:
            continue

        existing = Knowledge.search([("key", "=", key)], limit=1)
        tags = k.get("tags", [])
        if isinstance(tags, list):
            tags = ",".join(tags)

        vals = {
            "name": k.get("name", key),
            "key": key,
            "kind": k.get("kind", "text"),
            "url": k.get("url"),
            "model_name": k.get("model_name"),
            "content_text": k.get("content_text"),
            "tags": tags,
            "is_active": True,
        }

        if existing:
            existing.write(vals)
            _logger.debug("Updated knowledge: %s", key)
        else:
            Knowledge.create(vals)
            _logger.debug("Created knowledge: %s", key)

    # Upsert skills
    for s in manifest.get("skills", []):
        key = s.get("key")
        if not key:
            continue

        existing = Skill.search([("key", "=", key)], limit=1)

        intents = s.get("intents", [])
        if isinstance(intents, list):
            intents = "\n".join(intents)

        guardrails = s.get("guardrails", [])
        if isinstance(guardrails, list):
            guardrails = "\n".join(guardrails)

        vals = {
            "name": s.get("name", key),
            "key": key,
            "version": s.get("version", "1.0.0"),
            "description": s.get("description", ""),
            "intents": intents,
            "workflow_json": json.dumps(s.get("workflow", [])),
            "guardrails": guardrails,
            "is_active": True,
        }

        if existing:
            existing.write(vals)
            skill = existing
            _logger.debug("Updated skill: %s", key)
        else:
            skill = Skill.create(vals)
            _logger.debug("Created skill: %s", key)

        # Bind tools
        tool_keys = s.get("tools", [])
        if tool_keys:
            tools = Tool.search([("key", "in", tool_keys)])
            skill.write({"tool_ids": [(6, 0, tools.ids)]})

        # Bind knowledge
        knowledge_keys = s.get("knowledge", [])
        if knowledge_keys:
            knowledge = Knowledge.search([("key", "in", knowledge_keys)])
            skill.write({"knowledge_ids": [(6, 0, knowledge.ids)]})

    _logger.info(
        "Skillpack loaded: %d tools, %d knowledge, %d skills",
        len(manifest.get("tools", [])),
        len(manifest.get("knowledge", [])),
        len(manifest.get("skills", [])),
    )


def reload_skillpack(env):
    """Manually reload skillpack (can be called from shell or wizard)."""
    load_skillpack_from_default_paths(env)

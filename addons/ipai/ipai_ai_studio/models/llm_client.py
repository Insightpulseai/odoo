# -*- coding: utf-8 -*-
"""
LLM Client for AI Studio spec generation.

Uses OpenAI-compatible chat.completions API to draft Odoo module specs from prompts.
"""
import json
import re
import requests

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.S)


def _extract_json(text: str) -> str:
    """
    Tries to extract a JSON object from free-form text.
    If already valid JSON, returns it as-is.
    """
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty model response")
    # direct parse
    try:
        json.loads(text)
        return text
    except Exception:
        pass
    # attempt to find first {...} block
    m = _JSON_BLOCK_RE.search(text)
    if not m:
        raise ValueError("No JSON object found in response")
    block = m.group(0)
    json.loads(block)  # validate
    return block


def draft_spec_json(
    *,
    base_url: str,
    api_key: str,
    model: str,
    user_prompt: str,
    timeout_s: int = 60,
) -> str:
    """
    OpenAI-compatible chat.completions call.
    Expects endpoint: {base_url}/v1/chat/completions
    Returns JSON string for spec.
    """
    sys_prompt = (
        "You are an Odoo 18 CE module spec generator. Output ONLY valid JSON.\n\n"
        "Constraints:\n"
        "- Only Odoo CE + OCA dependencies that exist in addons_path.\n"
        "- Prefer simple CRUD app patterns.\n"
        "- All models must include security groups + ir.model.access.csv entries.\n"
        "- Views must be consistent with declared fields.\n"
        "- Avoid enterprise-only modules (web_studio, documents, voip, sale_amazon, sign, etc.).\n"
        "- module_name must start with ipai_.\n\n"
        "JSON schema:\n"
        "{\n"
        '  "module_name": "ipai_example",\n'
        '  "app_name": "Example App",\n'
        '  "depends": ["base"],\n'
        '  "models": [\n'
        "    {\n"
        '      "name": "ipai.example",\n'
        '      "description": "Example Model",\n'
        '      "mail_thread": false,\n'
        '      "fields": [\n'
        '        {"name": "name", "type": "char", "required": true},\n'
        '        {"name": "description", "type": "text"}\n'
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  "menus": [],\n'
        '  "views": {\n'
        '    "form": ["name", "description"],\n'
        '    "tree": ["name"],\n'
        '    "search": ["name"]\n'
        "  },\n"
        '  "security": {\n'
        '    "groups": [{"xml_id": "group_user", "name": "User"}],\n'
        '    "access": [\n'
        '      {"model": "ipai.example", "group": "group_user", "perm": "read,write,create,unlink"}\n'
        "    ]\n"
        "  }\n"
        "}\n\n"
        "No prose. No markdown. JSON only.\n"
    )

    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    r.raise_for_status()
    data = r.json()

    content = (
        (data.get("choices") or [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    return _extract_json(content)

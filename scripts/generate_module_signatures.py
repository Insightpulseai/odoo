#!/usr/bin/env python3
"""
Generate Feature Signatures for Custom Modules
Extracts feature signatures from Odoo database for OCA validation
"""

import os
import sys
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Any

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)


def get_db_connection():
    """Get PostgreSQL connection from environment"""
    postgres_url = os.environ.get("POSTGRES_URL")
    if postgres_url:
        return psycopg2.connect(postgres_url)

    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "6543")),
        database=os.environ.get("POSTGRES_DB", "postgres"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD"),
    )


def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from text"""
    if not text:
        return []

    import re

    # Lowercase, remove punctuation, split on whitespace
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()

    # Filter out common words and short words
    stopwords = {
        "the",
        "and",
        "for",
        "with",
        "this",
        "that",
        "from",
        "have",
        "will",
        "module",
        "odoo",
        "ipai",
    }
    keywords = [w for w in words if len(w) > 3 and w not in stopwords]

    return list(set(keywords))  # Unique keywords


def get_module_manifest(conn, module_name: str) -> Dict[str, Any]:
    """Get module manifest summary from ir_module_module"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT summary, description, author, category
            FROM ir_module_module
            WHERE name = %s
            """,
            (module_name,),
        )
        result = cur.fetchone()
        if result:
            return {
                "summary": result[0] or "",
                "description": result[1] or "",
                "author": result[2] or "",
                "category": result[3] or "",
            }
        return {}


def get_model_names(conn, module_name: str) -> List[str]:
    """Get list of models defined by module"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT model
            FROM ir_model_data
            WHERE module = %s AND model = 'ir.model'
            """,
            (module_name,),
        )
        return [row[0] for row in cur.fetchall()]


def get_view_titles(conn, module_name: str) -> List[str]:
    """Get list of view titles defined by module"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT v.name
            FROM ir_ui_view v
            INNER JOIN ir_model_data imd ON imd.res_id = v.id AND imd.model = 'ir.ui.view'
            WHERE imd.module = %s
            """,
            (module_name,),
        )
        return [row[0] for row in cur.fetchall()]


def get_menu_labels(conn, module_name: str) -> List[str]:
    """Get list of menu labels defined by module"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT m.name
            FROM ir_ui_menu m
            INNER JOIN ir_model_data imd ON imd.res_id = m.id AND imd.model = 'ir.ui.menu'
            WHERE imd.module = %s
            """,
            (module_name,),
        )
        return [row[0] for row in cur.fetchall()]


def get_action_names(conn, module_name: str) -> List[str]:
    """Get list of action names defined by module"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT DISTINCT a.name
            FROM ir_actions_act_window a
            INNER JOIN ir_model_data imd ON imd.res_id = a.id AND imd.model = 'ir.actions.act_window'
            WHERE imd.module = %s
            """,
            (module_name,),
        )
        return [row[0] for row in cur.fetchall()]


def compute_signature_hash(signature: Dict[str, Any]) -> str:
    """Compute SHA256 hash of signature for change detection"""
    sig_str = json.dumps(signature, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(sig_str.encode("utf-8")).hexdigest()


def generate_signature(conn, module_name: str) -> Dict[str, Any]:
    """Generate complete feature signature for a module"""
    print(f"  Generating signature for {module_name}...")

    manifest = get_module_manifest(conn, module_name)
    model_names = get_model_names(conn, module_name)
    view_titles = get_view_titles(conn, module_name)
    menu_labels = get_menu_labels(conn, module_name)
    action_names = get_action_names(conn, module_name)

    # Extract keywords from all text fields
    all_text = " ".join(
        [
            manifest.get("summary", ""),
            manifest.get("description", ""),
            " ".join(view_titles),
            " ".join(menu_labels),
            " ".join(action_names),
        ]
    )
    keywords = extract_keywords(all_text)

    signature = {
        "module_name": module_name,
        "manifest_summary": manifest.get("summary", ""),
        "model_names": model_names,
        "view_titles": view_titles,
        "menu_labels": menu_labels,
        "action_names": action_names,
        "keywords": keywords,
    }

    signature["signature_hash"] = compute_signature_hash(signature)

    return signature


def upsert_signature(conn, signature: Dict[str, Any]):
    """Upsert signature into oca.custom_module_signatures table"""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO oca.custom_module_signatures (
                module_name, manifest_summary, model_names, view_titles,
                menu_labels, action_names, keywords, signature_hash
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (module_name) DO UPDATE SET
                manifest_summary = EXCLUDED.manifest_summary,
                model_names = EXCLUDED.model_names,
                view_titles = EXCLUDED.view_titles,
                menu_labels = EXCLUDED.menu_labels,
                action_names = EXCLUDED.action_names,
                keywords = EXCLUDED.keywords,
                signature_hash = EXCLUDED.signature_hash,
                updated_at = NOW()
            """,
            (
                signature["module_name"],
                signature["manifest_summary"],
                signature["model_names"],
                signature["view_titles"],
                signature["menu_labels"],
                signature["action_names"],
                signature["keywords"],
                signature["signature_hash"],
            ),
        )
        conn.commit()


def get_custom_modules(conn) -> List[str]:
    """Get list of installed custom ipai_* modules"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT name
            FROM ir_module_module
            WHERE name LIKE 'ipai_%'
              AND state = 'installed'
            ORDER BY name
            """
        )
        return [row[0] for row in cur.fetchall()]


def main():
    """Main signature generation routine"""
    print("=" * 80)
    print("Custom Module Feature Signature Generation")
    print("=" * 80)
    print()

    # Connect to database
    try:
        conn = get_db_connection()
        print("✓ Connected to PostgreSQL")
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(1)

    try:
        # Get list of custom modules
        print("\n1. Scanning for custom modules...")
        modules = get_custom_modules(conn)
        print(f"  Found {len(modules)} installed ipai_* modules")

        if not modules:
            print("  No custom modules found. Nothing to do.")
            return

        # Generate signatures
        print("\n2. Generating feature signatures...")
        signatures = []
        for module_name in modules:
            try:
                signature = generate_signature(conn, module_name)
                signatures.append(signature)
                upsert_signature(conn, signature)
            except Exception as e:
                print(f"  ERROR: Failed to generate signature for {module_name}: {e}")
                continue

        print(f"  ✓ Generated {len(signatures)} signatures")

        # Summary statistics
        print("\n3. Signature summary:")
        for sig in signatures:
            print(
                f"  {sig['module_name']:40} "
                f"models={len(sig['model_names']):2} "
                f"views={len(sig['view_titles']):2} "
                f"menus={len(sig['menu_labels']):2} "
                f"keywords={len(sig['keywords']):2}"
            )

        print()
        print("=" * 80)
        print("✓ Signature generation complete")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Run validation: SELECT * FROM oca.validate_all_custom_modules();")
        print("  2. Review results: SELECT * FROM oca.validation_results ORDER BY match_confidence DESC;")
        print("  3. Execute retirements based on recommendations")
        print()

    except Exception as e:
        print(f"\nERROR: Signature generation failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

import sys
import json
import re
import jsonschema
from collections import Counter
from datetime import datetime, timezone


def normalize_trigger(raw):
    raw_lower = raw.lower()
    mapping = []
    if "http" in raw_lower:
        mapping.append("http")
    if "webhook" in raw_lower:
        mapping.append("webhook")
    if "schedule" in raw_lower or "cron" in raw_lower:
        mapping.append("cron")
    if "push" in raw_lower or "pr" in raw_lower:
        mapping.append("push_pr")
    if "manual" in raw_lower or "dispatch" in raw_lower:
        mapping.append("manual")
    if not mapping:
        mapping.append("unknown")
    if "cron" in mapping and len(mapping) > 1:
        if "mixed" not in mapping:
            mapping.append("mixed")
    return list(set(mapping))


def extract_cron(raw):
    match = re.search(r"Cron:\s*(.*)", raw)
    if match:
        return match.group(1).strip()
    return None


def main(inv_path, schema_path, sum_path):
    with open(inv_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    # 1. Update metadata
    data["metadata"]["status"] = "Repo-Static Verified"
    data["metadata"]["verification_scope"] = ["repo-static"]
    if "coverage" not in data["metadata"]:
        data["metadata"]["coverage"] = {
            "odoo_crons": "not_scanned",
            "supabase_edge_functions": "repo-scanned",
            "github_actions": "repo-scanned",
            "pg_cron": "not_scanned",
            "n8n": "not_scanned",
        }

    ids_seen = set()
    paths_seen = set()
    duplicates = []

    all_cat = ["odoo_crons", "edge_functions", "other_automations"]

    # 2. Iterate and normalize
    for cat in all_cat:
        for item in data.get(cat, []):
            item_id = item.get("id", "")
            if item_id in ids_seen:
                duplicates.append(item_id)
            ids_seen.add(item_id)
            paths_seen.add(item.get("source_path", ""))

            ck = f"{item['platform'].lower()}.{item['type'].replace('-', '_')}:{item['name']}"
            item["canonical_key"] = ck
            item["kind"] = item["type"].replace("-", "_")

            # Map statuses to schema bounds
            if item.get("enablement_status", "unknown") not in [
                "enabled",
                "disabled",
                "unknown",
                "not_applicable",
            ]:
                item["enablement_status"] = "unknown"
            if item.get("runtime_status", "unknown") not in [
                "healthy",
                "degraded",
                "failing",
                "unknown",
                "not_applicable",
                "failed",
            ]:
                item["runtime_status"] = "unknown"
            if item.get("confidence", "medium") not in ["high", "medium", "low"]:
                item["confidence"] = "medium"

            item.setdefault("status_provenance", "repo-scan")
            item["trigger_normalized"] = normalize_trigger(item.get("trigger", ""))
            item["schedule_cron"] = extract_cron(item.get("trigger", ""))
            item["runtime_probe"] = {"method": "none"}
            item["last_verified_at"] = datetime.now(timezone.utc).isoformat()
            item["last_verified_source"] = "repo-static"
            item["criticality"] = "tier2"
            item["owner_team"] = "platform"

            if "template" in item["name"].lower():
                item["status_lifecycle"] = "template"
            elif (
                "deprecated" in item["name"].lower()
                or "deprecated" in item.get("notes", "").lower()
            ):
                item["status_lifecycle"] = "deprecated"
            else:
                item["status_lifecycle"] = "active"

    # 3. Validate
    try:
        jsonschema.validate(instance=data, schema=schema)
        print("Schema validation successful.")
    except jsonschema.exceptions.ValidationError as e:
        print(f"Schema validation failed: {e.message}")
        sys.exit(1)

    if duplicates:
        print(f"Schema validation failed: Duplicate IDs found: {duplicates}")
        sys.exit(1)

    # 4. Save normalized JSON
    with open(inv_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # 5. Generate Markdown summary
    sum_md = [
        "# Automations Inventory Summary",
        "> Generated from normalized SSOT.",
        "",
        "## Coverage Disclosure",
        "| Surface | Status |",
        "|---|---|",
    ]
    for k, v in data["metadata"]["coverage"].items():
        sum_md.append(f"| {k} | {v} |")

    sum_md.extend(["", "## Total Counts", "| Platform | Type | Count |", "|---|---|---|"])

    plat_type = Counter()
    trig_counts = Counter()
    status_counts = Counter()
    scheduled_items = []
    suspicious = []

    for cat in all_cat:
        for item in data.get(cat, []):
            plat_type[(item["platform"], item["type"])] += 1
            for t in item["trigger_normalized"]:
                trig_counts[t] += 1
            status_counts[item["runtime_status"]] += 1
            if "cron" in item["trigger_normalized"]:
                scheduled_items.append(item)
            if item["status_lifecycle"] in ["template", "deprecated"]:
                suspicious.append(item)

    for (p, t), c in plat_type.items():
        sum_md.append(f"| {p} | {t} | {c} |")

    sum_md.extend(["", "## Trigger Breakdown (Normalized)"])
    for t, c in trig_counts.items():
        sum_md.append(f"- **{t}**: {c}")

    sum_md.extend(["", "## Unknown-Status Heatmap", "| Status | Count |", "|---|---|"])
    for s, c in status_counts.items():
        sum_md.append(f"| {s} | {c} |")

    sum_md.extend(["", "## Scheduled Automations"])
    if scheduled_items:
        sum_md.extend(["| Name | Platform | Trigger Node |", "|---|---|---|"])
        for i in scheduled_items:
            sum_md.append(f"| {i['name']} | {i['platform']} | {i['trigger']} |")
    else:
        sum_md.append("None explicitly defined as scheduled via repo config mapping.")

    sum_md.extend(["", "## Template / Deprecated (Needs Review)"])
    if suspicious:
        for i in suspicious:
            sum_md.append(f"- `[{i['status_lifecycle'].upper()}]` {i['name']} ({i['platform']})")
    else:
        sum_md.append("None flagged.")

    with open(sum_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sum_md))

    print(f"Normalization complete. Summary written to {sum_path}.")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python normalize.py <inventory_json> <schema_json> <summary_md>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])

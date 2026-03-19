from xml.etree import ElementTree as ET
import os

paths = [
    "addons/ipai/ipai_finance_ppm_tdi/data/month_end_tasks_seed.xml",
    "addons/ipai/ipai_finance_ppm_tdi/data/bir_calendar_seed.xml",
]

print("--- XML RECORD COUNTS ---")

for p in paths:
    if os.path.exists(p):
        try:
            tree = ET.parse(p)
            root = tree.getroot()
            # Count records
            records = root.findall(".//record")
            print(f"File: {os.path.basename(p)}")
            print(f"Total Records: {len(records)}")

            # Group by model
            models = {}
            for r in records:
                m = r.get("model")
                models[m] = models.get(m, 0) + 1

            for m, c in models.items():
                print(f"  Model {m}: {c}")

            # If project.task, group by project_id ref?
            if "project.task" in models:
                print("  Tasks by Project Ref:")
                from collections import Counter

                refs = []
                for r in records:
                    if r.get("model") == "project.task":
                        for f in r.findall("field"):
                            if f.get("name") == "project_id":
                                refs.append(f.get("ref"))

                for k, v in Counter(refs).items():
                    print(f"    {k}: {v}")

        except Exception as e:
            print(f"Error parsing {p}: {e}")
    else:
        print(f"File not found: {p}")

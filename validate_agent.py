import yaml
import os

REQUIRED_DIRS = [
    "agents/skills",
    "agents/registry",
    "docs/kb/odoo19/dev",
    "docs/kb/odoo19/contrib",
    "docs/kb/odoo19/admin",
    "docs/kb/odoo19/services",
    "agents/skills/drawio_diagramming",
    "agents/skills/dbml_schema",
]


def check_file_exists(path):
    if not os.path.exists(path):
        print(f"❌ MISSING: {path}")
        return False
    return True


def validate_skill_map():
    print("Validating Skill Map...")
    try:
        with open("agents/skills/odoo_developer_skill_map.yaml", "r") as f:
            data = yaml.safe_load(f)

        seen_ids = set()
        for skill in data["skills"]:
            sid = skill["id"]
            if sid in seen_ids:
                print(f"❌ DUPLICATE ID: {sid}")
            seen_ids.add(sid)

            if "kb" in skill:
                if not check_file_exists(skill["kb"]):
                    print(f"  -> referenced in skill '{sid}'")
            elif "path" in skill:
                if not check_file_exists(skill["path"]):
                    print(f"  -> referenced in skill '{sid}'")
            else:
                print(f"❌ SKILL DEFECT: '{sid}' has no 'kb' or 'path'")

        print(f"✅ Validated {len(data['skills'])} skills.")

    except Exception as e:
        print(f"❌ FAILED to parse Skill Map: {e}")


def main():
    print("Checking directories...")
    for d in REQUIRED_DIRS:
        if not os.path.isdir(d):
            print(f"❌ MISSING DIR: {d}")

    check_file_exists("docs/kb/odoo19/INDEX.md")
    check_file_exists("agents/skills/odoo_sh_workflow/SKILL.md")

    validate_skill_map()


if __name__ == "__main__":
    main()

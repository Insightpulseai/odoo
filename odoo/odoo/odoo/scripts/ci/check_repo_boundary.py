import os
import yaml
import sys

# Path to the SSOT file
SSOT_PATH = 'ssot/repo/top_level_ownership.yaml'
LEDGER_PATH = 'docs/architecture/REPO_DECOMPOSITION_LEDGER.md'

def load_ownership():
    with open(SSOT_PATH, 'r') as f:
        return yaml.safe_load(f)

def get_root_dirs():
    return [d for d in os.listdir('.') if os.path.isdir(d) and not d.startswith('.')]

def get_root_files():
    return [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.')]

def check_boundary():
    config = load_ownership()
    allowed = set(config.get('allowed_top_level', []))
    provisional = set(config.get('provisional_allowed', []))
    blocked = set(config.get('blocked_new_top_level', []))
    
    current_items = set(get_root_dirs() + get_root_files())
    
    violations = []
    
    for item in current_items:
        if item in blocked:
            violations.append(f"BLOCKED: Root item '{item}' is explicitly blocked.")
        elif item not in allowed and item not in provisional:
            violations.append(f"UNKNOWN: Root item '{item}' is not in the allowlist or provisional list.")

    # Check for provisional items in ledger
    with open(LEDGER_PATH, 'r') as f:
        ledger_content = f.read()
    
    for item in provisional:
        if item in current_items and item not in ledger_content:
            violations.append(f"PROVISIONAL: Item '{item}' is provisional but missing from REPO_DECOMPOSITION_LEDGER.md")

    if violations:
        print("\n".join(violations))
        # We don't exit(1) yet if we want it to be "warn-only" for existing, 
        # but for NEW sprawl we should.
        # For now, let's exit(1) to be strict as requested: "Fail on new sprawl"
        return False
    
    return True

if __name__ == "__main__":
    if not os.path.exists(SSOT_PATH):
        print(f"Error: {SSOT_PATH} not found.")
        sys.exit(1)
    
    if check_boundary():
        print("Repo boundary check passed.")
        sys.exit(0)
    else:
        sys.exit(1)

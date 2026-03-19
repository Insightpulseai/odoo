#!/usr/bin/env python3
import sys, json, pathlib
from typing import Dict, Any, List

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = pathlib.Path(__file__).resolve().parents[2]

BASE_TRACK_FILES = [
    ROOT / "docs/competency/accounting/month_end_close.yaml",
    ROOT / "docs/competency/accounting/tax_compliance.yaml",
]

LOCALES_DIR = ROOT / "docs/competency/accounting/locales"
OUT_MD = ROOT / "docs/competency/accounting/COMPETENCY_BOARD.md"

REQ_TOP = {"version", "domain", "track", "levels", "competencies"}
REQ_COMP = {"code", "name", "why_it_matters", "behaviors", "evidence", "tool_enablers"}

OVERLAY_TOP = {
    "version",
    "domain",
    "locale",
    "extends_track",
    "add_competencies",
    "override_competencies",
}


def load_yaml(p: pathlib.Path) -> Any:
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def validate_base_track(p: pathlib.Path, data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{p}: expected dict")
    missing = REQ_TOP - set(data.keys())
    if missing:
        raise ValueError(f"{p}: missing top keys: {sorted(missing)}")
    comps = data.get("competencies", [])
    if not isinstance(comps, list) or not comps:
        raise ValueError(f"{p}: competencies must be non-empty list")
    for c in comps:
        if not isinstance(c, dict):
            raise ValueError(f"{p}: competency must be dict")
        m2 = REQ_COMP - set(c.keys())
        if m2:
            raise ValueError(f"{p}: competency {c.get('code')} missing keys: {sorted(m2)}")


def validate_overlay(p: pathlib.Path, data: Dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{p}: expected dict")
    missing = OVERLAY_TOP - set(data.keys())
    if missing:
        raise ValueError(f"{p}: missing overlay keys: {sorted(missing)}")
    if not isinstance(data["add_competencies"], list):
        raise ValueError(f"{p}: add_competencies must be a list (can be empty)")
    if not isinstance(data["override_competencies"], dict):
        raise ValueError(f"{p}: override_competencies must be a dict (can be empty)")


def index_by_code(comps: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out = {}
    for c in comps:
        code = c.get("code")
        if not code:
            raise ValueError("competency missing code")
        if code in out:
            raise ValueError(f"duplicate competency code: {code}")
        out[code] = c
    return out


def apply_overlay_to_track(track: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a new track dict with overlay applied.
    - Adds new competencies (append)
    - Overrides existing competency fields by shallow merge on matching code
    - Adds overlay metadata under track['_overlays']
    """
    if overlay["extends_track"] != track["track"]:
        return track

    # copy track shallowly
    merged = dict(track)
    merged["competencies"] = list(track["competencies"])

    base_idx = index_by_code(merged["competencies"])

    # 1) override existing
    overrides = overlay.get("override_competencies", {}) or {}
    for code, patch in overrides.items():
        if code not in base_idx:
            # ignore unknown codes to keep overlay tolerant
            continue
        if not isinstance(patch, dict):
            raise ValueError(f"override_competencies[{code}] must be dict")
        base = base_idx[code]
        # shallow merge patch fields (e.g., notes, evidence, tool_enablers) onto base
        for k, v in patch.items():
            base[k] = v

    # 2) add new competencies
    additions = overlay.get("add_competencies", []) or []
    for c in additions:
        if not isinstance(c, dict):
            raise ValueError("add_competencies items must be dict")
        m2 = REQ_COMP - set(c.keys())
        if m2:
            raise ValueError(f"overlay competency {c.get('code')} missing keys: {sorted(m2)}")
        if c["code"] in base_idx:
            raise ValueError(f"overlay attempts to add existing code: {c['code']}")
        merged["competencies"].append(c)
        base_idx[c["code"]] = c

    # annotate overlays
    merged.setdefault("_overlays", [])
    merged["_overlays"].append(
        {
            "locale": overlay["locale"],
            "source": overlay.get("_source", "unknown"),
        }
    )

    return merged


def load_base_tracks() -> List[Dict[str, Any]]:
    tracks = []
    for p in BASE_TRACK_FILES:
        data = load_yaml(p)
        validate_base_track(p, data)
        tracks.append(data)
    return tracks


def load_overlays() -> List[Dict[str, Any]]:
    overlays = []
    if not LOCALES_DIR.exists():
        return overlays
    for p in sorted(LOCALES_DIR.glob("**/*.yaml")):
        data = load_yaml(p)
        validate_overlay(p, data)
        data["_source"] = str(p.relative_to(ROOT))
        overlays.append(data)
    return overlays


def render_md(all_tracks: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("# Accounting Competency Boards\n")
    for t in all_tracks:
        title = t["track"].replace("_", " ").title()
        lines.append(f"## {title}\n")

        if t.get("_overlays"):
            ov = ", ".join([o["locale"] for o in t["_overlays"]])
            lines.append(f"**Locale overlays applied:** {ov}\n")

        lines.append("### Levels\n")
        for k, v in t["levels"].items():
            lines.append(f"- **{k}**: {v}")
        lines.append("\n### Competencies\n")
        for c in t["competencies"]:
            lines.append(f"#### {c['code']} — {c['name']}\n")
            lines.append(f"{c['why_it_matters']}\n")

            lines.append("**Behaviors**\n")
            for lvl, arr in c["behaviors"].items():
                lines.append(f"- **{lvl}**: " + "; ".join(arr))

            lines.append("\n**Evidence**\n")
            for e in c["evidence"]:
                lines.append(f"- {e}")

            lines.append("\n**Tool enablers**\n")
            for e in c["tool_enablers"]:
                lines.append(f"- {e}")

            if "notes" in c and c["notes"]:
                lines.append("\n**Notes**\n")
                if isinstance(c["notes"], list):
                    for n in c["notes"]:
                        lines.append(f"- {n}")
                else:
                    lines.append(str(c["notes"]))

            lines.append("")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main():
    tracks = load_base_tracks()
    overlays = load_overlays()

    # Apply all overlays in deterministic order (file path order)
    for ov in overlays:
        for i, t in enumerate(tracks):
            tracks[i] = apply_overlay_to_track(t, ov)

    OUT_MD.write_text(render_md(tracks), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "tracks": [t["track"] for t in tracks],
                "overlays_loaded": [o.get("_source") for o in overlays],
                "out": str(OUT_MD),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

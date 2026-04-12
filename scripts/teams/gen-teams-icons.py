#!/usr/bin/env python3
"""Generate Teams manifest icons for 6 IPAI agent surfaces.

Produces (12 files total):
  agents/<name>-surface/appPackage/color.png    (192x192, brand-colored, glyph)
  agents/<name>-surface/appPackage/outline.png  (32x32,   white silhouette)

Accent colors match each agent's manifest.json `accentColor` value.

Run from repo root:
    python3 scripts/teams/gen-teams-icons.py
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]

# (agent_dir_name, accent_hex, glyph_letter)
AGENTS = [
    ("teams-surface",         "#0F6FC6", "P"),  # Pulser
    ("tax-guru-surface",      "#C62828", "T"),  # Tax Guru PH
    ("doc-intel-surface",     "#2E7D32", "D"),  # Doc Intelligence
    ("bank-recon-surface",    "#1565C0", "B"),  # Bank Recon
    ("ap-invoice-surface",    "#6A1B9A", "A"),  # AP Invoice
    ("finance-close-surface", "#EF6C00", "F"),  # Finance Close
]


def _hex_rgb(hx: str) -> tuple[int, int, int]:
    hx = hx.lstrip("#")
    return tuple(int(hx[i : i + 2], 16) for i in (0, 2, 4))


def _pick_font(size: int) -> ImageFont.ImageFont:
    for candidate in [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_color(out: Path, accent_hex: str, glyph: str) -> None:
    W = H = 192
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (0, 0, W - 1, H - 1), radius=32, fill=_hex_rgb(accent_hex)
    )
    font = _pick_font(size=120)
    left, top, right, bottom = draw.textbbox((0, 0), glyph, font=font)
    tw = right - left
    th = bottom - top
    draw.text(
        ((W - tw) / 2 - left, (H - th) / 2 - top - 6),
        glyph,
        fill=(255, 255, 255, 255),
        font=font,
    )
    img.save(out, "PNG")


def make_outline(out: Path, glyph: str) -> None:
    """Teams outline.png is a monochrome mask; color is ignored + tinted by client."""
    W = H = 32
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(
        (1, 1, W - 2, H - 2), radius=5, outline=(255, 255, 255, 255), width=2
    )
    font = _pick_font(size=18)
    left, top, right, bottom = draw.textbbox((0, 0), glyph, font=font)
    tw = right - left
    th = bottom - top
    draw.text(
        ((W - tw) / 2 - left, (H - th) / 2 - top - 1),
        glyph,
        fill=(255, 255, 255, 255),
        font=font,
    )
    img.save(out, "PNG")


def main() -> None:
    for dir_name, accent, glyph in AGENTS:
        pkg_dir = REPO / "agents" / dir_name / "appPackage"
        pkg_dir.mkdir(parents=True, exist_ok=True)
        color_path = pkg_dir / "color.png"
        outline_path = pkg_dir / "outline.png"
        make_color(color_path, accent, glyph)
        make_outline(outline_path, glyph)
        print(
            f"{dir_name}: accent={accent} glyph={glyph} "
            f"color={color_path.stat().st_size}B outline={outline_path.stat().st_size}B"
        )


if __name__ == "__main__":
    main()

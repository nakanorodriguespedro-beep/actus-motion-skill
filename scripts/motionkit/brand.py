"""Brand: read the skill's brand folder (brand/brand.json + logo + fonts).

The folder defaults to `<skill>/brand/`; point MOTION_BRAND_DIR at another folder to switch brands
without touching the skill. Colours are never inlined in recipes: they come from a palette here.
"""
import json, os
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[2]
BRAND_DIR = Path(os.environ.get("MOTION_BRAND_DIR") or SKILL_DIR / "brand").expanduser().resolve()

def rgb(h: str):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def load():
    """brand.json as a dict, with palettes converted to RGB tuples and file paths made absolute."""
    path = BRAND_DIR / "brand.json"
    if not path.exists():
        raise FileNotFoundError(f"No brand.json in {BRAND_DIR}. Fill in brand/brand.json (see brand/README.md).")
    b = json.loads(path.read_text())
    b["palettes"] = {k: {role: rgb(v) for role, v in p.items()} for k, p in b["palettes"].items()}
    b["logo_path"] = (BRAND_DIR / b["logo"]) if b.get("logo") else None
    if b["logo_path"] is not None and not b["logo_path"].exists():
        raise FileNotFoundError(f"brand.json names logo {b['logo']!r} but {b['logo_path']} does not exist")
    fonts = b.get("fonts") or {}
    b["font_paths"] = {role: (BRAND_DIR / f if f else None) for role, f in fonts.items()}
    return b

BRAND = load()
PALETTES = BRAND["palettes"]
DEFAULT_PALETTE = BRAND.get("default_palette") or next(iter(PALETTES))

def palette(name=None):
    name = name or DEFAULT_PALETTE
    if name not in PALETTES:
        raise KeyError(f"palette {name!r} not in brand.json (have: {', '.join(PALETTES)})")
    p = dict(PALETTES[name]); p.setdefault("bg_center", p["bg"]); p.setdefault("accent", p["fg"])
    return p

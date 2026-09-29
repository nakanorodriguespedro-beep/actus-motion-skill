"""Text -> float mask, in the brand's own fonts (brand.json "fonts"), so type beats match the brand.
If a font role is unset, Pillow's built-in scalable font is used (fine for drafts, not for shipping)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from . import brand

def font(role="display", px=48):
    path = brand.BRAND["font_paths"].get(role) or brand.BRAND["font_paths"].get("display")
    if path is not None:
        return ImageFont.truetype(str(path), int(px))
    return ImageFont.load_default(size=int(px))   # Pillow >= 10.1

def text_mask(s, role="display", px=48, tracking=0.0, pad=8):
    """Render one line to a float mask [h, w]. tracking = extra px between glyphs."""
    f = font(role, px)
    widths = [f.getlength(ch) for ch in s]
    w = int((sum(widths) + tracking * (len(s) - 1)) if tracking else f.getlength(s)) + 2 * pad
    asc, desc = f.getmetrics(); h = asc + desc + 2 * pad
    im = Image.new("L", (max(1, w), h), 0); d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for ch, cw in zip(s, widths):
            d.text((x, pad), ch, font=f, fill=255); x += cw + tracking
    else:
        d.text((pad, pad), s, font=f, fill=255)
    return np.asarray(im).astype(np.float32) / 255

def words_masks(s, **kw):
    """One mask per word, for per-word cascades."""
    return [text_mask(w, **kw) for w in s.split(" ")]

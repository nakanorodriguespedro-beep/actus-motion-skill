"""Compositing primitives. A frame is float32 [H, W, 3] in 0..255; masks are float32 [h, w] in 0..1."""
import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from . import brand
from .assets import resize_mask

class Scene:
    """Holds the frame size, palette, and a pre-built background."""
    def __init__(self, W, H, palette=None):
        self.W, self.H = W, H
        p = brand.palette(palette)
        self.bg_color = np.array(p["bg"], np.float32)
        self.fg = np.array(p["fg"], np.float32)
        self.accent = np.array(p["accent"], np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.xx, self.yy = xx, yy
        r = np.sqrt(((xx - W / 2) / (W * 0.6)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2)
        lift = np.clip(1 - r, 0, 1)[..., None] ** 1.6
        self.bg = self.bg_color[None, None] + (np.array(p["bg_center"], np.float32) - self.bg_color)[None, None] * lift

    def frame(self):
        return self.bg.copy()

    def paste(self, canvas, mask, x, y, gain=1.0, color=None):
        """Alpha-composite a mask (as fg color) onto canvas at integer offset (x, y)."""
        col = self.fg if color is None else np.array(color, np.float32)
        h, w = mask.shape
        x0, y0 = max(0, x), max(0, y); x1, y1 = min(self.W, x + w), min(self.H, y + h)
        if x1 <= x0 or y1 <= y0: return
        sub = mask[y0 - y:y1 - y, x0 - x:x1 - x][..., None] * gain
        canvas[y0:y1, x0:x1] = canvas[y0:y1, x0:x1] * (1 - sub) + col * sub

    def paste_centered(self, canvas, mask, gain=1.0, dx=0, dy=0):
        h, w = mask.shape
        self.paste(canvas, mask, (self.W - w) // 2 + dx, (self.H - h) // 2 + dy, gain)

    def rings(self, canvas, cx, cy, t, delays=(0.0, 0.18), life=0.9, max_r=None, strength=0.55, color=None):
        """Expanding, fading rings from (cx, cy). t = seconds since the impact. Drawn in the accent by default."""
        max_r = max_r or min(self.W, self.H) * 0.42
        layer = Image.new("L", (self.W, self.H), 0); d = ImageDraw.Draw(layer)
        for delay in delays:
            u = (t - delay) / life
            if 0 < u < 1:
                rad = 40 + u * max_r
                alpha = int(255 * (1 - u) ** 2 * strength)
                d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=alpha, width=max(2, int(4 * (1 - u) + 1)))
        l = np.asarray(layer.filter(ImageFilter.GaussianBlur(2.5))).astype(np.float32) / 255
        col = self.accent if color is None else np.array(color, np.float32)
        canvas[:] = canvas * (1 - l[..., None]) + col * l[..., None]

    def halo_sweep(self, canvas, mask, x, y, progress, width=70.0, slope=0.45, strength=0.55, blur_r=22):
        """A soft glow band travelling across `mask` placed at (x, y). progress in [0,1]."""
        if not 0 < progress < 1: return
        h, w = mask.shape
        full = np.zeros((self.H, self.W), np.float32)
        x0, y0 = max(0, x), max(0, y); x1, y1 = min(self.W, x + w), min(self.H, y + h)
        full[y0:y1, x0:x1] = mask[y0 - y:y1 - y, x0 - x:x1 - x]
        band_x = x - 200 + progress * (w + 400)
        diag = self.xx - slope * (self.yy - self.H / 2)
        band = np.exp(-((diag - band_x) / width) ** 2)
        halo = blur(full, blur_r) * band * strength * math.sin(progress * math.pi)
        canvas[:] = canvas * (1 - halo[..., None]) + self.fg * halo[..., None]

def blur(mask, radius):
    if radius <= 0.05: return mask
    return np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))).astype(np.float32) / 255

def scaled(mask, s):
    return mask if abs(s - 1) < 1e-3 else resize_mask(mask, s)

def wipe(mask, progress, x_from=0, soft=0.25, direction=1):
    """Reveal `mask` left→right (direction=1) or right→left (-1). Columns before `x_from` are
    treated as already revealed (use it to start a wipe from behind another element)."""
    from .ease import smoothstep
    cols = np.clip((np.arange(mask.shape[1], dtype=np.float32) - x_from) / max(1, mask.shape[1] - x_from), 0, 1)
    if direction < 0: cols = 1 - cols
    edge = 1 - smoothstep(progress * (1 + soft) - soft, progress * (1 + soft), cols)[None, :]
    return mask * edge

def fade(canvas, amount):
    """Multiply the whole frame toward black. amount 1 = untouched, 0 = black."""
    return canvas * amount

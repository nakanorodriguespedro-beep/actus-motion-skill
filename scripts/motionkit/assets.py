"""Turn the brand logo into a float alpha mask in [0, 1]."""
import numpy as np
from PIL import Image
from . import brand

def key_mask(path):
    """Any logo PNG -> float alpha mask.
    - PNG with real transparency: the alpha channel is the mask.
    - Opaque PNG (light logo on a flat ground, or dark on light): luminance key
      (median = background, p99.9 = foreground), inverted automatically for dark-on-light."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA", "P"):
        a = np.asarray(im.convert("RGBA"))[..., 3].astype(np.float32) / 255
        if a.min() < 0.98:
            return a
    rgb = np.asarray(im.convert("RGB")).astype(np.float32)
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    bg, fg = np.median(lum), np.percentile(lum, 99.9)
    if abs(fg - bg) < 1:          # light-on-light: try the dark end instead
        fg = np.percentile(lum, 0.1)
    if fg < bg:
        lum = -lum; bg, fg = -bg, -fg
    return np.clip((lum - bg) / max(fg - bg, 1e-3), 0, 1)

def crop_to_bbox(a, pad=4, thresh=0.02):
    ys, xs = np.where(a > thresh)
    if len(ys) == 0:
        raise ValueError("logo mask is empty: is the logo the same colour as its background?")
    return a[max(0, ys.min() - pad):ys.max() + pad + 1, max(0, xs.min() - pad):xs.max() + pad + 1]

def resize_mask(a, s):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    size = (max(1, round(im.width * s)), max(1, round(im.height * s)))
    return np.asarray(im.resize(size, Image.LANCZOS)).astype(np.float32) / 255

def fit_mask(a, max_w, max_h):
    """Scale a mask to fit inside max_w x max_h, keeping its aspect."""
    return resize_mask(a, min(max_w / a.shape[1], max_h / a.shape[0]))

def load_logo(max_w, max_h=None):
    """The brand logo as a cropped float mask that fits max_w x max_h (None if brand.json has no logo)."""
    if brand.BRAND["logo_path"] is None:
        return None
    m = crop_to_bbox(key_mask(brand.BRAND["logo_path"]))
    return fit_mask(m, max_w, max_h or max_w)

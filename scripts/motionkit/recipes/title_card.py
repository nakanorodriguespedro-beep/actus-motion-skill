"""Title card / animated type: a headline cascades in word by word -> an accent underline draws
under it -> a slow push-in keeps the hold alive -> the words leave accelerating, in the same order.

Storyboard card (default timing, 4.5 s, N words):
| t (s)            | subject   | verb                                    | ease       | why                        |
|------------------|-----------|-----------------------------------------|------------|----------------------------|
| 0.10 + 0.09*i    | word i    | rises 3 % and de-blurs into place       | out        | stagger leads the eye      |
| after last word  | underline | draws L->R under the last line          | in-out     | the one accent             |
| hold             | block     | breathes (1.5 % scale, 2.8 s period)        | sine       | nothing frozen             |
| last 0.7 s       | word i    | lifts and fades, same order             | in         | leaves accelerating        |
"""
import numpy as np
from ..compose import Scene, blur, scaled
from ..ease import ease_out, ease_in, ease_in_out, smoothstep, window
from ..assets import crop_to_bbox
from ..text import text_mask
from .. import brand

def _layout(words, W, H, px, max_w):
    """Greedy wrap; returns [(mask, x, y)] per word relative to a block, plus block size and last-line box."""
    space = int(px * 0.28); line_h = int(px * 1.18)
    lines, cur, cur_w = [], [], 0
    for m in words:
        w = m.shape[1]
        if cur and cur_w + space + w > max_w:
            lines.append(cur); cur, cur_w = [], 0
        cur.append(m); cur_w += (space if cur_w else 0) + w
    if cur: lines.append(cur)
    widths = [sum(m.shape[1] for m in ln) + space * (len(ln) - 1) for ln in lines]
    bw, bh = max(widths), line_h * len(lines)
    placed = []
    for li, ln in enumerate(lines):
        x = (bw - widths[li]) // 2
        for m in ln:
            placed.append((m, x, li * line_h + (line_h - m.shape[0]) // 2)); x += m.shape[1] + space
    last = ((bw - widths[-1]) // 2, bh, widths[-1])
    return placed, bw, bh, last

def build(W, H, palette=None, duration=4.5, text=None, size=0.085, stagger=0.09, push=0.05):
    """text: the headline (default: brand.json "tagline"). size: type size as a share of min(W, H).
    push: total slow push-in over the piece (the idle that keeps the hold alive; keep it at or under 0.06)."""
    sc = Scene(W, H, palette)
    S = min(W, H)
    text = text if text is not None else brand.BRAND.get("tagline") or brand.BRAND.get("name", "")
    px = S * size
    words = [crop_to_bbox(text_mask(w, "display", px=px), pad=2) for w in text.split()]
    placed, bw, bh, (ux, uy, uw) = _layout(words, W, H, px, int(W * 0.8))
    uh = max(2, int(S * 0.008)); under_gap = int(px * 0.15)
    block_h = bh + under_gap + uh
    bx, by = (W - bw) // 2, (H - block_h) // 2
    n = len(placed)
    t_in_end = 0.1 + stagger * (n - 1) + 0.6
    under = (t_in_end - 0.2, 0.6)
    t_out = duration - 0.7 - stagger * (n - 1) * 0.5
    rise = S * 0.03

    open_t = under[0] + under[1]
    cx, cy = W / 2, H / 2

    def frame(t):
        c = sc.frame()
        k = 1 + push * t / duration                    # slow push-in across the whole piece: never frozen
        def put(mask, x, y, gain, color=None):         # (x, y) in block coords -> pushed screen coords
            m = scaled(mask, k)
            sx = round(cx + (bx + x - cx) * k); sy = round(cy + (by + y - cy) * k)
            sc.paste(c, m, sx, sy, gain=gain, color=color)
        for i, (m, x, y) in enumerate(placed):
            if t < t_out:
                u = ease_out(window(t, 0.1 + stagger * i, 0.6)); g = u
                dy = round((1 - u) * rise); layer = blur(m, 4 * (1 - u)) if u < 1 else m
            else:
                u = ease_in(window(t, t_out + stagger * 0.5 * i, 0.5)); g = 1 - u
                dy = round(-u * rise); layer = m
            if g > 0.001: put(layer, x, y + dy, g)
        if t < t_out:
            cols, gain = int(uw * ease_in_out(window(t, *under))), 1.0
        else:
            cols, gain = uw, 1 - ease_in(window(t, t_out, 0.5))
        if cols > 0 and gain > 0.001:
            put(np.ones((uh, cols), np.float32), ux, bh + under_gap, gain, color=sc.accent)
        return c

    holds = [(open_t + 0.1, t_out - 0.1)] if t_out - open_t > 0.8 else []
    return frame, duration, holds

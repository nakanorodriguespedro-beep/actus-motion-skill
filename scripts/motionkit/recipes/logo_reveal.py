"""Logo reveal: the mark drops in -> accent ripple -> rises to make room -> the name wipes in
beneath it -> the lockup breathes -> a soft halo sweeps across -> fade to black.

Storyboard card (default timing, 6 s):
| t (s)     | subject  | verb                                    | ease          | why                          |
|-----------|----------|-----------------------------------------|---------------|------------------------------|
| 0.05-0.90 | mark     | drops in from above, settles from blur  | out-back 1.35 | arrival; calm overshoot      |
| 0.75-1.85 | rings x2 | expand + fade from the landing point    | quadratic     | impact; the one accent       |
| 1.60-2.70 | mark     | rises to its lockup slot                | in-out        | makes room for the name      |
| 1.75-2.80 | name     | wipes in L->R under the mark, de-blurs  | in-out        | rides the mark's live position |
| 2.70-5.35 | lockup   | breathes (1.2 % scale, 3.2 s period)    | sine          | nothing frozen               |
| 3.10-4.30 | halo     | soft glow sweeps across the lockup      | sine          | light passes, no new colour  |
| 5.35-5.95 | frame    | fades to black                          | smoothstep    | clean cut                    |
"""
import math
import numpy as np
from ..compose import Scene, blur, scaled, wipe, fade
from ..ease import ease_out_back, ease_in_out, smoothstep, window
from ..assets import load_logo, crop_to_bbox
from ..text import text_mask
from .. import brand

BEATS = dict(drop=(0.05, 0.85), rings=0.75, rise=(1.6, 1.1), wipe=(1.75, 1.05), open=2.7,
             breathe_in=(2.7, 3.4), sweep=(3.1, 1.2), fade=(5.35, 5.95))

def build(W, H, palette=None, duration=6.0, logo_width=0.34, overshoot=1.35, end="fade",
          text=None, show_name=1.0, name_scale=0.075):
    """logo_width: mark width as a share of min(W, H). text: overrides brand.json "name".
    show_name=0 reveals the mark alone. end="hold" keeps breathing instead of fading (precedes another shot)."""
    sc = Scene(W, H, palette)
    S = min(W, H)
    name = (text if text is not None else brand.BRAND.get("name", "")) if show_name else ""
    mark = load_logo(int(S * logo_width), int(S * logo_width))
    name_m = crop_to_bbox(text_mask(name, "display", px=S * name_scale, tracking=S * 0.004)) if name else None
    if mark is None:                       # no logo file: the name itself is the mark
        if name_m is None: raise ValueError("brand has no logo and no name: nothing to reveal")
        mark = crop_to_bbox(text_mask(name, "display", px=S * 0.14)); name_m = None

    mh, mw = mark.shape
    gap = int(S * 0.05)
    if name_m is not None:
        nh, nw = name_m.shape
        lw, lh = max(mw, nw), mh + gap + nh
        lock = np.zeros((lh, lw), np.float32)
        lock[:mh, (lw - mw) // 2:(lw - mw) // 2 + mw] = mark
        lock[mh + gap:, (lw - nw) // 2:(lw - nw) // 2 + nw] = np.maximum(lock[mh + gap:, (lw - nw) // 2:(lw - nw) // 2 + nw], name_m)
    else:
        lock, (lh, lw) = mark, mark.shape
    lock_x, lock_y = (W - lw) // 2, (H - lh) // 2
    mark_final = (lock_x + (lw - mw) // 2, lock_y)            # the mark's slot inside the lockup
    mark_centre = ((W - mw) // 2, (H - mh) // 2)
    b = BEATS

    def frame(t):
        c = sc.frame()
        drop = ease_out_back(window(t, *b["drop"]), overshoot)
        m = ease_in_out(window(t, *b["rise"])) if name_m is not None else 0.0
        mx = round(mark_centre[0] + (mark_final[0] - mark_centre[0]) * m)
        my = round(mark_centre[1] + (mark_final[1] - mark_centre[1]) * m + (1 - drop) * (-H * 0.55))
        breath = 1 + 0.012 * math.sin((t - b["open"]) * 2 * math.pi / 3.2) * smoothstep(*b["breathe_in"], t)

        if t < b["open"]:
            sc.rings(c, mark_centre[0] + mw / 2, mark_centre[1] + mh / 2, t - b["rings"], max_r=S * 0.42)
            sc.paste(c, blur(mark, 6 * (1 - smoothstep(0.0, 0.7, t))), mx, my, gain=smoothstep(0.0, 0.25, t))
            if name_m is not None and t >= b["wipe"][0]:
                u = ease_in_out(window(t, *b["wipe"]))
                layer = blur(wipe(name_m, u), 5 * (1 - u))
                nx = lock_x + (lw - nw) // 2
                ny = my + mh + gap + round((1 - u) * S * 0.02)   # rides the mark's LIVE position
                sc.paste(c, layer, nx, ny)
        else:
            layer = scaled(lock, breath); h, w = layer.shape
            x, y = (W - w) // 2, (H - h) // 2
            sc.paste(c, layer, x, y)
            sc.halo_sweep(c, layer, x, y, window(t, *b["sweep"]), width=S * 0.07, blur_r=S * 0.02)
        return c if end == "hold" else fade(c, 1 - smoothstep(*b["fade"], t))

    holds = [(b["open"] + 0.2, (duration if end == "hold" else b["fade"][0]) - 0.2)]
    return frame, duration, holds

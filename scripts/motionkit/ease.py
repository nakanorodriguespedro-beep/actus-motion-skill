"""Easing. Everything takes a normalized t (clipped to [0, 1]) and returns a float."""
import numpy as np

def clip01(t): return float(np.clip(t, 0.0, 1.0))
def linear(t): return clip01(t)
def ease_in_out(t):
    t = clip01(t); return t * t * (3 - 2 * t)
def ease_out(t):
    t = clip01(t); return 1 - (1 - t) ** 3
def ease_in(t):
    t = clip01(t); return t ** 3
def ease_out_back(t, s=1.35):
    """Arrives with a soft overshoot. s≈1.35 = calm; 1.7 = playful; 1.0 = barely."""
    t = clip01(t); return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2
def smoothstep(e0, e1, x):
    """Vectorized: works on scalars and numpy arrays."""
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)
def window(t, start, dur):
    """Normalized progress of a beat that starts at `start` and lasts `dur`."""
    return clip01((t - start) / dur)

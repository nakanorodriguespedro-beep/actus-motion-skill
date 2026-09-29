"""motionkit: deterministic brand-motion renderer (Python + Pillow + numpy + ffmpeg).

A recipe is a function `frame(t: float) -> np.ndarray[H, W, 3] float32` built from the primitives
here. No AI credits, no wall-clock, no randomness: every pixel is a pure function of `t`, so the
same brief renders the same video.
"""
__version__ = "1.0.0"

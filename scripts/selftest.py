"""Smoke test, ~15 s: the brand loads, the logo keys to a mask, both recipes render small MP4s,
and the self-check passes on them. Run once per machine:  python3 scripts/selftest.py

Renders at full 1080 px size: much smaller and the breath resizes in whole-pixel steps, frames
repeat, and the self-check rightly flags the hold as frozen."""
import shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

for tool in ("ffmpeg", "ffprobe"):
    if not shutil.which(tool):
        sys.exit(f"selftest FAILED: {tool} is not on PATH (macOS: brew install ffmpeg · Ubuntu: sudo apt install ffmpeg · Windows: winget install ffmpeg)")

from motionkit import brand, render as R, qa as Q
from motionkit.assets import load_logo
from motionkit.recipes import logo_reveal, title_card

print("brand:", brand.BRAND_DIR, "| palettes:", ", ".join(brand.PALETTES))
logo = load_logo(300)
if logo is not None:
    assert logo.max() > 0.9 and logo.sum() > 100, "logo mask is empty or faint: check brand/logo.png"

results = {}
with tempfile.TemporaryDirectory() as d:
    for name, mod, size in (("logo_reveal", logo_reveal, (1080, 1080)), ("title_card", title_card, (1080, 1080))):
        out = Path(d) / f"{name}.mp4"
        frame, dur, holds = mod.build(*size)
        R.render(frame, out, *size, fps=24, duration=dur, log=None)
        rep = Q.report(out, holds)
        assert rep["frames"] == round(24 * dur), rep
        assert rep["verdict"] == "PASS", (name, rep)
        results[name] = rep["holds"]
print("selftest OK", results)

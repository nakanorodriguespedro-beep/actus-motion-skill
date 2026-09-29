"""ffmpeg writer + helpers to render a recipe, cut a contact sheet, and make a GIF preview."""
import subprocess, sys
import numpy as np

class MP4Writer:
    def __init__(self, path, W, H, fps=60, crf=17, preset="slow"):
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                   "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", preset,
                                   "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)
    def write(self, frame):
        self.p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    def close(self):
        self.p.stdin.close(); return self.p.wait()

def render(frame_fn, out, W, H, fps=60, duration=6.0, log=sys.stderr):
    """frame_fn(t) -> float32 [H, W, 3]. Streams straight into ffmpeg."""
    n = int(round(fps * duration)); w = MP4Writer(out, W, H, fps)
    for i in range(n):
        w.write(frame_fn(i / fps))
        if log and i % fps == 0: print(f"  {i / fps:.0f}s/{duration:.0f}s", file=log)
    rc = w.close()
    if rc != 0: raise RuntimeError(f"ffmpeg exited {rc}")
    return out

def contact_sheet(mp4, out, frames, cols=3, width=360):
    sel = "+".join(f"eq(n\\,{f})" for f in frames)
    rows = -(-len(frames) // cols)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4), "-vf",
                    f"select='{sel}',scale={width}:-1,tile={cols}x{rows}", "-vsync", "0", "-frames:v", "1", str(out)], check=True)
    return out

def gif(mp4, out, fps=20, width=480):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(mp4), "-vf", f"fps={fps},scale={width}:-1", "-loop", "0", str(out)], check=True)
    return out

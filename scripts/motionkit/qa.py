"""Self-check on the ENCODED video (never on PNG stills: they carry no compression noise).

Works on any MP4, whichever engine rendered it (motionkit or the Remotion template).

- Corpse test (nothing frozen): sample frame PAIRS at 12 fps inside each hold window and count the
  share that are near-identical (fewer than 0.1 % of the analysis pixels, ~270 px on the short side, moved by more than
  3 luma levels). A hold passes when at most 20 % of its pairs are dead.
- Slam test: flags a luma jump completed in < 4 frames right after stillness.
"""
import subprocess, json, sys
import numpy as np

SAMPLE_FPS, PX_THRESH, DEAD_FRAC, MAX_DEAD = 12, 3, 0.001, 0.20

def probe(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_frames", "-of", "json", str(mp4)], capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]; num, den = s["r_frame_rate"].split("/")
    return int(s["width"]), int(s["height"]), int(num) / int(den), int(s.get("nb_frames", 0))

def frames_gray(mp4, W, H, scale=None):
    scale = scale or max(1, min(W, H) // 270)   # ~270 px on the SHORT side, so 9:16, 1:1 and 16:9 score alike
    w, h = W // scale, H // scale
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(mp4), "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)

def report(mp4, holds=(), slam_frames=4):
    """holds = [(start_s, end_s), ...] windows that must stay alive."""
    W, H, fps, _ = probe(mp4)
    g = frames_gray(mp4, W, H)
    step = max(1, round(fps / SAMPLE_FPS))
    res = {"frames": len(g), "fps": fps, "holds": [], "slams": []}
    for a, b in holds:
        idx = range(int(a * fps), int(b * fps) - step, step)
        dead = [float((np.abs(g[i + step] - g[i]) > PX_THRESH).mean() < DEAD_FRAC) for i in idx]
        pct = float(np.mean(dead)) if dead else 1.0
        res["holds"].append({"window": [round(a, 2), round(b, 2)], "pairs": len(dead), "dead_pct": round(pct, 3), "pass": pct <= MAX_DEAD})
    d = np.abs(np.diff(g, axis=0)).mean(axis=(1, 2))
    for i in np.where(d > 8 * max(float(d.mean()), 1e-3))[0]:
        if i >= slam_frames and d[i - slam_frames:i].mean() < 0.2:
            res["slams"].append(int(i))
    res["verdict"] = "PASS" if all(h["pass"] for h in res["holds"]) and not res["slams"] else "CHECK"
    return res

if __name__ == "__main__":
    print(json.dumps(report(sys.argv[1], [tuple(map(float, w.split("-"))) for w in sys.argv[2:]]), indent=2))

"""CLI. Run from anywhere with PYTHONPATH pointing at the skill's scripts/ folder
(outputs are relative to your current directory):

  python3 -m motionkit list
  python3 -m motionkit render <recipe> --out out/name.mp4 --formats all [--palette dark] [--sheet] [--gif] [--opt k=v ...]
  python3 -m motionkit render <recipe> --out out/name.mp4 --size 1080x1920
  python3 -m motionkit render ./my_recipe.py --out out/name.mp4 --formats all      (your own recipe file)
  python3 -m motionkit qa <mp4> [start-end ...]

--formats all|9x16,1x1,16x9 renders every ratio in one run as <out>_9x16.mp4, <out>_1x1.mp4, ...
Exit code 2 = the self-check says CHECK for at least one render; read the JSON before shipping.
"""
import argparse, importlib, importlib.util, json, sys
from pathlib import Path
from . import render as R, qa as Q
from .recipes import REGISTRY

FORMATS = {"9x16": (1080, 1920), "1x1": (1080, 1080), "16x9": (1920, 1080), "4x5": (1080, 1350)}

def _load_recipe(name):
    """A registered recipe name, or a path to your own recipe .py file (kept outside the skill folder)."""
    if name.endswith(".py"):
        path = Path(name).expanduser().resolve()
        spec = importlib.util.spec_from_file_location(f"motionkit_user_recipe_{path.stem}", path)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
    if name not in REGISTRY:
        sys.exit(f"unknown recipe {name!r}; registered: {', '.join(REGISTRY)} (or pass a path to a .py recipe)")
    return importlib.import_module(REGISTRY[name])

def _render_one(a, opts, W, H, out):
    mod = _load_recipe(a.recipe)
    frame, duration, holds = mod.build(W, H, a.palette, **opts)
    out.parent.mkdir(parents=True, exist_ok=True)
    print(f"render {a.recipe} {W}x{H} @{a.fps}fps {duration}s palette={a.palette or 'default'} -> {out}", file=sys.stderr)
    R.render(frame, out, W, H, a.fps, duration)
    if a.sheet:
        n = int(a.fps * duration)
        R.contact_sheet(out, out.with_suffix(".sheet.png"), [int(n * f) for f in (0.08, 0.2, 0.33, 0.45, 0.6, 0.85)])
    if a.gif: R.gif(out, out.with_suffix(".gif"))
    rep = Q.report(out, holds)
    print("QA:", rep["verdict"], json.dumps(rep["holds"]), "slams:", rep["slams"], file=sys.stderr)
    return rep

def main(argv=None):
    p = argparse.ArgumentParser(prog="motionkit"); sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render"); r.add_argument("recipe", help="a registered recipe (see `list`) or a path to your own recipe .py"); r.add_argument("--out", required=True)
    g = r.add_mutually_exclusive_group()
    g.add_argument("--size", help="WxH, e.g. 1080x1920")
    g.add_argument("--formats", help="all, or a comma list of " + ",".join(FORMATS))
    r.add_argument("--palette", default=None, help="a palette name from brand/brand.json (default: its default_palette)")
    r.add_argument("--fps", type=int, default=60); r.add_argument("--duration", type=float)
    r.add_argument("--sheet", action="store_true", help="also write <out>.sheet.png (six key frames)")
    r.add_argument("--gif", action="store_true", help="also write a 480 px <out>.gif preview")
    r.add_argument("--opt", action="append", default=[], help="recipe option key=value (repeatable)")
    q = sub.add_parser("qa"); q.add_argument("mp4"); q.add_argument("holds", nargs="*", help="start-end seconds, e.g. 2.9-5.1")
    sub.add_parser("list")
    a = p.parse_args(argv)

    if a.cmd == "list":
        for k in REGISTRY: print(k)
        return 0
    if a.cmd == "qa":
        rep = Q.report(a.mp4, [tuple(map(float, h.split("-"))) for h in a.holds])
        print(json.dumps(rep, indent=2)); return 0 if rep["verdict"] == "PASS" else 2

    opts = {}
    for kv in a.opt:
        k, v = kv.split("=", 1)
        try: opts[k] = float(v)
        except ValueError: opts[k] = v
    if a.duration: opts["duration"] = a.duration
    out = Path(a.out)
    if a.formats:
        names = ["9x16", "1x1", "16x9"] if a.formats == "all" else [n.strip() for n in a.formats.split(",")]
        bad = [n for n in names if n not in FORMATS]
        if bad: p.error(f"unknown format(s) {bad}; use {', '.join(FORMATS)}")
        jobs = [(FORMATS[n], out.with_name(f"{out.stem}_{n}{out.suffix or '.mp4'}")) for n in names]
    else:
        W, H = map(int, (a.size or "1080x1080").lower().split("x")); jobs = [((W, H), out)]
    reps = [_render_one(a, opts, W, H, o) for (W, H), o in jobs]
    ok = all(r["verdict"] == "PASS" for r in reps)
    print("ALL PASS" if ok else "CHECK: read the QA lines above", file=sys.stderr)
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())

# remotion-3d: the 3D render path

A minimal Remotion + three.js template: one object carrying your logo, one continuous camera move,
one accent ring, a caption that rides the object. It renders 9:16, 1:1 and 16:9 in one run. The
skill copies it into your work folder and rewrites `src/Stage.tsx` to the approved storyboard.

## Requirements

- Node.js 18 or newer (tested with Node 20).
- About 300 MB for `node_modules`, plus ~200 MB of headless Chrome that the first render downloads.
- `ffmpeg` is NOT needed for this path (Remotion bundles its own), but the skill's self-check uses it.

## Use it by hand

```bash
rsync -a --exclude node_modules --exclude out --exclude public/brand ~/.claude/skills/actus-motion/templates/remotion-3d/ my-video/
cd my-video && npm install
BRAND_DIR=~/.claude/skills/actus-motion/brand npm run render -- my-video   # -> out/my-video_9x16.mp4, _1x1, _16x9
BRAND_DIR=~/.claude/skills/actus-motion/brand npm run dev                  # Remotion Studio, scrub the timeline
```

`npm run render -- <name> --formats 9x16,1x1` renders a subset. `OUT_DIR=<dir>` changes the output
folder. First render: a few minutes (Chrome download); after that roughly 5-15 s per format on a laptop.

## Notes

- `scripts/sync-brand.mjs` copies the brand folder into `public/brand/` before every run
  (`BRAND_DIR`, default `../../brand` when used in place inside the skill).
- Headless WebGL: `angle` by default; set `REMOTION_GL=swangle` on Linux/CI without a GPU.
- Every animated value is a pure function of `useCurrentFrame()`.
- Licence: this template is MIT. Remotion itself is free for individuals and small companies;
  bigger companies need a company licence, see https://www.remotion.dev/license.

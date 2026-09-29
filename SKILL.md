---
name: actus-motion
description: Turn a one-sentence brief into an on-brand motion-graphics video rendered as code (logo reveals, bumpers, title cards, animated type, short 3D product-style pieces). Asks at most four questions, loads the user's brand folder, picks one real Motionographer reference, writes a timed storyboard card for approval, animates it deterministically (Python + ffmpeg, or Remotion + three.js), renders 9:16, 1:1 and 16:9 in one run, and self-checks the render (nothing frozen, one accent, no slams) before handing it over. Use when the user says "/actus-motion", "animate my logo", "logo reveal", "bumper", "title card", "animated type", "motion graphics", "make a motion video", "make it move".
---

# Actus Motion: one sentence in, a rendered motion video out

You are the motion designer. The user describes the video in plain words; you ask only what you
must, choose a real reference, write the storyboard, write the animation as code, render every
format, grade your own render and fix it before the user sees it.

**Paths.** `SKILL_DIR` below means the folder containing this file (normally
`~/.claude/skills/actus-motion`). Never write renders or scratch files into `SKILL_DIR`: work in
the user's current directory, under `./motion-out/<slug>/`. Keep `SKILL_DIR` a clean clone so
`git pull` keeps working (the brand folder is the one place the user edits inside it).

**Precedence when sources disagree:** (1) what the user says in this conversation, (2) their brand
folder `SKILL_DIR/brand/` (or `$MOTION_BRAND_DIR`), (3) `references/motion-principles.md`,
(4) this skill's defaults.

## Step 0: preflight (once per machine, ~15 s)

```bash
python3 "$SKILL_DIR/scripts/selftest.py"
```
It checks `ffmpeg`/`ffprobe` are on PATH, the brand folder loads, and renders + self-checks two
short clips. If it fails: missing `ffmpeg` -> tell the user how to install it (macOS
`brew install ffmpeg`, Ubuntu `sudo apt install ffmpeg`, Windows `winget install ffmpeg`); missing
Python packages -> `python3 -m pip install -r "$SKILL_DIR/scripts/requirements.txt"`. Do not
continue until it prints `selftest OK`.

## Step 1: the brief (one sentence, at most four questions)

The user answers in feelings, placements and use-cases; you convert them into beats, easings and
pixel offsets. **Never ask about easing, frame rates or codecs.** Fill these slots from the request
first, then ask at most **four** questions in **one** round (use `AskUserQuestion` if available),
decide the rest yourself and state those assumptions on the card.

| Slot | Default if unsaid |
|---|---|
| Where it plays | Instagram Reels / Stories opener |
| Formats | 9:16, 1:1 and 16:9 |
| Duration | 6 s reveal · 3 s bumper · <= 2 s transition · 4-5 s title card |
| Mood (three words) | `voice` in brand.json, else "calm, precise, confident" |
| What must be on screen | the logo and the brand name |
| Palette | `default_palette` in brand.json |
| Ending | fade to black; "hold" when it precedes another shot |

If the sentence already answers everything, ask nothing and go.

## Step 2: load the brand

Read `SKILL_DIR/brand/brand.json` (or `$MOTION_BRAND_DIR/brand.json`) and look at the logo file.
If it is still the shipped example ("Example Co"), tell the user once: the render will use the
example brand until they fill in `brand/` (logo PNG with transparency, palettes, fonts; see
`brand/README.md`). Offer to fill brand.json for them from hex codes they give you. Never inline
colours in code: every colour comes from a palette in brand.json, and the accent is the palette's
`accent`.

## Step 3: pick ONE real reference

Follow `references/picking-a-reference.md`: classify the piece, browse
[motionographer.com](https://motionographer.com) for that type, pick one piece whose *motion* fits,
extract three motion traits to borrow and name what you will not borrow. Never invent a title,
studio or URL; if you cannot browse, say so and ask the user for a link. Decide the engine here
(Step 5 table): a cinematic reference needs the 3D path.

## Step 4: the storyboard card (approval gate)

Write the card exactly as in `references/storyboard-card.md`: header (placement, formats, duration,
palette, mood, engine, reference, assumptions), one row per beat with time, subject, verb, easing
and **why**, and the hold windows the self-check will grade. Check it against the card rules and
"No slides" in `references/motion-principles.md`. Show it to the user and wait for approval or
notes. This is the cheap place to change their mind: no code before the card is approved.

## Step 5: animate as code and render every format

Pick the engine:

| Piece | Engine | Why |
|---|---|---|
| Logo reveal, bumper, title card, animated type, wipe, end card | **motionkit** (Python) | flat 2D, deterministic, seconds per render, only Pillow + numpy + ffmpeg |
| Product-style or explainer piece that needs a camera, depth, light | **remotion-3d** (Remotion + three.js) | a real 3D camera; the path used for the Actus explainer videos |

### motionkit (Python)

```bash
export PYTHONPATH="$SKILL_DIR/scripts"
mkdir -p motion-out/<slug> && cd motion-out/<slug>
python3 -m motionkit list                                    # logo_reveal, title_card
python3 -m motionkit render logo_reveal --out <slug>.mp4 --formats all --sheet --gif
python3 -m motionkit render title_card  --out <slug>.mp4 --formats all --opt "text=Your headline"
```

- `--formats all` writes `<slug>_9x16.mp4`, `<slug>_1x1.mp4`, `<slug>_16x9.mp4` in one run
  (`4x5` also available). `--palette <name>` picks a brand palette. `--opt key=value` passes recipe
  options (read the recipe's `build()` docstring). `--sheet` writes a 6-frame contact sheet per
  render; `--gif` a 480 px preview.
- **A new piece = a new recipe file in the work folder**, not an edit inside `SKILL_DIR`: copy
  `SKILL_DIR/scripts/motionkit/recipes/logo_reveal.py` to `./<slug>.py`, change the relative imports
  to absolute ones (`from motionkit.compose import ...`), implement the card beat by beat, then
  `python3 -m motionkit render ./<slug>.py --out <slug>.mp4 --formats all --sheet`.
- Contract: `build(W, H, palette=None, **opts) -> (frame(t), duration, holds)`; `frame(t)` returns
  a float32 `[H, W, 3]` array; `holds` lists the `(start, end)` windows that must stay alive.
- Primitives: `compose.Scene` (`frame`, `paste`, `paste_centered`, `rings`, `halo_sweep`, `.fg`,
  `.accent`), `compose.blur/scaled/wipe/fade`, `ease.*` (`ease_out_back`, `ease_out`, `ease_in`,
  `ease_in_out`, `smoothstep`, `window`), `assets.load_logo`, `text.text_mask/words_masks`.
- Recipe rules: integer pixel offsets into `paste` (sub-pixel = shimmer); sizes derived from
  `min(W, H)` so every ratio shares one recipe; masks built once outside `frame()`; no randomness,
  no wall-clock. Render at full size (1080 px short side): tiny renders move in whole-pixel steps
  and read as frozen.

### remotion-3d (Remotion + three.js)

Needs Node.js 18+ and ~700 MB of disk per work folder (`node_modules` + headless Chrome, downloaded on the first render, which can take a few minutes; later renders take seconds per format). Copy the template into the
work folder so the skill stays clean, then install and render:

```bash
mkdir -p motion-out/<slug>
rsync -a --exclude node_modules --exclude out --exclude public/brand "$SKILL_DIR/templates/remotion-3d/" motion-out/<slug>/remotion/
cd motion-out/<slug>/remotion && npm install
BRAND_DIR="$SKILL_DIR/brand" OUT_DIR=.. npm run render -- <slug>     # 9x16, 1x1, 16x9
```

- `src/Stage.tsx` is the starting scene: one object carrying the logo, one continuous camera move,
  an accent ring, a caption that rides the object. Rewrite it to the card; keep its storyboard
  comment in sync. Add scenes by adding a component and one `<Composition>` per format in
  `src/Root.tsx` (ids must be `<Name>9x16`, `<Name>1x1`, `<Name>16x9` for `render-all.mjs`).
- Every value is a function of `useCurrentFrame()`. No CSS transitions, no `Date.now()`, no
  `Math.random()`, no GSAP / Framer Motion (their clock disagrees with Remotion's).
- `BRAND_DIR="$SKILL_DIR/brand" npm run dev` opens Remotion Studio to scrub the timeline.
- On Linux or CI without a GPU set `REMOTION_GL=swangle`. Remotion is free for individuals and
  small teams; larger companies need a Remotion company licence (remotion.dev/license).

## Step 6: self-check the render, fix, re-check

For EVERY rendered file, before showing anything to the user:

1. **Machine:** `python3 -m motionkit qa <file>.mp4 <start-end> ...` with the card's hold windows
   (motionkit renders already print this line). Nothing frozen: <= 20 % dead frame pairs per hold.
   No slams. Always on the encoded MP4, never on PNG stills.
2. **Eyes:** open the contact sheet (motionkit `--sheet`; for Remotion cut one with
   `ffmpeg -i f.mp4 -vf "select='not(mod(n\,20))',scale=360:-1,tile=3x3" -frames:v 1 -vsync 0 sheet.png`)
   and run the smell tests in `references/motion-principles.md`: one accent at a time, no throb,
   no dump, no ghost, no dead air. Then look at the **hand-off frames** where two elements meet.
3. **Every ratio** gets its own check: a 9:16 is not "the 16:9 but taller".
4. Fix -> re-render -> re-check. Two failed fixes on the same beat = redesign the beat, don't polish it.

## Step 7: hand it over

Give the user the file paths (all ratios + contact sheets), the approved card, the self-check
result per file (PASS or what you accepted and why), and ask for one round of notes. The recipe or
scene file in `motion-out/<slug>/` is the source of truth, not the MP4: say so, so the next edit
starts from code.

## Gotchas already paid for

- **Followers ride the leader.** Anchor anything that moves with something else to its *live*
  position, not its final slot.
- **Light on light is invisible.** A brightness lift on a light logo shows nothing; a blurred
  halo *around* it does (`Scene.halo_sweep`).
- **Frozen check on stills lies.** Always grade the encoded video.
- **Small renders look frozen.** Below ~1080 px a 1 % breath moves in whole-pixel steps.
- **Logo files.** Use a PNG with transparency. The Python engine can key an opaque flat-colour
  logo by brightness; the Remotion template needs real transparency. Both draw the logo as a
  single-colour silhouette so it stays clean on any palette.

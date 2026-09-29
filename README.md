# Actus Motion — a free Claude Code skill for AI motion videos

Describe the video in one sentence. Claude picks a real reference, writes the storyboard, animates it as code, renders every format and checks its own render before you see it. It is the exact workflow behind the Actus videos.

**Everything about it, with the video and the six steps:** https://actusapp.io/skills/claude-motion

## Install

```sh
git clone https://github.com/nakanorodriguespedro-beep/actus-motion-skill ~/.claude/skills/actus-motion
```

Then:

1. Open `~/.claude/skills/actus-motion/brand/` and drop in your logo, colours and fonts (see [brand/README.md](brand/README.md)). It ships with a neutral example brand, so you can try it first.
2. In Claude Code, type `/actus-motion` and describe the video in one sentence, for example *"a six-second logo reveal for Reels"*.

The first time, the skill runs a 15-second self-test to check your setup.

## What it does

1. **Describe the video in one sentence.** The skill asks at most four questions, in one go, and decides the rest.
2. **Claude loads the skill and your brand.** Logo, colours and fonts live in a brand folder you fill in once.
3. **It picks a real reference.** One piece from Motionographer that matches the job; it learns the motion from it.
4. **It writes the storyboard.** Every beat gets a time and a reason. You read a one-page card, not code.
5. **It writes the animation as code and renders every format.** Deterministic, so the same brief gives the same video. 9:16, 1:1 and 16:9 in one run.
6. **It checks its own render.** Nothing frozen, one accent, no slams. What fails gets fixed before you see it.

## Requirements

Always:

- [Claude Code](https://claude.com/claude-code)
- `ffmpeg` and `ffprobe` on your PATH (macOS `brew install ffmpeg` · Ubuntu `sudo apt install ffmpeg` · Windows `winget install ffmpeg`)
- Python 3.9+ with Pillow 10.1+ and numpy: `python3 -m pip install -r ~/.claude/skills/actus-motion/scripts/requirements.txt`

Per render engine (the skill picks one per video):

| Engine | For | Also needs | Speed |
|---|---|---|---|
| **motionkit** (Python) | logo reveals, bumpers, title cards, animated type | nothing else | seconds per format |
| **remotion-3d** (Remotion + three.js) | 3D, product-style and explainer pieces with a moving camera | Node.js 18+, ~700 MB disk per video folder | first render downloads headless Chrome (a few minutes); then seconds per format |

Web browsing in Claude Code helps with the reference step; without it, the skill asks you for a Motionographer link.

## What's inside

```
SKILL.md                      the workflow Claude follows, brief to hand-over
brand/                        your logo, palettes, fonts (brand.json) — fill in once
references/
  picking-a-reference.md      how it chooses one Motionographer piece and what it borrows
  storyboard-card.md          the card format: every beat has a time and a reason
  motion-principles.md        the rules the render is graded against
scripts/
  motionkit/                  the Python render engine + self-check (qa)
  selftest.py                 setup check
templates/remotion-3d/        the Remotion + three.js starting scene
```

Renders go to `./motion-out/<name>/` in whatever folder you run Claude Code from, never into the skill folder. Keep several brands side by side with `MOTION_BRAND_DIR=/path/to/brand`.

Update later with `git -C ~/.claude/skills/actus-motion pull`.

## License

MIT — see [LICENSE](LICENSE). The Remotion path uses [Remotion](https://www.remotion.dev), which is free for individuals and small companies; larger companies need a [Remotion company licence](https://www.remotion.dev/license).

Made by Pedro Rodrigues, founder of [Actus](https://actusapp.io).

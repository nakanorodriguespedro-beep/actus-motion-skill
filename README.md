# Actus Motion — a free Claude Code skill for AI motion videos

Describe the video in one sentence. Claude picks a real reference, writes the storyboard, animates it as code, renders every format and checks its own render before you see it. It is the exact workflow behind the Actus videos.

**Everything about it, with the video and the six steps:** https://actusapp.io/skills/claude-motion

## Install

```sh
git clone https://github.com/nakanorodriguespedro-beep/actus-motion-skill ~/.claude/skills/actus-motion
```

Then in Claude Code, type `/actus-motion` and describe the video you want.

## Status

The skill is being packaged for public use (the brand folder is being made generic, private paths removed). The files land here in the next few days; watch or star the repo to be told.

## What it does

1. **Describe the video in one sentence.** The skill asks at most four questions, in one go, and decides the rest.
2. **Claude loads the skill and your brand.** Logo, colours and fonts live in a brand folder you fill in once.
3. **It picks a real reference.** One piece from Motionographer that matches the job; it learns the motion from it.
4. **It writes the storyboard.** Every beat gets a time and a reason. You read a one-page card, not code.
5. **It writes the animation as code and renders every format.** Deterministic, so the same brief gives the same video. 9:16, 1:1 and 16:9 in one run.
6. **It checks its own render.** Nothing frozen, one accent, no slams. What fails gets fixed before you see it.

## Requirements

Claude Code and `ffmpeg` on your PATH. The README will list anything else, per render engine, once the files land.

## License

MIT — see [LICENSE](LICENSE).

Made by Pedro Rodrigues, founder of [Actus](https://actusapp.io).

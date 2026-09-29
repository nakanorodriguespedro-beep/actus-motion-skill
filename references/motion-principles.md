# Motion principles: the rules every storyboard and every render is graded against

Distilled from Material motion easing, Emil Kowalski's interface-animation writing and Disney's
twelve principles. They are not optional: the storyboard card applies them, the self-check grades them.

## The discipline

1. **Ease-out in, ease-in out.** Things ARRIVE decelerating (fast start, soft landing) and LEAVE
   accelerating. Linear motion reads as robotic; a symmetric ease reads as floaty.
2. **Calm overshoot.** Back-ease with `s = 1.35` (or a spring with damping 11-14, stiffness ~120,
   mass ~0.8). Above 1.7 is a toy; no overshoot at all is a corpse.
3. **Stagger, don't dump.** Multi-part entries cascade 0.05-0.15 s apart so the eye is led through
   the composition. Everything landing on one frame reads as a slide deck.
4. **One accent per beat.** At most ONE element in the accent colour is live at a time. Accent
   inflation is how "premium" dies first.
5. **Nothing frozen.** Every hold of 1 s or more carries exactly ONE faint idle: a breathe
   (<= 1.5 % scale), a slow drift, a slow camera push or turn. Never two at once, never a throb.
6. **Follow-through.** Exits mirror entrances. Anything that leaves does so on purpose (fade,
   slide, tilt away); nothing just vanishes.
7. **Followers ride the leader.** If B moves with A, compute B from A's *live* position, not from
   A's final slot, or B will peek out on the wrong side mid-move.
8. **Secondary action serves the primary.** A ripple on landing supports "arrival". Motion that
   carries no meaning gets deleted.
9. **Deterministic.** Every value is a pure function of time (Python: `t`; Remotion:
   `useCurrentFrame()`). No wall-clock, no `Math.random()`, no CSS transitions, no GSAP/Framer
   Motion inside Remotion: they run on their own clock and flicker when rendered frame by frame.

## No slides

A beat whose job is done by a headline is a slide, not motion. Banned: the *number + bold
headline + subtitle* card; text blocks that fade in / hold / fade out in sequence; "chapter"
labels; a decorative visual parked beside the text. Instead:

- **The object performs the step.** Every step is an action the hero object does on screen (it
  scans, splits, assembles, lights up). If you can't show the step, cut it; don't caption it.
- **Captions ride the object.** One short line per step, attached to the part it describes and
  moving with it. Open with a hook line. Too little text is also a failure: the viewer still needs
  the story.
- **The camera moves.** One continuous shot (push-in, orbit, rack focus) carries the chapters.
- **Judge against the reference, not the brief.** If the reference has no text cards, neither do we.

## Smell tests (run on the contact sheet and the video)

| Test | Question | Fail |
|---|---|---|
| **Throb** | Does anything visibly change SIZE across idle frames? | > ~3 % scale oscillation |
| **Dump** | Do 3+ elements land on the same frame? | yes |
| **Corpse** | Is any held beat pixel-identical across two idle samples? | machine-checked (see below) |
| **Confetti** | Is there motion you can't explain in one sentence of meaning? | yes |
| **Slam** | Does anything arrive at full opacity/scale in under 4 frames without intent? | machine-checked |
| **Drift** | Does the composition's optical centre wander off-centre during a hold? | yes |
| **Ghost** | Is any "de-emphasised" element below 35 % opacity? | reads as a bug |
| **Accent count** | More than one accent-coloured element live at once? | yes |
| **Dead air** | Is the canvas ever empty while a caption is on screen? | yes |

## What the machine checks vs. what your eyes check

`python3 -m motionkit qa <mp4> <start-end> ...` (from `scripts/`) measures, on the ENCODED video:
- **Nothing frozen (corpse):** within each hold window, frame pairs sampled at 12 fps; a pair is
  "dead" when < 0.1 % of pixels (analysed at ~270 px on the short side) moved by > 3 luma levels.
  A hold passes with <= 20 % dead pairs.
- **No slams:** a luma jump 8x the clip's average, completed right after >= 4 still frames.

Your eyes check the rest on the contact sheet: one accent, throb, dump, confetti, drift, ghost,
dead air, and the **hand-off frames**, the 2-3 frames where two elements meet (a mark becoming a
lockup, a wipe crossing a mark). That is where most defects live.

Never grade on PNG stills: they carry no compression noise and the frozen check lies on them.

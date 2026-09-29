# The storyboard card: the contract before any code

Write this BEFORE touching code. It is what the user approves and what the code implements line
by line. One beat per row; every beat names its subject, its verb, its easing and **why** it is there.

```
# <slug> — storyboard card
Plays: <placement> · Formats: 9:16, 1:1, 16:9 · Duration: 6.0 s · Palette: dark · Mood: <3 words>
Engine: motionkit (recipe: logo_reveal) | remotion-3d (scene: Stage)
Reference: <title> · <studio> · <motionographer url> — borrowing: <3 motion traits>; not borrowing: <…>
Assumptions: <anything you decided instead of asking>

| t (s)      | subject   | verb                                     | ease          | why                            |
|------------|-----------|------------------------------------------|---------------|--------------------------------|
| 0.05–0.90  | mark      | drops in from above, settles from blur   | out-back 1.35 | arrival; calm overshoot        |
| 0.75–1.85  | rings ×2  | expand + fade from the landing point     | quadratic     | impact; the one accent         |
| 1.60–2.70  | mark      | rises to its lockup slot                 | in-out        | makes room for the name        |
| 1.75–2.80  | name      | wipes in L→R, de-blurs                   | in-out        | rides the mark's live position |
| 2.70–5.35  | lockup    | breathes (1.2 % scale, 3.2 s period)     | sine          | nothing frozen                 |
| 3.10–4.30  | halo      | soft glow sweeps across                  | sine          | light passes, no new colour    |
| 5.35–5.95  | frame     | fades to black                           | smoothstep    | clean cut                      |

Self-check holds: 2.9–5.15
```

## Rules the card must satisfy

- Arrive decelerating (`out`, `out-back`), leave accelerating (`in`).
- Overshoot `s = 1.35` unless the mood explicitly says playful (max 1.7).
- Multi-part entries stagger 0.05–0.15 s.
- One accent per beat; name which row is the accent.
- Every hold ≥ 1 s names its ONE idle (breathe, drift, camera push/turn).
- Every exit is designed (fade, slide, tilt), never a vanish.
- Followers are computed from the leader's live position.
- No slide beats (see `motion-principles.md` → No slides).
- List the hold windows the self-check will grade.

## Defaults when the brief doesn't say

| Slot | Default |
|---|---|
| Where it plays | Instagram Reels / Stories opener |
| Formats | 9:16, 1:1 and 16:9 |
| Duration | 6 s reveal · 3 s bumper · ≤ 2 s transition · 4–5 s title card |
| Mood | brand.json `voice`, else "calm, precise, confident" |
| On screen | the logo and the brand name |
| Palette | brand.json `default_palette` |
| Ending | fade to black (cuts clean); "hold" when it precedes another shot |

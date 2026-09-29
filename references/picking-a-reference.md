# Picking one real reference from Motionographer

Every piece starts from a real reference, never from a blank page. Source:
[motionographer.com](https://motionographer.com), a long-running curated showcase of motion design.
`/quickie/` posts are short pieces; full posts often include breakdowns.

## Steps

1. **Classify the piece:** logo reveal / bumper · product or feature promo · data story ·
   animated type / title card · transition · explainer.
2. **Browse for that type** and pick **one** piece (two at most) whose *motion* fits the job, not
   whose subject matches. Rules of thumb:
   - Product / feature promo -> premium product films (macro detail, cinematic light, sound-led).
   - Data story -> infographic pieces where numbers are built, not faded in.
   - Title card / animated type -> kinetic-typography pieces.
   - Logo reveal -> ident and brand-refresh pieces.
3. **Extract what to borrow, in 3 bullets, in motion terms:** pacing and cuts; the camera or
   reveal verb; light and texture; how type behaves; how motion syncs to sound.
4. **Name what you do NOT borrow:** their palette, logo, footage, typefaces. The user's brand
   folder always wins.
5. **Put it on the storyboard card:**
   `Reference: <title> · <studio> · <url> — borrowing: <trait 1>; <trait 2>; <trait 3>`
   The user approves the reference together with the card.

## If you can't browse

If web access is unavailable, say so, ask the user to paste a Motionographer link they like, or
proceed with a named, clearly-described motion style and flag on the card that no live reference
was checked. Never invent a title, studio or URL.

## Engine check (decide before writing the card)

The Python engine (`motionkit`) is a flat 2D compositor: great for logo reveals, bumpers, title
cards, animated type and transitions. It has no camera, depth or real light. If the reference is
cinematic (product film, macro, a lab stand, an orbiting camera), use the Remotion + three.js
template (`templates/remotion-3d/`) and say so on the card. Forcing a cinematic reference into a
2D engine produces text-driven slides.

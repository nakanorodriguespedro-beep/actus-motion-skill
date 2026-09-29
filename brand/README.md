# Your brand folder

Fill this in once; every video after that is on-brand without you saying so. It ships with a
neutral example brand ("Example Co") so the skill renders out of the box.

| File | What to put there |
|---|---|
| `logo.png` | Your logo or mark. Best: a PNG with a transparent background, 1000 px or larger. An opaque PNG also works if the logo is a flat colour on a flat background (it is keyed by brightness). |
| `brand.json` | Name, tagline, palettes, fonts, voice (see below). |
| `fonts/` | Your font files (`.ttf` / `.otf`). Reference them from `brand.json`. |

## brand.json

```json
{
  "name": "Example Co",                      // shown under the mark in the logo reveal
  "tagline": "One sentence in. Motion out.", // default headline for title cards
  "logo": "logo.png",                        // path relative to this folder, or null
  "fonts": { "display": "fonts/YourFont-SemiBold.ttf", "body": "fonts/YourFont-Regular.ttf" },
  "palettes": {
    "dark":  { "bg": "#0E1013", "bg_center": "#1A1E23", "fg": "#F3F1EC", "accent": "#FF6B3D" },
    "light": { "bg": "#F3F1EC", "bg_center": "#FFFFFF", "fg": "#16181C", "accent": "#E4572E" }
  },
  "default_palette": "dark",
  "voice": "calm, precise, confident"         // the default mood the skill writes the storyboard in
}
```

(JSON has no comments: the ones above are only explanation.)

- **Palettes.** `bg` is the frame background, `bg_center` a soft radial lift in the middle (use the
  same value as `bg` for a flat ground), `fg` the logo and type colour, `accent` the ONE accent
  colour. Add as many palettes as you like; pick one per render with `--palette <name>`.
- **Fonts.** `null` falls back to a built-in font, which is fine for drafts but not for shipping.
  Check your font licence allows use in video.
- **Logo colour.** Both engines draw the logo as a single-colour silhouette taken from the palette
  (that is what keeps it clean on any ground). The Remotion template needs a PNG with real
  transparency; the Python engine can also key an opaque flat-colour logo.

Keep several brands side by side by pointing `MOTION_BRAND_DIR` (Python) / `BRAND_DIR` (Remotion)
at another folder with the same layout.

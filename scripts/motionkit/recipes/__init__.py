"""Recipes: each module exposes `build(W, H, palette, **opts) -> (frame_fn, duration, holds)`.
`holds` lists the (start, end) windows, in seconds, that must stay alive for the self-check.
Register a new recipe here by module path."""
REGISTRY = {
    "logo_reveal": "motionkit.recipes.logo_reveal",
    "title_card": "motionkit.recipes.title_card",
}

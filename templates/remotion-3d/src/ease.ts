// Every animated value is a pure function of the frame: no CSS transitions, no Date.now(), no Math.random().
export const clamp = (x: number) => Math.min(1, Math.max(0, x));
export const win = (t: number, start: number, dur: number) => clamp((t - start) / dur);
export const out = (x: number) => 1 - Math.pow(1 - clamp(x), 3);            // arrive decelerating
export const inn = (x: number) => Math.pow(clamp(x), 3);                    // leave accelerating
export const inOut = (x: number) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
export const outBack = (x: number, s = 1.35) => { x = clamp(x); return 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2); };
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;

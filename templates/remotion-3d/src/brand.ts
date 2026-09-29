// The brand, as synced from the skill's brand/ folder by scripts/sync-brand.mjs.
import brandJson from "../public/brand/brand.json";
import { staticFile } from "remotion";

type Palette = { bg: string; bg_center?: string; fg: string; accent?: string };
type Brand = {
  name: string;
  tagline?: string;
  logo: string | null;
  fonts?: { display?: string | null; body?: string | null };
  palettes: Record<string, Palette>;
  default_palette?: string;
};

export const brand = brandJson as unknown as Brand;

export const palette = (name?: string) => {
  const key = name ?? brand.default_palette ?? Object.keys(brand.palettes)[0];
  const p = brand.palettes[key];
  if (!p) throw new Error(`palette "${key}" not in brand.json`);
  return { bg: p.bg, bgCenter: p.bg_center ?? p.bg, fg: p.fg, accent: p.accent ?? p.fg };
};

export const logoUrl = brand.logo ? staticFile(`brand/${brand.logo}`) : null;
export const displayFontUrl = brand.fonts?.display ? staticFile(`brand/${brand.fonts.display}`) : null;

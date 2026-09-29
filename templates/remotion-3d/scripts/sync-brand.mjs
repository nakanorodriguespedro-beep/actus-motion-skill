// Copies the skill's brand folder (../../brand, or $BRAND_DIR) into public/brand so Remotion can
// serve the logo and fonts with staticFile(). Runs before every dev / render / typecheck.
import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const src = resolve(process.env.BRAND_DIR ?? resolve(here, "../../../brand"));
const dest = resolve(here, "../public/brand");
if (!existsSync(resolve(src, "brand.json"))) {
  console.error(`No brand.json in ${src}. Fill in the skill's brand/ folder (see brand/README.md) or set BRAND_DIR.`);
  process.exit(1);
}
rmSync(dest, { recursive: true, force: true });
mkdirSync(dest, { recursive: true });
cpSync(src, dest, { recursive: true });
console.log(`brand: ${src} -> public/brand`);

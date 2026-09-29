// Renders every format of one scene in one run:  npm run render -- [name] [--formats 9x16,1x1,16x9]
// Output: $OUT_DIR (default ./out)/<name>_<ratio>.mp4. Then run the skill's self-check on each file.
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const fi = args.indexOf("--formats");
const formats = (fi >= 0 ? args[fi + 1] : "9x16,1x1,16x9").split(",");
const name = args.find((a, i) => !a.startsWith("--") && i !== fi + 1) ?? "stage";
const outDir = resolve(process.env.OUT_DIR ?? resolve(root, "out"));
mkdirSync(outDir, { recursive: true });

execFileSync("node", [resolve(root, "scripts/sync-brand.mjs")], { stdio: "inherit" });
for (const f of formats) {
  const id = `Stage${f}`;            // composition ids in src/Root.tsx
  const out = resolve(outDir, `${name}_${f}.mp4`);
  console.log(`\nrender ${id} -> ${out}`);
  execFileSync("npx", ["remotion", "render", "src/index.ts", id, out], { cwd: root, stdio: "inherit" });
}
console.log(`\nDone. Self-check each file:  PYTHONPATH=<skill>/scripts python3 -m motionkit qa <file> <start-end ...>`);

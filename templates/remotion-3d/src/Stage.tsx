/**
 * Stage: the brand mark on one 3D object, one continuous camera move, every format.
 * A minimal starting point: copy this file, rewrite the storyboard, keep the rules.
 *
 * Storyboard card (5 s):
 * | t (s)     | subject  | verb                                              | ease          | why                          |
 * |-----------|----------|---------------------------------------------------|---------------|------------------------------|
 * | 0.00-5.00 | camera   | one continuous push-in with a slight orbit        | in-out        | the camera carries the piece |
 * | 0.05-1.10 | slab     | drops in from above carrying the logo, settles    | out-back 1.35 | arrival; calm overshoot      |
 * | 0.85-1.85 | ring     | accent ring expands and fades behind the slab     | out           | impact; the ONE accent       |
 * | 1.20-2.10 | caption  | words rise in, 0.08 s apart, riding under the slab| out           | stagger leads the eye        |
 * | 1.10-4.20 | slab     | slow turn (idle)                                  | sine          | nothing frozen               |
 * | 4.20-5.00 | slab+cap | tilt back, sink and fade                          | in            | leaves accelerating          |
 */
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { useEffect, useMemo, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, useCurrentFrame, useVideoConfig } from "remotion";
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/examples/jsm/geometries/RoundedBoxGeometry.js";
import { brand, displayFontUrl, logoUrl, palette } from "./brand";
import { inn, inOut, lerp, out, outBack, win } from "./ease";

export const STAGE_SECONDS = 5;
const FOV = 35;
const SLAB = 2.4;                 // slab width = height (scene units)
const EXIT = 4.2;

// The logo as a single-colour silhouette (same rule as the Python engine): needs a PNG with transparency.
function useLogoTexture(url: string | null, tint: string) {
  const [tex, setTex] = useState<THREE.Texture | null>(null);
  const [handle] = useState(() => (url ? delayRender("logo") : null));
  useEffect(() => {
    if (!url || handle === null) return;
    const img = new Image();
    img.onload = () => {
      const c = document.createElement("canvas");
      c.width = img.width; c.height = img.height;
      const ctx = c.getContext("2d")!;
      ctx.drawImage(img, 0, 0);
      ctx.globalCompositeOperation = "source-in";
      ctx.fillStyle = tint; ctx.fillRect(0, 0, c.width, c.height);
      const t = new THREE.CanvasTexture(c);
      t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8;
      setTex(t); continueRender(handle);
    };
    img.onerror = () => { console.error(`could not load ${url}`); continueRender(handle); };
    img.src = url;
  }, [url, tint, handle]);
  return tex;
}

function useDisplayFont() {
  const [handle] = useState(() => (displayFontUrl ? delayRender("font") : null));
  useEffect(() => {
    if (!displayFontUrl || handle === null) return;
    const face = new FontFace("BrandDisplay", `url(${displayFontUrl})`);
    face.load().then((f) => { (document.fonts as unknown as Set<FontFace>).add(f); continueRender(handle); })
      .catch((e) => { console.error(e); continueRender(handle); });
  }, [handle]);
}

// Distance at which the slab fits the frame in any aspect ratio.
const fitDistance = (aspect: number) => {
  const k = 2 * Math.tan(THREE.MathUtils.degToRad(FOV / 2));
  return Math.max((SLAB / 0.45) / k, (SLAB / 0.5) / (k * aspect));
};

function Camera({ t, dist }: { t: number; dist: number }) {
  const camera = useThree((s) => s.camera);
  const u = inOut(t / STAGE_SECONDS);
  const z = dist * lerp(1.12, 0.96, u);
  const a = lerp(-0.22, 0.14, u);                     // orbit angle (radians)
  camera.position.set(Math.sin(a) * z, lerp(0.35, 0.1, u), Math.cos(a) * z);
  camera.lookAt(0, 0, 0);
  return null;
}

export const Stage: React.FC<{ paletteName?: string }> = ({ paletteName }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const t = frame / fps;
  const p = palette(paletteName);
  const logo = useLogoTexture(logoUrl, p.bg);
  useDisplayFont();
  const geo = useMemo(() => new RoundedBoxGeometry(SLAB, SLAB, 0.18, 6, 0.16), []);
  const dist = fitDistance(width / height);

  // slab
  const drop = outBack(win(t, 0.05, 1.05));
  const exit = inn(win(t, EXIT, 0.8));
  const idle = Math.sin((t - 1.1) * 2 * Math.PI / 6) * 0.12 * out(win(t, 1.1, 0.8));
  const slabY = lerp(4.5, 0, drop) - exit * 0.6;
  const slabOpacity = Math.min(win(t, 0.05, 0.25), 1 - exit);

  // accent ring (the one accent)
  const r = out(win(t, 0.85, 1.0));
  const ringOpacity = t > 0.85 && t < 1.85 ? (1 - r) * 0.9 : 0;

  // caption rides the slab: project its bottom edge to screen space
  const pxPerUnit = height / (2 * dist * Math.tan(THREE.MathUtils.degToRad(FOV / 2)));
  const capY = height / 2 + (SLAB / 2 + 0.3 - slabY) * pxPerUnit;
  const words = (brand.tagline || brand.name).split(" ");
  const capPx = Math.round(Math.min(width, height) * 0.052);

  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at center, ${p.bgCenter} 0%, ${p.bg} 70%)` }}>
      <ThreeCanvas width={width} height={height} camera={{ fov: FOV, near: 0.1, far: 100 }} gl={{ antialias: true }}>
        <Camera t={t} dist={dist} />
        <ambientLight intensity={0.9} />
        <directionalLight position={[3, 4, 6]} intensity={2.2} />
        <directionalLight position={[-4, -1, 3]} intensity={0.6} />
        <group position={[0, slabY, 0]} rotation={[-exit * 0.5, idle, 0]}>
          <mesh geometry={geo}>
            <meshStandardMaterial color={p.fg} roughness={0.35} metalness={0.05} transparent opacity={slabOpacity} />
          </mesh>
          {logo ? (
            <mesh position={[0, 0, 0.095]}>
              <planeGeometry args={[SLAB * 0.62, SLAB * 0.62]} />
              <meshBasicMaterial map={logo} transparent opacity={slabOpacity} toneMapped={false} />
            </mesh>
          ) : null}
        </group>
        <mesh position={[0, 0, -0.4]} scale={0.8 + r * 1.6}>
          <ringGeometry args={[SLAB * 0.72, SLAB * 0.75, 96]} />
          <meshBasicMaterial color={p.accent} transparent opacity={ringOpacity} toneMapped={false} />
        </mesh>
      </ThreeCanvas>
      <div style={{ position: "absolute", left: 0, right: 0, top: capY, display: "flex", flexWrap: "wrap", justifyContent: "center", padding: "0 7%",
        gap: capPx * 0.28, fontFamily: displayFontUrl ? "BrandDisplay" : "system-ui, -apple-system, Helvetica, Arial, sans-serif",
        fontSize: capPx, fontWeight: 600, color: p.fg, letterSpacing: "-0.01em" }}>
        {words.map((w, i) => {
          const u = out(win(t, 1.2 + i * 0.08, 0.6));
          return (
            <span key={i} style={{ opacity: Math.min(u, 1 - exit), transform: `translateY(${(1 - u) * capPx * 0.5}px)`,
              filter: `blur(${(1 - u) * 6}px)` }}>{w}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

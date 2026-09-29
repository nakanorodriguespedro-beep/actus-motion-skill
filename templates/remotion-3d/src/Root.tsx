import { Composition } from "remotion";
import { Stage, STAGE_SECONDS } from "./Stage";

export const FPS = 30;

// One scene, three formats. The scene reads the frame size and reframes itself; a 9:16 is not
// "the 16:9 but taller". Add a scene = add a component + one <Composition> per format.
export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Stage9x16" component={Stage} durationInFrames={FPS * STAGE_SECONDS} fps={FPS} width={1080} height={1920} defaultProps={{}} />
    <Composition id="Stage1x1" component={Stage} durationInFrames={FPS * STAGE_SECONDS} fps={FPS} width={1080} height={1080} defaultProps={{}} />
    <Composition id="Stage16x9" component={Stage} durationInFrames={FPS * STAGE_SECONDS} fps={FPS} width={1920} height={1080} defaultProps={{}} />
  </>
);

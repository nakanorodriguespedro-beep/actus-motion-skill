// All options: https://www.remotion.dev/docs/config
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// three.js needs WebGL in headless Chrome. "angle" works on macOS/Windows with a GPU;
// on a Linux box or CI without a GPU use "swangle" (software, slower).
Config.setChromiumOpenGlRenderer((process.env.REMOTION_GL as "angle" | "swangle" | undefined) ?? "angle");

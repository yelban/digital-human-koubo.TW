import React from "react";
import { Composition, getInputProps, staticFile } from "remotion";
import { Episode } from "./Episode";
import type { Timeline } from "./lib/types";
import timeline from "../public/timeline.json";

// timeline.json 由 scripts/build_timeline.py 寫入 public/；--props 可覆蓋角標文字與起止段（試渲染用）
export const Root: React.FC = () => {
  const tl = timeline as unknown as Timeline;
  const { fps, width, height, duration } = tl.meta;
  const props = getInputProps() as { badge?: string };
  return (
    <Composition id="Episode" component={Episode} fps={fps} width={width} height={height}
                 durationInFrames={Math.max(1, Math.round(duration * fps))}
                 defaultProps={{ tl, badge: props.badge ?? (tl.meta as any).badge }} />
  );
};

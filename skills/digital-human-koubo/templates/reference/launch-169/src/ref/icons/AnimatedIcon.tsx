// 逐幀播放 lucide-animated 圖示：在 at 幀觸發原圖示的 startAnimation()，之後按幀號求值。
// <AnimatedIcon name="rocket" at={at(4)} size={120} color="#fff" />
//  - at：整片絕對幀（在 <Sequence> 裡傳局部幀也可以，只要和 useCurrentFrame 同一座標）
//  - stop：可選，在該幀呼叫 stopAnimation()（回到 normal）
//  - cycles：原圖示裡無限循環的動畫播幾輪，預設 1（播一次後停住，符合「只在接觸幀動一次」）
//  - strokeWidth：預設 1.75，與 skill 的 Lucide 規範一致
import React, { useEffect, useRef, useState } from "react";
import { continueRender, delayRender, useCurrentFrame } from "remotion";
import { useVideoConfig } from "remotion";
import { IconScope, drain, type Recorder } from "./motion-shim";
import { ICONS, type IconName } from "./la";

export const AnimatedIcon: React.FC<{
  name: IconName;
  at: number;
  stop?: number;
  size?: number;
  color?: string;
  strokeWidth?: number;
  cycles?: number;
  style?: React.CSSProperties;
}> = ({ name, at, stop, size = 96, color = "currentColor", strokeWidth = 1.75, cycles = 1, style }) => {
  const Icon = ICONS[name] as any;
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const rec = useRef<Recorder>({ vt: 0, active: false }).current;
  const handle = useRef<any>(null);
  const done = useRef(false);
  const [, bump] = useState(0);
  const [h] = useState(() => delayRender(`AnimatedIcon ${name}`));

  useEffect(() => {
    if (done.current) return;
    done.current = true;
    (async () => {
      rec.active = true;
      rec.vt = 0;
      const stopT = stop === undefined ? Infinity : (stop - at) / fps;
      handle.current?.startAnimation?.();
      await drain(rec, stopT);
      if (stop !== undefined) {
        rec.queue = [];
        rec.vt = stopT;
        handle.current?.stopAnimation?.();
        await drain(rec);
      }
      rec.active = false;
      bump((n) => n + 1);
      continueRender(h);
    })();
  }, []);

  const cls = `ai-${name}`;
  return (
    <IconScope.Provider value={{ rec, t: (frame - at) / fps, cycles }}>
      <style>{`.${cls} svg{stroke-width:${strokeWidth}px;overflow:visible}`}</style>
      <div className={cls} style={{ width: size, height: size, color, lineHeight: 0, ...style }}>
        <Icon ref={handle} size={size} />
      </div>
    </IconScope.Provider>
  );
};

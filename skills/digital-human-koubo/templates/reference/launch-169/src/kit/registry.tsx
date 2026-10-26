// 包裝元件註冊表：按名字呼叫元件（edit.json / brief.json 裡的 "pack" 列表直接用）。
// 每條：{ "use": "Counter", "at": "3:積分", "until": "3:end", ...元件參數 }
// 時間：任何叫 at / until 的欄位（包括數組裡巢狀的，如 words[].at、pins[].at、camera[].at）都可以寫 "段:詞"，由呼叫方傳入的 T() 換成秒。
// 直式 9:16 時，沒寫位置參數的元件自動換成直式預設位置（VERT）。
import React from "react";
import { AbsoluteFill } from "remotion";
import { useT } from "./core";
import { FreezeFrame, HandDraw, Highlight, ZoomFocus } from "./Annotate";
import { ChapterCard, Countdown, Counter, LowerThird, RetentionCaption, SourceTag, SpecCard } from "./Text";
import { CompareWipe, Danmaku, PaperCollage, ProgressChapters, ReactionPop, TeaserColdOpen } from "./Overlay";
import { MapRoute } from "./Map";
import { ArchiveCards, BarCompare, CalloutPill, DocFocus, GhostWord, LeaderLabel, LineDraw, PunchInHost, RecapBoard, SearchTyping, SlamText, TornStrip, TypedNameTag } from "./Explain";
import { NumberSpike, ProgressTracker, ReviewCards, WordStack } from "./Beast";
import { GlassPanel, KeywordStack, Odometer, SourceDoc } from "./Polish";
import { TextBehind } from "./Depth";
import { Aside, ColdOpenFreeze, EvidenceCard, GlitchInterstitial, HostFloaters, MemeWindow, NamePlate, PollPop, TiltLine } from "./Wangan";

export const PACK: Record<string, React.FC<any>> = {
  RetentionCaption, ZoomFocus, HandDraw, FreezeFrame, Highlight, LowerThird, SourceTag, Counter, Countdown, ChapterCard, SpecCard,
  Danmaku, ReactionPop, ProgressChapters, TeaserColdOpen, CompareWipe, PaperCollage, MapRoute,
  MemeWindow, ColdOpenFreeze, EvidenceCard, PollPop, GlitchInterstitial, NamePlate, HostFloaters, Aside, TiltLine,
  DocFocus, TypedNameTag, PunchInHost, RecapBoard, SearchTyping, CalloutPill, LeaderLabel, LineDraw, BarCompare, GhostWord, SlamText, TornStrip, ArchiveCards,
  NumberSpike, ProgressTracker, ReviewCards, WordStack,
  KeywordStack, GlassPanel, Odometer, SourceDoc, TextBehind,
};
/** 直式預設位置（1080×1920） */
const VERT: Record<string, Record<string, any>> = {
  RetentionCaption: { y: 1180, size: 92 },
  ZoomFocus: { box: { x: 40, y: 420, w: 1000, h: 1000 } },
  LowerThird: { x: 60, y: 1300 },
  SourceTag: { y: 1780 },
  Counter: { y: 720, size: 190 },
  Countdown: { x: 640, y: 270 },
  SpecCard: { x: 90, y: 880 },
  Danmaku: { top: 320, width: 1080, lanes: 6 },
  ReactionPop: { x: 640, y: 640, size: 280 },
  CompareWipe: { box: { x: 40, y: 420, w: 1000, h: 1100 } },
  NamePlate: { x: 60, y: 1250, qx: 80, qy: 420 },
  PollPop: { qy: 330 },
  KeywordStack: { x: 90, y: 1000 },
  GlassPanel: { x: 76, y: 980 },
  Odometer: { y: 760 },
  TextBehind: { crop: 60, y: 0.28 },
};
export type PackItem = { use: string; [k: string]: any };
const walk = (v: any, T: (r: any) => number, key = ""): any => {
  if (Array.isArray(v)) return v.map((x) => walk(x, T));
  if (v && typeof v === "object") return Object.fromEntries(Object.entries(v).map(([k, x]) => [k, walk(x, T, k)]));
  if ((key === "at" || key === "until") && (typeof v === "string" || typeof v === "number")) return T(v);
  return v;
};
/** 一層包裝：items 裡每條按 use 找元件渲染。T 把 "段:詞" 換成秒（不傳就只認數字秒）。 */
export const PackLayer: React.FC<{ items: PackItem[]; T?: (r: any) => number }> = ({ items, T = (r) => Number(r) }) => {
  const { W, H, t } = useT();
  const vertical = H > W;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {items.map((it, k) => {
        const Comp = PACK[it.use];
        if (!Comp) throw new Error(`沒有包裝元件「${it.use}」，可用：${Object.keys(PACK).join("、")}`);
        const { use, ...props } = it;
        const p = walk({ ...(vertical ? VERT[use] ?? {} : {}), ...props }, T);
        if (use === "Highlight") return null; // 熒光筆要包在文字外面用，不能單獨疊層
        // 可見視窗：有頂層 at 的條目只在 [at, until] 裡渲染；沒寫 until 就用 at + (dur ?? 0) + hold（預設 3.5 秒）
        if (typeof p.at === "number") {
          const end = typeof p.until === "number" ? p.until : p.at + (typeof p.dur === "number" ? p.dur : 0) + (p.hold ?? 3.5);
          if (t < p.at - 0.1 || t > end) return null;
        }
        return <Comp key={k} {...p} />;
      })}
    </AbsoluteFill>
  );
};
export { Highlight };

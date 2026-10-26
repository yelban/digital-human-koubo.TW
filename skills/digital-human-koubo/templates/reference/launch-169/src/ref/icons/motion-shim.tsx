// motion/react 的逐幀替身：讓 lucide-animated（pqoqubbw/icons, MIT）的圖示在 Remotion 裡按幀號渲染。
// 編排（variants、controls.start、await 串聯、staggerChildren、delay、repeat）在這裡重寫；
// 數值計算直接用 motion-dom 自己的生成器（keyframes / spring / mix）和 buildSVGAttrs，
// 所以緩動、彈簧、預設過渡、SVG 描邊與 transform-origin 都與原庫一致。
// 用法見 AnimatedIcon.tsx；不要在別處直接 import 本檔案的 motion。
import React, { createContext, forwardRef, useContext, useMemo, useRef } from "react";
import {
  buildHTMLStyles,
  buildSVGAttrs,
  calcGeneratorDuration,
  getDefaultTransition,
  getFinalKeyframe,
  getValueTransition,
  isTransitionDefined,
  keyframes as keyframesGen,
  mix,
  spring as springGen,
  transformProps,
} from "motion-dom";
import { cubicBezier, easeInOut, easeOut } from "motion-utils";

export { cubicBezier, easeInOut, easeOut };
export type Variants = Record<string, any>;
export type Variant = any;
export type Transition = any;

// ---------- 時鐘與錄製 ----------

// 錄製：startAnimation() 裡的 controls.start 按虛擬時間記成事件；
// 每個 await 按「這段動畫結束的虛擬時間」進佇列，由 drain() 按時間先後喚醒——
// 併發的 async 流程（Promise.all 裡一路長一路短）也能各自拿到正確的時間
export type Recorder = { vt: number; active: boolean; queue?: { time: number; seq: number; fn: () => void }[]; seq?: number };
const flush = () => new Promise((r) => setTimeout(r, 0));
export async function drain(rec: Recorder, until = 60) {
  for (let k = 0; k < 4; k++) await flush();
  let guard = 0;
  while (rec.queue?.length && guard++ < 500) {
    rec.queue.sort((x, y) => x.time - y.time || x.seq - y.seq);
    const e = rec.queue.shift()!;
    if (e.time > until) break;
    rec.vt = e.time;
    e.fn();
    for (let k = 0; k < 4; k++) await flush();
  }
}
export type Scope = { rec: Recorder; t: number; cycles: number };
export const IconScope = createContext<Scope | null>(null);

// 確定性隨機數：圖示原始碼裡的 Math.random() 在 vendor 時被替換成它
let seed = 1;
export const __rand = () => {
  seed = (seed * 16807) % 2147483647;
  return (seed - 1) / 2147483646;
};

type Def = string | Record<string, any> | ((custom: any) => any);
type Ev = { def: Def; t: number; instant?: boolean; override?: any };
type Member = { duration: (def: Def, override?: any) => number };

export class Controls {
  __isControls = true;
  events: Ev[] = [];
  members = new Map<object, Member>();
  constructor(private scopeRef: { current: Scope | null }) {}
  private push(def: Def, instant: boolean, override?: any) {
    const rec = this.scopeRef.current?.rec;
    if (!rec?.active) return Promise.resolve() as Promise<void>;
    const t0 = rec.vt;
    this.events.push({ def, t: t0, instant, override });
    const dur = instant ? 0 : this.durationOf(def, override);
    // 被 await / .then 時才把虛擬時鐘推進到這段動畫結束，模擬「等動畫播完再下一步」
    const p: any = {
      then(onF?: () => any, onR?: (e: any) => any) {
        if (!Number.isFinite(dur)) return new Promise(() => {});
        const q = (rec.queue ??= []);
        return new Promise<void>((res) => q.push({ time: t0 + dur, seq: (rec.seq = (rec.seq ?? 0) + 1), fn: res })).then(onF, onR);
      },
      catch: () => p,
      finally: (f?: () => any) => p.then(f),
    };
    return p as Promise<void>;
  }
  // 第二個參數與 motion 相同：transitionOverride，整體替換目標裡的 transition
  start(def: Def, override?: any) {
    return this.push(def, false, override);
  }
  set(def: Def) {
    this.push(def, true);
  }
  stop() {}
  mount() {
    return () => {};
  }
  durationOf(def: Def, override?: any) {
    let d = 0;
    this.members.forEach((m) => (d = Math.max(d, m.duration(def, override))));
    return d;
  }
}

export const useAnimation = () => {
  const scope = useContext(IconScope);
  const ref = useRef<Scope | null>(scope);
  ref.current = scope;
  return useMemo(() => new Controls(ref), []);
};
export const useAnimationControls = useAnimation;

export const AnimatePresence: React.FC<{ children?: React.ReactNode }> = ({ children }) => <>{children}</>;

// ---------- 單個數值的取樣（復刻 motion-dom JSAnimation.tick） ----------

const DEFAULTS: Record<string, number> = {
  opacity: 1, scale: 1, scaleX: 1, scaleY: 1, x: 0, y: 0, z: 0, translateX: 0, translateY: 0,
  rotate: 0, rotateX: 0, rotateY: 0, rotateZ: 0, skew: 0, skewX: 0, skewY: 0,
  pathLength: 1, pathOffset: 0, pathSpacing: 1, strokeDashoffset: 0, fillOpacity: 1, strokeOpacity: 1,
};
const num = (v: any) => (typeof v === "string" && /^-?[\d.]+$/.test(v.trim()) ? parseFloat(v) : v);
const defaultFor = (key: string, props: any) => {
  if (props[key] !== undefined) return num(props[key]);
  if (key in DEFAULTS) return DEFAULTS[key];
  if (key === "strokeWidth") return 2;
  return undefined;
};

type Resolved = { value: any; end: number };

export function sampleValue(
  key: string,
  from: any,
  target: any,
  transition: any,
  tSec: number,
  extraDelay: number,
  cycles: number,
  instant: boolean,
): Resolved {
  const vt = getValueTransition(transition, key) || {};
  const delay = (vt.delay || transition?.delay || 0) + extraDelay;
  const kf: any[] = Array.isArray(target) ? [...target] : [null, target];
  if (kf[0] === null || kf[0] === undefined) kf[0] = from;
  for (let i = 1; i < kf.length; i++) if (kf[i] === null || kf[i] === undefined) kf[i] = kf[i - 1];
  if (kf[0] === undefined) kf[0] = kf[kf.length - 1];
  // 數字與帶單位字串混用（未寫 initial 時起點是 0，目標是 "2px"）：motion 會先讀 DOM 統一單位，這裡按目標單位補齊
  const unitKf = kf.find((v) => typeof v === "string" && /^-?[\d.]+[a-z%]+$/i.test(v.trim()));
  if (unitKf) {
    const unit = unitKf.trim().replace(/^-?[\d.]+/, "");
    for (let i = 0; i < kf.length; i++) if (typeof kf[i] === "number") kf[i] = `${kf[i]}${unit}`;
  }
  const o: any = { keyframes: kf, ease: "easeOut", velocity: 0, ...vt };
  if (!isTransitionDefined(vt)) Object.assign(o, getDefaultTransition(key as any, o));
  if (o.from !== undefined) kf[0] = o.from;
  let repeat = o.repeat ?? 0;
  if (!Number.isFinite(repeat)) repeat = Math.max(0, cycles - 1);
  const repeatDelay = (o.repeatDelay || 0) * 1000;
  const final = getFinalKeyframe(kf, { repeat, repeatType: o.repeatType });
  if (instant || o.type === false || (o.duration === 0 && !repeatDelay) || kf.length === 1) {
    return { value: final, end: delay };
  }
  const opts: any = { ...o, keyframes: kf, velocity: 0 };
  if (o.duration !== undefined) opts.duration = o.duration * 1000;
  const isSpring = o.type === "spring";
  const factory: any = isSpring ? springGen : keyframesGen;
  let mixer: ((p: number) => any) | null = null;
  let genKf = kf;
  if (isSpring) {
    genKf = [kf[0], kf[kf.length - 1]];
    if (typeof genKf[0] !== "number" || typeof genKf[1] !== "number") {
      const m = mix(genKf[0], genKf[1]) as (p: number) => any;
      mixer = (v) => m(v / 100);
      genKf = [0, 100];
    }
  }
  const gen = factory({ ...opts, keyframes: genKf });
  const mirrored = o.repeatType === "mirror" ? factory({ ...opts, keyframes: [...genKf].reverse() }) : null;
  const calc = gen.calculatedDuration ?? calcGeneratorDuration(gen);
  const resolvedDur = calc + repeatDelay;
  const total = resolvedDur * (repeat + 1) - repeatDelay;
  const endSec = delay + total / 1000;
  const tMs = (tSec - delay) * 1000;
  if (tMs < 0) return { value: kf[0], end: endSec };
  if (tMs >= total) return { value: final, end: endSec };
  let elapsed = tMs;
  let g = gen;
  if (repeat) {
    const progress = Math.min(tMs, total) / resolvedDur;
    let it = Math.floor(progress);
    let ip = progress % 1;
    if (!ip && progress >= 1) ip = 1;
    if (ip === 1) it--;
    it = Math.min(it, repeat + 1);
    if (it % 2) {
      if (o.repeatType === "reverse") {
        ip = 1 - ip;
        if (repeatDelay) ip -= repeatDelay / resolvedDur;
      } else if (o.repeatType === "mirror" && mirrored) g = mirrored;
    }
    elapsed = Math.min(1, Math.max(0, ip)) * resolvedDur;
  }
  const v = g.next(elapsed).value;
  return { value: mixer ? mixer(v) : v, end: endSec };
}

// ---------- 變體解析 ----------

const resolveDef = (def: Def | undefined, variants: any, custom: any): Record<string, any> | null => {
  if (def === undefined || def === null || (def as any) === false) return null;
  let v: any = def;
  if (typeof def === "string") v = variants?.[def];
  if (typeof v === "function") v = v(custom);
  return v && typeof v === "object" ? v : null;
};
const SKIP = new Set(["transition", "transitionEnd"]);

// 父級把「事件來源 + 給孩子的延遲」傳下去
type Source = {
  events: () => Ev[];
  offset: (def: Def) => number;
  labelsOnly: boolean;
  controls: Controls | null;
};
type VCtx = { source: Source | null; initial: any; childOffset: (def: Def, i: number) => number; n: number };
const VariantCtx = createContext<VCtx | null>(null);
const IndexCtx = createContext<number>(0);

const MOTION_PROPS = new Set([
  "variants", "initial", "animate", "exit", "transition", "custom", "inherit",
  "whileHover", "whileTap", "whileFocus", "whileDrag", "whileInView", "viewport",
  "onAnimationStart", "onAnimationComplete", "onUpdate", "layout", "layoutId",
  "drag", "dragConstraints", "onHoverStart", "onHoverEnd", "transformTemplate",
]);

function makeMotion(tag: string) {
  const C = forwardRef<any, any>((props, ref) => {
    const scope = useContext(IconScope);
    const parent = useContext(VariantCtx);
    const index = useContext(IndexCtx);
    const key = useRef({}).current;
    const { variants, initial, animate, custom, transition, style, children } = props;
    const rest: any = {};
    for (const k in props) if (!MOTION_PROPS.has(k) && k !== "style" && k !== "children") rest[k] = props[k];

    let source: Source | null = null;
    if (animate && animate.__isControls) {
      const c = animate as Controls;
      source = { events: () => c.events, offset: () => 0, labelsOnly: false, controls: c };
    } else if (animate !== undefined && animate !== null && typeof animate !== "boolean") {
      const ev: Ev[] = [{ def: animate, t: 0 }];
      source = { events: () => ev, offset: () => 0, labelsOnly: false, controls: null };
    } else if (parent?.source && variants && props.inherit !== false) {
      const p = parent;
      source = {
        events: () => p.source!.events().filter((e) => typeof e.def === "string"),
        offset: (def) => p.source!.offset(def) + p.childOffset(def, index),
        labelsOnly: true,
        controls: p.source!.controls,
      };
    }
    const initialDef = initial !== undefined ? initial : source?.labelsOnly ? parent?.initial : undefined;
    const cycles = scope?.cycles ?? 1;

    // 註冊到 controls，供 await 計算時長
    if (source?.controls) {
      const src = source;
      src.controls!.members.set(key, {
        duration: (def, override) => {
          if (src.labelsOnly && typeof def !== "string") return 0;
          const tg = resolveDef(def, variants, custom);
          if (!tg) return 0;
          const tr = override ?? tg.transition ?? transition ?? {};
          let d = 0;
          for (const k in tg) {
            if (SKIP.has(k)) continue;
            const r = sampleValue(k, defaultFor(k, props), tg[k], tr, 0, src.offset(def), cycles, false);
            d = Math.max(d, r.end);
          }
          return d;
        },
      });
    }

    // 靜止值
    const restVals: Record<string, any> = {};
    const initTarget =
      initialDef === false
        ? resolveDef(source?.events()[0]?.def, variants, custom)
        : resolveDef(initialDef, variants, custom);
    if (initTarget)
      for (const k in initTarget) {
        if (SKIP.has(k)) continue;
        const v = initTarget[k];
        restVals[k] = Array.isArray(v) ? v[initialDef === false ? v.length - 1 : 0] : v;
      }

    const t = scope ? scope.t : 0;
    const events = source ? [...source.events()].sort((a, b) => a.t - b.t) : [];
    const memo = new Map<string, Record<string, any>>();
    const evalAt = (tSec: number, upto: number): Record<string, any> => {
      if (upto < 0) return { ...restVals };
      const mk = `${tSec}|${upto}`;
      const hit = memo.get(mk);
      if (hit) return { ...hit };
      const e = events[upto];
      let out: Record<string, any>;
      if (tSec < e.t) out = evalAt(tSec, upto - 1);
      else {
        out = evalAt(tSec, upto - 1);
        const tg = resolveDef(e.def, variants, custom);
        if (tg) {
          const fromVals = evalAt(e.t, upto - 1);
          const tr = e.override ?? tg.transition ?? transition ?? {};
          const off = source!.offset(e.def);
          for (const k in tg) {
            if (SKIP.has(k)) continue;
            const from = fromVals[k] !== undefined ? fromVals[k] : defaultFor(k, props);
            out[k] = sampleValue(k, from, tg[k], tr, tSec - e.t, off, cycles, !!e.instant).value;
          }
        }
      }
      memo.set(mk, out);
      return { ...out };
    };
    const animated = evalAt(t, events.length - 1);

    // 與 motion 相同的渲染路徑：style 裡的靜態值也算進 latest
    // motion 只把 style 裡的 transform 類與 origin* 當作動畫值，其餘當原始 CSS，且被生成的樣式覆蓋
    // （所以 style={{transformOrigin:"12px 12px"}} 一旦有 transform 就會被 50% 50% + fill-box 蓋掉，與原庫一致）
    const latest: Record<string, any> = {};
    const rawStyle: Record<string, any> = {};
    if (style)
      for (const k in style) {
        if (style[k] === undefined) continue;
        if (transformProps.has(k) || k.startsWith("origin")) latest[k] = style[k];
        else rawStyle[k] = style[k];
      }
    for (const k in animated) if (animated[k] !== undefined) latest[k] = animated[k];
    const state: any = { style: {}, vars: {}, transform: {}, transformOrigin: {}, attrs: {} };
    const isSVG = tag === "svg";
    const svgFamily = SVG_TAGS.has(tag);
    let outProps: any;
    if (svgFamily) {
      buildSVGAttrs(state, latest, isSVG, undefined, style);
      outProps = { ...rest, ...state.attrs, style: { ...rawStyle, ...state.style, ...state.vars } };
    } else {
      buildHTMLStyles(state, latest, undefined);
      outProps = { ...rest, style: { ...rawStyle, ...state.style, ...state.vars } };
    }

    // 子元素：variant 傳遞 + staggerChildren
    let kids = children;
    let n = 0;
    React.Children.forEach(children, (c: any) => c?.type?.__motion && n++);
    const ctx: VCtx = {
      source,
      initial: typeof initialDef === "string" ? initialDef : parent?.initial,
      n,
      childOffset: (def, i) => {
        const tg = resolveDef(def, variants, custom);
        const tr = tg?.transition ?? transition ?? {};
        const stagger = tr.staggerChildren || 0;
        const dc = typeof tr.delayChildren === "number" ? tr.delayChildren : 0;
        const idx = tr.staggerDirection === -1 ? n - 1 - i : i;
        return dc + idx * stagger;
      },
    };
    let i = 0;
    kids = React.Children.map(children, (c: any) => {
      if (c?.type?.__motion) return <IndexCtx.Provider value={i++}>{c}</IndexCtx.Provider>;
      return c;
    });
    return React.createElement(tag, { ...outProps, ref }, <VariantCtx.Provider value={ctx}>{kids}</VariantCtx.Provider>);
  });
  (C as any).__motion = true;
  C.displayName = `motion.${tag}`;
  return C;
}

const SVG_TAGS = new Set([
  "svg", "g", "path", "line", "circle", "rect", "ellipse", "polyline", "polygon", "text", "tspan", "use", "defs", "mask", "clipPath", "linearGradient", "radialGradient", "stop",
]);
const cache: Record<string, any> = {};
export const motion: Record<string, any> = new Proxy(
  {},
  { get: (_, tag: string) => (cache[tag] ??= makeMotion(tag)) },
);

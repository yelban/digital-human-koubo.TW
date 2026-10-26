// 科技評測質感派（MKBHD / 影視颶風 / 何同學 實測，見 packaging-research/reports/2）：
// 關鍵詞圖示堆疊、玻璃資料面板（跑分 / 參數條）、里程錶數字滾動、官方文件慢推 + 中文譯句熒光底。
import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile } from "remotion";
import { C, F, FONT, clamp, ease, lerp, sp, useT } from "./core";
import { NotoEmoji } from "./NotoEmoji";

/** 關鍵詞堆疊：主播說到「效能 / 續航 / 發熱」時身旁依次彈出 圖示 + 彩色詞（0.3 秒彈入，間隔 0.5–0.9 秒），結束一起模糊淡出。 */
export const KeywordStack: React.FC<{ items: Array<{ t: string; at: number; icon?: string; color?: string }>; until: number; x?: number; y?: number; gap?: number }> = ({ items, until, x, y, gap }) => {
  const { f, t, W, H } = useT();
  if (!items.length || t < items[0].at - 0.05 || t > until) return null;
  const out = lerp(f, until - 0.35, until, 0, 1, ease.inOut);
  const sz = H * (W > H ? 0.075 : 0.05);
  return (
    <div style={{ position: "absolute", left: x ?? W * 0.62, top: y ?? H * 0.26, opacity: 1 - out, filter: `blur(${out * 14}px)` }}>
      {items.map((it, k) => {
        if (t < it.at) return null;
        const p = sp(f, it.at, 11, 260, 0.55);
        return (
          <div key={k} style={{ display: "flex", alignItems: "center", gap: sz * 0.35, marginBottom: gap ?? sz * 0.45, transform: `translateX(${(1 - p) * 60}px) scale(${0.7 + 0.3 * p})`, opacity: Math.min(1, p * 1.6), transformOrigin: "0 50%" }}>
            {it.icon && <NotoEmoji char={it.icon} at={F(it.at)} size={sz * 1.15} />}
            <span style={{ fontFamily: FONT.zh, fontWeight: 900, fontSize: sz, color: it.color ?? [C.cyan, C.yellow, C.pink, C.green][k % 4], textShadow: "0 6px 24px rgba(0,0,0,.45)" }}>{it.t}</span>
          </div>
        );
      })}
    </div>
  );
};

/** 玻璃資料面板：深色毛玻璃卡 0.6 秒上浮入場，條形和數字一起滾到終值（1.8 秒）；highlight 那一行用產品色。 */
export const GlassPanel: React.FC<{ at: number; until: number; title: string; unit?: string; rows: Array<{ label: string; value: number; highlight?: boolean }>; x?: number; y?: number; w?: number; color?: string; note?: string }> = ({ at, until, title, unit = "", rows, x, y, w, color = C.orange, note }) => {
  const { f, t, W, H } = useT();
  if (t < at || t > until) return null;
  const p = lerp(f, at, at + 0.6, 0, 1, ease.out), out = lerp(f, until - 0.3, until, 0, 1);
  const g = lerp(f, at + 0.4, at + 2.2, 0, 1, ease.out);
  const mx = Math.max(...rows.map((r) => r.value));
  const pw = w ?? W * (W > H ? 0.42 : 0.86);
  return (
    <div style={{ position: "absolute", left: x ?? W * 0.52, top: y ?? H * 0.2, width: pw, padding: H * 0.03, borderRadius: 26, background: "rgba(18,18,22,.62)", backdropFilter: "blur(22px)", border: "1px solid rgba(255,255,255,.14)",
      boxShadow: "0 30px 80px rgba(0,0,0,.45)", opacity: p * (1 - out), transform: `translateY(${(1 - p) * 50}px)` }}>
      <div style={{ fontFamily: FONT.zh, fontWeight: 700, fontSize: H * 0.03, color: "rgba(255,255,255,.65)", marginBottom: H * 0.025 }}>{title}</div>
      {rows.map((r, k) => (
        <div key={k} style={{ marginBottom: H * 0.022 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontFamily: FONT.zh, fontWeight: r.highlight ? 800 : 600, fontSize: H * 0.028, color: r.highlight ? "#fff" : "rgba(255,255,255,.7)" }}>
            <span>{r.label}</span><span style={{ fontFamily: FONT.en, fontVariantNumeric: "tabular-nums", color: r.highlight ? color : undefined }}>{Math.round(r.value * g).toLocaleString("en-US")}{unit}</span>
          </div>
          <div style={{ height: H * 0.012, borderRadius: 99, background: "rgba(255,255,255,.1)", marginTop: 8 }}><div style={{ width: `${(r.value / mx) * g * 100}%`, height: "100%", borderRadius: 99, background: r.highlight ? color : "rgba(255,255,255,.45)" }} /></div>
        </div>
      ))}
      {note && <div style={{ fontFamily: FONT.zh, fontSize: H * 0.018, color: "rgba(255,255,255,.4)", marginTop: 6 }}>{note}</div>}
    </div>
  );
};

/** 里程錶：大數字逐位滾動（1.2 秒，高位先停），單位 0.58 倍，標籤用產品色。 */
export const Odometer: React.FC<{ at: number; until: number; value: string; unit?: string; label?: string; x?: number; y?: number; size?: number; color?: string; labelColor?: string }> = ({ at, until, value, unit, label, x, y, size, color = "#fff", labelColor = C.orange }) => {
  const { f, t, W, H } = useT();
  if (t < at || t > until) return null;
  const sz = size ?? H * 0.17;
  const digits = Array.from(value);
  const nd = digits.filter((d) => /\d/.test(d)).length;
  let di = 0;
  const out = lerp(f, until - 0.3, until, 0, 1);
  return (
    <div style={{ position: "absolute", left: x ?? 0, right: x === undefined ? 0 : undefined, top: y ?? H * 0.36, textAlign: x === undefined ? "center" : "left", opacity: (1 - out) * lerp(f, at, at + 0.15, 0, 1) }}>
      {label && <div style={{ fontFamily: FONT.zh, fontWeight: 700, fontSize: sz * 0.2, color: labelColor, marginBottom: sz * 0.05, letterSpacing: 2 }}>{label}</div>}
      <div style={{ display: "inline-flex", alignItems: "baseline", fontFamily: FONT.en, fontWeight: 700, fontSize: sz, color, letterSpacing: -sz * 0.02, lineHeight: 1 }}>
        {digits.map((d, k) => {
          if (!/\d/.test(d)) return <span key={k}>{d}</span>;
          const idx = di++;
          const stop = at + 0.4 + (1.2 * (idx + 1)) / nd;          // 高位先停
          const spin = interpolate(f, [F(at), F(stop)], [0, 1], { ...clamp, easing: ease.out });
          const n = Number(d) + 10 * 2;                              // 先多滾兩圈
          const pos = spin * n;
          return (
            <span key={k} style={{ display: "inline-block", height: sz, overflow: "hidden", position: "relative", width: sz * 0.6 }}>
              <span style={{ position: "absolute", left: 0, top: -(pos % 10) * sz, display: "flex", flexDirection: "column" }}>
                {Array.from({ length: 11 }, (_, j) => <span key={j} style={{ height: sz, lineHeight: `${sz}px`, textAlign: "center", width: sz * 0.6 }}>{j % 10}</span>)}
              </span>
            </span>
          );
        })}
        {unit && <span style={{ fontFamily: FONT.zh, fontSize: sz * 0.58 * 0.6, marginLeft: sz * 0.08, color: "rgba(255,255,255,.8)" }}>{unit}</span>}
      </div>
    </div>
  );
};

/** 官方文件慢推：截圖（或渲染的英文原文）緩慢推近 + 底部黃色熒光中文譯句 + 左上灰色來源角標。 */
export const SourceDoc: React.FC<{ at: number; until: number; src: string; iw: number; ih: number; zh: string; source: string; focusY?: number }> = ({ at, until, src, iw, ih, zh, source, focusY = 0.4 }) => {
  const { f, t, W, H } = useT();
  if (t < at || t > until) return null;
  const z = lerp(f, at, until, 1.0, 1.12, (x) => x);
  const base = Math.max(W / iw, H / ih);
  const zp = lerp(f, at + 0.5, at + 0.9, 0, 1, ease.inOut);
  return (
    <AbsoluteFill style={{ background: "#111", overflow: "hidden" }}>
      <Img src={staticFile(src)} style={{ position: "absolute", left: (W - iw * base * z) / 2, top: H * 0.5 - ih * base * z * focusY, width: iw * base * z, height: ih * base * z, filter: "brightness(.55) blur(.4px)" }} />
      <div style={{ position: "absolute", left: W * 0.04, top: H * 0.05, fontFamily: FONT.zh, fontWeight: 600, fontSize: H * 0.022, color: "rgba(255,255,255,.7)", background: "rgba(0,0,0,.45)", padding: "6px 14px", borderRadius: 8 }}>來源：{source}</div>
      <div style={{ position: "absolute", left: W * 0.08, right: W * 0.08, bottom: H * 0.16, textAlign: "center" }}>
        <span style={{ position: "relative", display: "inline", fontFamily: FONT.zh, fontWeight: 800, fontSize: H * 0.05, color: zp > 0.6 ? "#111" : "#fff", lineHeight: 1.6,
          backgroundImage: `linear-gradient(${C.yellow}, ${C.yellow})`, backgroundRepeat: "no-repeat", backgroundSize: `${zp * 100}% 100%`, boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone", padding: "2px 10px" }}>{zh}</span>
      </div>
    </AbsoluteFill>
  );
};

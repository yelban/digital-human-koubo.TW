// 圖鑑演示：每個元件一段 3–5 秒的獨立 Composition，用真實素材（數位人、場景圖、截圖）演示用法。
import React from "react";
import { AbsoluteFill, Img, OffthreadVideo, staticFile } from "remotion";
import { C, FONT, Sfx } from "../kit/core";
import { FreezeFrame, HandDraw, Highlight, ZoomFocus } from "../kit/Annotate";
import { ChapterCard, Countdown, Counter, LowerThird, RetentionCaption, SourceTag, SpecCard } from "../kit/Text";
import { CompareWipe, Danmaku, PaperCollage, ProgressChapters, ReactionPop, TeaserColdOpen } from "../kit/Overlay";
import { MapRoute } from "../kit/Map";
import { ArchiveCards, BarCompare, CalloutPill, DocFocus, GhostWord, LeaderLabel, LineDraw, PunchInHost, RecapBoard, SearchTyping, SlamText, TornStrip, TypedNameTag } from "../kit/Explain";
import { NumberSpike, ProgressTracker, ReviewCards, WordStack } from "../kit/Beast";
import { GlassPanel, KeywordStack, Odometer, SourceDoc } from "../kit/Polish";
import { TextBehind } from "../kit/Depth";
import { Aside, ColdOpenFreeze, EvidenceCard, GlitchInterstitial, HostFloaters, MemeWindow, NamePlate, PollPop, TiltLine } from "../kit/Wangan";

const HostH: React.FC<{ dim?: number }> = ({ dim = 0 }) => (
  <AbsoluteFill><OffthreadVideo src={staticFile("media/host_h.mp4")} muted style={{ width: "100%", height: "100%", objectFit: "cover", filter: `brightness(${1 - dim})` }} /></AbsoluteFill>
);
const Tag: React.FC<{ n: string; d: string }> = ({ n, d }) => (
  <div style={{ position: "absolute", left: 30, bottom: 26, fontFamily: FONT.zh, fontSize: 24, color: "#fff", background: "rgba(0,0,0,.6)", padding: "6px 14px", borderRadius: 8, zIndex: 99 }}><b style={{ color: C.yellow }}>{n}</b> · {d}</div>
);

export const DemoRetention: React.FC = () => (
  <AbsoluteFill><HostH />
    <RetentionCaption y={780} words={[{ t: "一張", at: 0.3 }, { t: "照片", at: 0.55, key: true }, { t: "做出", at: 0.95 }, { t: "數位人", at: 1.2, key: true }, { t: "只要", at: 1.8 }, { t: "23 積分", at: 2.1, key: true }]} />
    <Sfx at={0.55} name="pop" vol={0.35} /><Sfx at={1.2} name="pop" vol={0.35} /><Sfx at={2.1} name="ding" vol={0.4} />
    <Tag n="RetentionCaption" d="留存大字幕 · 逐詞砸出、關鍵詞變色" /></AbsoluteFill>
);
export const DemoZoomFocus: React.FC = () => (
  <AbsoluteFill style={{ background: "#1a1a1f" }}>
    <ZoomFocus src="media/screen.png" iw={2880} ih={1800} at={0.6} until={3.6} focus={{ x: 2520, y: 30, w: 330, h: 70 }} label="右上角點「註冊」" box={{ x: 120, y: 80, w: 1680, h: 920 }} />
    <Sfx at={0.6} name="whoosh" vol={0.4} /><Sfx at={1.2} name="click" vol={0.5} />
    <Tag n="ZoomFocus" d="螢幕錄影 / 截圖推近聚焦 + 壓暗 + 標籤" /></AbsoluteFill>
);
export const DemoHandDraw: React.FC = () => (
  <AbsoluteFill><Img src={staticFile("media/shop.jpg")} style={{ position: "absolute", left: 660, top: 0, height: 1080 }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg,#111 0 34%,transparent 34% 66%,#111 66%)" }} />
    <HandDraw kind="circle" at={0.4} x={760} y={300} w={200} h={330} color={C.yellow} />
    <HandDraw kind="arrow" at={1.1} x={760} y={380} w={200} h={200} from={[300, 200]} color={C.yellow} />
    <div style={{ position: "absolute", left: 120, top: 120, fontFamily: FONT.zh, fontWeight: 900, fontSize: 64, color: "#fff" }}>道具也是 AI 合成的</div>
    <HandDraw kind="underline" at={1.7} x={120} y={130} w={540} h={70} color={C.red} />
    <Sfx at={0.4} name="swish-1" vol={0.35} /><Sfx at={1.1} name="swish-2" vol={0.35} />
    <Tag n="HandDraw" d="手繪圈 / 箭頭 / 下劃線 · 描邊生長" /></AbsoluteFill>
);
export const DemoFreeze: React.FC = () => (
  <AbsoluteFill><HostH />
    <FreezeFrame src="media/ad.jpg" at={0.8} until={3.6} label="等等！" note="耳機也是 AI 生成的，不是實拍" mark={{ x: 640, y: 560, w: 260, h: 220 }} />
    <Sfx at={0.8} name="impact" vol={0.5} />
    <Tag n="FreezeFrame" d="定格 + 去色 + 大字 + 圈注（打斷節奏）" /></AbsoluteFill>
);
export const DemoLowerThird: React.FC = () => (
  <AbsoluteFill><HostH />
    <LowerThird at={0.4} until={3.6} name="Berryxia 的數位人" title="AI 影片創作者 · 用本人照片生成" />
    <SourceTag at={0.8} until={3.6} text="形象：GPT Image 2.5 · 口播：Grok Video 1.5" />
    <Tag n="LowerThird + SourceTag" d="人名條 + 出處角標" /></AbsoluteFill>
);
export const DemoCounter: React.FC = () => (
  <AbsoluteFill style={{ background: C.ink }}>
    <Counter at={0.4} dur={1.3} to={3409} unit="積分" label="這期總共花了" y={330} />
    <Countdown at={0.2} seconds={4} label="生成中" />
    <Sfx at={0.4} name="processing" vol={0.3} /><Sfx at={1.7} name="ding" vol={0.5} />
    <Tag n="Counter + Countdown" d="數字滾動落地彈一下 · 倒計時最後 3 秒變紅" /></AbsoluteFill>
);
export const DemoChapter: React.FC = () => (
  <AbsoluteFill><HostH />
    <ChapterCard at={0.3} until={3.4} n="02" title="進場景" sub="同一個數位人，換個地方開工" color={C.green} />
    <Sfx at={0.3} name="whoosh" vol={0.45} />
    <Tag n="ChapterCard" d="章節卡 · 色條掃過 + 大序號" /></AbsoluteFill>
);
export const DemoSpec: React.FC = () => (
  <AbsoluteFill style={{ background: "#0B0B0D" }}>
    <Img src={staticFile("media/ad.jpg")} style={{ position: "absolute", left: -200, top: 0, height: 1080, filter: "brightness(.85)" }} />
    <AbsoluteFill style={{ background: "linear-gradient(90deg, transparent 40%, #0B0B0D 62%)" }} />
    <SpecCard at={0.4} until={3.8} rows={[{ k: "續航", v: "40", u: "小時" }, { k: "重量", v: "4.8", u: "克 / 只" }, { k: "價格", v: "¥599" }]} x={1240} y={220} />
    <Tag n="SpecCard" d="質感參數卡 · 大數字小單位、留白、逐行淡入（示意資料）" /></AbsoluteFill>
);
export const DemoDanmaku: React.FC = () => (
  <AbsoluteFill><HostH />
    <Danmaku items={[{ t: "真的假的？", at: 0.1 }, { t: "這是 AI？？", at: 0.4, hot: true }, { t: "口型好準", at: 0.8 }, { t: "求教學", at: 1.1 }, { t: "23 積分就能做？", at: 1.4, hot: true }, { t: "已三連", at: 1.9 }, { t: "前排", at: 2.3 }]} />
    <Tag n="Danmaku" d="彈幕 · 替觀眾說出質疑 / 起鬨" /></AbsoluteFill>
);
export const DemoReaction: React.FC = () => (
  <AbsoluteFill><HostH />
    <ReactionPop at={0.4} emoji="😱" caption="才 23 積分？" x={1380} y={380} />
    <ReactionPop at={1.9} emoji="🤯" caption="口型也太準" x={120} y={420} rot={-8} />
    <Sfx at={0.4} name="pop" vol={0.45} /><Sfx at={1.9} name="pop" vol={0.45} />
    <Tag n="ReactionPop" d="反應貼紙 · 動態表情 + 吐槽（不用影視劇截圖）" /></AbsoluteFill>
);
export const DemoProgress: React.FC = () => (
  <AbsoluteFill><HostH />
    <ProgressChapters total={4} chapters={[{ at: 0, t: "① 接工具" }, { at: 1.2, t: "② 做形象" }, { at: 2.4, t: "③ 配聲音" }, { at: 3.2, t: "④ 進場景" }]} />
    <Tag n="ProgressChapters" d="頂部進度條 + 章節刻度" /></AbsoluteFill>
);
export const DemoTeaser: React.FC = () => (
  <AbsoluteFill>
    <TeaserColdOpen clips={[{ src: "media/cat.jpg", img: true, dur: 0.55, label: "貓也能開口？" }, { src: "media/travel.jpg", img: true, dur: 0.55, label: "日語導覽" }, { src: "media/ad.jpg", img: true, dur: 0.55, label: "英文廣告" }, { src: "media/shop.jpg", img: true, dur: 0.55, label: "直播帶貨" }]} question={"這些全是\n一張照片做的"} />
    {[0, 0.55, 1.1, 1.65].map((a) => <Sfx key={a} at={a} name="cut" vol={0.45} />)}<Sfx at={2.2} name="impact" vol={0.5} />
    <Tag n="TeaserColdOpen" d="開場預告閃回 → 問題字卡" /></AbsoluteFill>
);
export const DemoCompare: React.FC = () => (
  <AbsoluteFill style={{ background: "#111" }}>
    <CompareWipe at={0.5} a="media/class.jpg" b="media/ad.jpg" la="原照片場景" lb="換成廣告棚" box={{ x: 160, y: 90, w: 1600, h: 900 }} />
    <Sfx at={0.5} name="swish-2" vol={0.45} />
    <Tag n="CompareWipe" d="前後對比擦除" /></AbsoluteFill>
);
export const DemoPaper: React.FC = () => (
  <AbsoluteFill>
    <PaperCollage at={0.1} title="一張照片，四個場景" items={[{ src: "media/shop.jpg", x: 140, y: 250, w: 300, caption: "直播間" }, { src: "media/ad.jpg", x: 520, y: 300, w: 520, caption: "廣告棚" }, { src: "media/travel.jpg", x: 1110, y: 230, w: 290, caption: "京都" }, { src: "media/class.jpg", x: 1440, y: 330, w: 420, caption: "教室" }]} note={{ text: "都沒出門！", x: 1180, y: 860, at: 2.0 }} />
    {[0.3, 0.65, 1.0, 1.35].map((a) => <Sfx key={a} at={a} name="paper-place-1" vol={0.5} />)}
    <Tag n="PaperCollage" d="紙張拼貼 · 白邊照片 + 膠帶 + 手寫批註" /></AbsoluteFill>
);
export const DemoHighlight: React.FC = () => (
  <AbsoluteFill style={{ background: C.paper, padding: 140 }}>
    <div style={{ fontFamily: FONT.serif, fontSize: 52, color: C.ink, lineHeight: 1.9, maxWidth: 1500 }}>
      （示意文字）生成數位人口播之前，<Highlight at={0.5}>系統會先告訴你要花多少積分</Highlight>，使用者確認後才開始生成；<Highlight at={1.6} color="rgba(255,90,138,.45)">先拍第 1 段確認音色</Highlight>，可以避免整批返工。
    </div>
    <Sfx at={0.5} name="swish-1" vol={0.3} /><Sfx at={1.6} name="swish-1" vol={0.3} />
    <Tag n="Highlight" d="熒光筆刷重點（原文 / 公告 / 文件）" /></AbsoluteFill>
);
export const DemoMap: React.FC = () => (
  <AbsoluteFill>
    <MapRoute theme="dark" title={{ text: "一個數位人，跑遍五個國家", at: 0.2 }}
      camera={[{ at: 0, lon: 100, lat: 25, zoom: 1 }, { at: 1.6, lon: 125, lat: 34, zoom: 2.6 }, { at: 3.8, lon: 125, lat: 34, zoom: 2.6 }]}
      highlight={[{ name: "China", at: 1.6 }, { name: "Japan", at: 2.2, color: C.pink }, { name: "South Korea", at: 2.6, color: C.cyan }]}
      pins={[{ name: "上海", lon: 121.5, lat: 31.2, at: 1.8 }, { name: "京都", lon: 135.8, lat: 35.0, at: 2.4, color: C.pink }, { name: "首爾", lon: 127.0, lat: 37.6, at: 2.8, color: C.cyan }]}
      routes={[{ from: [121.5, 31.2], to: [135.8, 35.0], at: 2.0 }, { from: [135.8, 35.0], to: [127.0, 37.6], at: 2.6 }]} />
    <Sfx at={1.8} name="pop" vol={0.4} /><Sfx at={2.4} name="pop" vol={0.4} /><Sfx at={2.8} name="pop" vol={0.4} />
    <Tag n="MapRoute" d="地圖推近 + 國家高亮 + 圖釘 + 航線生長" /></AbsoluteFill>
);

export const DemoMeme: React.FC = () => (
  <AbsoluteFill>
    <MemeWindow until={4} watermark="@你的頻道" items={[{ src: "media/cat.jpg", at: 0, caption: "本喵：又要加班？" }, { src: "media/dog.jpg", at: 1.3, caption: "突發：老闆說今天不開會", pos: "bottom" }, { src: "media/shop.jpg", at: 2.6, caption: "家人們誰懂啊" }]} />
    <div style={{ position: "absolute", left: 0, right: 0, top: 930, textAlign: "center", fontFamily: FONT.zh, fontWeight: 800, fontSize: 50, color: "#fff" }}>一句話配一張圖，觀眾的情緒就跟上了</div>
    <Sfx at={1.3} name="tap" vol={0.3} /><Sfx at={2.6} name="tap" vol={0.3} />
    <Tag n="MemeWindow" d="黑底梗圖窗 · 一句一圖硬切（素材用原創 IP 表情包）" /></AbsoluteFill>
);
export const DemoColdFreeze: React.FC = () => (
  <AbsoluteFill>
    <ColdOpenFreeze src="media/cat.mp4" freezeAt={1.6} until={4.2} title={["一隻貓", "憑什麼能帶貨？"]} vol="VOL.003" />
    <Sfx at={1.6} name="impact" vol={0.5} /><Sfx at={1.8} name="swish-2" vol={0.4} />
    <Tag n="ColdOpenFreeze" d="冷開場 → 定格去色 → 未完待續 → 片名卡 → 雪花轉場" /></AbsoluteFill>
);
export const DemoEvidence: React.FC = () => (
  <AbsoluteFill>
    <EvidenceCard src="media/screen.png" iw={2880} ih={1800} at={0.1} until={4} focus={{ x: 1810, y: 62 }} label="30% OFF 限時" labelAt={1.4} tilt={-14} source="截圖：renoise.ai 官網，2026-10" />
    <Sfx at={0.1} name="whoosh" vol={0.4} /><Sfx at={1.4} name="pop" vol={0.45} />
    <Tag n="EvidenceCard" d="證據截圖飛入 · 品牌色框 + 滑鼠 + 推近數值籤" /></AbsoluteFill>
);
export const DemoPoll: React.FC = () => (
  <AbsoluteFill><HostH />
    <PollPop at={0.3} until={4} options={[{ n: "1", t: "能看出是 AI", at: 0.9 }, { n: "2", t: "完全看不出", at: 2.0 }]} />
    <Sfx at={0.9} name="pop" vol={0.5} /><Sfx at={2.0} name="pop" vol={0.5} />
    <Tag n="PollPop" d="投票彈窗 · 評論區打 1 還是 2（揭曉前站隊）" /></AbsoluteFill>
);
export const DemoGlitch: React.FC = () => (
  <AbsoluteFill><HostH />
    <GlitchInterstitial at={1.2} dur={0.6} text="點贊關注" host="media/host_h.mp4" />
    <Sfx at={1.2} name="cut" vol={0.6} />
    <Tag n="GlitchInterstitial" d="0.5 秒故障插屏 · 中段號召" /></AbsoluteFill>
);
export const DemoNamePlate: React.FC = () => (
  <AbsoluteFill><Img src={staticFile("media/class.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "grayscale(1) brightness(.75)" }} />
    <NamePlate at={0.3} until={4} name="林老師" title="某培訓機構講師（示意角色）" x={140} y={700} quotes={[{ t: "三分鐘搞懂大模型", at: 1.0 }, { t: "不用寫一行程式碼", at: 1.7 }, { t: "一張照片就夠", at: 2.4 }]} qx={1080} qy={220} />
    {[1.0, 1.7, 2.4].map((a) => <Sfx key={a} at={a} name="pop" vol={0.4} />)}
    <Tag n="NamePlate" d="去色人物 + 雙層名牌 + 語錄藥丸氣泡" /></AbsoluteFill>
);
export const DemoFloaters: React.FC = () => (
  <AbsoluteFill><HostH />
    <HostFloaters at={0.2} until={4} windows={[{ src: "media/screen.png", pos: "tl", title: "renoise.ai" }, { src: "media/doc.png", pos: "tr", title: "外掛安裝" }]}
      chips={[{ t: "不用複製 API key", icon: "ok", at: 1.4, x: 120, y: 760 }, { t: "別裝來路不明的外掛", icon: "x", at: 2.2, x: 1240, y: 760 }]} />
    <Sfx at={1.4} name="pop" vol={0.4} /><Sfx at={2.2} name="pop" vol={0.4} />
    <Tag n="HostFloaters" d="主播旁懸浮窗 + 圖示小標籤（主播一直在畫面裡）" /></AbsoluteFill>
);
export const DemoAsideTilt: React.FC = () => (
  <AbsoluteFill><HostH dim={0.25} />
    <TiltLine at={0.3} until={2.4} text="照片不是重點，流程才是" keys={["流程"]} />
    <Aside items={[{ t: "剪輯師：這句我聽了八遍", at: 2.5, until: 4 }]} />
    <Sfx at={0.3} name="slam-1" vol={0.4} />
    <Tag n="TiltLine + Aside" d="傾斜金句逐字彈出 · 括號旁白吐槽" /></AbsoluteFill>
);

export const DemoDocFocus: React.FC = () => (
  <AbsoluteFill>
    <DocFocus at={0} until={4} source="示意文件（非真實公告）" title="數位人口播生成流程（示意）" paras={[[{ t: "為保證效果，系統會把口播稿切成不超過 15 秒的片段。" }, { t: "每段生成前都會先顯示預計消耗的積分，", focus: true }, { t: "使用者確認後才會開始生成，", hl: true, hlAt: 1.3 }, { t: "中途取消不扣費。" }], [{ t: "建議先生成第一段確認音色與口型，再批次生成其餘片段。" }]]} />
    <Sfx at={1.3} name="swish-1" vol={0.35} />
    <Tag n="DocFocus" d="句子聚焦：其他字壓暗 35% + 黃塊掃關鍵詞（示意公告）" /></AbsoluteFill>
);
export const DemoTypedName: React.FC = () => (
  <AbsoluteFill><HostH />
    <TypedNameTag at={0.3} until={4} name={"Berryxia\n的數位人"} title="用本人一張照片生成 · Grok Video 1.5" x={80} y={420} target={[880, 360]} />
    {[0.6, 0.75, 0.9, 1.05, 1.2, 1.35].map((a) => <Sfx key={a} at={a} name="key-1" vol={0.25} />)}
    <Tag n="TypedNameTag" d="手繪箭頭 + 粗襯線名字逐字打出" /></AbsoluteFill>
);
export const DemoPunchIn: React.FC = () => (
  <AbsoluteFill><PunchInHost src="media/host_h.mp4" cuts={[1.1, 2.0, 3.0]} />
    <Tag n="PunchInHost" d="跳切推近：同一條素材按句子邊界 1.0× ↔ 1.3× 硬切" /></AbsoluteFill>
);
export const DemoRecap: React.FC = () => (
  <AbsoluteFill>
    <RecapBoard at={0} until={4} reveal={[3, 2]} newAt={0.6} columns={[{ title: "為什麼難", color: "#C0504D", items: ["口型對不上", "聲音不統一", "畫面太單調"] }, { title: "怎麼辦", color: "#95C96B", items: ["用目標語言開口", "統一頻譜 + 房間混響"] }]} />
    <Sfx at={0.6} name="ding" vol={0.35} />
    <Tag n="RecapBoard" d="累積復盤板：每章回來亮一條新的" /></AbsoluteFill>
);
export const DemoSearch: React.FC = () => (
  <AbsoluteFill>
    <SearchTyping at={0} until={4} query="怎麼用一張照片做數位人" suggestions={["怎麼用一張照片做數位人 免費", "怎麼用一張照片做數位人 口型", "怎麼用一張照片做數位人 教學"]} />
    {Array.from({ length: 11 }).map((_, k) => <Sfx key={k} at={0.2 + k / 9} name={`key-${(k % 8) + 1}`} vol={0.2} />)}
    <Tag n="SearchTyping" d="搜尋框打字冷開場 + 聯想詞 + 推近（中性搜尋框，不仿品牌）" /></AbsoluteFill>
);
export const DemoPillLeader: React.FC = () => (
  <AbsoluteFill style={{ background: "#3B3A3A" }}>
    <Img src={staticFile("media/ad.jpg")} style={{ position: "absolute", left: 80, top: 190, height: 700, borderRadius: 20 }} />
    <CalloutPill at={0.3} until={4} text="AI 生成的耳機" sub="GPT Image 2.5 · 23 積分" x={330} y={360} color="#9F36CB" />
    <LeaderLabel at={1.1} until={4} target={[760, 330]} zh="同一張臉" en="Same face, new scene" len={560} tag="參考圖一張" />
    <LeaderLabel at={1.6} until={4} target={[800, 640]} zh="換了衣服" en="Outfit swapped" len={520} />
    <Sfx at={0.3} name="pop" vol={0.4} /><Sfx at={1.1} name="tap" vol={0.3} /><Sfx at={1.6} name="tap" vol={0.3} />
    <Tag n="CalloutPill + LeaderLabel" d="指標膠囊 · 引線雙語標註" /></AbsoluteFill>
);
export const DemoCharts: React.FC = () => (
  <AbsoluteFill>
    <LineDraw at={0} until={2.4} title="每段口播成本（積分）" series={[{ label: "720p", color: C.green, data: [17, 51, 85, 119, 153, 187, 221, 255] }, { label: "480p", color: "#E8E3D3", data: [10, 30, 50, 70, 90, 110, 130, 150] }]} xLabels={["1s", "3s", "5s", "7s", "9s", "11s", "13s", "15s"]} source="Renoise estimate_cost 實測 · 2026-10" />
    <BarCompare at={2.4} until={4.6} title="同一句 8 秒對比" ghost="Cost" rows={[{ label: "Grok Video 1.5 · 720p", value: 136, text: "136 積分" }, { label: "Wan 3.0 · 720p", value: 96, text: "96 積分", color: "#6B8F71" }]} />
    <Tag n="LineDraw + BarCompare" d="折線逐段畫出 + 末端標籤 · 對比條 + 鬼影大字" /></AbsoluteFill>
);
export const DemoSlam: React.FC = () => (
  <AbsoluteFill><HostH dim={0.15} />
    <SlamText at={0.3} until={3} lines={["一張照片", "就是一個主播"]} year="2026" />
    <Sfx at={0.3} name="slam-1" vol={0.5} /><Sfx at={0.8} name="slam-2" vol={0.5} />
    <Tag n="SlamText" d="衝擊句砸字 + 年份角標" /></AbsoluteFill>
);
export const DemoTorn: React.FC = () => (
  <AbsoluteFill><Img src={staticFile("media/class.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "brightness(.7)" }} />
    <TornStrip at={0.3} until={4} title="數位人進階" sub="VOL.003 · DIGITAL HUMAN" />
    <Sfx at={0.3} name="page-2" vol={0.5} />
    <Tag n="TornStrip" d="撕紙標題條（片名 / 章節）" /></AbsoluteFill>
);
export const DemoArchive: React.FC = () => (
  <AbsoluteFill>
    <ArchiveCards at={0} per={0.6} images={[{ src: "media/class.jpg", label: "講師 · 2026" }, { src: "media/shop.jpg", label: "直播間" }, { src: "media/travel.jpg", label: "京都 · 祇園" }, { src: "media/dog.jpg", label: "新聞台" }, { src: "media/cat.jpg", label: "寵物店" }, { src: "media/ad.jpg", label: "廣告棚" }]} />
    <Tag n="ArchiveCards" d="檔案卡快切（真實檔案請用公有領域素材）" /></AbsoluteFill>
);
export const DemoSpike: React.FC = () => (
  <AbsoluteFill><HostH />
    <NumberSpike at={0.3} until={4} text="23 積分" label="做一個數位人形象" pinAt={2.2} />
    <Sfx at={0.3} name="impact" vol={0.6} /><Sfx at={2.2} name="swish-1" vol={0.35} />
    <Tag n="NumberSpike" d="數字釘子：超大數字 0.5 秒縮到頂部 + 閃光 → 縮成角標常駐" /></AbsoluteFill>
);
export const DemoTracker: React.FC = () => (
  <AbsoluteFill><HostH />
    <ProgressTracker at={0} until={4} mode="steps" steps={["接工具", "做形象", "配聲音", "進場景"]} stepAt={[0, 1, 2, 3]} />
    <ProgressTracker at={0} until={4} from="一張照片" to="一條成品" icon="🎬" progress={[{ at: 0.2, v: 0.25 }, { at: 1.2, v: 0.5 }, { at: 2.2, v: 0.75 }, { at: 3.2, v: 1 }]} />
    <Tag n="ProgressTracker" d="常駐進度：步驟徽章 + 路線條" /></AbsoluteFill>
);
export const DemoWordStack: React.FC = () => (
  <AbsoluteFill>
    <WordStack until={3} words={[{ t: "一張照片", at: 0.2 }, { t: "六種語言", at: 0.6 }, { t: "四個場景", at: 1.0 }, { t: "0 拍攝", at: 1.4 }]} />
    {[0.2, 0.6, 1.0, 1.4].map((a) => <Sfx key={a} at={a} name="slam-3" vol={0.4} />)}
    <Tag n="WordStack" d="逐詞堆疊大字，一拍一個詞" /></AbsoluteFill>
);
export const DemoReviews: React.FC = () => (
  <AbsoluteFill><HostH dim={0.45} />
    <ReviewCards at={0.2} cards={[{ name: "小王", stars: 2, text: "數位人口型總對不上，看著很假" }, { name: "Lily", stars: 1, text: "聲音一段一個樣，混響忽遠忽近" }, { name: "阿杰", stars: 2, text: "畫面太單調，看兩分鐘就划走了" }]} />
    {[0.2, 1.3, 2.4].map((a) => <Sfx key={a} at={a} name="pop" vol={0.4} />)}
    <Tag n="ReviewCards" d="評論 / 差評卡連彈（示意評論，非真實使用者）" /></AbsoluteFill>
);

export const DemoKeyword: React.FC = () => (
  <AbsoluteFill><PunchInHost src="media/host_h.mp4" cuts={[1.6, 3.0]} levels={[{ s: 1 }, { s: 1.18, dx: -0.06 }, { s: 1.32, dx: 0.04 }]} />
    <KeywordStack until={3.8} items={[{ t: "形象", at: 0.3, icon: "🧑" }, { t: "聲音", at: 0.9, icon: "🎙️" }, { t: "口型", at: 1.5, icon: "👄" }]} x={1240} y={260} />
    {[0.3, 0.9, 1.5].map((a) => <Sfx key={a} at={a} name="pop" vol={0.35} />)}
    <Tag n="KeywordStack + 多檔景別" d="圖示彩色詞依次彈出 · 1.0/1.18/1.32 景別 + 左右偏置" /></AbsoluteFill>
);
export const DemoGlass: React.FC = () => (
  <AbsoluteFill><Img src={staticFile("media/ad.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "brightness(.6)" }} />
    <GlassPanel at={0.2} until={4} title="8 秒口播 · 720p 積分消耗（實測報價）" unit=" 積分" rows={[{ label: "Grok Video 1.5", value: 136, highlight: true }, { label: "Wan 3.0", value: 96 }]} note="Renoise estimate_cost 實測 · 2026-10" />
    <Tag n="GlassPanel" d="毛玻璃資料面板 · 條形和數字一起滾到終值" /></AbsoluteFill>
);
export const DemoOdometer: React.FC = () => (
  <AbsoluteFill style={{ background: "#0A0A0C" }}>
    <Odometer at={0.2} until={3.6} value="4833" unit="積分" label="帳戶餘額" />
    <Sfx at={0.2} name="processing" vol={0.3} /><Sfx at={1.8} name="ding" vol={0.45} />
    <Tag n="Odometer" d="里程錶逐位滾動，高位先停" /></AbsoluteFill>
);
export const DemoSourceDoc: React.FC = () => (
  <AbsoluteFill>
    <SourceDoc at={0} until={4} src="media/screen.png" iw={2880} ih={1800} zh="（示意）這裡放官方原文對應的中文譯句" source="示意截圖" focusY={0.2} />
    <Sfx at={0.5} name="swish-1" vol={0.3} />
    <Tag n="SourceDoc" d="官方文件慢推 + 中文譯句熒光底 + 來源角標" /></AbsoluteFill>
);

export const DemoTextBehind: React.FC = () => (
  <AbsoluteFill><HostH />
    <TextBehind src="media/host_h.mp4" cutout="media/host_h_cut.webm" at={0.3} until={2.3} lines={[{ t: "一張照片" }]} gradient={["#FFFFFF", "#B9C6DA"]} y={0.33} bgDim={0.15} />
    <TextBehind src="media/host_h.mp4" cutout="media/host_h_cut.webm" at={2.5} until={4.6} mode="count" lines={[{ t: "23", color: C.yellow, font: "en", size: 0.42 }]} count={{ to: 23, unit: "", dur: 0.9 }} y={0.3} bgDim={0.15} />
    <Sfx at={0.3} name="whoosh" vol={0.4} /><Sfx at={3.4} name="impact" vol={0.45} />
    <div style={{ position: "absolute", right: 70, top: 640, fontFamily: FONT.zh, fontWeight: 800, fontSize: 40, color: "#fff", opacity: 0 }} />
    <Tag n="TextBehind" d="景深字：文字 / 數字在人身後（Vision 去背，透明 webm 疊回）" /></AbsoluteFill>
);

export const DEMOS: Array<[string, React.FC, number]> = [
  ["RetentionCaption", DemoRetention, 3.5], ["ZoomFocus", DemoZoomFocus, 4.2], ["HandDraw", DemoHandDraw, 3.2], ["FreezeFrame", DemoFreeze, 4], ["LowerThird", DemoLowerThird, 4],
  ["Counter", DemoCounter, 4], ["ChapterCard", DemoChapter, 3.6], ["SpecCard", DemoSpec, 4.2], ["Danmaku", DemoDanmaku, 4.5], ["ReactionPop", DemoReaction, 3.8],
  ["ProgressChapters", DemoProgress, 4], ["TeaserColdOpen", DemoTeaser, 3.6], ["CompareWipe", DemoCompare, 3.2], ["PaperCollage", DemoPaper, 3.6], ["Highlight", DemoHighlight, 3], ["MapRoute", DemoMap, 4.2],
  ["MemeWindow", DemoMeme, 4], ["ColdOpenFreeze", DemoColdFreeze, 4.2], ["EvidenceCard", DemoEvidence, 4], ["PollPop", DemoPoll, 3.6], ["GlitchInterstitial", DemoGlitch, 2.4],
  ["NamePlate", DemoNamePlate, 3.8], ["HostFloaters", DemoFloaters, 3.8], ["TiltAside", DemoAsideTilt, 4],
  ["DocFocus", DemoDocFocus, 3.6], ["TypedNameTag", DemoTypedName, 3.6], ["PunchInHost", DemoPunchIn, 3.6], ["RecapBoard", DemoRecap, 3.2], ["SearchTyping", DemoSearch, 3.6], ["CalloutLeader", DemoPillLeader, 3.6],
  ["Charts", DemoCharts, 4.6], ["SlamText", DemoSlam, 3], ["TornStrip", DemoTorn, 3.2], ["ArchiveCards", DemoArchive, 3.6],
  ["NumberSpike", DemoSpike, 3.6], ["ProgressTracker", DemoTracker, 4], ["WordStack", DemoWordStack, 2.8], ["ReviewCards", DemoReviews, 4],
  ["TextBehind", DemoTextBehind, 4.8], ["KeywordStack", DemoKeyword, 3.8], ["GlassPanel", DemoGlass, 3.6], ["Odometer", DemoOdometer, 3.2], ["SourceDoc", DemoSourceDoc, 3.6],
];

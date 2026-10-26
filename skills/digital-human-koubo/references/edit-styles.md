# 剪輯模板

幾個模板都是 Remotion 工程，`node_modules` 用 `cp -cR` 從任一現有工程克隆（npm 源常 SSL 失敗）。時間軸全部來自逐字對齊（tl.json / timeline.json），改文案後重跑對齊即可。

| 風格 | 工程 | 入口 | 適合 |
|---|---|---|---|
| B 花字口播（資料驅動） | skill 內 templates/huazi-916 | src/Huazi.tsx + src/edit.json | 抖音 / 小紅書口播、帶貨、種草 |
| C 發布解讀 | templates/reference/launch-169 | src/Film.tsx | 新品發布、橫式 B 站 |
| D 教學 | templates/reference/tutorial-169 | src/Tutorial.tsx | 保姆級教學、操作演示 |
| E 多主播多語言 | templates/reference/multihost-169 | src/Tutorial.tsx（nar / clip / title / outro） | 能力展示、多場景、出海 |
| A 小林式解說 | finance-explainer skill 的 templates/engine | src/Episode.tsx + episode.json | 財經 / 科技事件解說 |

## 花字口播
新片一律用 templates/huazi-916（edit.json 驅動），欄位見 references/huazi.md。

## 渲染
`npx remotion render src/index.ts <Composition> out/raw.mp4 --concurrency=6` → `ffmpeg -af loudnorm=I=-16:TP=-1.5:LRA=11 -crf 20` 出片。抽幀檢查時一定要看過渡中間幀。

## 聲音統一（2026-10-24 教學第二期實測）
- **數位人影片軌一定要 `muted`**：畫面用 OffthreadVideo、聲音另鋪一條時，影片軌不靜音會雙聲疊加，差幾毫秒就梳狀濾波——聽感就是「刺耳、混響忽遠忽近」。
- Grok 分段生成的原聲：段間齒音差可達 13 dB、混響尾巴 60–380 ms。用 `scripts/voicefx/unify.py`：1/3 倍頻程頻譜向中位數匹配（±4 dB）→ 去齒音 + 3–7 kHz 輕收 → 同一個小房間 IR（原本溼的段 wet 少、乾的段多）→ 每段 -18 LUFS → 整片鋪 -60 dBFS 房間底噪。實測齒音段間差 13.2→5.9 dB。
- 只改音訊時不用重渲畫面：`AUDIO_ONLY=1 npx remotion render … out/mix.wav --codec=wav`（remotion.config.ts 裡 CRF/codec 要按 AUDIO_ONLY 跳過），再和舊畫面 mux。
- 換聲 + 保留 Grok 口型（MiMo 克隆重念 → 按逐字時間 WSOLA 對齊）實測口型差中位約 100 ms，全螢幕特寫能看出來；要換聲又要口型準，得用 Wan 3.0 參考音訊重生成畫面。
